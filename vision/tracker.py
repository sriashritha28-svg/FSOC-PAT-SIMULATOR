from vision.detector import DetectionResult, OpticalBeaconDetector
from vision.kalman import KalmanFilter2D

class AdaptiveBeaconTracker:
    """
    State machine for FSOC Beacon Tracking:
    Decomposes process into Detection -> Estimation -> Prediction -> Reacquisition.
    Modes: NORMAL, PREDICTIVE, REACQUISITION.
    """
    def __init__(self):
        self.detector = OpticalBeaconDetector()
        self.kalman = KalmanFilter2D()
        self.mode = "REACQUISITION"
        self.lost_frames = 0
        self.max_lost_threshold = 15
        
        self.estimated_x = 0.0
        self.estimated_y = 0.0
        self.predicted_x = 0.0
        self.predicted_y = 0.0

    def process_frame(self, frame) -> tuple[DetectionResult, tuple[float, float], str]:
        # Step 1: Raw Optical Detection
        detection = self.detector.detect(frame)
        
        # Step 2: Kalman Prediction Step
        if self.kalman.initialized:
            self.predicted_x, self.predicted_y = self.kalman.predict()
        
        # Step 3: State Machine Logic & Correction
        if detection.found:
            if not self.kalman.initialized:
                self.kalman.init(detection.x, detection.y)
                
            self.estimated_x, self.estimated_y = self.kalman.correct(detection.x, detection.y)
            self.lost_frames = 0
            self.mode = "NORMAL"
        else:
            self.lost_frames += 1
            if self.kalman.initialized and self.lost_frames <= self.max_lost_threshold:
                # Use Kalman velocity prediction during transient atmospheric signal drops
                self.estimated_x, self.estimated_y = self.predicted_x, self.predicted_y
                self.mode = "PREDICTIVE"
            else:
                self.mode = "REACQUISITION"
                
        return detection, (self.estimated_x, self.estimated_y), self.mode

    def reset(self):
        self.kalman.initialized = False
        self.lost_frames = 0
        self.mode = "REACQUISITION"