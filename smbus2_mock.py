# smbus2_mock.py
# Simulates MPU-6050 sensor readings on Windows
# On Raspberry Pi, the real smbus2 library will be used instead

import random

class SMBus:
    def __init__(self, bus):
        print(f"[MOCK] SMBus initialized on bus {bus}")

    def write_byte_data(self, addr, reg, val):
        pass

    def read_byte_data(self, addr, reg):
        return random.randint(0, 255)

    def read_i2c_block_data(self, addr, reg, length):
        return [random.randint(0, 255) for _ in range(length)]

    def close(self):
        pass