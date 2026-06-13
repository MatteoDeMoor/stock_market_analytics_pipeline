# Market Data Engineering Pipeline

A local end-to-end data engineering project that ingests stock and ETF market data from an external API, stores raw and transformed data in PostgreSQL, and visualizes financial performance through a dashboard.

## Project Overview

This project is a practical data engineering portfolio project focused on financial market data.

The goal is to build a small but realistic pipeline that extracts daily stock and ETF prices from an external API, stores the original API responses in PostgreSQL, transforms the data into analytics-ready tables, and visualizes the results in a dashboard.

The first version focuses on a small watchlist of stocks and ETFs such as:

- AAPL
- MSFT
- NVDA
- SPY
- QQQ

Future versions may include additional ETFs, crypto assets, financial fundamentals, orchestration, data quality checks, and a custom API layer.

## Why This Project?

This project is designed to simulate a real-world data engineering workflow using free and local tools.

It covers several important data engineering concepts:

- Consuming external APIs
- Working with API keys
- Managing secrets with environment variables
- Handling JSON responses
- Storing raw API responses
- Designing PostgreSQL schemas
- Building staging and analytics layers
- Performing incremental loads
- Using upserts to avoid duplicate data
- Adding pipeline logging and observability
- Creating SQL-based analytics views
- Building a dashboard on top of PostgreSQL

## Tech Stack

The initial version of the project uses:

- Python
- PostgreSQL
- Docker Compose
- Alpha Vantage API
- SQL
- Streamlit
- pandas
- psycopg or SQLAlchemy
- python-dotenv
- PyYAML

Possible future additions:

- dbt
- Prefect
- FastAPI
- Metabase
- Grafana
- GitHub Actions
- pytest

## High-Level Architecture

```text
Financial Market API
        ↓
Python Extractor
        ↓
Raw API Response Storage
        ↓
PostgreSQL Raw Layer
        ↓
PostgreSQL Staging Layer
        ↓
PostgreSQL Analytics Layer
        ↓
Streamlit Dashboard
```

## Data Flow

1. The pipeline reads a list of stock and ETF symbols from a configuration file.
2. For each symbol, the pipeline calls the external market data API.
3. The raw JSON response is stored in PostgreSQL.
4. The response is parsed into structured daily price records.
5. The structured records are loaded into analytics tables using upserts.
6. SQL views calculate metrics such as daily returns and cumulative returns.
7. A Streamlit dashboard visualizes the results.

## Repository Structure

```text
market-data-engineering-pipeline/
│
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── docker-compose.yml
│
├── config/
│   └── symbols.yaml
│
├── sql/
│   ├── 001_create_schemas.sql
│   ├── 002_create_tables.sql
│   └── 003_create_views.sql
│
├── src/
│   ├── config.py
│   ├── db.py
│   ├── api_client.py
│   ├── load_raw.py
│   ├── transform_prices.py
│   ├── run_pipeline.py
│   └── logging_config.py
│
├── dashboard/
│   └── app.py
│
└── tests/
    ├── test_api_client.py
    └── test_transform_prices.py
```

## Database Design

The PostgreSQL database is organised into four schemas:

### `raw`

Stores the original API responses as JSONB.

This layer makes it possible to reprocess historical API responses without calling the external API again.

Example table:

```text
raw.api_responses
```

### `staging`

Stores parsed and cleaned data before it is loaded into the analytics layer.

Example table:

```text
staging.daily_prices
```

### `analytics`

Stores analysis-ready dimension and fact tables.

Example tables:

```text
analytics.dim_symbol
analytics.fact_daily_price
```

Example views:

```text
analytics.v_latest_prices
analytics.v_daily_returns
analytics.v_cumulative_returns
analytics.v_moving_averages
```

### `metadata`

Stores pipeline run information and logging metadata.

Example table:

```text
metadata.pipeline_runs
```

## Planned Database Tables

### `metadata.pipeline_runs`

Tracks each pipeline execution.

Main columns:

```text
run_id
pipeline_name
started_at
finished_at
status
records_loaded
error_message
```

### `raw.api_responses`

Stores raw API responses.

Main columns:

```text
response_id
run_id
source_name
endpoint
symbol
request_params
response_json
status_code
ingested_at
```

### `analytics.dim_symbol`

Stores information about each stock or ETF symbol.

Main columns:

```text
symbol_id
symbol
name
asset_type
currency
exchange
is_active
```

### `analytics.fact_daily_price`

Stores historical daily price data.

Main columns:

