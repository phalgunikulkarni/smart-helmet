import sys
import time
import threading
import requests
import pandas as pd
import os

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QFrame
)

from PyQt6.QtCore import Qt
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtGui import QFont

from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

# ════════════════════════════════════════
# LOAD DATASET
# ════════════════════════════════════════

print("\n📡 Loading Bengaluru speed checkpoints...")

df = pd.read_csv("bengaluru_speed_roads.csv")

print("✅ Speed checkpoint dataset loaded")
print(df.head())

# ════════════════════════════════════════
# DASHBOARD
# ════════════════════════════════════════

class Dashboard(QWidget):

    def __init__(self):

        super().__init__()

        self.index = 0

        self.init_ui()

        self.start_simulation()

    # ════════════════════════════════════
    # UI
    # ════════════════════════════════════

    def init_ui(self):

        self.setWindowTitle(
            "Smart Helmet Intelligent Dashboard"
        )

        self.setGeometry(
            50,
            50,
            1600,
            950
        )

        self.setStyleSheet(
            "background-color: #1a1a2e;"
        )

        main_layout = QVBoxLayout()

        # TITLE

        title = QLabel(
            "🪖 Smart Helmet Road Intelligence Dashboard"
        )

        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        title.setStyleSheet(
            "color: white;"
        )

        title.setFont(
            QFont("Helvetica", 20)
        )

        main_layout.addWidget(title)

        # ════════════════════════════════
        # TOP CARDS
        # ════════════════════════════════

        cards_layout = QHBoxLayout()

        self.speed_card = self.create_card(
            "🏍 Rider Speed",
            "0 km/h",
            "#00d4ff"
        )

        self.road_card = self.create_card(
            "🛣 Current Road",
            "Detecting...",
            "white"
        )

        self.limit_card = self.create_card(
            "🚦 Active Speed Limit",
            "0 km/h",
            "#ffaa00"
        )

        self.gps_card = self.create_card(
            "📍 GPS Status",
            "LIVE TRACKING",
            "#00ff88"
        )

        cards_layout.addWidget(self.speed_card[0])
        cards_layout.addWidget(self.road_card[0])
        cards_layout.addWidget(self.limit_card[0])
        cards_layout.addWidget(self.gps_card[0])

        main_layout.addLayout(cards_layout)

        # ════════════════════════════════
        # ALERT BAR
        # ════════════════════════════════

        self.alert_bar = QLabel(
            "✅ Rider within speed limit"
        )

        self.alert_bar.setStyleSheet("""

            background-color: #0f3460;
            color: white;
            padding: 14px;
            font-size: 16px;
            font-weight: bold;

        """)

        main_layout.addWidget(self.alert_bar)

        # ════════════════════════════════
        # LOWER SECTION
        # ════════════════════════════════

        lower_layout = QHBoxLayout()

        # LOG PANEL

        log_frame = QFrame()

        log_frame.setStyleSheet("""

            background-color: #16213e;
            border: 1px solid #0f3460;

        """)

        log_layout = QVBoxLayout()

        log_title = QLabel(
            "📜 Live Event Log"
        )

        log_title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        log_title.setStyleSheet(
            "color: white; font-size: 18px;"
        )

        self.log_box = QTextEdit()

        self.log_box.setReadOnly(True)

        self.log_box.setStyleSheet("""

            background-color: #050510;
            color: #d0d0d0;
            font-family: Courier;
            font-size: 12px;

        """)

        log_layout.addWidget(log_title)
        log_layout.addWidget(self.log_box)

        log_frame.setLayout(log_layout)

                # MAP PANEL

        map_frame = QFrame()

        map_frame.setStyleSheet("""

            background-color: #16213e;
            border: 1px solid #0f3460;

        """)

        map_layout = QVBoxLayout()

        map_title = QLabel(
            "🌍 Live Map"
        )

        map_title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        map_title.setStyleSheet(
            "color: white; font-size: 18px;"
        )

        map_layout.addWidget(map_title)

        # EMBED LIVE MAP

        self.browser = QWebEngineView()

        self.browser.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls,
            True
        )

        self.browser.settings().setAttribute(
            QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls,
            True
        )

        map_path = os.path.abspath(
            "live_map.html"
        )

        self.browser.load(
            QUrl.fromLocalFile(map_path)
        )

        map_layout.addWidget(
            self.browser
        )

        map_frame.setLayout(
            map_layout
        )

        lower_layout.addWidget(
            log_frame,
            1
        )

        lower_layout.addWidget(
            map_frame,
            1
        )

        main_layout.addLayout(lower_layout)

        self.setLayout(main_layout)

    # ════════════════════════════════════
    # CARD CREATOR
    # ════════════════════════════════════

    def create_card(

        self,
        title,
        value,
        color

    ):

        frame = QFrame()

        frame.setStyleSheet("""

            background-color: #16213e;
            border: 1px solid #0f3460;
            padding: 12px;

        """)

        layout = QVBoxLayout()

        title_label = QLabel(title)

        title_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        title_label.setStyleSheet(
            "color: #a0a0a0;"
        )

        value_label = QLabel(value)

        value_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        value_label.setStyleSheet(
            f"color: {color};"
        )

        value_label.setFont(
            QFont("Helvetica", 16)
        )

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        frame.setLayout(layout)

        return frame, value_label

    # ════════════════════════════════════
    # LOGGING
    # ════════════════════════════════════

    def log(self, message):

        timestamp = time.strftime("%H:%M:%S")

        self.log_box.append(
            f"[{timestamp}] {message}"
        )

    # ════════════════════════════════════
    # SIMULATION LOOP
    # ════════════════════════════════════

    def start_simulation(self):

        thread = threading.Thread(

            target=self.simulation_loop,

            daemon=True

        )

        thread.start()

    def simulation_loop(self):

        speeds = [

            20,
            25,
            30,
            35,
            40,
            45,
            50,
            55,
            60,
            70,
            80

        ]

        while True:

            row = df.iloc[
                self.index % len(df)
            ]

            road = row["Road Name"]

            limit = int(
                row["Speed Limit"]
            )

            lat = float(
                row["Latitude"]
            )

            lon = float(
                row["Longitude"]
            )

            speed = speeds[
                self.index % len(speeds)
            ]

            status = "safe"

            if speed > limit:
                status = "warning"

            # MAP SYNC

            try:

                requests.post(

                    "http://127.0.0.1:5050/location",

                    json={

                        "lat": lat,
                        "lon": lon,
                        "speed": speed,
                        "road": road,
                        "limit": limit,
                        "status": status

                    }

                )

            except Exception as e:

                print(
                    "Map sync failed:",
                    e
                )

            # UPDATE UI

            self.speed_card[1].setText(
                f"{speed} km/h"
            )

            self.road_card[1].setText(
                road
            )

            self.limit_card[1].setText(
                f"{limit} km/h"
            )

            self.log(

                f"Rider on {road} | "
                f"Speed: {speed} km/h | "
                f"Limit: {limit} km/h"

            )

            if status == "warning":

                self.alert_bar.setText(
                    f"⚠ Overspeed detected on {road}"
                )

                self.alert_bar.setStyleSheet("""

                    background-color: #9b0000;
                    color: white;
                    padding: 14px;
                    font-size: 16px;
                    font-weight: bold;

                """)

                self.log(
                    f"WARNING | {speed} km/h on {road}"
                )

            else:

                self.alert_bar.setText(
                    "✅ Rider within speed limit"
                )

                self.alert_bar.setStyleSheet("""

                    background-color: #0f3460;
                    color: white;
                    padding: 14px;
                    font-size: 16px;
                    font-weight: bold;

                """)

            self.index += 1

            time.sleep(2)

# ════════════════════════════════════════
# MAIN
# ════════════════════════════════════════

app = QApplication(sys.argv)

window = Dashboard()

window.show()

sys.exit(app.exec())