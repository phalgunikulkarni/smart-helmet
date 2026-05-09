# gps_zone.py
# Detects if rider is inside a speed-restricted zone (school, hospital etc.)
# On Windows: uses hardcoded simulated GPS coordinates
# On Raspberry Pi: reads real GPS data from Neo-6M via gpsd

import platform
import time

SIMULATED = platform.system() == "Windows"

# ── Define zones (hardcode your school/area coordinates here) ──
# Format: (name, center_lat, center_lon, radius_in_meters, speed_limit_kmph)
ZONES = [
    ("School Zone",    12.9716, 77.5946, 200, 20),
    ("Hospital Zone",  12.9750, 77.5900, 150, 15),
    ("College Zone",   12.9800, 77.6000, 250, 25),
]

# ── Simulated GPS waypoints (mimics a rider moving around) ──
SIMULATED_PATH = [
    (12.9800, 77.6100),  # outside all zones
    (12.9790, 77.6050),  # approaching college zone
    (12.9800, 77.6000),  # inside college zone
    (12.9760, 77.5960),  # moving toward school zone
    (12.9716, 77.5946),  # inside school zone
    (12.9740, 77.5920),  # between zones
    (12.9750, 77.5900),  # inside hospital zone
    (12.9600, 77.5800),  # outside all zones
]

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in meters between two GPS coordinates"""
    import math
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (math.sin(dphi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def get_gps_position(index=0):
    """Return current GPS coordinates (simulated or real)"""
    if SIMULATED:
        lat, lon = SIMULATED_PATH[index % len(SIMULATED_PATH)]
        return lat, lon
    else:
        try:
            import gps
            session = gps.gps("localhost", "2947")
            session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
            for report in session:
                if report["class"] == "TPV":
                    if hasattr(report, 'lat') and hasattr(report, 'lon'):
                        return report.lat, report.lon
        except ImportError:
            print("[ERROR] gps module not installed. Install with: pip install gps")
            raise
        except Exception as e:
            print(f"[ERROR] GPS connection failed: {e}")
            raise

def check_zone(lat, lon):
    """Check if coordinates fall inside any defined zone"""
    for name, zlat, zlon, radius, speed_limit in ZONES:
        distance = haversine_distance(lat, lon, zlat, zlon)
        if distance <= radius:
            return True, name, speed_limit, distance
    return False, None, None, None

# ── Main loop ──────────────────────────────────────────────
if __name__ == "__main__":
    print("[INFO] GPS Zone Monitor started...\n")

    try:
        if SIMULATED:
            # Simulate movement through predefined path
            for i in range(len(SIMULATED_PATH)):
                lat, lon = get_gps_position(i)
                in_zone, zone_name, speed_limit, distance = check_zone(lat, lon)

                print(f"📍 Position: ({lat}, {lon})")

                if in_zone:
                    print(f"⚠️  ZONE ALERT: {zone_name}")
                    print(f"   Speed limit : {speed_limit} km/h")
                    print(f"   Distance    : {distance:.1f}m from zone center")
                else:
                    print("   Open road — no restrictions")

                print()
                time.sleep(1)
        else:
            # Real GPS: continuously monitor position
            while True:
                try:
                    lat, lon = get_gps_position()
                    in_zone, zone_name, speed_limit, distance = check_zone(lat, lon)

                    print(f"📍 Position: ({lat}, {lon})")

                    if in_zone:
                        print(f"⚠️  ZONE ALERT: {zone_name}")
                        print(f"   Speed limit : {speed_limit} km/h")
                        print(f"   Distance    : {distance:.1f}m from zone center")
                    else:
                        print("   Open road — no restrictions")

                    print()
                    time.sleep(5)  # Check every 5 seconds for real GPS
                except Exception as e:
                    print(f"[ERROR] Failed to get GPS position: {e}")
                    time.sleep(10)  # Wait longer before retrying

    except KeyboardInterrupt:
        print("\n[INFO] Stopped.")