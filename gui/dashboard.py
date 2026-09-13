from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame
from PyQt6.QtCore import Qt

class MetricCard(QFrame):
    def __init__(self, title: str, initial_val: str = "0.0"):
        super().__init__()
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("background-color: #1e222a; border-radius: 6px; border: 1px solid #3a3f4d;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #8a93a5; font-size: 10px; font-weight: bold;")
        
        self.lbl_val = QLabel(initial_val)
        self.lbl_val.setStyleSheet("color: #00ffcc; font-size: 16px; font-weight: bold;")
        
        layout.addWidget(lbl_title)
        layout.addWidget(self.lbl_val)

    def set_value(self, val: str):
        self.lbl_val.setText(val)

class PerformanceDashboard(QWidget):
    """Real-time HUD displaying telemetry cards."""
    def __init__(self):
        super().__init__()
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.card_fps = MetricCard("SYSTEM FPS", "0.0")
        self.card_err = MetricCard("AVG ERROR (PX)", "0.0")
        self.card_lock = MetricCard("LOCK RETENTION", "100%")
        self.card_mode = MetricCard("TRACKING MODE", "NORMAL")
        self.card_pan_tilt = MetricCard("PAN / TILT", "1000 / 1000")
        self.card_events = MetricCard("LOST / REACQ", "0 / 0")

        layout.addWidget(self.card_fps, 0, 0)
        layout.addWidget(self.card_err, 0, 1)
        layout.addWidget(self.card_lock, 0, 2)
        layout.addWidget(self.card_mode, 1, 0)
        layout.addWidget(self.card_pan_tilt, 1, 1)
        layout.addWidget(self.card_events, 1, 2)

    def update_metrics(self, fps: float, avg_err: float, lock_pct: float, mode: str, pan: float, tilt: float, lost: int, reacq: int):
        self.card_fps.set_value(f"{fps:.1f}")
        self.card_err.set_value(f"{avg_err:.2f}")
        self.card_lock.set_value(f"{lock_pct:.1f}%")
        self.card_mode.set_value(mode)
        self.card_pan_tilt.set_value(f"{int(pan)} / {int(tilt)}")
        self.card_events.set_value(f"{lost} / {reacq}")