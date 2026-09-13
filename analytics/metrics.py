import time
import numpy as np

class PerformanceTracker:
    """Computes real-time telemetry metrics and system performance evaluation data."""
    def __init__(self):
        self.start_time = time.time()
        self.total_frames = 0
        self.errors = []
        self.fps_history = []
        self.proc_times = []
        self.lock_frames = 0
        self.lost_events = 0
        self.reacquisition_events = 0
        self.prev_status = "LOST"

    def record_frame(self, tracking_error: float, status_str: str, proc_time_ms: float, fps: float):
        self.total_frames += 1
        self.errors.append(tracking_error)
        self.proc_times.append(proc_time_ms)
        self.fps_history.append(fps)
        
        if status_str == "LOCKED":
            self.lock_frames += 1
            
        if self.prev_status != "TARGET LOST" and status_str == "TARGET LOST":
            self.lost_events += 1
        elif self.prev_status == "TARGET LOST" and status_str in ["TRACKING", "LOCKED"]:
            self.reacquisition_events += 1
            
        self.prev_status = status_str

    def get_summary(self) -> dict:
        duration = max(0.1, time.time() - self.start_time)
        avg_err = float(np.mean(self.errors)) if self.errors else 0.0
        max_err = float(np.max(self.errors)) if self.errors else 0.0
        avg_fps = float(np.mean(self.fps_history)) if self.fps_history else 0.0
        min_fps = float(np.min(self.fps_history)) if self.fps_history else 0.0
        avg_proc = float(np.mean(self.proc_times)) if self.proc_times else 0.0
        max_proc = float(np.max(self.proc_times)) if self.proc_times else 0.0
        lock_rate = (self.lock_frames / max(1, self.total_frames)) * 100.0

        return {
            "duration_sec": round(duration, 2),
            "total_frames": self.total_frames,
            "avg_fps": round(avg_fps, 1),
            "min_fps": round(min_fps, 1),
            "avg_error_px": round(avg_err, 2),
            "max_error_px": round(max_err, 2),
            "lock_retention_pct": round(lock_rate, 1),
            "avg_proc_time_ms": round(avg_proc, 2),
            "max_proc_time_ms": round(max_proc, 2),
            "lost_events": self.lost_events,
            "reacquisition_events": self.reacquisition_events
        }