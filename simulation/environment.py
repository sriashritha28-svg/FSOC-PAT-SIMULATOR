import numpy as np
import cv2
import random
from simulation.beacon import OpticalBeacon

class VirtualEnvironment:
    """
    Simulates dark space environment containing static background stars,
    distractor bright objects, and the primary target FSOC beacon.
    """
    def __init__(self, width: int = 2000, height: int = 2000, star_count: int = 200):
        self.width = width
        self.height = height
        self.canvas = np.zeros((height, width), dtype=np.uint8)
        self.stars = [(random.randint(0, width - 1), random.randint(0, height - 1), random.randint(50, 180)) 
                      for _ in range(star_count)]
        
        # Primary target optical beacon
        self.target_beacon = OpticalBeacon("BEACON-01", width / 2, height / 2, is_target=True)
        
        # Distractor objects (unmodulated bright space debris/secondary satellites)
        self.distractors = [
            OpticalBeacon("DISTRACTOR-A", width / 2 - 300, height / 2 + 200, is_target=False),
            OpticalBeacon("DISTRACTOR-B", width / 2 + 400, height / 2 - 250, is_target=False)
        ]
        
        # Static distractors do not pulse
        for d in self.distractors:
            d.pulsing_freq = 0.0

    def update(self, t: float):
        self.target_beacon.update(t, self.width / 2, self.height / 2)
        # Distractors slowly drift
        for i, d in enumerate(self.distractors):
            d.x += np.sin(t * 0.1 + i) * 0.5
            d.y += np.cos(t * 0.1 + i) * 0.5

    def render(self, t: float) -> np.ndarray:
        self.canvas.fill(0)
        # Draw background stars
        for sx, sy, s_int in self.stars:
            self.canvas[sy, sx] = s_int
            
        # Draw distractors and target beacon
        for d in self.distractors:
            d.render(self.canvas, t)
        self.target_beacon.render(self.canvas, t)
        
        return self.canvas