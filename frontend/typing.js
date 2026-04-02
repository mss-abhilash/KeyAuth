let REQUIRED_PHRASE = '';
const keystrokes = [];
const input = document.getElementById('typingInput');
const verifyBtn = document.getElementById('verifyBtn');
const matchStatus = document.getElementById('matchStatus');
const phraseDisplay = document.getElementById('phraseDisplay');

// =====================
// Attempt Tracking
// =====================
const MAX_ATTEMPTS = 2;
let currentAttempt = 1;

// =====================
// Webcam Support
// =====================
let webcamStream = null;
const webcamVideo = document.getElementById('webcamVideo');

/**
 * Initialize webcam on page load (hidden, for security capture only)
 */
async function initializeWebcam() {
  try {
    webcamStream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        facingMode: 'user'
      },
      audio: false
    });
    
    if (webcamVideo) {
      webcamVideo.muted = true;
      webcamVideo.srcObject = webcamStream;
    }
    console.log('[WEBCAM] Camera initialized successfully');
  } catch (err) {
    console.warn('[WEBCAM] Camera permission denied or not available:', err.message);
    // System continues to work without webcam
    webcamStream = null;
  }
}

/**
 * Ensure webcam stream is active and the video element has a readable frame.
 * @returns {Promise<boolean>} True when webcam is ready for capture
 */
async function ensureWebcamReady() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia || !webcamVideo) {
    return false;
  }

  const hasActiveTrack = webcamStream && webcamStream.getVideoTracks().some(track => track.readyState === 'live');

  if (!hasActiveTrack) {
    try {
      webcamStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        },
        audio: false
      });
      webcamVideo.srcObject = webcamStream;
      console.log('[WEBCAM] Camera re-initialized for capture');
    } catch (err) {
      console.warn('[WEBCAM] Unable to initialize camera for capture:', err.message);
      return false;
    }
  }

  try {
    await webcamVideo.play();
  } catch (_) {
    // Continue; in many browsers stream can still render without explicit play.
  }

  if (webcamVideo.readyState >= 2 && webcamVideo.videoWidth > 0 && webcamVideo.videoHeight > 0) {
    return true;
  }

  return await new Promise((resolve) => {
    const timeoutId = setTimeout(() => resolve(false), 1000);

    const onReady = () => {
      clearTimeout(timeoutId);
      webcamVideo.removeEventListener('loadeddata', onReady);
      webcamVideo.removeEventListener('canplay', onReady);
      resolve(webcamVideo.videoWidth > 0 && webcamVideo.videoHeight > 0);
    };

    webcamVideo.addEventListener('loadeddata', onReady, { once: true });
    webcamVideo.addEventListener('canplay', onReady, { once: true });
  });
}

/**
 * Capture webcam image as Base64 JPEG
 * @returns {string|null} Base64 image data or null if capture fails
 */
async function captureWebcamImage() {
  const isReady = await ensureWebcamReady();
  if (!webcamStream) {
    console.warn('[WEBCAM] No webcam stream available for capture');
    return null;
  }
  
  try {
    // Prefer direct frame capture from video track when available.
    const videoTrack = webcamStream.getVideoTracks()[0];
    if (videoTrack && typeof ImageCapture !== 'undefined') {
      try {
        const imageCapture = new ImageCapture(videoTrack);
        const bitmap = await imageCapture.grabFrame();
        const canvas = document.createElement('canvas');
        canvas.width = bitmap.width;
        canvas.height = bitmap.height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(bitmap, 0, 0);
        const imageData = canvas.toDataURL('image/jpeg', 0.8);
        console.log('[WEBCAM] Image captured via ImageCapture');
        return imageData;
      } catch (trackErr) {
        console.warn('[WEBCAM] ImageCapture failed, falling back to video element:', trackErr.message);
      }
    }

    if (!isReady) {
      console.warn('[WEBCAM] Video element is not ready for fallback capture');
      return null;
    }

    const canvas = document.createElement('canvas');
    canvas.width = webcamVideo.videoWidth || 640;
    canvas.height = webcamVideo.videoHeight || 480;
    
    const ctx = canvas.getContext('2d');
    ctx.drawImage(webcamVideo, 0, 0, canvas.width, canvas.height);
    
    const imageData = canvas.toDataURL('image/jpeg', 0.8);
    console.log('[WEBCAM] Image captured successfully');
    return imageData;
  } catch (err) {
    console.error('[WEBCAM] Failed to capture image:', err.message);
    return null;
  }
}

/**
 * Update attempt indicator display
 */
function updateAttemptIndicator() {
  const indicator = document.getElementById('attemptIndicator');
  if (indicator) {
    indicator.textContent = `Attempt ${currentAttempt} of ${MAX_ATTEMPTS}`;
  }
}

/**
 * Show retry message after first failed attempt
 */
function showRetryMessage() {
  const retryMessage = document.getElementById('retryMessage');
  const retryMessageText = document.getElementById('retryMessageText');
  if (retryMessage && retryMessageText) {
    retryMessageText.textContent = `Verification failed. ${MAX_ATTEMPTS - currentAttempt} attempt remaining.`;
    retryMessage.style.display = 'block';
  }
}

