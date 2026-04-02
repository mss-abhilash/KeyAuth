"""
Synthetic sample generation for keystroke biometrics

Generates synthetic typing samples from real samples to improve
model robustness when limited real training data is available.

Methods:
1. Gaussian Noise - adds small random variations to real samples
2. Statistical Distribution - generates samples from mean/std of features

Recommended ratio: 1:3 (10 real → 30 synthetic = 40 total)
"""

import numpy as np
from typing import Tuple


# ===== Configuration =====
SYNTHETIC_RATIO = 3  # Generate 3x synthetic samples per real sample
MAX_SYNTHETIC_SAMPLES = 40  # Maximum synthetic samples to generate
MIN_REAL_SAMPLES = 5  # Minimum real samples needed for augmentation

# Noise scales for different feature types (feature indices)
# Features 0-3: Statistical features (mean_hold, std_hold, mean_flight, std_flight)
# Features 4-9: Normalized hold times (hold_0 to hold_5)
# Features 10-15: Normalized flight times (flight_0 to flight_5)
STATISTICAL_NOISE_SCALE = 0.08  # ±8% for statistical features
RHYTHM_NOISE_SCALE = 0.05      # ±5% for rhythm features (more sensitive)


def generate_gaussian_noise_samples(
    real_samples: np.ndarray, 
    num_samples: int = 15
) -> np.ndarray:
    """
    Generate synthetic samples by adding Gaussian noise to real samples.
    
    This method preserves the individual characteristics of each real sample
    while introducing small realistic variations.
    
    Args:
        real_samples: Array of shape (n_samples, 16) with real feature vectors
        num_samples: Number of synthetic samples to generate
        
    Returns:
        Array of shape (num_samples, 16) with synthetic samples
    """
    if len(real_samples) == 0:
        return np.array([])
    
    n_features = real_samples.shape[1]
    synthetic = []
    
    # Cycle through real samples, adding noise to each
    for i in range(num_samples):
        # Pick a real sample to base this synthetic one on
        base_sample = real_samples[i % len(real_samples)].copy()
        
        # Apply feature-specific noise
        for j in range(n_features):
            if j < 4:
                # Statistical features - allow more variation
                noise_scale = STATISTICAL_NOISE_SCALE
            else:
                # Rhythm features - less variation to preserve identity
                noise_scale = RHYTHM_NOISE_SCALE
            
            # Multiplicative Gaussian noise: value * (1 + noise)
            noise = np.random.normal(0, noise_scale)
            base_sample[j] = base_sample[j] * (1 + noise)
        
        synthetic.append(base_sample)
    
    return np.array(synthetic)


def generate_statistical_samples(
    real_samples: np.ndarray, 
    num_samples: int = 15
) -> np.ndarray:
    """
    Generate synthetic samples from the statistical distribution of real samples.
    
    This method captures the natural variation across all real samples and
    generates new samples that fit the same distribution.
    
    Args:
        real_samples: Array of shape (n_samples, 16) with real feature vectors
        num_samples: Number of synthetic samples to generate
        
    Returns:
        Array of shape (num_samples, 16) with synthetic samples
    """
    if len(real_samples) < 2:
        # Need at least 2 samples to compute meaningful std
        return np.array([])
    
    # Compute mean and std for each feature
    mean = np.mean(real_samples, axis=0)
    std = np.std(real_samples, axis=0)
    
    # Ensure minimum std to avoid generating identical samples
    # Use 5% of mean as minimum std for each feature
    min_std = np.abs(mean) * 0.05
    std = np.maximum(std, min_std)
    
    # Generate samples from normal distribution
    synthetic = np.random.normal(mean, std, size=(num_samples, len(mean)))
    
    return synthetic


def validate_synthetic_samples(
    real_samples: np.ndarray, 
    synthetic_samples: np.ndarray
) -> np.ndarray:
    """
    Validate and filter synthetic samples to ensure they're realistic.
    
    Removes samples that:
    - Have negative values (impossible for timing data)
    - Deviate too far from real sample range
    
    Args:
        real_samples: Original real samples for reference
        synthetic_samples: Generated synthetic samples
        
    Returns:
        Filtered array of valid synthetic samples
    """
    if len(synthetic_samples) == 0:
        return synthetic_samples
    
    # Calculate acceptable bounds from real samples
    real_min = np.min(real_samples, axis=0)
    real_max = np.max(real_samples, axis=0)
    real_range = real_max - real_min
    
    # Allow synthetic samples within 50% beyond real range
    margin = real_range * 0.5
    lower_bound = real_min - margin
    upper_bound = real_max + margin
    
    # Ensure no negative values for timing features (indices 0-3)
    lower_bound[:4] = np.maximum(lower_bound[:4], 1.0)  # Min 1ms
    
    # Filter valid samples
    valid_mask = np.all(
        (synthetic_samples >= lower_bound) & (synthetic_samples <= upper_bound),
        axis=1
    )
    
    return synthetic_samples[valid_mask]


