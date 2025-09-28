# src/config.py
from typing import Any, Dict
import yaml
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "database": {"path": "financial_data.db"},
    "logging": {"level": "INFO"},
    "data_settings": {
        "historical_period": "5y",
        "min_trading_days_for_sma": 200,
        "sma_short_window": 50,
        "sma_long_window": 200,
        "lookback_trading_days_for_52w": 252,
    },
}

def load_config(path: str | None = None) -> Dict[str, Any]:
    if path:
        p = Path(path)
        if p.exists():
            with p.open("r", encoding="utf-8") as fh:
                cfg = yaml.safe_load(fh) or {}
                # shallow merge defaults
                merged = DEFAULT_CONFIG.copy()
                merged.update(cfg)
                return merged
        else:
            logger.warning("Config file %s not found, using defaults", path)
    return DEFAULT_CONFIG.copy()