/**
 * Reset for next attempt
 */
function resetForNextAttempt() {
  // Clear input and keystrokes
  input.value = '';
  keystrokes.length = 0;
  
  // Update UI
  matchStatus.textContent = '';
  matchStatus.className = 'match-status';
  verifyBtn.disabled = true;
  verifyBtn.textContent = 'Verify Identity';
  
  // Focus input for next attempt
  input.focus();
}

// Initialize webcam on page load
initializeWebcam();

// Fetch phrase from API on page load
async function loadPhrase() {
  try {
    const res = await fetch('http://localhost:8000/phrase');
    const data = await res.json();
    REQUIRED_PHRASE = data.phrase;
    phraseDisplay.textContent = REQUIRED_PHRASE;
  } catch (err) {
    REQUIRED_PHRASE = 'secure login verification';
    phraseDisplay.textContent = REQUIRED_PHRASE;
    console.error('Failed to fetch phrase, using default');
  }
}

loadPhrase();

input.addEventListener('keydown', (e) => {
  keystrokes.push({
    key: e.key,
    type: 'down',
    time: performance.now()
  });
});

input.addEventListener('keyup', (e) => {
  keystrokes.push({
    key: e.key,
    type: 'up',
    time: performance.now()
  });
  updateMatchStatus();
});

function updateMatchStatus() {
  const typed = input.value;
  if (typed === REQUIRED_PHRASE) {
    matchStatus.textContent = '✓ Phrase matches';
    matchStatus.className = 'match-status match';
    verifyBtn.disabled = false;
  } else {
    matchStatus.textContent = typed.length > 0 ? '✗ Phrase does not match yet' : '';
    matchStatus.className = 'match-status no-match';
    verifyBtn.disabled = true;
  }
}

verifyBtn.addEventListener('click', async () => {
  if (input.value !== REQUIRED_PHRASE) return;

  const userId = localStorage.getItem('user_id');
  if (!userId) {
    alert('Session expired. Please login again.');
    window.location.href = 'login.html';
    return;
  }

  verifyBtn.disabled = true;
  verifyBtn.textContent = 'Verifying...';

  // Capture webcam image only on second attempt
  let imageData = null;
  if (currentAttempt === 2) {
    imageData = await captureWebcamImage();
  }

  try {
    const res = await fetch('http://localhost:8000/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        user_id: parseInt(userId), 
        keystrokes,
        attempt_number: currentAttempt,
        image_data: imageData
      })
    });
    const data = await res.json();
    
    if (!res.ok) {
      // Handle error responses (e.g., model not trained)
      alert(data.detail || 'Verification failed');
      verifyBtn.disabled = false;
      verifyBtn.textContent = 'Verify Identity';
      return;
    }
    
    // Handle verification result based on status
    if (data.status === 'verified') {
      // Success - redirect to success page
      localStorage.setItem('verificationResult', JSON.stringify(data));
      window.location.href = 'success.html';
      return;
    }
    
    if (data.status === 'retry') {
      // First attempt failed - allow retry
      currentAttempt = 2;
      updateAttemptIndicator();
      showRetryMessage();
      resetForNextAttempt();
      return;
    }
    
    if (data.status === 'otp_required') {
      // Second attempt failed - redirect to OTP fallback
      console.log('[VERIFY] Second attempt failed. Image captured:', data.image_captured);
      showOtpFallback();
      return;
    }
    
    // Legacy support: Handle old 'suspicious' status with fallback_available
    if (data.status === 'suspicious' && data.fallback_available) {
      showOtpFallback();
      return;
    }
    
    // If we get here with suspicious status but no fallback, show error
    localStorage.setItem('verificationResult', JSON.stringify(data));
    window.location.href = 'success.html';
  } catch (err) {
    alert('Cannot connect to server');
    verifyBtn.disabled = false;
    verifyBtn.textContent = 'Verify Identity';
  }
});

// =====================
// OTP Fallback Handlers
// =====================

function showOtpFallback() {
  // Hide typing section elements and disable input
  const typingInstruction = document.querySelector('.typing-instruction');
  if (typingInstruction) typingInstruction.style.display = 'none';
  document.getElementById('phraseDisplay').style.display = 'none';
  const inputGroup = input.closest('.input-group');
  if (inputGroup) inputGroup.style.display = 'none';
  input.disabled = true;  // Prevent capturing keystrokes
  input.blur();  // Remove focus
  matchStatus.style.display = 'none';
  verifyBtn.style.display = 'none';
  
  // Show OTP section
  document.getElementById('otpSection').style.display = 'block';
}

