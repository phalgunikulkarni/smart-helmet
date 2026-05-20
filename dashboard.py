# dashboard.py
# Main dashboard showing all sensor data in one window
# Combines bump detection, GPS zone, rear camera, and heuristic curve analysis
# REAL DATA MODE: Loads actual CSV sensor data instead of simulation
# Built with Tkinter

import tkinter as tk
from tkinter import font
import threading
import time
import platform
import random
import cv2
import numpy as np
import pandas as pd
from collections import deque
from scipy.signal import find_peaks
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
SIMULATED = False

# ── Import bump detection ──────────────────────────────────
if platform.system() == "Windows":
    from smbus2_mock import SMBus
else:
    from smbus2 import SMBus

from bump_detection import initialize_sensor, get_acceleration, detect_bump
from gps_zone import get_gps_position, check_zone, SIMULATED_PATH
from curve_detection_pipeline import calculate_curve_features, classify_anomaly

# ── Camera setup ───────────────────────────────────────────
CAMERA_INDEX  = 0
OBSTACLE_AREA = 8000

# ── CSV Data Loading ───────────────────────────────────────
CSV_DATA_FILE = r'5th_A_Cross_Road-2026-05-13_06-34-36/merged_data.csv'  # Real sensor data

def load_csv_data():
    """Load sensor data from CSV file"""
    try:
        df = pd.read_csv(CSV_DATA_FILE)
        return df
    except Exception as e:
        print(f"[ERROR] Failed to load CSV: {e}")
        return None

