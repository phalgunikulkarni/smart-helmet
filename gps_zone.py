# gps_zone.py
# Real Bangalore road checkpoint speed system

import platform
import time
import pandas as pd
import math

SIMULATED = platform.system() != "Linux"

# ════════════════════════════════════════════════════════
# LOAD REAL ROAD CHECKPOINT DATA
# ════════════════════════════════════════════════════════

print("\n📡 Loading Bengaluru speed checkpoints...")

roads_df = pd.read_csv("bengaluru_speed_roads.csv")

print("✅ Speed checkpoint dataset loaded")
print(roads_df.head())

# ════════════════════════════════════════════════════════
# SIMULATED GPS PATH
# ════════════════════════════════════════════════════════

# ════════════════════════════════════════════════════════
# CREATE GPS PATH FROM REAL BENGALURU DATA
# ════════════════════════════════════════════════════════

SIMULATED_PATH = []

for _, row in roads_df.iterrows():

    try:

        lat = float(row["Latitude"])
        lon = float(row["Longitude"])

        SIMULATED_PATH.append((lat, lon))

    except:
        continue

print(
    f"✅ Loaded {len(SIMULATED_PATH)} GPS path points"
)
# ════════════════════════════════════════════════════════
# ACTIVE SPEED LIMIT MEMORY
# ════════════════════════════════════════════════════════

current_speed_limit = 50
current_road_name = "Unknown Road"

# ════════════════════════════════════════════════════════
# DISTANCE CALCULATION
# ════════════════════════════════════════════════════════

def haversine_distance(lat1, lon1, lat2, lon2):

    R = 6371000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        +
        math.cos(phi1)
        *
        math.cos(phi2)
        *
        math.sin(dlambda / 2) ** 2
    )

    return R * 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

# ════════════════════════════════════════════════════════
# GET GPS POSITION
# ════════════════════════════════════════════════════════

def get_gps_position(index=0):

    if SIMULATED:

        lat, lon = SIMULATED_PATH[
            index % len(SIMULATED_PATH)
        ]

        return lat, lon

    else:

        try:

            import gps

            session = gps.gps(
                "localhost",
                "2947"
            )

            session.stream(
                gps.WATCH_ENABLE |
                gps.WATCH_NEWSTYLE
            )

            for report in session:

                if report["class"] == "TPV":

                    if (
                        hasattr(report, 'lat')
                        and
                        hasattr(report, 'lon')
                    ):

                        return (
                            report.lat,
                            report.lon
                        )

        except Exception as e:

            print(f"[ERROR] GPS failed: {e}")

            raise

# ════════════════════════════════════════════════════════
# CHECKPOINT-BASED SPEED SYSTEM
# ════════════════════════════════════════════════════════

def check_zone(lat, lon):

    global current_speed_limit
    global current_road_name

    nearest_distance = 999999

    nearest_checkpoint = None

    # ---------------------------------------------------
    # FIND NEAREST CHECKPOINT
    # ---------------------------------------------------

    for _, row in roads_df.iterrows():

        try:

            road_lat = float(row["Latitude"])
            road_lon = float(row["Longitude"])

            distance = haversine_distance(
                lat,
                lon,
                road_lat,
                road_lon
            )

            # Nearby checkpoint
            if distance < nearest_distance:

                nearest_distance = distance

                nearest_checkpoint = row

        except:
            continue

    # ---------------------------------------------------
    # ACTIVATE CHECKPOINT
    # ---------------------------------------------------

    if (
        nearest_checkpoint is not None
        and
        nearest_distance <= 40
    ):

        try:

            speed_limit = int(
                nearest_checkpoint["Speed Limit"]
            )

        except:

            speed_limit = current_speed_limit

        road_name = nearest_checkpoint[
            "Road Name"
        ]

        # Update active memory
        current_speed_limit = speed_limit

        current_road_name = road_name

        return (
            True,
            road_name,
            current_speed_limit,
            nearest_distance
        )

    # ---------------------------------------------------
    # KEEP PREVIOUS SPEED LIMIT
    # ---------------------------------------------------

    return (
        False,
        current_road_name,
        current_speed_limit,
        nearest_distance
    )

# ════════════════════════════════════════════════════════
# MAIN TEST LOOP
# ════════════════════════════════════════════════════════

if __name__ == "__main__":

    print("\n🚀 Real GPS checkpoint monitor started...\n")

    try:

        if SIMULATED:

            for i in range(len(SIMULATED_PATH)):

                lat, lon = get_gps_position(i)

                (
                    crossed,
                    road_name,
                    speed_limit,
                    distance
                ) = check_zone(lat, lon)

                print(
                    f"📍 Position: ({lat}, {lon})"
                )

                if crossed:

                    print(
                        f"🚦 CHECKPOINT CROSSED"
                    )

                else:

                    print(
                        f"🛣 Continuing previous zone"
                    )

                print(
                    f"Road: {road_name}"
                )

                print(
                    f"Active Speed Limit: {speed_limit} km/h"
                )

                print(
                    f"Distance: {distance:.1f}m"
                )

                print()

                time.sleep(1)

        else:

            while True:

                lat, lon = get_gps_position()

                (
                    crossed,
                    road_name,
                    speed_limit,
                    distance
                ) = check_zone(lat, lon)

                print(
                    f"📍 Position: ({lat}, {lon})"
                )

                print(
                    f"Road: {road_name}"
                )

                print(
                    f"Active Speed Limit: {speed_limit} km/h"
                )

                print(
                    f"Distance: {distance:.1f}m"
                )

                print()

                time.sleep(2)

    except KeyboardInterrupt:

        print("\n[INFO] Stopped.")