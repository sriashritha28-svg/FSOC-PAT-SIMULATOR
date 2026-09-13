import numpy as np
from simulation.camera import VirtualCamera
from control.pid import PIDController

class CameraController:
    """
    Closed-Loop Camera Stepper converting Tracking Error into Pan/Tilt Drive Commands.
    """
    def __init__(self, camera: VirtualCamera, pid: PIDController):
        self.camera = camera
        self.pid = pid
        self.max_speed = 15.0  # Max angular pixel motion per step

    def update_pointing(self, target_vx: float, target_vy: float, lock_mode: str) -> tuple[float, float]:
        # Target error relative to viewport center
        center_x = self.camera.width / 2.0
        center_y = self.camera.height / 2.0
        
        error_x = target_vx - center_x
        error_y = target_vy - center_y
        
        if lock_mode == "REACQUISITION":
            # In reacquisition mode, perform slow search sweep or stay stationary
            return error_x, error_y
            
        cmd_pan, cmd_tilt = self.pid.compute(error_x, error_y)
        
        # Limit maximum actuation velocity per frame
        cmd_pan = np.clip(cmd_pan, -self.max_speed, self.max_speed)
        cmd_tilt = np.clip(cmd_tilt, -self.max_speed, self.max_speed)
        
        # Drive physical camera pan/tilt angles
        new_pan = self.camera.pan + cmd_pan
        new_tilt = self.camera.tilt + cmd_tilt
        self.camera.set_position(new_pan, new_tilt)
        
        return error_x, error_y