📊 Financial Analyzer (Fund Screener)

A production-grade financial analysis pipeline for fetching, processing, and screening stock data.
It combines market price history with fundamental data, computes financial metrics (SMA, 52-week high, P/B ratio, EV), and detects Golden Cross / Death Cross signals.
Data is persisted to a SQLite database and can be exported as JSON for downstream use.


✨ Features

Fetch historical stock prices & fundamentals from Yahoo Finance (yfinance).

Robust fallbacks: quarterly balance sheet → annual balance sheet → ticker.info.

Compute technical indicators:

SMA50, SMA200

52-week high

Compute fundamental ratios:

Price-to-Book (P/B)

Enterprise Value (EV)

Detect trading signals:

Golden Cross (bullish)

Death Cross (bearish)

Store results in SQLite database (financial_data.db).

Export clean JSON files with all metrics, signals, and issues.

Built with production standards (logging, config file, validation, retries).



🛠 Tech Stack

Python 3.9+

pandas
 – data processing

yfinance
 – stock/fundamentals data

pydantic
 – validation & schema models

Typer
 – CLI interface

SQLAlchemy
 – database ORM

PyYAML
 – config

pytest
 – testing

ruff
 – linting/formatting


 🚀 Installation & Setup
1. Clone the repository
git clone https://github.com/yourusername/financial-analyzer.git
cd financial-analyzer

2. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

3. Install dependencies
pip install --upgrade pip
pip install pandas yfinance pydantic typer[all] sqlalchemy pyyaml
# dev tools
pip install pytest ruff


(Optional) If using uv:

uv sync


4. Verify structure
financial_analyzer/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── data_fetcher.py
│   ├── processor.py
│   ├── signals.py
│   └── database.py
├── tests/
│   └── test_signals.py
├── config.yaml.example
├── pyproject.toml
└── README.md

Usage
Run analysis for a stock
python -m src.main --ticker NVDA --output nvda_analysis.json


Examples:

# US stock
python -m src.main --ticker MSFT --output msft.json

# Indian NSE stock
python -m src.main --ticker RELIANCE.NS --output reliance.json

CLI help
python -m src.main --help


📂 Outputs
JSON file

Example (nvda_analysis.json):

{
  "ticker": "NVDA",
  "generated_at": "2025-09-28T11:29:31Z",
  "company_info": { ... },
  "metrics": [
    {
      "date": "2023-01-02",
      "close": 143.2,
      "sma50": 142.1,
      "sma200": 137.4,
      "high_52week": 146.0,
      "pb_ratio": 21.5,
      "ev": 1140000000000,
      "fundamentals_quarter_end": "2022-12-31"
    }
  ],
  "signals": [
    {
      "date": "2023-05-15",
      "signal_type": "golden_cross",
      "sma_short": 112.3,
      "sma_long": 110.5
    }
  ],
  "issues": [],
  "source": "quarterly_balance_sheet"
}


SQLite database

Default: financial_data.db

Tables:
*tickers
*daily_metrics
*signal_events

Inspect with:

python - <<'PY'
import sqlite3
conn = sqlite3.connect("financial_data.db")
print(conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall())
conn.close()
PY


🧪 Testing

Run all tests:
pytest -q

Lint/format:
ruff format src/ --fix

