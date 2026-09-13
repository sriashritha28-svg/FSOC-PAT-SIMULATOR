import numpy as np
import cv2

class TurbulenceEngine:
    """
    Simulates atmospheric optical turbulence using Gaussian point-spread blur,
    intensity scintillation, and beam wandering refraction.
    """
    @staticmethod
    def apply(image: np.ndarray, intensity: float) -> np.ndarray:
        if intensity <= 0.0:
            return image
        
        factor = intensity / 100.0
        
        # 1. Optical blurring (Gaussian PSFs)
        kernel_size = int(factor * 10) | 1  # Ensure odd kernel size
        if kernel_size > 1:
            blurred = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        else:
            blurred = image.copy()
            
        # 2. Intensity scintillation (Random atmospheric fading)
        scintillation = 1.0 + np.random.uniform(-0.4 * factor, 0.2 * factor)
        scintillated = np.clip(blurred.astype(np.float32) * scintillation, 0, 255).astype(np.uint8)
        
        # 3. Micro-refraction beam wander displacement
        if factor > 0.2:
            dx = int(np.random.uniform(-3 * factor, 3 * factor))
            dy = int(np.random.uniform(-3 * factor, 3 * factor))
            M = np.float32([[1, 0, dx], [0, 1, dy]])
            h, w = scintillated.shape
            scintillated = cv2.warpAffine(scintillated, M, (w, h))
            
        return scintillated