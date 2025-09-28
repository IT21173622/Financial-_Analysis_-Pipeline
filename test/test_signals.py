# tests/test_signals.py
import pandas as pd
from src.signals import detect_golden_cross, detect_death_cross

def test_cross_detection_simple():
    dates = pd.date_range("2023-01-01", periods=6, freq="D")
    sma50 = [10, 11, 12, 13, 14, 15]
    sma200 = [12, 12, 12, 12, 12, 12]
    df = pd.DataFrame({"date": dates, "sma50": sma50, "sma200": sma200})
    goldens = detect_golden_cross(df)
    assert len(goldens) == 1
    assert goldens[0] == dates[2] or goldens[0] == dates[3]  # tolerant check
