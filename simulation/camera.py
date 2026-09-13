import numpy as np
import cv2

class VirtualCamera:
    """
    Simulates a pan-tilt optical camera viewport sampling a sub-region 
    of the global space environment based on current pan/tilt angles.
    """
    def __init__(self, width: int = 640, height: int = 480, fov: float = 30.0):
        self.width = width
        self.height = height
        self.fov = fov
        self.pan = 1000.0   # Center X in global space
        self.tilt = 1000.0  # Center Y in global space
        self.pan_limit = 1800.0
        self.tilt_limit = 1800.0

    def set_position(self, pan: float, tilt: float):
        self.pan = np.clip(pan, 200.0, self.pan_limit)
        self.tilt = np.clip(tilt, 200.0, self.tilt_limit)

    def capture(self, env_canvas: np.ndarray) -> np.ndarray:
        """Extracts viewport frame cropped around (pan, tilt)."""
        env_h, env_w = env_canvas.shape
        
        x1 = int(round(self.pan - self.width / 2))
        y1 = int(round(self.tilt - self.height / 2))
        x2 = x1 + self.width
        y2 = y1 + self.height
        
        # Handle boundary padding gracefully
        pad_x1 = max(0, -x1)
        pad_y1 = max(0, -y1)
        pad_x2 = max(0, x2 - env_w)
        pad_y2 = max(0, y2 - env_h)
        
        src_x1 = max(0, x1)
        src_y1 = max(0, y1)
        src_x2 = min(env_w, x2)
        src_y2 = min(env_h, y2)
        
        crop = env_canvas[src_y1:src_y2, src_x1:src_x2]
        
        if pad_x1 > 0 or pad_y1 > 0 or pad_x2 > 0 or pad_y2 > 0:
            viewport = np.pad(crop, ((pad_y1, pad_y2), (pad_x1, pad_x2)), mode='constant', constant_values=0)
        else:
            viewport = crop
            
        return viewport.copy()

    def global_to_viewport(self, gx: float, gy: float) -> tuple[float, float]:
        """Converts global environment coordinates to local viewport pixel coordinates."""
        vx = gx - (self.pan - self.width / 2)
        vy = gy - (self.tilt - self.height / 2)
        return vx, vy

    def viewport_to_global(self, vx: float, vy: float) -> tuple[float, float]:
        """Converts local viewport pixel coordinates to global environment coordinates."""
        gx = vx + (self.pan - self.width / 2)
        gy = vy + (self.tilt - self.height / 2)
        return gx, gy