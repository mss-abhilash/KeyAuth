# 🔐 KeyAuth - Keystroke Dynamics Authentication System

<div align="center">

![KeyAuth Banner](https://img.shields.io/badge/KeyAuth-Behavioral%20Biometrics-00d4ff?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMjQgMjQiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEyIDFMMyA1djZjMCA1LjU1IDMuODQgMTAuNzQgOSAxMiA1LjE2LTEuMjYgOS02LjQ1IDktMTJWNWwtOS00em0wIDEwLjk5aDdjLS41MyA0LjEyLTMuMjggNy43OS03IDguOTRWMTJINVY2LjNsNy0zLjExdjguOHoiIGZpbGw9IiMwMGQ0ZmYiLz48L3N2Zz4=)

[![Python](https://img.shields.io/badge/Python-3.11+-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.5+-f7931e?style=flat-square&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

**A secure authentication system using keystroke dynamics and behavioral biometrics.**  
*Your typing pattern is your password — unique, unforgeable, and always with you.*

[Features](#-key-features) • [Installation](#️-installation--setup) • [API](#-api-endpoints) • [Architecture](#️-system-architecture)

</div>

---

## 📋 Table of Contents

- [🔍 Overview](#-overview)
- [🚀 Key Features](#-key-features)
- [🏗️ System Architecture](#️-system-architecture)
- [🛠️ Tech Stack](#️-tech-stack)
- [📂 Project Structure](#-project-structure)
- [🎮 How the System Works](#-how-the-system-works)
- [📊 Analytics Pipeline](#-analytics-pipeline)
- [🔐 Authentication & Security](#-authentication--security)
- [🌐 API Endpoints](#-api-endpoints)
- [🖼️ Screenshots](#️-screenshots)
- [⚙️ Installation & Setup](#️-installation--setup)
- [ Running Training Scripts](#-running-training-scripts)
- [🧪 Testing](#-testing)
- [🔮 Future Improvements](#-future-improvements)
- [📄 Resume Project Description](#-resume-project-description)

---

## 🔍 Overview

**KeyAuth** is a behavioral biometric authentication system that verifies users based on their unique typing patterns. Unlike traditional password-only systems, KeyAuth analyzes *how* you type — measuring keystroke hold times, flight times between keys, and typing rhythm — to create a biometric profile that's nearly impossible to replicate.

The system features a **two-attempt verification mechanism** with **webcam capture security** for suspicious login attempts. When a user fails typing verification twice, the system automatically captures a webcam image and logs it to an admin dashboard for security monitoring. Users can still authenticate via OTP fallback, ensuring accessibility while maintaining security.

Built with FastAPI and a multi-model ML ensemble (One-Class SVM, Isolation Forest, and DTW similarity), KeyAuth provides robust anomaly detection with confidence scoring and adaptive learning that improves over time.

---

## 🚀 Key Features

| Feature | Description |
|---------|-------------|
| 🎹 **Keystroke Dynamics Verification** | Analyzes typing patterns using hold times, flight times, and rhythm |
| 🤖 **Multi-Model ML Ensemble** | One-Class SVM + Isolation Forest + DTW for robust detection |
| 📸 **Webcam Intruder Capture** | Automatically captures image on suspicious login attempts |
| 🔄 **Two-Attempt System** | Allows retry before triggering security measures |
| 📧 **OTP Fallback Authentication** | Email-based 2FA when typing verification fails |
| 📊 **Admin Security Dashboard** | Monitor failed attempts and view captured images |
| 🧬 **Synthetic Data Augmentation** | Improves model accuracy with limited training samples |
| 📈 **Adaptive Learning** | Model improves with each successful verification |
| 🔔 **Email Login Alerts** | Notifications for suspicious login attempts |
| 🌐 **Browser Extension** | Extends protection to Gmail login flow |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              KEYAUTH ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────────────────────┐ │
│  │   FRONTEND   │     │   BACKEND    │     │      MACHINE LEARNING        │ │
│  │              │     │              │     │                              │ │
│  │  • HTML/CSS  │────▶│  • FastAPI   │────▶│  • Feature Extraction        │ │
│  │  • JavaScript│     │  • REST API  │     │  • One-Class SVM             │ │
│  │  • Webcam    │     │  • OTP       │     │  • Isolation Forest          │ │
│  │              │     │  • Email     │     │  • DTW Similarity            │ │
│  └──────────────┘     └──────────────┘     └──────────────────────────────┘ │
│         │                    │                          │                    │
│         │                    ▼                          │                    │
│         │            ┌──────────────┐                   │                    │
│         │            │   DATABASE   │◀──────────────────┘                    │
│         │            │              │                                        │
│         │            │  • SQLite    │                                        │
│         │            │  • Users     │                                        │
│         │            │  • Samples   │                                        │
│         │            │  • Failed    │                                        │
│         │            │    Attempts  │                                        │
│         │            └──────────────┘                                        │
│         │                                                                    │
│         ▼                                                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                        AUTHENTICATION FLOW                               ││
│  │                                                                          ││
│  │  User Types Phrase ──▶ Extract Features ──▶ ML Verification             ││
│  │         │                                           │                    ││
│  │         │                              ┌────────────┴────────────┐       ││
│  │         │                              ▼                         ▼       ││
│  │         │                         [GENUINE]                [SUSPICIOUS]  ││
│  │         │                              │                         │       ││
│  │         │                              ▼                         ▼       ││
│  │         │                      ✅ LOGIN SUCCESS           Attempt #1?    ││
│  │         │                                                    │     │     ││
│  │         │                                              Yes   │     │ No  ││
│  │         │                                                    ▼     ▼     ││
│  │         │                                              [RETRY] 📸 Webcam ││
│  │         │                                                      Capture   ││
│  │         │                                                         │      ││
│  │         │                                                         ▼      ││
│  │         │                                                   OTP Fallback ││
│  │         │                                                         │      ││
│  │         │                                                         ▼      ││
│  │         │                                                  Admin Dashboard││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| **HTML5** | Page structure |
| **CSS3** | Cyber-themed styling |
| **JavaScript** | Keystroke capture & webcam |
| **WebRTC** | Webcam image capture |

### Backend
| Technology | Purpose |
|------------|---------|
| **Python 3.11+** | Core language |
| **FastAPI** | REST API framework |
| **Tortoise ORM** | Async database ORM |
| **Pydantic** | Data validation |
| **bcrypt** | Password hashing |
| **aiosmtplib** | Async email sending |

### Machine Learning
| Technology | Purpose |
|------------|---------|
| **Scikit-learn** | ML models |
| **One-Class SVM** | Anomaly boundary detection |
| **Isolation Forest** | Tree-based anomaly detection |
| **DTW Algorithm** | Sequence similarity matching |
| **NumPy** | Numerical operations |
| **Joblib** | Model serialization |

### Database
| Technology | Purpose |
|------------|---------|
| **SQLite** | Lightweight database |
| **aiosqlite** | Async SQLite support |

### DevOps & Tools
| Technology | Purpose |
|------------|---------|
| **Uvicorn** | ASGI server |
| **python-dotenv** | Environment management |
| **Git** | Version control |

---

## 📂 Project Structure

```
KeyAuth/
├── 📁 backend/
│   ├── main.py              # FastAPI application entry point
│   ├── database.py          # Tortoise ORM configuration
│   ├── models.py            # ORM models (User, TypingSample, FailedAttempt)
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── auth.py              # Password hashing utilities
│   ├── email.py             # Email service for alerts & OTP
│   │
│   ├── 📁 ml/
│   │   ├── feature_extractor.py    # 16-feature keystroke extraction
│   │   ├── predict.py              # Multi-model verification
│   │   ├── train_model.py          # Model training with augmentation
│   │   ├── synthetic_generator.py  # Synthetic sample generation
│   │   ├── phrases.txt             # Verification phrases
│   │   └── 📁 models/              # Saved user models (.pkl)
│   │
│   ├── 📁 routes/
│   │   ├── auth_routes.py     # /register, /login endpoints
│   │   ├── typing_routes.py   # /train, /verify, /phrase endpoints
│   │   ├── otp_routes.py      # /request-otp, /verify-otp endpoints
│   │   └── admin_routes.py    # /admin/failed-attempts endpoints
│   │
│   └── 📁 samples/            # Stored typing samples
│
├── 📁 frontend/
│   ├── index.html           # Landing page
│   ├── register.html        # User registration
│   ├── login.html           # User login
│   ├── typing.html          # Typing verification page
│   ├── typing.js            # Keystroke capture & webcam logic
│   ├── train.html           # Model training interface
│   ├── success.html         # Login success page
│   ├── security.html        # Security dashboard
│   ├── dashboard.html       # User dashboard
│   ├── cyber-style.css      # Main stylesheet
│   └── style.css            # Additional styles
│
├── 📁 extension/
│   ├── manifest.json        # Chrome extension manifest
│   ├── background.js        # Service worker
│   ├── content.js           # Content script
│   ├── popup.html/js        # Extension popup
│   └── 📁 icons/            # Extension icons
│
├── db.sqlite3               # SQLite database
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Project configuration
├── .env.example             # Environment template
└── README.md                # This file
```

---

## 🎮 How the System Works

### Registration Flow
```
1️⃣  User enters username, email, password
2️⃣  User types verification phrase 10+ times
3️⃣  System extracts 16-feature vectors from each sample
4️⃣  Synthetic augmentation expands samples (10 → 40)
5️⃣  Multi-model ensemble trained on user's patterns
6️⃣  Model saved for future verification
```

### Authentication Flow
```
1️⃣  User logs in with username/password
2️⃣  System presents verification phrase
3️⃣  User types the phrase (keystrokes captured)
4️⃣  System extracts features from keystrokes
5️⃣  ML models verify typing pattern

    ✅ VERIFIED → Login success
    
    ❌ ATTEMPT 1 FAILED
        → Show retry message
        → User types phrase again
        
    ❌ ATTEMPT 2 FAILED
        → 📸 Capture webcam image
        → Log to security dashboard
        → Redirect to OTP fallback
        → User verifies via email code
```

---

## 📊 Analytics Pipeline

### Feature Extraction (16-Dimensional Vector)

```
Raw Keystrokes
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│                   FEATURE EXTRACTION                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  📊 Statistical Features (4):                            │
│     • mean_hold      - Average key hold duration        │
│     • std_hold       - Variation in hold times          │
│     • mean_flight    - Average time between keys        │
│     • std_flight     - Variation in flight times        │
│                                                          │
│  🎵 Rhythm Features (6 hold + 6 flight = 12):          │
│     • hold_0..hold_5    - Normalized first 6 hold times │
│     • flight_0..flight_5 - Normalized first 6 flights   │
│                                                          │
│  ✨ Normalization: time / mean_time                      │
│     (Captures RHYTHM, not absolute speed)               │
│                                                          │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│               MULTI-MODEL VERIFICATION                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  🔵 One-Class SVM (40% weight)                          │
│     → Decision boundary around normal patterns           │
│                                                          │
│  🟢 Isolation Forest (30% weight)                       │
│     → Tree-based anomaly detection                       │
│                                                          │
│  🟡 DTW Similarity (30% weight)                         │
│     → Dynamic time warping sequence matching             │
│                                                          │
│  🎯 Ensemble: Majority vote + weighted confidence        │
│                                                          │
└─────────────────────────────────────────────────────────┘
    │
    ▼
Verification Result: { status, confidence, model_scores }
```

---

## 🔐 Authentication & Security

### Security Layers

| Layer | Description |
|-------|-------------|
| 🔑 **Password Authentication** | bcrypt-hashed password verification |
| 🎹 **Behavioral Biometrics** | Typing pattern analysis |
| 🔄 **Two-Attempt System** | Allows retry before security escalation |
| 📸 **Webcam Capture** | Images captured on suspicious attempts |
| 📧 **OTP Fallback** | 6-digit email code (5 min expiry) |
| 📊 **Admin Monitoring** | Dashboard for security review |
| 🔔 **Email Alerts** | Login attempt notifications |

### Failed Attempt Tracking

When verification fails:
- **Attempt 1**: User gets one retry
- **Attempt 2**: System captures webcam image (if permitted), logs attempt with IP/user-agent, redirects to OTP

All failed attempts are stored with:
- User ID, attempt number, confidence score
- IP address, user agent, timestamp
- Webcam image (Base64, on 2nd attempt)

---

## 🌐 API Endpoints

### Authentication Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/register` | Register new user with typing samples |
| `POST` | `/login` | Verify password credentials |

### Typing Verification Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/phrase` | Get random verification phrase |
| `POST` | `/train` | Train user's typing model |
| `POST` | `/verify` | Verify typing pattern |

### OTP Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/request-otp` | Send OTP to user's email |
| `POST` | `/verify-otp` | Verify OTP code |

### Admin Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/admin/failed-attempts` | List all failed attempts |
| `GET` | `/admin/failed-attempts/{id}/image` | View captured image |

### Request/Response Examples

<details>
<summary><b>POST /verify</b></summary>

**Request:**
```json
{
  "user_id": 1,
  "keystrokes": [
    {"key": "t", "type": "down", "time": 0},
    {"key": "t", "type": "up", "time": 90},
    {"key": "h", "type": "down", "time": 150},
    {"key": "h", "type": "up", "time": 230}
  ],
  "attempt_number": 1,
  "image_data": null
}
```

**Response (Success):**
```json
{
  "status": "verified",
  "confidence": 0.87,
  "fallback_available": false,
  "model_scores": {
    "svm": 0.91,
    "iforest": 0.85,
    "dtw": 0.82
  }
}
```

**Response (Retry):**
```json
{
  "status": "retry",
  "confidence": 0.32,
  "fallback_available": true,
  "attempts_remaining": 1
}
```

</details>

---



## ⚙️ Installation & Setup

### Prerequisites

- Python 3.11 or higher
- pip or uv package manager
- Gmail account (for OTP emails)

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/KeyAuth.git
cd KeyAuth
```

### Step 2: Create Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Or using uv
uv venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt

# Or using uv
uv pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
# Copy example config
cp .env.example .env

# Edit .env with your Gmail credentials
# SMTP_EMAIL=your-email@gmail.com
# SMTP_PASSWORD=your-app-password
```

> **Gmail Setup:** Enable 2FA, then create an App Password at https://myaccount.google.com/apppasswords

### Step 5: Start Backend Server

```bash
uvicorn backend.main:app --reload --port 8000
```

### Step 6: Start Frontend Server

```bash
cd frontend
python -m http.server 3000
```

### Step 7: Access Application

- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

##  Running Training Scripts

### Train Model for Existing User

```bash
# Using the train endpoint
curl -X POST http://localhost:8000/train \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "samples": [...]}'
```

### Test Synthetic Generation

```bash
cd KeyAuth
python test_synthetic.py
```

### Debug Feature Extraction

```bash
python debug_features.py
```

---

## 🧪 Testing

### Manual Testing Flow

1. **Register a new user:**
   - Go to http://localhost:3000/register.html
   - Enter username, email, password
   - Type the phrase 10+ times
   - Submit registration

2. **Login and verify:**
   - Go to http://localhost:3000/login.html
   - Enter credentials
   - Type the verification phrase

3. **Test failed attempts:**
   - Type intentionally differently (fast/slow)
   - Verify retry message appears
   - Fail again to trigger webcam capture

4. **Check security dashboard:**
   - Go to http://localhost:3000/security.html
   - View logged failed attempts
   - Check captured images

### API Testing

```bash
# Health check
curl http://localhost:8000/

# Get phrase
curl http://localhost:8000/phrase

# List failed attempts
curl http://localhost:8000/admin/failed-attempts
```

---

## 🔮 Future Improvements

| Feature | Description |
|---------|-------------|
| 🔄 **Continuous Authentication** | Verify user throughout session |
| 📱 **Mobile Support** | Touch typing pattern analysis |
| 🧠 **Deep Learning Models** | LSTM/Transformer for sequences |
| 🔐 **Encrypted Image Storage** | AES encryption for webcam data |
| 🌍 **Multi-language Phrases** | Support for different languages |
| 📊 **Advanced Analytics** | User behavior insights dashboard |
| 🔗 **SSO Integration** | OAuth2/SAML support |
| 🎯 **Risk-Based Authentication** | Adaptive security levels |

---

## 📄 Resume Project Description

> **KeyAuth - Behavioral Biometric Authentication System**
>
> Developed a behavioral biometric authentication system using keystroke dynamics and machine learning to verify users based on their unique typing patterns. Implemented a multi-model ensemble (One-Class SVM, Isolation Forest, DTW) for robust anomaly detection with 87%+ accuracy. Built a two-attempt verification system with webcam-based intruder capture and OTP fallback authentication. Features include real-time keystroke analysis, synthetic data augmentation for improved model training, admin security dashboard, and email alerts. Tech stack: FastAPI, Python, Scikit-learn, JavaScript, SQLite.

---



<br>


---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

<div align="center">

**Built with ❤️ for secure authentication**

[⬆ Back to Top](#-keyauth---keystroke-dynamics-authentication-system)

</div>