```text
symbol_id
price_date
open_price
high_price
low_price
close_price
adjusted_close
volume
ingested_at
```

The primary key is:

```text
symbol_id + price_date
```

This allows the pipeline to safely upsert records and avoid duplicates.

## API Provider

The first version of this project uses Alpha Vantage as the financial market data provider.

The API key is stored locally in a `.env` file and should never be committed to GitHub.

## Environment Variables

Create a local `.env` file based on `.env.example`.

Example:

```env
ALPHA_VANTAGE_API_KEY=your_api_key_here
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=market_data
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/market-data-engineering-pipeline.git
cd market-data-engineering-pipeline
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows
.venv\Scripts\activate
```

```bash
# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```bash
cp .env.example .env
```

Then add your API key and PostgreSQL credentials.

### 5. Start PostgreSQL with Docker Compose

```bash
docker compose up -d
```

This starts a local PostgreSQL database.

Optionally, pgAdmin can be included in the Docker Compose setup to inspect the database through a browser.

### 6. Create database schemas and tables

Run the SQL scripts in order:

```bash
psql -h localhost -U postgres -d market_data -f sql/001_create_schemas.sql
psql -h localhost -U postgres -d market_data -f sql/002_create_tables.sql
psql -h localhost -U postgres -d market_data -f sql/003_create_views.sql
```

### 7. Configure symbols

Edit the file:

```text
config/symbols.yaml
```

Example:

```yaml
symbols:
  - AAPL
  - MSFT
  - NVDA
  - SPY
  - QQQ
```

### 8. Run the pipeline

```bash
python src/run_pipeline.py
```

### 9. Start the dashboard

```bash
streamlit run dashboard/app.py
```

## Example Analytics

The analytics layer can be used to answer questions such as:

- What is the latest available price for each symbol?
- Which symbol had the highest daily return?
- How did each stock or ETF perform over time?
- What is the cumulative return since the start date?
- How do individual stocks compare with benchmark ETFs?
- Which symbols show the highest volatility?
- When was the last successful pipeline run?

## Dashboard Ideas

The Streamlit dashboard may include:

- Latest price per symbol
- Historical close price chart
- Cumulative return chart
- Daily return chart
- Trading volume chart
- Moving average chart
- Symbol comparison
- Pipeline status overview
- Last successful data refresh

## Project Roadmap

### Version 1 — MVP

- Set up PostgreSQL with Docker Compose
- Create raw, staging, analytics, and metadata schemas
- Connect to Alpha Vantage API using an API key
- Load raw JSON responses into PostgreSQL
- Parse daily price data
- Load data into analytics tables
- Build basic SQL views
- Create a simple Streamlit dashboard

### Version 2 — Data Engineering Improvements

- Add robust logging
- Add retry logic
- Add rate-limit handling
- Improve error handling
- Add incremental loading
- Add data quality checks
- Add unit tests

### Version 3 — Analytics Layer

- Add daily returns
- Add cumulative returns
- Add moving averages
- Add volatility metrics
- Add benchmark comparison
- Add monthly performance views

### Version 4 — Dashboard Improvements

- Add filters by symbol and date range
- Add performance comparison charts
- Add pipeline monitoring page
- Add data freshness indicators
- Add interactive metrics

### Version 5 — Advanced Extensions

Possible future extensions:

- Add more ETF symbols
- Add crypto market data
- Add financial fundamentals
- Add a second API provider
- Add dbt for transformations
- Add Prefect for orchestration
- Add FastAPI to expose the analytics data through a custom API
- Add Metabase or Grafana
- Add GitHub Actions for automated checks

## Learning Goals

This project helps develop practical experience with:

- API integration
- API key management
- Python-based ETL pipelines
- PostgreSQL data modelling
- JSONB storage
- Incremental data loading
- SQL transformations
- Data quality thinking
- Dashboarding
- Local development with Docker
- Building portfolio-ready data engineering projects

## Security Notes

The `.env` file should never be committed to GitHub.

Only `.env.example` should be included in the repository.

Make sure `.gitignore` contains:

```text
.env
.venv/
__pycache__/
*.pyc
```

## Financial Disclaimer

This project is for educational and portfolio purposes only.

The data, dashboards, and analyses produced by this project should not be considered financial advice or investment recommendations.

## Project Status

This project is currently under development.

The first milestone is to build a working MVP that extracts daily market data, stores it in PostgreSQL, transforms it into analytics-ready tables, and visualizes the results in a Streamlit dashboard.
