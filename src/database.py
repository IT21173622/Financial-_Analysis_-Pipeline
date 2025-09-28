# src/database.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Float,
    Numeric,
    create_engine,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import IntegrityError
from typing import List
import logging
import json

Base = declarative_base()
logger = logging.getLogger(__name__)


class Ticker(Base):
    __tablename__ = "tickers"
    id = Column(Integer, primary_key=True)
    ticker = Column(String, unique=True, nullable=False)
    market = Column(String, nullable=True)
    extra = Column(String, nullable=True)  # json string


class DailyMetric(Base):
    __tablename__ = "daily_metrics"
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    close = Column(Float, nullable=True)
    sma50 = Column(Float, nullable=True)
    sma200 = Column(Float, nullable=True)
    pb_ratio = Column(Float, nullable=True)
    ev = Column(Float, nullable=True)
    __table_args__ = (UniqueConstraint("ticker", "date", name="uix_ticker_date"),)


class SignalEvent(Base):
    __tablename__ = "signal_events"
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    signal_type = Column(String, nullable=False)
    sma_short = Column(Float, nullable=True)
    sma_long = Column(Float, nullable=True)
    note = Column(String, nullable=True)
    __table_args__ = (UniqueConstraint("ticker", "date", "signal_type", name="uix_signal"),)


def init_db(db_path: str):
    engine = create_engine(f"sqlite:///{db_path}", echo=False, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


def save_daily_metrics(Session, ticker: str, df):
    session = Session()
    inserted = 0
    try:
        for _, r in df.iterrows():
            dm = DailyMetric(
                ticker=ticker,
                date=r["date"].date() if hasattr(r["date"], "date") else r["date"],
                close=float(r.get("close")) if r.get("close") is not None else None,
                sma50=float(r.get("sma50")) if r.get("sma50") is not None else None,
                sma200=float(r.get("sma200")) if r.get("sma200") is not None else None,
                pb_ratio=float(r.get("pb_ratio")) if r.get("pb_ratio") is not None else None,
                ev=float(r.get("ev")) if r.get("ev") is not None else None,
            )
            # session.merge will insert or update based on primary key/unique constraints
            try:
                session.merge(dm)
            except Exception:
                logger.exception("Failed merging daily metric row for %s %s", ticker, r.get("date"))
        session.commit()
    except Exception:
        session.rollback()
        logger.exception("Failed to save daily metrics for %s", ticker)
    finally:
        session.close()


def save_signals(Session, ticker: str, signal_rows: List[dict]):
    session = Session()
    try:
        for s in signal_rows:
            se = SignalEvent(
                ticker=ticker,
                date=s["date"].date() if hasattr(s["date"], "date") else s["date"],
                signal_type=s["signal_type"],
                sma_short=float(s.get("sma_short")) if s.get("sma_short") is not None else None,
                sma_long=float(s.get("sma_long")) if s.get("sma_long") is not None else None,
                note=s.get("note"),
            )
            session.merge(se)
        session.commit()
    except Exception:
        session.rollback()
        logger.exception("Failed to save signals for %s", ticker)
    finally:
        session.close()
