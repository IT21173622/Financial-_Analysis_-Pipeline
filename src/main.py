# src/main.py
from typing import Optional
import typer
import logging
import json
from src.config import load_config
from src.data_fetcher import fetch_stock_data
from src.processor import process_data
from src.signals import detect_golden_cross, detect_death_cross
from src.database import init_db, save_daily_metrics, save_signals
from src.models import ExportSchema, CompanyInfo, ProcessedRow, SignalEvent
from datetime import datetime
import pandas as pd

app = typer.Typer()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

@app.command()
def analyze(
    ticker: str = typer.Option(..., help="Ticker to analyze, e.g. NVDA or RELIANCE.NS"),
    output: Optional[str] = typer.Option(None, help="Path to JSON output"),
    config_path: Optional[str] = typer.Option(None, help="Path to config.yaml"),
):
    cfg = load_config(config_path)
    try:
        raw = fetch_stock_data(ticker, period=cfg["data_settings"].get("historical_period", "5y"))
        df = process_data(raw, cfg)
        golden_dates = detect_golden_cross(df)
        death_dates = detect_death_cross(df)

        signals = []
        for d in golden_dates:
            row = df.loc[df["date"] == d]
            if not row.empty:
                signals.append({
                    "date": d,
                    "signal_type": "golden_cross",
                    "sma_short": float(row.iloc[0]["sma50"]) if row.iloc[0]["sma50"] is not None else None,
                    "sma_long": float(row.iloc[0]["sma200"]) if row.iloc[0]["sma200"] is not None else None,
                    "note": None,
                })
        for d in death_dates:
            row = df.loc[df["date"] == d]
            if not row.empty:
                signals.append({
                    "date": d,
                    "signal_type": "death_cross",
                    "sma_short": float(row.iloc[0]["sma50"]) if row.iloc[0]["sma50"] is not None else None,
                    "sma_long": float(row.iloc[0]["sma200"]) if row.iloc[0]["sma200"] is not None else None,
                    "note": None,
                })

        # Save to DB
        Session = init_db(cfg["database"]["path"])
        save_daily_metrics(Session, ticker, df)
        save_signals(Session, ticker, signals)

        processed_rows = []
        for _, r in df.iterrows():
            processed_rows.append({
                "date": r["date"].date() if hasattr(r["date"], "date") else r["date"],
                "close": float(r["close"]) if r.get("close") is not None else None,
                "sma50": float(r["sma50"]) if r.get("sma50") is not None else None,
                "sma200": float(r["sma200"]) if r.get("sma200") is not None else None,
                "high_52week": float(r.get("high_52week")) if r.get("high_52week") is not None else None,
                "pb_ratio": float(r.get("pb_ratio")) if r.get("pb_ratio") is not None else None,
                "ev": float(r.get("ev")) if r.get("ev") is not None else None,
                "fundamentals_quarter_end": r.get("quarter_end").date() if not pd.isna(r.get("quarter_end")) and hasattr(r.get("quarter_end"), "date") else None,
            })

        export_obj = {
            "ticker": ticker,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "company_info": raw.get("company_info"),
            "metrics": processed_rows,
            "signals": signals,
        }

        if output:
            with open(output, "w", encoding="utf-8") as fh:
                json.dump(export_obj, fh, default=str, indent=2)
            logger.info("Wrote JSON to %s", output)
        else:
            print(json.dumps(export_obj, default=str))

    except Exception as exc:
        logger.exception("Failed to run analysis for %s", ticker)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
