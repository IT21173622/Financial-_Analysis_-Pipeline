# Financial Analyzer

A **Financial Data Analysis Pipeline** that fetches historical stock data, calculates technical metrics, detects trading signals (Golden Cross & Death Cross), stores results in a database, and exports JSON reports. Built with Python, Pydantic, SQLAlchemy, and Typer for CLI.

---

## Features

- Fetch historical stock data using `yfinance`.
- Compute moving averages (SMA50, SMA200), PB ratio, EV, and other metrics.
- Detect **Golden Cross** and **Death Cross** signals.
- Save processed metrics and signals to **SQLite database**.
- Export analysis to JSON.
- Command-line interface (CLI) for easy usage.

---

## Project Structure

financial_analyzer/
├── src/
│ ├── init.py
│ ├── config.py # Loads YAML configuration
│ ├── data_fetcher.py # API calls & validation
│ ├── processor.py # Data merging & metrics computation
│ ├── signals.py # Signal detection logic
│ ├── database.py # SQLite database operations
│ ├── models.py # Pydantic schemas
│ └── main.py # CLI entry point
├── tests/ # Unit tests
├── config.yaml.example # Example configuration file
├── pyproject.toml # Project dependencies
└── README.md



---

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/IT21173622/Financial-_Analysis_-Pipeline.git
cd Financial-_Analysis_-Pipeline


python -m venv .venv
.\.venv\Scripts\Activate.ps1   # For PowerShell
# Or use: .\.venv\Scripts\activate.bat  # For CMD

pip install -e .


Usage

Run the analysis from the project root:

python -m src.main analyze --ticker NVDA --output nvda_analysis.json

Options

--ticker : Stock symbol (e.g., NVDA, AAPL, RELIANCE.NS)

--output : JSON file path to save results

--config-path : Optional path to custom config YAML

Example:

python -m src.main analyze --ticker AAPL --output aapl_analysis.json --config-path config.yaml

Output

The output JSON contains:

{
  "ticker": "NVDA",
  "generated_at": "2025-09-28T12:00:00Z",
  "company_info": {...},
  "metrics": [
    {
      "date": "2025-09-27",
      "close": 500.12,
      "sma50": 495.22,
      "sma200": 480.44,
      "high_52week": 550.00,
      "pb_ratio": 10.5,
      "ev": 300000000000,
      "fundamentals_quarter_end": "2025-06-30"
    }
  ],
  "signals": [
    {
      "date": "2025-07-15",
      "signal_type": "golden_cross",
      "sma_short": 490.12,
      "sma_long": 480.44,
      "note": null
    }
  ]
}

Running Tests
pytest