def augment_samples(
    real_samples: list | np.ndarray, 
    target_total: int = 40
) -> Tuple[np.ndarray, dict]:
    """
    Main entry point: Augment real samples with synthetic ones.
    
    Uses a combination of Gaussian noise and statistical sampling
    to generate diverse but realistic synthetic samples.
    
    Args:
        real_samples: List or array of 16-feature vectors
        target_total: Target total number of samples (real + synthetic)
        
    Returns:
        Tuple of:
        - Combined array of real + synthetic samples
        - Metadata dict with generation stats
    """
    real_samples = np.array(real_samples)
    n_real = len(real_samples)
    
    metadata = {
        "real_samples": n_real,
        "synthetic_samples": 0,
        "total_samples": n_real,
        "augmentation_used": False,
        "methods": []
    }
    
    # Don't augment if we have enough real samples or too few to work with
    if n_real >= target_total:
        return real_samples, metadata
    
    if n_real < MIN_REAL_SAMPLES:
        print(f"[SYNTHETIC] Warning: Only {n_real} real samples, need {MIN_REAL_SAMPLES}+ for augmentation")
        return real_samples, metadata
    
    # Calculate how many synthetic samples to generate
    n_synthetic_needed = min(
        target_total - n_real,
        n_real * SYNTHETIC_RATIO,
        MAX_SYNTHETIC_SAMPLES
    )
    
    # Split between two methods (roughly 50/50)
    n_noise = n_synthetic_needed // 2
    n_statistical = n_synthetic_needed - n_noise
    
    all_synthetic = []
    
    # Method 1: Gaussian noise samples
    if n_noise > 0:
        noise_samples = generate_gaussian_noise_samples(real_samples, n_noise)
        noise_samples = validate_synthetic_samples(real_samples, noise_samples)
        all_synthetic.append(noise_samples)
        metadata["methods"].append(f"gaussian_noise:{len(noise_samples)}")
    
    # Method 2: Statistical distribution samples
    if n_statistical > 0:
        stat_samples = generate_statistical_samples(real_samples, n_statistical)
        stat_samples = validate_synthetic_samples(real_samples, stat_samples)
        all_synthetic.append(stat_samples)
        metadata["methods"].append(f"statistical:{len(stat_samples)}")
    
    # Combine all synthetic samples
    if all_synthetic:
        synthetic_combined = np.vstack([s for s in all_synthetic if len(s) > 0])
        combined = np.vstack([real_samples, synthetic_combined])
        
        metadata["synthetic_samples"] = len(synthetic_combined)
        metadata["total_samples"] = len(combined)
        metadata["augmentation_used"] = True
        
        print(f"[SYNTHETIC] Generated {len(synthetic_combined)} synthetic samples "
              f"from {n_real} real samples (total: {len(combined)})")
        
        return combined, metadata
    
    return real_samples, metadata


def get_augmentation_stats(
    real_samples: list | np.ndarray, 
    synthetic_samples: np.ndarray
) -> dict:
    """
    Get statistics comparing real and synthetic samples for debugging.
    
    Args:
        real_samples: Original real samples
        synthetic_samples: Generated synthetic samples
        
    Returns:
        Dict with comparison statistics
    """
    real = np.array(real_samples)
    
    stats = {
        "real": {
            "count": len(real),
            "mean": np.mean(real, axis=0).tolist(),
            "std": np.std(real, axis=0).tolist(),
            "min": np.min(real, axis=0).tolist(),
            "max": np.max(real, axis=0).tolist()
        }
    }
    
    if len(synthetic_samples) > 0:
        stats["synthetic"] = {
            "count": len(synthetic_samples),
            "mean": np.mean(synthetic_samples, axis=0).tolist(),
            "std": np.std(synthetic_samples, axis=0).tolist(),
            "min": np.min(synthetic_samples, axis=0).tolist(),
            "max": np.max(synthetic_samples, axis=0).tolist()
        }
        
        # Calculate similarity between distributions
        real_mean = np.mean(real, axis=0)
        synth_mean = np.mean(synthetic_samples, axis=0)
        mean_diff = np.abs(real_mean - synth_mean) / (real_mean + 1e-6)
        stats["mean_difference_pct"] = (np.mean(mean_diff) * 100)
    
    return stats
