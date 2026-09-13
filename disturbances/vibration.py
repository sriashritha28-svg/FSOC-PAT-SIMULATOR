import numpy as np

class VibrationEngine:
    """Simulates high-frequency angular vibration of the camera platform."""
    @staticmethod
    def get_offset(intensity: float) -> tuple[float, float]:
        if intensity <= 0.0:
            return 0.0, 0.0
        max_jitter = (intensity / 100.0) * 12.0
        dx = np.random.uniform(-max_jitter, max_jitter)
        dy = np.random.uniform(-max_jitter, max_jitter)
        return dx, dy