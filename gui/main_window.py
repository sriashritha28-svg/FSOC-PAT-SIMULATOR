import time
import numpy as np
import cv2
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                             QPushButton, QComboBox, QSlider, QGroupBox, QFileDialog, QMessageBox)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap

from simulation.environment import VirtualEnvironment
from simulation.camera import VirtualCamera
from vision.tracker import AdaptiveBeaconTracker
from control.pid import PIDController
from control.camera_controller import CameraController
from disturbances.noise import NoiseEngine
from disturbances.vibration import VibrationEngine
from disturbances.turbulence import TurbulenceEngine
from analytics.metrics import PerformanceTracker
from analytics.report import ReportExporter
from gui.dashboard import PerformanceDashboard

class FSOCMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SIH 2026 PS 26169 — AI-Assisted FSOC Virtual Camera Tracking System")
        self.resize(1280, 800)
        self.setStyleSheet("background-color: #121417; color: #ffffff; font-family: Segoe UI, Arial;")

        # Initialize Simulation Subsystems
        self.env = VirtualEnvironment()
        self.camera = VirtualCamera()
        self.tracker = AdaptiveBeaconTracker()
        self.pid = PIDController()
        self.cam_controller = CameraController(self.camera, self.pid)
        self.perf_tracker = PerformanceTracker()

        self.sim_time = 0.0
        self.is_running = False
        self.demo_mode = False
        self.demo_step = 0

        self.init_ui()

        # Timer loop running at ~30 FPS
        self.timer = QTimer()
        self.timer.timeout.connect(self.simulation_step)

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # Left Column: Viewport & Telemetry Dashboard
        left_box = QVBoxLayout()
        
        # Camera Feed Viewport
        self.viewport_label = QLabel()
        self.viewport_label.setFixedSize(640, 480)
        self.viewport_label.setStyleSheet("border: 2px solid #00ffcc; background-color: #000000;")
        left_box.addWidget(self.viewport_label)

        # Performance Dashboard
        self.dashboard = PerformanceDashboard()
        left_box.addWidget(self.dashboard)

        main_layout.addLayout(left_box)

        # Right Column: Control Panels
        right_box = QVBoxLayout()

        # Group 1: Scenario & Target Trajectory Controls
        grp_scen = QGroupBox("Scenario & Target Configuration")
        grp_scen.setStyleSheet("QGroupBox { border: 1px solid #3a3f4d; bold; color: #00ffcc; margin-top: 6px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }")
        layout_scen = QVBoxLayout(grp_scen)
        
        layout_scen.addWidget(QLabel("Preset Test Scenario:"))
        self.combo_scenario = QComboBox()
        self.combo_scenario.addItems([
            "Custom Controls", "Scenario 1 — EASY", "Scenario 2 — MOVING",
            "Scenario 3 — NOISY", "Scenario 4 — VIBRATION", 
            "Scenario 5 — TURBULENCE", "Scenario 6 — STRESS TEST"
        ])
        self.combo_scenario.currentIndexChanged.connect(self.apply_scenario_preset)
        layout_scen.addWidget(self.combo_scenario)

        layout_scen.addWidget(QLabel("Target Trajectory:"))
        self.combo_traj = QComboBox()
        self.combo_traj.addItems(["Stationary", "Linear", "Circular", "Sinusoidal", "Accelerated", "Random"])
        self.combo_traj.currentTextChanged.connect(self.change_trajectory)
        layout_scen.addWidget(self.combo_traj)

        right_box.addWidget(grp_scen)

        # Group 2: Disturbance Simulation Engine
        grp_dist = QGroupBox("Disturbance Engine (0 - 100%)")
        grp_dist.setStyleSheet("QGroupBox { border: 1px solid #3a3f4d; bold; color: #00ffcc; margin-top: 6px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }")
        layout_dist = QVBoxLayout(grp_dist)

        self.slider_noise = self.create_slider(layout_dist, "Sensor Noise Level")
        self.slider_vib = self.create_slider(layout_dist, "Camera Platform Vibration")
        self.slider_turb = self.create_slider(layout_dist, "Atmospheric Turbulence")

        right_box.addWidget(grp_dist)

        # Action Buttons
        self.btn_start = QPushButton("START SIMULATION")
        self.btn_start.setStyleSheet("background-color: #0088cc; font-weight: bold; padding: 10px;")
        self.btn_start.clicked.connect(self.toggle_start)
        right_box.addWidget(self.btn_start)

        self.btn_demo = QPushButton("RUN SIH DEMO MODE")
        self.btn_demo.setStyleSheet("background-color: #ff9900; font-weight: bold; padding: 10px; color: #000000;")
        self.btn_demo.clicked.connect(self.start_demo_mode)
        right_box.addWidget(self.btn_demo)

        self.btn_reset = QPushButton("RESET POSITION / TRACKER")
        self.btn_reset.setStyleSheet("background-color: #444444; padding: 8px;")
        self.btn_reset.clicked.connect(self.reset_simulation)
        right_box.addWidget(self.btn_reset)

        self.btn_export = QPushButton("EXPORT EVALUATION REPORT")
        self.btn_export.setStyleSheet("background-color: #00aa66; font-weight: bold; padding: 10px;")
        self.btn_export.clicked.connect(self.export_report)
        right_box.addWidget(self.btn_export)

        main_layout.addLayout(right_box)

    def create_slider(self, layout, label_text) -> QSlider:
        lbl = QLabel(f"{label_text}: 0%")
        layout.addWidget(lbl)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(0)
        slider.valueChanged.connect(lambda v, l=lbl, t=label_text: l.setText(f"{t}: {v}%"))
        layout.addWidget(slider)
        return slider

    def change_trajectory(self, text: str):
        self.env.target_beacon.trajectory_type = text

    def apply_scenario_preset(self, idx: int):
        if idx == 1: # Easy
            self.combo_traj.setCurrentText("Stationary")
            self.slider_noise.setValue(0)
            self.slider_vib.setValue(0)
            self.slider_turb.setValue(0)
        elif idx == 2: # Moving
            self.combo_traj.setCurrentText("Circular")
            self.slider_noise.setValue(0)
            self.slider_vib.setValue(0)
            self.slider_turb.setValue(0)
        elif idx == 3: # Noisy
            self.combo_traj.setCurrentText("Linear")
            self.slider_noise.setValue(45)
            self.slider_vib.setValue(0)
            self.slider_turb.setValue(0)
        elif idx == 4: # Vibration
            self.combo_traj.setCurrentText("Sinusoidal")
            self.slider_noise.setValue(0)
            self.slider_vib.setValue(50)
            self.slider_turb.setValue(0)
        elif idx == 5: # Turbulence
            self.combo_traj.setCurrentText("Circular")
            self.slider_noise.setValue(10)
            self.slider_vib.setValue(0)
            self.slider_turb.setValue(60)
        elif idx == 6: # Stress Test
            self.combo_traj.setCurrentText("Random")
            self.slider_noise.setValue(40)
            self.slider_vib.setValue(40)
            self.slider_turb.setValue(50)

    def toggle_start(self):
        if not self.is_running:
            self.is_running = True
            self.btn_start.setText("PAUSE SIMULATION")
            self.btn_start.setStyleSheet("background-color: #cc3333; font-weight: bold; padding: 10px;")
            self.timer.start(33)  # ~30 FPS loop
        else:
            self.is_running = False
            self.btn_start.setText("START SIMULATION")
            self.btn_start.setStyleSheet("background-color: #0088cc; font-weight: bold; padding: 10px;")
            self.timer.stop()

    def start_demo_mode(self):
        self.demo_mode = True
        self.demo_step = 0
        self.apply_scenario_preset(1)  # Start easy
        if not self.is_running:
            self.toggle_start()

    def reset_simulation(self):
        self.camera.set_position(1000.0, 1000.0)
        self.tracker.reset()
        self.pid.reset()
        self.sim_time = 0.0

    def simulation_step(self):
        t0 = time.time()
        self.sim_time += 0.033

        # Demo Mode automated sequence progression
        if self.demo_mode:
            if self.sim_time > 5.0 and self.demo_step == 0:
                self.apply_scenario_preset(2) # Switch to circular motion
                self.demo_step = 1
            elif self.sim_time > 10.0 and self.demo_step == 1:
                self.apply_scenario_preset(5) # Add heavy turbulence
                self.demo_step = 2
            elif self.sim_time > 15.0 and self.demo_step == 2:
                self.apply_scenario_preset(6) # Full stress test
                self.demo_step = 3

        # 1. Update Environment Objects
        self.env.update(self.sim_time)

        # 2. Apply Camera Vibration Disturbances
        vib_dx, vib_dy = VibrationEngine.get_offset(self.slider_vib.value())
        self.camera.set_position(self.camera.pan + vib_dx, self.camera.tilt + vib_dy)

        # 3. Capture Camera Viewport Frame
        raw_frame = self.camera.capture(self.env.render(self.sim_time))

        # 4. Apply Visual Optical Disturbances (Noise & Turbulence)
        frame_distorted = NoiseEngine.apply(raw_frame, self.slider_noise.value())
        frame_distorted = TurbulenceEngine.apply(frame_distorted, self.slider_turb.value())

        # 5. Process Vision Tracking Pipeline
        detection, estimated_pos, lock_mode = self.tracker.process_frame(frame_distorted)

        # 6. Execute Closed-Loop Pointing Control
        if detection.found or lock_mode == "PREDICTIVE":
            target_vx, target_vy = estimated_pos
        else:
            target_vx, target_vy = self.camera.width / 2.0, self.camera.height / 2.0

        err_x, err_y = self.cam_controller.update_pointing(target_vx, target_vy, lock_mode)
        current_error = np.sqrt(err_x**2 + err_y**2)

        # Determine Display Lock Status
        if detection.found and current_error < 15.0:
            status_text = "LOCKED"
            status_color = (0, 255, 0)
        elif detection.found or lock_mode == "PREDICTIVE":
            status_text = "TRACKING"
            status_color = (0, 255, 255)
        else:
            status_text = "TARGET LOST"
            status_color = (0, 0, 255)

        # 7. Render Overlay Graphics on Viewport Frame
        view_rgb = cv2.cvtColor(frame_distorted, cv2.COLOR_GRAY2RGB)
        
        # Center Crosshair (Camera Optical Axis)
        cx, cy = self.camera.width // 2, self.camera.height // 2
        cv2.line(view_rgb, (cx - 15, cy), (cx + 15, cy), (255, 255, 255), 1)
        cv2.line(view_rgb, (cx, cy - 15), (cx, cy + 15), (255, 255, 255), 1)

        # Target Bounding Box & Centroid Indicator
        if detection.found:
            bx, by, bw, bh = detection.bbox
            cv2.rectangle(view_rgb, (bx, by), (bx + bw, by + bh), status_color, 2)
            cv2.circle(view_rgb, (int(detection.x), int(detection.y)), 3, (255, 0, 255), -1)
            cv2.putText(view_rgb, f"{detection.target_id} ({detection.confidence:.2f})", 
                        (bx, max(15, by - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, status_color, 1)

        # Telemetry Text Overlay
        cv2.putText(view_rgb, f"STATUS: {status_text}", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        cv2.putText(view_rgb, f"MODE: {lock_mode}", (15, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        # Display Frame in GUI
        h, w, ch = view_rgb.shape
        qimg = QImage(view_rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.viewport_label.setPixmap(QPixmap.fromImage(qimg))

        # Record Metrics
        t1 = time.time()
        proc_time_ms = (t1 - t0) * 1000.0
        fps = 1.0 / max(0.001, (t1 - t0))
        self.perf_tracker.record_frame(current_error, status_text, proc_time_ms, fps)

        # Update HUD Cards
        summary = self.perf_tracker.get_summary()
        self.dashboard.update_metrics(
            fps, summary["avg_error_px"], summary["lock_retention_pct"],
            lock_mode, self.camera.pan, self.camera.tilt,
            summary["lost_events"], summary["reacquisition_events"]
        )

    def export_report(self):
        metrics = self.perf_tracker.get_summary()
        params = {
            "trajectory": self.env.target_beacon.trajectory_type,
            "noise_pct": self.slider_noise.value(),
            "vibration_pct": self.slider_vib.value(),
            "turbulence_pct": self.slider_turb.value(),
            "kp": self.pid.kp, "ki": self.pid.ki, "kd": self.pid.kd
        }
        
        ReportExporter.export_csv("FSOC_Performance_Report.csv", metrics, params)
        ReportExporter.export_json("FSOC_Performance_Report.json", metrics, params)
        ReportExporter.export_plots("FSOC_Performance_Graphs.png", self.perf_tracker.errors, self.perf_tracker.fps_history)
        
        QMessageBox.information(self, "Report Exported", 
                                "Successfully generated:\n- FSOC_Performance_Report.csv\n- FSOC_Performance_Report.json\n- FSOC_Performance_Graphs.png")