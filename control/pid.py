import numpy as np

class PIDController:
    """
    Proportional-Integral-Derivative (PID) Controller for optical pan-tilt steering.
    Includes anti-windup clamp on integral terms.
    """
    def __init__(self, kp: float = 0.08, ki: float = 0.001, kd: float = 0.02):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        
        self.integral_x = 0.0
        self.integral_y = 0.0
        self.prev_error_x = 0.0
        self.prev_error_y = 0.0
        
        self.integral_limit = 100.0

    def compute(self, error_x: float, error_y: float, dt: float = 0.033) -> tuple[float, float]:
        if dt <= 0:
            dt = 0.033
            
        # Proportional term
        p_out_x = self.kp * error_x
        p_out_y = self.kp * error_y
        
        # Integral term with anti-windup clamping
        self.integral_x = np.clip(self.integral_x + error_x * dt, -self.integral_limit, self.integral_limit)
        self.integral_y = np.clip(self.integral_y + error_y * dt, -self.integral_limit, self.integral_limit)
        i_out_x = self.ki * self.integral_x
        i_out_y = self.ki * self.integral_y
        
        # Derivative term
        d_out_x = self.kd * (error_x - self.prev_error_x) / dt
        d_out_y = self.kd * (error_y - self.prev_error_y) / dt
        
        self.prev_error_x = error_x
        self.prev_error_y = error_y
        
        cmd_pan = p_out_x + i_out_x + d_out_x
        cmd_tilt = p_out_y + i_out_y + d_out_y
        
        return cmd_pan, cmd_tilt

    def reset(self):
        self.integral_x = 0.0
        self.integral_y = 0.0
        self.prev_error_x = 0.0
        self.prev_error_y = 0.0