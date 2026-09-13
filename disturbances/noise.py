import numpy as np

class NoiseEngine:
    """Applies sensor readout noise (Gaussian zero-mean noise) to the camera frame."""
    @staticmethod
    def apply(image: np.ndarray, intensity: float) -> np.ndarray:
        if intensity <= 0.0:
            return image
        std_dev = (intensity / 100.0) * 50.0
        gauss = np.random.normal(0, std_dev, image.shape).astype(np.float32)
        noisy = image.astype(np.float32) + gauss
        return np.clip(noisy, 0, 255).astype(np.uint8)