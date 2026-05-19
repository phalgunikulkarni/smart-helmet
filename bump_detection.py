# bump_detection.py
# Detects bumps/potholes using MPU-6050 accelerometer data
# On Windows: uses simulated values
# On Raspberry Pi: reads real sensor data

import platform
import time
import random

# Import real or mock smbus2 based on OS
if platform.system() != "Linux":
    from smbus2_mock import SMBus
    SIMULATED = True
else:
    from smbus2 import SMBus
    SIMULATED = False

# MPU-6050 constants
MPU6050_ADDR = 0x68
PWR_MGMT_1   = 0x6B
ACCEL_XOUT_H = 0x3B

# Sensitivity threshold — tweak this to detect bumps
BUMP_THRESHOLD = 2.0  # in g-force units

def initialize_sensor(bus):
    """Wake up the MPU-6050 (it sleeps by default)"""
    bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)
    print("[INFO] MPU-6050 initialized")

def read_raw_data(bus, addr):
    """Read 2 bytes and combine into a signed 16-bit value"""
    high = bus.read_byte_data(MPU6050_ADDR, addr)
    low  = bus.read_byte_data(MPU6050_ADDR, addr + 1)
    value = (high << 8) | low
    if value > 32768:
        value -= 65536
    return value

def get_acceleration(bus):
    """Return X, Y, Z acceleration in g-force units"""
    if SIMULATED:
        # Simulate normal riding with occasional bump
        ax = random.uniform(-0.3, 0.3)
        ay = random.uniform(-0.3, 0.3)
        az = random.uniform(0.8, 1.2)  # gravity on Z axis

        # Randomly simulate a pothole every ~10 readings
        if random.randint(1, 10) == 1:
            az = random.uniform(2.5, 4.0)  # spike = bump!
            print("[SIMULATED] Pothole spike injected!")
    else:
        ax = read_raw_data(bus, ACCEL_XOUT_H)     / 16384.0
        ay = read_raw_data(bus, ACCEL_XOUT_H + 2) / 16384.0
        az = read_raw_data(bus, ACCEL_XOUT_H + 4) / 16384.0

    return ax, ay, az

def detect_bump(ax, ay, az):
    """Check if acceleration spike crosses the bump threshold"""
    magnitude = (ax**2 + ay**2 + az**2) ** 0.5
    if magnitude > BUMP_THRESHOLD:
        return True, magnitude
    return False, magnitude

# ── Main loop ──────────────────────────────────────────────
if __name__ == "__main__":
    bus = SMBus(1)
    initialize_sensor(bus)

    print("[INFO] Monitoring for bumps... (Ctrl+C to stop)\n")

    try:
        while True:
            ax, ay, az = get_acceleration(bus)
            bump_detected, magnitude = detect_bump(ax, ay, az)

            if bump_detected:
                print(f"🚨 BUMP DETECTED! Magnitude: {magnitude:.2f}g")
                print(f"   AX: {ax:.2f}  AY: {ay:.2f}  AZ: {az:.2f}")
            else:
                print(f"   Riding smooth — Magnitude: {magnitude:.2f}g")

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n[INFO] Stopped.")
        bus.close()