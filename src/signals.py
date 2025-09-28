# src/signals.py
from typing import List
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def detect_golden_cross(df: pd.DataFrame, short_col: str = "sma50", long_col: str = "sma200") -> List[pd.Timestamp]:
    """
    Return list of dates (as pandas Timestamp) where sma_short crosses above sma_long.
    """
    if short_col not in df.columns or long_col not in df.columns:
        logger.warning("SMA columns not found in DataFrame")
        return []

    a = df[short_col]
    b = df[long_col]
    # must have previous-day comparison: cross when today (a > b) and yesterday (a <= b)
    cond = (a > b) & (a.shift(1) <= b.shift(1))
    cross_dates = df.loc[cond, "date"]
    return list(cross_dates)


def detect_death_cross(df: pd.DataFrame, short_col: str = "sma50", long_col: str = "sma200") -> List[pd.Timestamp]:
    """
    Dates where sma_short crosses below sma_long (sell signal).
    """
    if short_col not in df.columns or long_col not in df.columns:
        return []
    a = df[short_col]
    b = df[long_col]
    cond = (a < b) & (a.shift(1) >= b.shift(1))
    return list(df.loc[cond, "date"])
