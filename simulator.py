"""Data source module.
Phase 1: SimulatedSource generates fake readings.
Phase 2: write a SerialSource with the same read() method and swap it in app.py.
"""
import random
from datetime import datetime

# (min, max) typical ranges per water type. Tune these as you research.
WATER_PROFILES = {
    "RO water":        {"tds": (20, 80),    "turbidity": (0.1, 0.5), "temp": (20, 28), "ph": (6.5, 7.2)},
    "Tap water":       {"tds": (150, 400),  "turbidity": (0.3, 1.5), "temp": (22, 30), "ph": (6.8, 8.0)},
    "Borewell water":  {"tds": (400, 1000), "turbidity": (0.5, 3.0), "temp": (24, 30), "ph": (7.0, 8.5)},
    "Bottled water":   {"tds": (50, 200),   "turbidity": (0.1, 0.4), "temp": (18, 28), "ph": (6.8, 7.8)},
    "Contaminated":    {"tds": (1500, 3000),"turbidity": (5, 15),    "temp": (25, 35), "ph": (4.5, 9.5)},
}


class SimulatedSource:
    def __init__(self, water_type="Tap water"):
        self.water_type = water_type

    def read(self):
        p = WATER_PROFILES[self.water_type]
        return {
            "time": datetime.now().strftime("%H:%M:%S"),
            "water_type": self.water_type,
            "tds": round(random.uniform(*p["tds"]), 1),
            "turbidity": round(random.uniform(*p["turbidity"]), 2),
            "temp": round(random.uniform(*p["temp"]), 1),
            "ph": round(random.uniform(*p["ph"]), 2),
        }


# Phase 2 idea (leave for later):
# class SerialSource:
#     def __init__(self, port="COM3"):
#         import serial
#         self.ser = serial.Serial(port, 9600, timeout=2)
#     def read(self):
#         # parse a line like "TDS:230,TURB:0.8,TEMP:26.5" sent by the ESP32
#         ...
