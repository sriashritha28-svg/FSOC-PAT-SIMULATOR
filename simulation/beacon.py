import numpy as np
import cv2
from simulation.trajectories import TrajectoryGenerator

class OpticalBeacon:
    """
    Represents an FSOC Optical Beacon emitting a distinct optical signal signature
    with modulated intensity (pulsing frequency) for identification.
    """
    def __init__(self, beacon_id: str = "BEACON-01", x: float = 1000.0, y: float = 1000.0, is_target: bool = True):
        self.id = beacon_id
        self.x = x
        self.y = y
        self.is_target = is_target
        self.trajectory_type = "Stationary"
        self.speed = 5.0
        self.base_intensity = 255
        self.pulsing_freq = 0.1  # Pulsing frequency for target signature verification
        self.radius = 6

    def update(self, t: float, origin_x: float, origin_y: float):
        self.x, self.y = TrajectoryGenerator.get_position(
            self.trajectory_type, t, origin_x, origin_y, self.speed
        )

    def render(self, canvas: np.ndarray, time_sec: float):
        # Unique temporal intensity modulation (signature)
        modulation = 0.85 + 0.15 * np.sin(2 * np.pi * self.pulsing_freq * time_sec * 10)
        curr_intensity = int(self.base_intensity * modulation)
        
        ix, iy = int(round(self.x)), int(round(self.y))
        h, w = canvas.shape[:2]
        
        if 0 <= ix < w and 0 <= iy < h:
            color = (curr_intensity, curr_intensity, curr_intensity) if self.is_target else (160, 160, 160)
            cv2.circle(canvas, (ix, iy), self.radius, color, -1)
            # Optical beam halo effect (Gaussian beam profile model)
            cv2.circle(canvas, (ix, iy), self.radius * 3, (curr_intensity // 4, curr_intensity // 4, curr_intensity // 4), 1)