// Request OTP
document.getElementById('requestOtpBtn')?.addEventListener('click', async () => {
  const userId = localStorage.getItem('user_id');
  const requestBtn = document.getElementById('requestOtpBtn');
  const otpMessage = document.getElementById('otpMessage');
  
  requestBtn.disabled = true;
  requestBtn.textContent = 'Sending...';
  otpMessage.textContent = '';
  
  try {
    const res = await fetch('http://localhost:8000/request-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: parseInt(userId) })
    });
    const data = await res.json();
    
    if (res.ok && data.status === 'otp_sent') {
      // Show OTP input section
      requestBtn.style.display = 'none';
      const otpInputSection = document.getElementById('otpInputSection');
      otpInputSection.classList.add('visible');
      document.getElementById('otpSentMsg').textContent = data.message || 'OTP sent to your email. Valid for 5 minutes.';
      setTimeout(() => document.getElementById('otpInput').focus(), 100);
    } else {
      otpMessage.textContent = data.detail || 'Failed to send OTP';
      otpMessage.className = 'otp-message error';
      requestBtn.disabled = false;
      requestBtn.textContent = 'Send OTP to Email';
    }
  } catch (err) {
    otpMessage.textContent = 'Cannot connect to server';
    otpMessage.className = 'otp-message error';
    requestBtn.disabled = false;
    requestBtn.textContent = 'Send OTP to Email';
  }
});

// Verify OTP
document.getElementById('verifyOtpBtn')?.addEventListener('click', async () => {
  const userId = localStorage.getItem('user_id');
  const code = document.getElementById('otpInput').value.trim();
  const verifyOtpBtn = document.getElementById('verifyOtpBtn');
  const otpMessage = document.getElementById('otpMessage');
  
  if (code.length !== 6) {
    otpMessage.textContent = 'Please enter a 6-digit code';
    otpMessage.className = 'otp-message error';
    return;
  }
  
  verifyOtpBtn.disabled = true;
  verifyOtpBtn.textContent = 'Verifying...';
  otpMessage.textContent = '';
  
  try {
    const res = await fetch('http://localhost:8000/verify-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: parseInt(userId), code: code })
    });
    const data = await res.json();
    
    if (res.ok && data.status === 'verified') {
      // OTP verified successfully - redirect to success page
      localStorage.setItem('verificationResult', JSON.stringify({
        status: 'verified',
        method: 'otp',
        message: 'Verified via OTP'
      }));
      window.location.href = 'success.html';
    } else {
      otpMessage.textContent = data.detail || 'Invalid or expired OTP';
      otpMessage.className = 'otp-message error';
      verifyOtpBtn.disabled = false;
      verifyOtpBtn.textContent = 'Verify OTP';
      document.getElementById('otpInput').value = '';
      document.getElementById('otpInput').focus();
    }
  } catch (err) {
    otpMessage.textContent = 'Cannot connect to server';
    otpMessage.className = 'otp-message error';
    verifyOtpBtn.disabled = false;
    verifyOtpBtn.textContent = 'Verify OTP';
  }
});

// Resend OTP
document.getElementById('resendOtpBtn')?.addEventListener('click', async () => {
  const userId = localStorage.getItem('user_id');
  const resendBtn = document.getElementById('resendOtpBtn');
  const otpMessage = document.getElementById('otpMessage');
  
  resendBtn.disabled = true;
  resendBtn.textContent = 'Sending...';
  otpMessage.textContent = '';
  
  try {
    const res = await fetch('http://localhost:8000/request-otp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: parseInt(userId) })
    });
    const data = await res.json();
    
    if (res.ok && data.status === 'otp_sent') {
      document.getElementById('otpSentMsg').textContent = 'New OTP sent to your email. Valid for 5 minutes.';
      document.getElementById('otpInput').value = '';
      document.getElementById('otpInput').focus();
    } else {
      otpMessage.textContent = data.detail || 'Failed to resend OTP';
      otpMessage.className = 'otp-message error';
    }
  } catch (err) {
    otpMessage.textContent = 'Cannot connect to server';
    otpMessage.className = 'otp-message error';
  }
  
  resendBtn.disabled = false;
  resendBtn.textContent = 'Resend OTP';
});

// Allow Enter key to verify OTP
document.getElementById('otpInput')?.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    document.getElementById('verifyOtpBtn')?.click();
  }
});

// Developer tools: Load sample from JSON
document.getElementById('loadSampleBtn')?.addEventListener('click', () => {
  document.getElementById('loadSampleInput').click();
});

document.getElementById('loadSampleInput')?.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (event) => {
    try {
      const data = JSON.parse(event.target.result);
      // Can load either a single sample or pick first from samples array
      let sample = null;
      if (data.keystrokes) {
        sample = data.keystrokes;
      } else if (data.samples && data.samples.length > 0) {
        sample = data.samples[0];
      }
      
      if (sample && Array.isArray(sample)) {
        // Clear existing keystrokes and load new ones
        keystrokes.length = 0;
        sample.forEach(k => keystrokes.push(k));
        
        // Set input to match phrase
        input.value = REQUIRED_PHRASE;
        updateMatchStatus();
        
        document.getElementById('message').textContent = `Loaded sample with ${keystrokes.length} keystrokes`;
        document.getElementById('message').style.color = 'green';
      } else {
        alert('Invalid file format - need keystrokes or samples array');
      }
    } catch (err) {
      alert('Failed to parse JSON file');
    }
  };
  reader.readAsText(file);
  e.target.value = '';
});
