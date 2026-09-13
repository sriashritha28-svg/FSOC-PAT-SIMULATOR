import cv2
import numpy as np
from dataclasses import dataclass

@dataclass
class DetectionResult:
    found: bool
    x: float
    y: float
    confidence: float
    bbox: tuple[int, int, int, int]  # (x, y, w, h)
    target_id: str

class OpticalBeaconDetector:
    """
    Computer-Vision Optical Beacon Detector.
    Employs adaptive thresholding, morphological filtering, continuous contour analysis,
    and beam signature verification (aspect ratio and circularity).
    """
    def __init__(self, min_threshold: int = 180):
        self.min_threshold = min_threshold

    def detect(self, frame: np.ndarray) -> DetectionResult:
        # 1. Preprocessing: Gaussian smoothing
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        
        # 2. Adaptive/Global Intensity Thresholding
        _, thresh = cv2.threshold(blurred, self.min_threshold, 255, cv2.THRESH_BINARY)
        
        # 3. Morphological Operations (Remove isolated noise points)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        # 4. Contour Detection
        contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        best_candidate = None
        max_score = -1.0
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 3 or area > 800:  # Filter out noise stars or huge optical blooms
                continue
                
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w) / h if h > 0 else 0
            
            # Optical beam circularity evaluation
            perimeter = cv2.arcLength(cnt, True)
            circularity = (4 * np.pi * area) / (perimeter ** 2) if perimeter > 0 else 0
            
            # Brightness centroid evaluation
            mask = np.zeros_like(frame)
            cv2.drawContours(mask, [cnt], -1, 255, -1)
            mean_val = cv2.mean(frame, mask=mask)[0]
            
            # Combined detection score (Confidence)
            score = (mean_val / 255.0) * 0.5 + circularity * 0.3 + (1.0 - abs(1.0 - aspect_ratio)) * 0.2
            
            if score > max_score and score > 0.35:
                max_score = score
                # Exact spatial moments for sub-pixel centroid position
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cx = float(M["m10"] / M["m00"])
                    cy = float(M["m01"] / M["m00"])
                else:
                    cx = float(x + w / 2.0)
                    cy = float(y + h / 2.0)
                    
                best_candidate = (cx, cy, score, (x, y, w, h))
                
        if best_candidate:
            cx, cy, score, bbox = best_candidate
            return DetectionResult(
                found=True,
                x=cx,
                y=cy,
                confidence=min(score, 1.0),
                bbox=bbox,
                target_id="BEACON-01"
            )
            
        return DetectionResult(found=False, x=0.0, y=0.0, confidence=0.0, bbox=(0,0,0,0), target_id="NONE")