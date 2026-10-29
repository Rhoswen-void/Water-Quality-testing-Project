"""Quick check without the dashboard: python test_logic.py"""
from simulator import SimulatedSource, WATER_PROFILES
from classifier import classify

for wt in WATER_PROFILES:
    src = SimulatedSource(wt)
    results = [classify(src.read())[1] for _ in range(200)]
    summary = {s: results.count(s) for s in ("Safe", "Caution", "Unsafe")}
    print(f"{wt:16} -> {summary}")
