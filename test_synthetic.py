"""Quick test for synthetic data augmentation"""
import numpy as np
from backend.ml.synthetic_generator import augment_samples, get_augmentation_stats
from backend.ml.train_model import train_model

# Create 10 fake 'real' samples (16 features each)
np.random.seed(42)
real_samples = np.array([
    [100, 10, 80, 15, 0.9, 1.1, 1.0, 0.95, 1.05, 1.0, 0.85, 1.15, 0.9, 1.1, 0.95, 1.05]
    for _ in range(10)
])
# Add some variation to make them realistic
real_samples += np.random.normal(0, 5, real_samples.shape)

# Test augmentation
augmented, metadata = augment_samples(real_samples, target_total=40)

print('=== Augmentation Test ===')
print(f'Real samples: {metadata["real_samples"]}')
print(f'Synthetic samples: {metadata["synthetic_samples"]}')
print(f'Total samples: {metadata["total_samples"]}')
print(f'Methods used: {metadata["methods"]}')
print(f'Augmentation shape: {augmented.shape}')

# Get stats
stats = get_augmentation_stats(real_samples, augmented[10:])  # synthetic only
print(f'Mean difference: {stats.get("mean_difference_pct", 0):.2f}%')

# Test training integration
print('\n=== Training Integration Test ===')
result = train_model(real_samples.tolist(), user_id=9999)
print(f'Raw samples stored: {len(result["raw_samples"])}')
print(f'Training samples used: {len(result["training_samples"])}')
aug_meta = result["augmentation_metadata"]
print(f'Augmentation used: {aug_meta["augmentation_used"]}')
print(f'Methods: {aug_meta["methods"]}')

print('\n=== ALL TESTS PASSED ===')
