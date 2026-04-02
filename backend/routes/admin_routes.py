"""
Admin routes for viewing failed authentication attempts
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from backend.models import FailedAttempt
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["Admin"])


class FailedAttemptResponse(BaseModel):
    """Response model for failed attempt"""
    id: int
    user_id: int
    attempt_number: int
    confidence: float
    ip_address: Optional[str]
    created_at: datetime
    has_image: bool


@router.get(
    "/failed-attempts",
    response_model=list[FailedAttemptResponse],
    summary="List all failed attempts",
    description="Get a list of all failed verification attempts with metadata."
)
async def list_failed_attempts():
    """
    List all failed verification attempts.
    
    Returns:
    - id: Attempt ID
    - user_id: User who failed verification
    - attempt_number: Which attempt (1 or 2)
    - confidence: Verification confidence score
    - ip_address: Client IP address
    - created_at: Timestamp of the attempt
    - has_image: Whether a webcam image was captured
    """
    attempts = await FailedAttempt.all().prefetch_related("user")
    
    return [
        {
            "id": attempt.id,
            "user_id": attempt.user_id,
            "attempt_number": attempt.attempt_number,
            "confidence": attempt.confidence,
            "ip_address": attempt.ip_address,
            "created_at": attempt.created_at,
            "has_image": attempt.image_data is not None and len(attempt.image_data) > 0
        }
        for attempt in attempts
    ]


@router.get(
    "/failed-attempts/{attempt_id}/image",
    response_class=HTMLResponse,
    summary="View captured image",
    description="View the webcam image captured during a failed verification attempt."
)
async def view_failed_attempt_image(attempt_id: int):
    """
    View the webcam image captured during a failed verification attempt.
    
    Returns an HTML page displaying the captured image.
    """
    attempt = await FailedAttempt.filter(id=attempt_id).first()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Failed attempt not found")
    
    if not attempt.image_data:
        raise HTTPException(status_code=404, detail="No image captured for this attempt")
    
    # Return HTML page with the image
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Failed Attempt Image - #{attempt_id}</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: #1a1a2e;
                color: #eee;
                padding: 20px;
                margin: 0;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
            }}
            h1 {{
                color: #00d4ff;
            }}
            .metadata {{
                background: #16213e;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            .metadata p {{
                margin: 8px 0;
            }}
            .metadata strong {{
                color: #00d4ff;
            }}
            img {{
                max-width: 100%;
                border-radius: 8px;
                border: 2px solid #00d4ff;
            }}
            .back-link {{
                color: #00d4ff;
                text-decoration: none;
                display: inline-block;
                margin-bottom: 20px;
            }}
            .back-link:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/admin/failed-attempts" class="back-link">← Back to Failed Attempts</a>
            <h1>Failed Attempt Image #{attempt_id}</h1>
            <div class="metadata">
                <p><strong>User ID:</strong> {attempt.user_id}</p>
                <p><strong>Attempt Number:</strong> {attempt.attempt_number}</p>
                <p><strong>Confidence:</strong> {attempt.confidence:.2%}</p>
                <p><strong>IP Address:</strong> {attempt.ip_address or 'Unknown'}</p>
                <p><strong>Timestamp:</strong> {attempt.created_at}</p>
            </div>
            <img src="{attempt.image_data}" alt="Captured webcam image" />
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)
