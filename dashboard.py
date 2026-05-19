from tkinterweb import HtmlFrame
import tkinter as tk
from tkinter import font
import threading
import time
import platform
import requests
import importlib

SIMULATED = platform.system() != "Linux"

# ════════════════════════════════════════════════
# SMBUS
# ════════════════════════════════════════════════

try:

    if platform.system() == "Linux":
        smbus_mod = importlib.import_module("smbus2")
    else:
        smbus_mod = importlib.import_module("smbus2_mock")

    SMBus = getattr(smbus_mod, "SMBus")

except Exception:

    SMBus = None

# ════════════════════════════════════════════════
# IMPORTS
# ════════════════════════════════════════════════

from bump_detection import initialize_sensor

from gps_zone import (

    get_gps_position,
    check_zone,
    SIMULATED_PATH

)

# ════════════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════════════

class SmartHelmetDashboard:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Smart Helmet Intelligent Dashboard"
        )

        self.root.geometry("1550x950")

        self.root.configure(
            bg="#1a1a2e"
        )

        self.running = True

        self.gps_index = 0

        self.build_ui()

        self.root.after(
            100,
            self.start_sensors
        )

    # ════════════════════════════════════════════
    # UI
    # ════════════════════════════════════════════

    def build_ui(self):

        title_font = font.Font(
            family="Helvetica",
            size=20,
            weight="bold"
        )

        value_font = font.Font(
            family="Helvetica",
            size=18,
            weight="bold"
        )

        # ════════════════════════════════════════
        # TITLE
        # ════════════════════════════════════════

        title = tk.Label(

            self.root,

            text="🪖 Smart Helmet Road Intelligence Dashboard",

            bg="#1a1a2e",

            fg="#ffffff",

            font=title_font,

            pady=18

        )

        title.pack(fill="x")

        # ════════════════════════════════════════
        # TOP SECTION
        # ════════════════════════════════════════

        top_frame = tk.Frame(
            self.root,
            bg="#1a1a2e"
        )

        top_frame.pack(
            fill="x",
            padx=15,
            pady=10
        )

        # SPEED CARD

        self.speed_card = self.make_card(
            top_frame,
            "🏍 Rider Speed"
        )

        self.speed_card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=6
        )

        self.speed_value = tk.Label(

            self.speed_card,

            text="0 km/h",

            bg="#16213e",

            fg="#00d4ff",

            font=value_font

        )

        self.speed_value.pack(pady=10)

        self.speed_status = tk.Label(

            self.speed_card,

            text="SAFE",

            bg="#16213e",

            fg="#00ff88",

            font=("Helvetica", 11, "bold")

        )

        self.speed_status.pack()

        # ROAD CARD

        self.road_card = self.make_card(
            top_frame,
            "🛣 Current Road"
        )

        self.road_card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=6
        )

        self.road_label = tk.Label(

            self.road_card,

            text="Detecting...",

            bg="#16213e",

            fg="#ffffff",

            font=value_font,

            wraplength=250

        )

        self.road_label.pack(pady=10)

        # LIMIT CARD

        self.limit_card = self.make_card(
            top_frame,
            "🚦 Active Speed Limit"
        )

        self.limit_card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=6
        )

        self.limit_label = tk.Label(

            self.limit_card,

            text="0 km/h",

            bg="#16213e",

            fg="#ffaa00",

            font=value_font

        )

        self.limit_label.pack(pady=10)

        # GPS CARD

        self.gps_card = self.make_card(
            top_frame,
            "📍 GPS Status"
        )

        self.gps_card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=6
        )

        self.gps_label = tk.Label(

            self.gps_card,

            text="LIVE TRACKING",

            bg="#16213e",

            fg="#00ff88",

            font=value_font

        )

        self.gps_label.pack(pady=10)

        # ════════════════════════════════════════
        # ALERT BAR
        # ════════════════════════════════════════

        self.alert_var = tk.StringVar(
            value="✅ System Normal"
        )

        self.alert_bar = tk.Label(

            self.root,

            textvariable=self.alert_var,

            bg="#0f3460",

            fg="white",

            font=("Helvetica", 12, "bold"),

            pady=12,

            padx=15,

            anchor="w"

        )

        self.alert_bar.pack(
            fill="x",
            padx=15,
            pady=10
        )

        # ════════════════════════════════════════
        # LOWER SECTION
        # ════════════════════════════════════════

        lower_frame = tk.Frame(
            self.root,
            bg="#1a1a2e"
        )

        lower_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        # ════════════════════════════════════════
        # LEFT PANEL
        # ════════════════════════════════════════

        log_frame = tk.Frame(

            lower_frame,

            bg="#16213e",

            highlightbackground="#0f3460",

            highlightthickness=1

        )

        log_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 8)
        )

        log_title = tk.Label(

            log_frame,

            text="📜 Live Event Log",

            bg="#16213e",

            fg="white",

            font=("Helvetica", 13, "bold")

        )

        log_title.pack(pady=8)

        self.log_box = tk.Text(

            log_frame,

            bg="#050510",

            fg="#d0d0d0",

            font=("Courier", 10),

            relief="flat",

            state="disabled"

        )

        self.log_box.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # ════════════════════════════════════════
        # RIGHT PANEL
        # ════════════════════════════════════════

        map_frame = tk.Frame(

            lower_frame,

            bg="#16213e",

            highlightbackground="#0f3460",

            highlightthickness=1

        )

        map_frame.pack(
            side="right",
            fill="both",
            expand=True
        )

        map_title = tk.Label(

            map_frame,

            text="🌍 Live Map",

            bg="#16213e",

            fg="white",

            font=("Helvetica", 13, "bold")

        )

        map_title.pack(pady=8)

        map_info = tk.Label(

            map_frame,

            text="🌍 Live Map Running In Browser",

            bg="#16213e",

            fg="#00ff88",

            font=("Helvetica", 16, "bold")

        )

        map_info.pack(pady=40)

        open_button = tk.Button(

            map_frame,

            text="OPEN LIVE MAP",

            bg="#00aa88",

            fg="white",

            font=("Helvetica", 14, "bold"),

            relief="flat",

            padx=20,

            pady=15,

            command=self.open_map

        )

        open_button.pack(pady=20)


    # ════════════════════════════════════════════
    # CARD CREATOR
    # ════════════════════════════════════════════

    def make_card(self, parent, title):

        frame = tk.Frame(

            parent,

            bg="#16213e",

            highlightbackground="#0f3460",

            highlightthickness=1

        )

        tk.Label(

            frame,

            text=title,

            bg="#16213e",

            fg="#a0a0a0",

            font=("Helvetica", 11)

        ).pack(pady=6)

        return frame

    # ════════════════════════════════════════════
    # LOGGING
    # ════════════════════════════════════════════

    def log(self, message):

        timestamp = time.strftime("%H:%M:%S")

        self.log_box.configure(
            state="normal"
        )

        self.log_box.insert(
            "end",
            f"[{timestamp}] {message}\n"
        )

        self.log_box.see("end")

        self.log_box.configure(
            state="disabled"
        )

    # ════════════════════════════════════════════
    # ALERT BAR
    # ════════════════════════════════════════════

    def set_alert(self, message, color):

        self.alert_var.set(message)

        self.alert_bar.configure(
            bg=color
        )

    def open_map(self):

        import webbrowser
        import os

        path = os.path.abspath("live_map.html")

        webbrowser.open(f"file://{path}")

    # ════════════════════════════════════════════
    # START SENSOR THREAD
    # ════════════════════════════════════════════

    def start_sensors(self):

        if SMBus is not None:

            self.bus = SMBus(1)

            initialize_sensor(self.bus)

        thread = threading.Thread(

            target=self.sensor_loop,

            daemon=True

        )

        thread.start()

    # ════════════════════════════════════════════
    # SENSOR LOOP
    # ════════════════════════════════════════════

    def sensor_loop(self):

        simulated_speeds = [

            20, 25, 30, 35, 40,
            45, 50, 55, 60, 70,
            80, 90, 40, 30, 20

        ]

        while self.running:

            lat, lon = get_gps_position(
                self.gps_index
            )

            (
                crossed,
                road_name,
                speed_limit,
                distance

            ) = check_zone(lat, lon)

            speed = simulated_speeds[
                self.gps_index % len(simulated_speeds)
            ]

            status = "safe"

            if speed > speed_limit:
                status = "warning"

            # ════════════════════════════════════
            # MAP + DASHBOARD SYNC
            # ════════════════════════════════════

            try:

                requests.post(

                    "http://127.0.0.1:5050/location",

                    json={

                        "lat": lat,
                        "lon": lon,
                        "speed": speed,
                        "road": road_name,
                        "limit": speed_limit,
                        "status": status

                    },

                    timeout=1

                )

            except Exception as e:

                print(
                    "Map sync failed:",
                    e
                )

            self.root.after(

                0,

                self.update_dashboard,

                speed,
                speed_limit,
                road_name,
                status

            )

            self.gps_index = (

                self.gps_index + 1

            ) % len(SIMULATED_PATH)

            time.sleep(2)

    # ════════════════════════════════════════════
    # UPDATE DASHBOARD
    # ════════════════════════════════════════════

    def update_dashboard(

        self,
        speed,
        limit,
        road,
        status

    ):

        self.speed_value.configure(
            text=f"{speed:.1f} km/h"
        )

        self.limit_label.configure(
            text=f"{limit} km/h"
        )

        self.road_label.configure(
            text=road
        )

        self.log(

            f"Rider on {road} | "
            f"Speed: {speed:.1f} km/h | "
            f"Limit: {limit} km/h"

        )

        if status == "safe":

            self.speed_status.configure(

                text="SAFE",

                fg="#00ff88"

            )

            self.set_alert(

                "✅ Rider within speed limit",

                "#0f3460"

            )

        else:

            self.speed_status.configure(

                text="WARNING",

                fg="#ff4444"

            )

            self.set_alert(

                f"⚠ Overspeed detected on {road}",

                "#9b0000"

            )

            self.log(

                f"WARNING | {speed:.1f} km/h on {road}"

            )

    # ════════════════════════════════════════════
    # CLOSE
    # ════════════════════════════════════════════

    def on_close(self):

        self.running = False

        self.root.destroy()

# ════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════

if __name__ == "__main__":

    root = tk.Tk()

    app = SmartHelmetDashboard(root)

    root.protocol(
        "WM_DELETE_WINDOW",
        app.on_close
    )

    root.mainloop()