# ══════════════════════════════════════════════════════════
#  Dashboard App
# ══════════════════════════════════════════════════════════
class SmartHelmetDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Helmet Dashboard - Advanced Heuristic Analysis")
        self.root.geometry("1200x720")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(False, False)

        # State variables
        self.bump_status    = "Monitoring..."
        self.bump_magnitude = 0.0
        self.zone_status    = "Checking..."
        self.zone_name      = ""
        self.speed_limit    = 0
        self.obstacle_status = "Clear"
        self.gps_index      = 0
        self.running        = True
        
        # Heuristic analysis state
        self.hazard_type    = "Unknown"
        self.confidence     = 0.0
        self.pothole_score  = 0.0
        self.speed_bump_score = 0.0
        self.curve_features = {}
        
        # Rolling buffer for curve data (for heuristic analysis)
        self.accel_buffer   = deque(maxlen=50)
        self.gyro_buffer    = deque(maxlen=50)
        # Real-time graph buffers
        self.graph_buffer = deque(maxlen=100)
        self.time_buffer = deque(maxlen=100)

        # Current sensor values
        self.current_ax = 0
        self.current_ay = 0
        self.current_az = 0

        # Camera
        self.cap        = None
        self.prev_frame = None

        self.build_ui()
        # Start sensors and camera after UI is built
        self.root.after(100, self.start_sensors)
        self.root.after(100, self.start_camera)

    # ── UI Layout ─────────────────────────────────────────
    def build_ui(self):
        title_font  = font.Font(family="Helvetica", size=18, weight="bold")
        label_font  = font.Font(family="Helvetica", size=11)
        value_font  = font.Font(family="Helvetica", size=14, weight="bold")
        status_font = font.Font(family="Helvetica", size=12)

        # ── Title bar ──
        title = tk.Label(
            self.root, text="🪖 Smart Helmet Dashboard",
            bg="#1a1a2e", fg="#e0e0e0", font=title_font, pady=10
        )
        title.pack(fill="x")

        # ── Top row: 4 status cards ──
        top_frame = tk.Frame(self.root, bg="#1a1a2e")
        top_frame.pack(fill="x", padx=15, pady=5)

        # Bump card
        self.bump_card = self.make_card(top_frame, "🚗  Bump / Pothole")
        self.bump_card.pack(side="left", expand=True, fill="both", padx=5)

        self.bump_label = tk.Label(
            self.bump_card, text="Monitoring...",
            bg="#16213e", fg="#00d4ff", font=value_font
        )
        self.bump_label.pack(pady=5)

        self.bump_mag_label = tk.Label(
            self.bump_card, text="Magnitude: 0.00g",
            bg="#16213e", fg="#a0a0a0", font=label_font
        )
        self.bump_mag_label.pack(pady=2)

        self.sensor_xyz_label = tk.Label(
    self.bump_card,
    text="X: 0.00  Y: 0.00  Z: 0.00",
    bg="#16213e",
    fg="#ffffff",
    font=label_font
)
        self.sensor_xyz_label.pack(pady=2)
        # Heuristic Analysis card (NEW)
        self.heuristic_card = self.make_card(top_frame, "🧠  Heuristic Analysis")
        self.heuristic_card.pack(side="left", expand=True, fill="both", padx=5)

        self.hazard_label = tk.Label(
            self.heuristic_card, text="Analyzing...",
            bg="#16213e", fg="#00d4ff", font=value_font
        )
        self.hazard_label.pack(pady=5)

        self.confidence_label = tk.Label(
            self.heuristic_card, text="Confidence: 0%",
            bg="#16213e", fg="#a0a0a0", font=label_font
        )
        self.confidence_label.pack(pady=2)

        # GPS Zone card
        self.zone_card = self.make_card(top_frame, "📍  GPS Zone")
        self.zone_card.pack(side="left", expand=True, fill="both", padx=5)

        self.zone_label = tk.Label(
            self.zone_card, text="Checking...",
            bg="#16213e", fg="#00d4ff", font=value_font
        )
        self.zone_label.pack(pady=5)

        self.speed_label = tk.Label(
            self.zone_card, text="Speed limit: --",
            bg="#16213e", fg="#a0a0a0", font=label_font
        )
        self.speed_label.pack(pady=2)

        # Obstacle card
        self.obstacle_card = self.make_card(top_frame, "📷  Rear Camera")
        self.obstacle_card.pack(side="left", expand=True, fill="both", padx=5)

        self.obstacle_label = tk.Label(
            self.obstacle_card, text="Clear",
            bg="#16213e", fg="#00ff88", font=value_font
        )
        self.obstacle_label.pack(pady=5)

        self.obstacle_count_label = tk.Label(
            self.obstacle_card, text="Objects detected: 0",
            bg="#16213e", fg="#a0a0a0", font=label_font
        )
        self.obstacle_count_label.pack(pady=2)

        # ── Alert bar ──
        self.alert_var = tk.StringVar(value="  ✅  All systems normal")
        self.alert_bar = tk.Label(
            self.root,
            textvariable=self.alert_var,
            bg="#0f3460", fg="#ffffff",
            font=status_font, pady=8, anchor="w", padx=15
        )
        self.alert_bar.pack(fill="x", padx=15, pady=8)

        # ── Bottom row: camera feed + log ──
        bottom_frame = tk.Frame(self.root, bg="#1a1a2e")
        bottom_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # Camera feed
        cam_frame = tk.Frame(
            bottom_frame, bg="#16213e",
            relief="flat", bd=1,
            highlightbackground="#0f3460", highlightthickness=1
        )
        cam_frame.pack(side="left", padx=5, pady=5)

        cam_title = tk.Label(
            cam_frame, text="Live Camera Feed",
            bg="#16213e", fg="#a0a0a0",
            font=label_font
        )
        cam_title.pack(pady=4)

        self.cam_label = tk.Label(cam_frame, bg="#0a0a1a")
        self.cam_label.pack(padx=8, pady=4)

        # Event log
        log_frame = tk.Frame(
            bottom_frame, bg="#16213e",
            relief="flat", bd=1,
            highlightbackground="#0f3460", highlightthickness=1
        )
        log_frame.pack(
            side="left", expand=True,
            fill="both", padx=5, pady=5
        )

        log_title = tk.Label(
            log_frame, text="Event Log",
            bg="#16213e", fg="#a0a0a0", font=label_font
        )
        log_title.pack(pady=4)

        self.log_box = tk.Text(
            log_frame, bg="#0a0a1a", fg="#c0c0c0",
            font=("Courier", 9), state="disabled",
            relief="flat", wrap="word"
        )
        self.log_box.pack(
            fill="both", expand=True, padx=8, pady=4
        )

    def make_card(self, parent, title):
        """Create a dark card panel with a title"""
        frame = tk.Frame(
            parent, bg="#16213e",
            relief="flat", bd=1,
            highlightbackground="#0f3460",
            highlightthickness=1
        )
        tk.Label(
            frame, text=title,
            bg="#16213e", fg="#a0a0a0",
            font=font.Font(family="Helvetica", size=10)
        ).pack(pady=6)
        return frame

    # ── Logging ───────────────────────────────────────────
    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{timestamp}] {message}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    # ── Alert bar ─────────────────────────────────────────
    def set_alert(self, message, color="#0f3460"):
        self.alert_var.set(f"  {message}")
        self.alert_bar.configure(bg=color)

    # ── Sensor thread ─────────────────────────────────────
    def start_sensors(self):
        self.bus = SMBus(1)
        initialize_sensor(self.bus)
        
        # Load CSV data for real analysis
        self.csv_data = load_csv_data()
        if self.csv_data is not None:
            self.log("[CSV] Loaded real sensor data for heuristic analysis")
        
        thread = threading.Thread(
            target=self.sensor_loop, daemon=True
        )
        thread.start()

    def sensor_loop(self):
        # Use CSV data if available, otherwise fall back to simulation
        if self.csv_data is not None:
            self.csv_sensor_loop()
        else:
            self.simulated_sensor_loop()

    def csv_sensor_loop(self):
        """Process real sensor data from CSV file"""
        df = self.csv_data.copy()
        
        # Calculate baseline and spike for peak detection
        baseline_gravity = df['magnitude'].median()
        df['abs_spike'] = (df['magnitude'] - baseline_gravity).abs()
        
        # Find peaks in the real data
        peaks, _ = find_peaks(df['abs_spike'], height=2.5, distance=20)
        
        self.log(f"[CSV] Found {len(peaks)} potential peaks in sensor data")
        
        # Process each peak
        for peak_idx in peaks:
            if not self.running:
                break
            
            try:
                # Extract data around the peak
                slice_start = max(0, peak_idx - 20)
                slice_end = min(len(df), peak_idx + 20)
                curve_slice = df.iloc[slice_start:slice_end].copy()
                
                # Get peak metrics
                peak_height = df.iloc[peak_idx]['abs_spike']
                timestamp = df.iloc[peak_idx]['seconds_elapsed']
                magnitude = df.iloc[peak_idx]['magnitude']
                
                # Get live XYZ sensor values
                ax = df.iloc[peak_idx]['accel_x']
                ay = df.iloc[peak_idx]['accel_y']
                az = df.iloc[peak_idx]['accel_z']

                # Update live XYZ display
                self.root.after(
                    0,
                    lambda ax=ax, ay=ay, az=az:
                    self.sensor_xyz_label.configure(
                    text=f"X:{ax:.2f}  Y:{ay:.2f}  Z:{az:.2f}"
                )
                )
                # Update UI with bump detection
                self.bump_magnitude = cv2.magnitude
                self.root.after(0, self.update_bump_ui, True, magnitude)
                
                # Calculate vibration duration
                elevated_duration = (curve_slice['abs_spike'] > 1.2).sum()
                
                # Run heuristic analysis with REAL DataFrame
                if len(curve_slice) >= 15:
                    # Create proper pandas DataFrame for heuristic functions
                    analysis_frame = pd.DataFrame({
                        'absolute_spike': curve_slice['abs_spike'].values,
                        'accel_z': curve_slice['accel_z'].values,
                        'gyro_x': curve_slice['gyro_x'].values if 'gyro_x' in curve_slice.columns else np.zeros(len(curve_slice)),
                        'gyro_y': curve_slice['gyro_y'].values if 'gyro_y' in curve_slice.columns else np.zeros(len(curve_slice)),
                        'gyro_z': curve_slice['gyro_z'].values if 'gyro_z' in curve_slice.columns else np.zeros(len(curve_slice)),
                    })
                    
                    # Calculate features
                    features = calculate_curve_features(analysis_frame)
                    
                    # Classify
                    anomaly_class, confidence, pothole_score, speed_bump_score = classify_anomaly(
                        peak_height, elevated_duration, features
                    )
                    
                    # Store results
                    self.hazard_type = anomaly_class
                    self.confidence = confidence
                    self.pothole_score = pothole_score
                    self.speed_bump_score = speed_bump_score
                    self.curve_features = features
                    
                    # Update UI
                    self.root.after(0, self.update_heuristic_ui, anomaly_class, confidence, features)
                    
                    # Log classification
                    if anomaly_class != "False error" and confidence > 0.45:
                        self.log(f"✅ CLASSIFICATION: {anomaly_class} | Confidence: {confidence:.0%} | Peak: {peak_height:.2f}g | Duration: {elevated_duration}")
                    else:
                        self.log(f"⚠️  Low confidence: {confidence:.0%} (peak: {peak_height:.2f}g)")
                
                # Delay between peak processing
                time.sleep(1.5)
                
            except Exception as e:
                self.log(f"[ERROR] Peak analysis failed: {str(e)[:80]}")
                time.sleep(0.5)
                continue
        
        self.log("[CSV] Completed analysis of all peaks")
        self.log("[INFO] Playback finished - monitoring paused")

    def simulated_sensor_loop(self):
        """Fall back to simulated sensor data if CSV not available"""
        last_peak_time = 0
        peak_cooldown = 2.0
        
        while self.running:
            # Simulate data with occasional bumps
            ax = np.random.uniform(-0.3, 0.3)
            ay = np.random.uniform(-0.3, 0.3)
            az = np.random.uniform(0.8, 1.2) + (5.0 if random.random() < 0.05 else 0)
            
            magnitude = np.sqrt(ax**2 + ay**2 + az**2)
            self.bump_magnitude = magnitude
            
            bump = magnitude > 2.0
            
            if bump:
                self.root.after(0, self.update_bump_ui, True, magnitude)
            else:
                self.root.after(0, self.update_bump_ui, False, magnitude)
            
            time.sleep(0.2)

    # ── UI update helpers (called from main thread) ───────
    def update_bump_ui(self, bump, magnitude):
        if bump:
            self.bump_label.configure(
                text="🚨 BUMP!", fg="#ff4444"
            )
            self.set_alert(
                f"🚨 Bump detected! Magnitude: {magnitude:.2f}g",
                color="#7a0000"
            )
        else:
            self.bump_label.configure(
                text="✅ Smooth", fg="#00ff88"
            )
        self.bump_mag_label.configure(
            text=f"Magnitude: {magnitude:.2f}g"
        )

    def update_zone_ui(self, in_zone, zone_name, speed_limit):
        if in_zone:
            self.zone_label.configure(
                text=f"⚠️ {zone_name}", fg="#ffaa00"
            )
            self.speed_label.configure(
                text=f"Speed limit: {speed_limit} km/h"
            )
            self.set_alert(
                f"⚠️  {zone_name} — Max {speed_limit} km/h",
                color="#7a4400"
            )
        else:
            self.zone_label.configure(
                text="✅ Open Road", fg="#00ff88"
            )
            self.speed_label.configure(text="Speed limit: --")

    def update_obstacle_ui(self, count):
        if count > 0:
            self.obstacle_label.configure(
                text="🚨 OBSTACLE!", fg="#ff4444"
            )
            self.obstacle_count_label.configure(
                text=f"Objects detected: {count}"
            )
            self.set_alert(
                f"🚨 {count} obstacle(s) detected behind you!",
                color="#7a0000"
            )
            self.log(f"Obstacle detected — {count} object(s) in view")
        else:
            self.obstacle_label.configure(
                text="✅ Clear", fg="#00ff88"
            )
            self.obstacle_count_label.configure(
                text="Objects detected: 0"
            )

    # ── Heuristic Analysis ────────────────────────────────
    def update_heuristic_ui(self, hazard_type, confidence, features):
        """Update heuristic analysis card with classification results"""
        if hazard_type == "Pothole":
            color = "#ff6666"
            icon = "🕳️"
        elif hazard_type == "Speed bump":
            color = "#ffaa00"
            icon = "⛔"
        elif hazard_type == "Smooth road":
            color = "#00ff88"
            icon = "🛣️"
        else:
            color = "#ffffff"
            icon = "?"
        
        self.hazard_label.configure(
            text=f"{icon} {hazard_type}", fg=color
        )
        self.confidence_label.configure(
            text=f"Confidence: {confidence:.0%} | Rise: {features.get('rise_rate', 0):.3f}"
        )
        
        # Update alert bar
        if hazard_type == "Pothole":
            self.set_alert(
                f"🕳️  POTHOLE DETECTED! Confidence: {confidence:.0%}",
                color="#7a0000"
            )
        elif hazard_type == "Speed bump":
            self.set_alert(
                f"⛔  SPEED BUMP! Confidence: {confidence:.0%}",
                color="#7a4400"
            )

    # ── Camera thread ─────────────────────────────────────
    def start_camera(self):
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

        if not self.cap.isOpened():
            self.log("[WARN] Camera not found — skipping feed")
            return

        ret, self.prev_frame = self.cap.read()
        thread = threading.Thread(
            target=self.camera_loop, daemon=True
        )
        thread.start()

    def camera_loop(self):
        while self.running:
            if self.cap is None or not self.cap.isOpened():
                break

            ret, frame = self.cap.read()
            if not ret:
                break

            # Obstacle detection
            obstacles = self.detect_obstacles(frame)
            self.root.after(
                0, self.update_obstacle_ui, len(obstacles)
            )

            # Draw boxes
            for (x, y, w, h, area) in obstacles:
                cv2.rectangle(
                    frame, (x, y), (x+w, y+h), (0, 0, 255), 2
                )

            # Convert to RGB for PIL
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.root.after(0, self.update_camera_feed, rgb)
            self.prev_frame = frame.copy()

            time.sleep(0.03)

    def detect_obstacles(self, frame):
        if self.prev_frame is None:
            return []

        gray_curr = cv2.cvtColor(frame,           cv2.COLOR_BGR2GRAY)
        gray_prev = cv2.cvtColor(self.prev_frame, cv2.COLOR_BGR2GRAY)
        gray_curr = cv2.GaussianBlur(gray_curr, (21, 21), 0)
        gray_prev = cv2.GaussianBlur(gray_prev, (21, 21), 0)

        diff    = cv2.absdiff(gray_prev, gray_curr)
        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
        thresh  = cv2.dilate(thresh, None, iterations=2)

        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        return [
            (*cv2.boundingRect(c), cv2.contourArea(c))
            for c in contours
            if cv2.contourArea(c) > OBSTACLE_AREA
        ]

    def update_camera_feed(self, rgb_array):
        img = Image.fromarray(rgb_array)
        imgtk = ImageTk.PhotoImage(image=img)
        self.cam_label.imgtk = imgtk
        self.cam_label.configure(image=imgtk)

    # ── Cleanup ───────────────────────────────────────────
    def on_close(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.bus.close()
        self.root.destroy()

# ══════════════════════════════════════════════════════════
#  Entry point
# ══════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    app  = SmartHelmetDashboard(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()