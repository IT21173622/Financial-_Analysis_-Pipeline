from __future__ import annotations
from pydantic import BaseModel , fields, validator
from typing import Optional, List ,Dict ,Any
from decimal import Decimal
from datetime import datetime , date
 
class PriceRow(BaseModel):
    date: date
    open: Decimal
    high : Decimal
    low : Decimal
    close : Decimal
    volume : int
    adj_close : Optional[Decimal] = None
    
    @validator("high")
    
    def high_must_be_ge_low(cls ,v , values):
        low = values.get("low")
        if low is not None and v < low:
            raise ValueError("high must be greater than or equal to low")
        return v
    
    @validator('open')
    
    def open_between_low_high(cls , v ,values):
        low = values.get("low")
        high = values.get("high")
        
        if low is not None and high is not None and not (low <=v <high):
            
            raise ValueError("open must be between low and high")
        return v
    

class FundamentalQuarter(BaseModel):
    quarter_end : date
    total_assets: Optional[Decimal] = None
    total_equity :Optional[Decimal] = None
    total_equity :Optional[Decimal] = None
    cash_and_equivalents :Optional[Decimal] = None
    short_term_debt : Optional[Decimal] = None
    long_term_debt : Optional[Decimal] = None
    shares_outstanding : Optional[Decimal] = None
    
    raw : Optional[Dict[str ,Any]] = None
    
class CompanyInfo(BaseModel):
    ticker : str
    maket_cap : Optional[Decimal] = None
    currency : Optional[str] = None
    info_raw : Optional[Dict[str ,Any]] = None    
    
    
class ProcessedRow(BaseModel):
    date: date
    close : Decimal
    volume : int
    sma50: Optional[Decimal] = None
    sma200: Optional[Decimal] = None
    high_52week: Optional[Decimal] = None
    pb_ratio: Optional[Decimal] = None
    ev: Optional[Decimal] = None
    fundamentals_quarter_end: Optional[date] = None
    

class SignalEvent(BaseModel):
    ticker: str
    date: date
    signal_type: str  # "golden_cross" or "death_cross"
    sma_short: Decimal
    sma_long: Decimal
    note: Optional[str] = None   
    
    

class ExportSchema(BaseModel):
    ticker: str
    generated_at: datetime
    company_info: Optional[CompanyInfo] = None
    metrics: List[ProcessedRow]
    signals: List[SignalEvent]     