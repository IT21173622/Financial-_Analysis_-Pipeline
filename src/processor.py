from typing import Dict , Any, List
import pandas as pd
import numpy as np
import logging
from decimal import Decimal, InvalidOperation
from .models import ProcessedRow
from datetime import date

logger = logging.getLogger(__name__)


def _to_decimal_safe(x):
    try:
        if pd.isna(x):
            return None
        return Decimal(str(x))
    except (InvalidOperation, TypeError):
        return None
    

def process_data(raw_data: Dict[str, Any], config: Dict[str, Any]) -> pd.DataFrame:
    """
    Merge daily prices with nearest prior quarterly fundamentals.
    Compute SMA50, SMA200, 52-week high, P/B ratio (if possible), simplified EV.
    Returns pandas DataFrame with metrics and enough fields for saving/exporting.
    """
    
    prices = raw_data.get("prices", [])
    
    if not prices:
        raise ValueError("No price data to process")
    
    prices_df = pd.DataFrame(prices)    
    
    prices_df['date'] = pd.to_datetime(prices_df['date'])
    prices_df = prices_df.sort_values("date").reset_index(drop=True)
    
    fundamentals = raw_data.get("fundamentals", [])
    
    if fundamentals:
        fund_df = pd.DataFrame(fundamentals)
        fund_df['quarter_end'] = pd.to_datetime(fund_df['quarter_end'])
        fund_df = fund_df.sort_values("quarter_end").reset_index(drop=True)
        
        merged = pd.merge_asof(
            prices_df,
            fund_df,
            left_on="date",
            right_on="quarter_end",
            direction="backward",
            suffixes=("", "_fund")
        )
    
    else:
        merged = prices_df.copy()
        merged['quarter_end'] = pd.NaT
        
        # fill fundamental columns as NaN
        # compute SMA windows from config
        
    ds = config.get("data_settings", {})
    short_w = ds.get("sma_short_window", 50)
    long_w = ds.get("sma_long_window", 200)
    lookback_52w = ds.get("lookback_trading_days_for_52w", 252)
        
    # ensure numeric close/high columns
        
    merged['close_float'] = pd.to_numeric(merged['close'], errors='coerce')
    merged['high_float'] = pd.to_numeric(merged['high'], errors='coerce')
        
    merged['sma50'] = merged['close_float'].rolling(window=short_w, min_periods=1).mean()
    merged['sma200'] = merged['close_float'].rolling(window=long_w, min_periods=1).mean()
        
    merged["high_52week"] = merged["high_float"].rolling(window=lookback_52w, min_periods=1).max()
        
    # compute book value per share if possible: total_equity / shares_outstanding
        
    merged["book_value_per_share"] = None
        
    if "total_equity" in merged.columns and "shares_outstanding" in merged.columns:
        
            
        # attempt to compute (may be Decimal or numeric)
            
        def compute_bvps(row):
            try:
                eq = row("total_equity")
                so = row("shares_outstanding")
                    
                if eq is None or so is None:
                    return None
                    
                eqf = float(eq)
                sof = float(so)
                    
                if sof == 0:
                    return None
                return eqf / sof
            except Exception:
                return None
        merged["book_value_per_share"] = merged.apply(compute_bvps, axis=1)
        
    else:
        merged["book_value_per_share"] = None
    
    
    # compute P/B ratio (close / bvps)
    
    def compute_pb(row):
        
        try:
            byps = row.get("book_value_per_share")
            closef = row.get("close_float")
            
            if byps is None or byps == pd.isna(closef):
                return None
            
            return float(closef) / float(byps)
        
        except Exception:
            return None
    
    merged["pb_ratio"] = merged.apply(compute_pb, axis=1)
    
     # simplified Enterprise Value = market_cap + total_debt - cash
    def compute_ev(row):
        info = raw_data.get("company_info",{}).get("info_raw",{}) or {}
        
        try:
            market_cap = info.get("marketCap")
            total_debt = info.get("totalDebt") or (row.get("short_term_debt") or 0) + (row.get("long_term_debt") or 0)
            cash = info.get("totalCash") or row.get("cash_and_equivalents") or 0
            
            if market_cap is None:
                return None
            
            return float(market_cap) + float(total_debt or 0) - float(cash or 0)
        except Exception:
            return None
        
    merged["ev"] = merged.apply(compute_ev, axis=1)    
    
    # final clean columns and convert sma to Decimal for downstream models if desired
    out_df = merged[[
        "date", "open", "high", "low", "close", "volume", "quarter_end", "sma50", "sma200", "high_52week", "book_value_per_share", "pb_ratio", "ev"
    ]].copy()

    # rename columns to match ProcessedRow model expectations
    out_df = out_df.rename(columns={"high_52week": "high_52week"})
    return out_df       


        
            
            
        
            
            
            
            
        
        
        
          
          