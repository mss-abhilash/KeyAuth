from fastapi import APIRouter, HTTPException, Request
from backend.models import User, TypingSample, FailedAttempt
from backend.ml.feature_extractor import extract_features
from backend.ml.predict import verify_user
from backend.ml.train_model import train_model, model_exists, update_model
from backend.schemas import (
    PhraseResponse, TrainRequest, TrainResponse, 
    VerifyRequest, VerifyResponse
)
import random
from pathlib import Path

router = APIRouter(tags=["Typing Biometrics"])

# Load phrases from file
PHRASES_FILE = Path(__file__).parent.parent / "ml" / "phrases.txt"


def get_random_phrase() -> str:
    """Get a random phrase from the phrases file."""
    if not PHRASES_FILE.exists():
        return "The quick brown fox jumps over the lazy dog"
    
    with open(PHRASES_FILE, "r") as f:
        phrases = [line.strip() for line in f if line.strip()]
    
    return random.choice(phrases) if phrases else "The quick brown fox jumps over the lazy dog"


@router.get(
    "/phrase",
    response_model=PhraseResponse,
    summary="Get verification phrase",
    description="Returns a random phrase for the user to type during training or verification."
)
async def get_phrase():
    """
    Get a random phrase to type.
    
    Use this phrase for:
    - **Training**: User types it 8-10 times to build typing profile
    - **Verification**: User types it once for authentication
    """
    return {"phrase": get_random_phrase()}


@router.post(
    "/train",
    response_model=TrainResponse,
    summary="Train user's typing model",
    description="Train typing model using 10+ samples with synthetic augmentation for robustness."
)
async def train_user(data: TrainRequest):
    """
    Train a user's typing pattern model.
    
    Uses synthetic data augmentation to improve model robustness:
    10 real samples → expanded to ~40 samples via statistical generation.
    
    **Workflow:**
    1. Get phrase from GET /phrase
    2. User types the phrase 10+ times
    3. Capture keystroke events (key down/up with timestamps)
    4. Send all samples to this endpoint
    
    **Keystroke Event Format:**
    ```json
    {"key": "a", "type": "down", "time": 0}    // key pressed
    {"key": "a", "type": "up", "time": 90}     // key released
    ```
    
    - **time**: Milliseconds from start of session
    - **type**: "down" when key pressed, "up" when released
    
    After training, user can authenticate via POST /verify.
    """
    user_id = data.user_id
    samples = data.samples
    
    print(f"[TRAIN] User: {user_id}, Samples received: {len(samples) if samples else 0}")
    
    # Reduced from 20 to 10 - synthetic augmentation fills the gap
    if not samples or len(samples) < 10:
        raise HTTPException(
            status_code=400, 
            detail="At least 10 typing samples required for training"
        )
    
    # Verify user exists
    user = await User.filter(id=user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Extract features from each sample
    feature_vectors = []
    for keystrokes in samples:
        features = extract_features(keystrokes)
        feature_vectors.append(features)
    
    # Train the model (with synthetic augmentation enabled by default)
    model_package = train_model(feature_vectors, user_id)
    
    # Get augmentation stats from model
    aug_meta = model_package.get('augmentation_metadata', {})
    synthetic_count = aug_meta.get('synthetic_samples', 0)
    total_count = aug_meta.get('total_samples', len(feature_vectors))
    
    print(f"[TRAIN] Success: Model trained for user {user_id} with {len(feature_vectors)} real + {synthetic_count} synthetic samples")
    
    return {
        "status": "training_complete",
        "samples_used": total_count
    }


@router.post(
    "/verify",
    response_model=VerifyResponse,
    summary="Verify user's typing pattern",
    description="Verify if the typing pattern matches the user's trained profile. Use after POST /login."
)
async def verify_typing(data: VerifyRequest, request: Request):
    """
    Verify typing pattern against trained model.
    
    **Workflow:**
    1. User logs in via POST /login (password check)
    2. Get phrase from GET /phrase
    3. User types the phrase
    4. Capture keystroke events
    5. Send to this endpoint for behavioral verification
    
    **Response:**
    - **status**: "verified" (genuine user), "retry" (first attempt failed), or "otp_required" (second attempt failed)
    - **confidence**: Score from 0.0 to 1.0
    
    **Note:** Model must be trained first via POST /train.
    """
    user_id = data.user_id
    keystrokes = data.keystrokes
    attempt_number = data.attempt_number
    image_data = data.image_data
    
    # Check user exists
    user = await User.filter(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check model is trained
    if not model_exists(user_id):
        raise HTTPException(status_code=400, detail="User model not trained. Complete training first.")
    
    # Extract features from keystrokes
    features = extract_features(keystrokes)
    print(f"[VERIFY] User: {user_id}, Features: {features}")
    
    # Run prediction
    result = verify_user(features, user_id)
    print(f"[VERIFY] Prediction: {result}")
    
    # Handle prediction error
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # Save typing sample if verified (adaptive learning)
    if result["prediction"] == 1:
        await TypingSample.create(
            user=user,
            # Statistical features
            mean_hold=features[0],
            std_hold=features[1],
            mean_flight=features[2],
            std_flight=features[3],
            # First 6 normalized hold times
            hold_0=features[4],
            hold_1=features[5],
            hold_2=features[6],
            hold_3=features[7],
            hold_4=features[8],
            hold_5=features[9],
            # First 6 normalized flight times
            flight_0=features[10],
            flight_1=features[11],
            flight_2=features[12],
            flight_3=features[13],
            flight_4=features[14],
            flight_5=features[15]
        )
        
        # Retrain model with new verified sample (adaptive learning)
        update_model(features, user_id)
        
        # Verification successful
        return {
            "status": "verified",
            "confidence": result["confidence"],
            "fallback_available": False,
            "model_scores": result.get("model_scores", {})
        }
    
    # Verification failed - handle failed attempt
    # Get request metadata
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    # Save failed attempt to database
    await FailedAttempt.create(
        user=user,
        attempt_number=attempt_number,
        confidence=result["confidence"],
        ip_address=client_ip,
        user_agent=user_agent,
        # Only save image on second attempt
        image_data=image_data if attempt_number == 2 else None
    )
    
    print(f"[VERIFY] Failed attempt {attempt_number} for user {user_id}, confidence: {result['confidence']}")
    
    # Return based on attempt number
    if attempt_number == 1:
        # First failure - allow retry
        return {
            "status": "retry",
            "confidence": result["confidence"],
            "fallback_available": True,
            "model_scores": result.get("model_scores", {}),
            "attempts_remaining": 1
        }
    else:
        # Second failure - require OTP fallback
        image_captured = image_data is not None and len(image_data) > 0
        print(f"[VERIFY] Second attempt failed. Image captured: {image_captured}")
        
        return {
            "status": "otp_required",
            "confidence": result["confidence"],
            "fallback_available": True,
            "model_scores": result.get("model_scores", {}),
            "attempts_remaining": 0,
            "image_captured": image_captured
        }
