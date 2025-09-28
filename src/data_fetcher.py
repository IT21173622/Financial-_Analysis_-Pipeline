from typing import Dict , Any ,List
import time
import yfinance as yf
import pandas as pd
import logging
from  decimal import Decimal 
from .models import PriceRow,FundamentalQuarter,CompanyInfo
from datetime import datetime

logger = logging.getLogger(__name__)


def _df_to_decimal_rows(df: pd.DataFrame) -> List[Dict[str , Any]]:
    
    rows = []
    df = df.reset_index()
    
    for _,r in df.iterrows():
        
        row = PriceRow(
            date = r['Date'].date() if isinstance(r['Date'], pd.Timestamp) else r['Date'],
            open = Decimal(str(r.get("Open", r.get("open")))) if not pd.isna(r.get("Open")) else None,
            high = Decimal(str(r.get("High", r.get("high")))) if not pd.isna(r.get("High")) else None,
            low = Decimal(str(r.get("Low", r.get("low")))) if not pd.isna(r.get("Low")) else None,
            close = Decimal(str(r.get("Close", r.get("close")))) if not pd.isna(r.get("Close")) else None,
            volume = int(r.get("Volume", r.get("volume"))) if not pd.isna(r.get("Volume")) else None,
            adj_close = Decimal(str(r.get("Adj Close", r.get("adj_close")))) if not pd.isna(r.get("Adj Close")) else None,  
        )
        rows.append(row.dict())
    return rows
        
    
def fetch_stock_data(ticker: str, period: str = "5y", max_retries: int = 3, retry_backoff: float = 1.0) -> Dict[str, Any]:
    
    """
    Fetch stock price history and fundamentals using yfinance.
    Returns dict:
      {
        "ticker": ticker,
        "prices": [ {date, open, high, low, close, volume, adj_close}, ... ],
        "fundamentals": [ {quarter_end, total_assets, ...}, ... ],
        "company_info": {...}
      }
    """
    
    attempt = 0
    last_exc = None
    
    while attempt<max_retries:
        attempt+=1
        
        try:
            logger.info("Fetching %s (attempt %d)", ticker, attempt)
            t = yf.Ticker(ticker)
            hist = t.history(period=period, auto_adjust=False, actions = False)
            
            if hist is None or hist.empty:
                logger.warning(f"No historical data for {ticker}")
                price =[]
            else:
                prices = _df_to_decimal_rows(hist) 
                
                
            # fundamentals: try quarterly balance sheet      
            fundamentals = []   
            try:
                qbs = t.quarterly_balance_sheet 
                 # yfinance returns DataFrame with columns as quarter-ends 
                if isinstance(qbs , pd.DataFrame) and not qbs.empty:
                    qdf = qbs.T
                    qdf.index = pd.to_datetime(qdf.index)
                    
                    for idx, row in qdf.iterrows():
                        fundamentals.append({
                            "quarter_end": idx.date(),
                            "total_asserts": Decimal(str(row.get("Total Assets"))) if "Total Assets" in row and not pd.isna(row.get("Total Assets")) else None,
                            "total_liabilities": None,
                            "total_equity": Decimal(str(row.get("Total Stockholder Equity"))) if "Total Stockholder Equity" in row and not pd.isna(row.get("Total Stockholder Equity")) else None,
                            "cash_and_equivalents": Decimal(str(row.get("Cash And Cash Equivalents"))) if "Cash And Cash Equivalents" in row and not pd.isna(row.get("Cash And Cash Equivalents")) else None,
                            "raw": row.to_dict()
                        })
                    
                    
                else:
                    logger.debug("Quarterly balance sheet missing for %s; will try annual", ticker)  

            except Exception:
                logger.exception("Failed to parse quarterly balance sheet for %s", ticker)
               
            # fallback to annual balance sheet if quarterly not present    
            
            if not  fundamentals:
                try:
                    qbs = t.balance_sheet
                    if isinstance(qbs , pd.DataFrame) and not qbs.empty:
                        qdf = qbs.T
                        qdf.index = pd.to_datetime(qdf.index)
                        
                        for idx, row in qdf.iterrows():
                            fundamentals.append({
                                "quarter_end": idx.date(),
                                "total_asserts": Decimal(str(row.get("Total Assets"))) if "Total Assets" in row and not pd.isna(row.get("Total Assets")) else None,
                                "total_liabilities": None,
                                "total_equity": Decimal(str(row.get("Total Stockholder Equity"))) if "Total Stockholder Equity" in row and not pd.isna(row.get("Total Stockholder Equity")) else None,
                                "cash_and_equivalents": Decimal(str(row.get("Cash And Cash Equivalents"))) if "Cash And Cash Equivalents" in row and not pd.isna(row.get("Cash And Cash Equivalents")) else None,
                                "raw": row.to_dict()
                            })
                        
                    else:
                        logger.debug("Annual balance sheet missing for %s", ticker) 
            
                except Exception:
                    logger.exception("Failed to parse annual balance sheet for %s", ticker) 
            
            
            # company info (marketCap etc.)
            company_info = {}
            try:
                info = t.info or {}
                if info:
                    company_info = {
                        "ticker": ticker,
                        "market_cap": Decimal(str(info.get("marketCap"))) if "marketCap" in info and not pd.isna(info.get("marketCap")) else None,
                        "currency": info.get("currency"),
                        "info_raw": info
                    }
                    
                    return{
                        "ticker": ticker,
                        "prices": prices,
                        "fundamentals": fundamentals,
                        "company_info": company_info,
                        "Source": "yfinance"
                    }
                        
                else:
                    logger.debug("No company info for %s", ticker)
                    
            except Exception:
                logger.exception("Failed to fetch company info for %s", ticker)
            
            
        except Exception as exc:
            
            logger.exception("Attempt %d failed for ticker %s", attempt, ticker)
            last_exc = exc
            time.sleep(retry_backoff * attempt)
            
    raise RuntimeError(f"Failed to fetch data for {ticker} after {max_retries} attempts") from last_exc   
                       
            
    
    