import cv2
import numpy as np

class KalmanFilter2D:
    """
    2D Kinematic Kalman Filter for Optical Tracking.
    State Vector: [x, y, vx, vy]^T
    Measurement Vector: [x, y]^T
    Provides continuous state estimation and predictive trajectory tracking during loss-of-signal.
    """
    def __init__(self, dt: float = 0.033):
        self.kf = cv2.KalmanFilter(4, 2)
        
        # State Transition Matrix (F)
        self.kf.transitionMatrix = np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1,  0],
            [0, 0, 0,  1]
        ], np.float32)
        
        # Measurement Matrix (H)
        self.kf.measurementMatrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ], np.float32)
        
        # Process Noise Covariance (Q)
        self.kf.processNoiseCov = np.eye(4, dtype=np.float32) * 1e-2
        self.kf.processNoiseCov[2, 2] *= 5.0
        self.kf.processNoiseCov[3, 3] *= 5.0
        
        # Measurement Noise Covariance (R)
        self.kf.measurementNoiseCov = np.eye(2, dtype=np.float32) * 1e-1
        
        # Posterior Error Covariance (P)
        self.kf.errorCovPost = np.eye(4, dtype=np.float32)
        
        self.initialized = False

    def init(self, x: float, y: float):
        self.kf.statePost = np.array([[np.float32(x)], [np.float32(y)], [0.0], [0.0]], np.float32)
        self.initialized = True

    def predict(self) -> tuple[float, float]:
        """Predicts target position for the next time step."""
        prediction = self.kf.predict()
        return float(prediction[0][0]), float(prediction[1][0])

    def correct(self, x: float, y: float) -> tuple[float, float]:
        """Corrects internal state estimation using measured visual detector coordinates."""
        measurement = np.array([[np.float32(x)], [np.float32(y)]], np.float32)
        estimated = self.kf.correct(measurement)
        return float(estimated[0][0]), float(estimated[1][0])