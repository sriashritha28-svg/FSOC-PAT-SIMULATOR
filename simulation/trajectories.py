import math
import numpy as np

class TrajectoryGenerator:
    """Generates 2D trajectory coordinates (x, y) for space targets over time."""
    
    @staticmethod
    def get_position(pattern: str, t: float, center_x: float, center_y: float, speed: float) -> tuple[float, float]:
        scale = speed * 10.0
        
        if pattern == "Stationary":
            return center_x, center_y
            
        elif pattern == "Linear":
            # Linear horizontal offset back and forth
            x = center_x + (t * scale * 2.0) % 800 - 400
            y = center_y
            return x, y
            
        elif pattern == "Circular":
            radius = 250.0
            omega = (speed * 0.2)
            x = center_x + radius * math.cos(omega * t)
            y = center_y + radius * math.sin(omega * t)
            return x, y
            
        elif pattern == "Sinusoidal":
            x = center_x + (t * scale * 1.5) % 800 - 400
            y = center_y + 150.0 * math.sin(0.1 * t * speed)
            return x, y
            
        elif pattern == "Accelerated":
            # Parabolic acceleration trajectory
            accel = 0.5 * speed
            x = center_x + 0.5 * accel * ((t % 20) ** 2) - 300
            y = center_y + 50.0 * math.sin(0.2 * t)
            return x, y
            
        elif pattern == "Random":
            # Smooth Perlin-like pseudo-random walk using multiple sine waves
            x = center_x + 300.0 * math.sin(0.05 * t * speed) + 100.0 * math.cos(0.13 * t * speed)
            y = center_y + 200.0 * math.cos(0.07 * t * speed) + 80.0 * math.sin(0.17 * t * speed)
            return x, y
            
        return center_x, center_y