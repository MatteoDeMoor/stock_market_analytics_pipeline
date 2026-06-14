# Market Data Engineering Pipeline

A local end-to-end data engineering portfolio project that ingests stock and ETF market data from the Alpha Vantage API, stores raw and transformed data in PostgreSQL, and visualizes financial performance through a Streamlit dashboard.

The project is built to demonstrate practical data engineering skills such as API ingestion, PostgreSQL modelling, raw/staging/analytics layers, SQL transformations, pipeline logging, Docker-based local development, and dashboarding.

## Project Status

Current status: **Local MVP working**.

The current version can:

- Read stock symbols from a YAML configuration file
- Fetch daily price data from the Alpha Vantage API
- Store raw API responses as JSONB in PostgreSQL
- Transform raw JSON responses into structured daily price records
- Upsert price records into a staging table
- Expose analytics views for price history, latest prices, daily returns and cumulative returns
- Display the results in a Streamlit dashboard
- Show pipeline run history from a metadata table

The next major goal is to move from a local setup to a cloud-ready architecture using **Cloud PostgreSQL, GitHub Actions and Streamlit Community Cloud**.

## Project Overview

This project simulates a realistic data engineering workflow using free, local and open-source tools.

The goal is to build a small but professional market data pipeline that extracts daily stock and ETF prices from an external API, stores the original API responses, transforms the data into analytics-ready structures, and visualizes the results in a dashboard.

The first working version currently focuses on a small watchlist because the free Alpha Vantage tier has request limits.

Currently active example symbols:

- AAPL
- MSFT
- NVDA

Additional prepared symbols may include:

- GOOGL
- AMZN
- META
- TSLA
- SPY
- QQQ
- VTI
- IWM
- GLD
- NFLX

## Why This Project?

This project is designed to show more than just dashboarding. It focuses on the full data engineering flow from API ingestion to analytics-ready data.

It covers several important data engineering concepts:

- Consuming external APIs
- Working with API keys
- Managing secrets with environment variables
- Handling API rate limits
- Parsing JSON responses
- Storing raw API responses in PostgreSQL as JSONB
- Designing layered database schemas
- Building raw, staging, analytics and metadata layers
- Using upserts to avoid duplicate records
- Creating SQL analytics views
- Tracking pipeline runs and errors
- Building a Streamlit dashboard on top of PostgreSQL
- Preparing the project for cloud deployment

## Tech Stack

Current stack:

- Python
- PostgreSQL
- Docker Compose
- pgAdmin
- Alpha Vantage API
- SQL
- Streamlit
- pandas
- Plotly
- psycopg
- SQLAlchemy
- python-dotenv
- PyYAML
- requests

Planned cloud/deployment stack:

- Neon or Supabase Postgres
- GitHub Actions
- Streamlit Community Cloud
- GitHub Secrets
- Streamlit Secrets

Possible future additions:

- dbt
- Prefect
- pytest
- FastAPI
- Metabase or Grafana

## High-Level Architecture

Current local architecture:

```text
Alpha Vantage API
        ↓
Python API client
        ↓
Pipeline runner
        ↓
raw.api_responses in PostgreSQL
        ↓
Python transformation step
        ↓
staging.daily_prices
        ↓
analytics SQL views
        ↓
read_data.py
        ↓
Streamlit dashboard
```

Target cloud architecture:

```text
Alpha Vantage API
        ↓
GitHub Actions scheduled workflow
        ↓
Python pipeline
        ↓
Cloud PostgreSQL database
        ↓
Streamlit Community Cloud dashboard
        ↓
Public portfolio link
```

## Data Flow

1. The pipeline reads a list of stock and ETF symbols from `config/symbols.yaml`.
2. For each active symbol, the pipeline calls the Alpha Vantage `TIME_SERIES_DAILY` endpoint.
3. The raw JSON response is stored in `raw.api_responses`.
4. The response is parsed into structured daily price rows.
5. The structured records are upserted into `staging.daily_prices`.
6. SQL views in the analytics layer prepare the data for reporting.
7. `read_data.py` reads from the analytics views.
8. The Streamlit dashboard displays prices, returns, volume and pipeline run history.

Important design choice: the dashboard does **not** call the external API directly. The dashboard only reads from PostgreSQL. This improves caching, performance, reproducibility and rate-limit handling.

## Repository Structure

```text
stock_market_analytics_pipeline/
│
├── README.md
├── .gitignore
├── .env.example
├── requirements.txt
├── docker-compose.yml
│
├── config/
│   └── symbols.yaml
│
├── sql/
│   ├── 001_create_schemas.sql
│   ├── 002_create_tables.sql
│   ├── 003_create_staging_tables.sql
│   └── 004_create_analytics_views.sql
│
├── src/
│   ├── api_client.py
│   ├── config.py
│   ├── db.py
│   ├── load_raw.py
│   ├── read_data.py
│   ├── run_pipeline.py
│   └── transform_prices.py
│
└── dashboard/
    └── app.py
```

## Database Design

The PostgreSQL database is organized into four schemas:

### `raw`

Stores original API responses as JSONB.

This allows the project to keep the source data exactly as received from the API. It also makes it possible to reprocess historical API responses without calling the external API again.

Main table:

```text
raw.api_responses
```

### `staging`

Stores parsed and structured intermediate data.

Main table:

```text
staging.daily_prices
```

This table contains one row per symbol and price date. The primary key is:

```text
symbol + price_date
```

This makes safe upserts possible and prevents duplicate price rows.

### `analytics`

Contains analysis-ready SQL views used by the dashboard.

Current views:

```text
analytics.v_price_history
analytics.v_latest_prices
analytics.v_daily_returns
analytics.v_cumulative_returns
```

### `metadata`

Stores pipeline run information.

Main table:

```text
metadata.pipeline_runs
```

This table tracks pipeline status, start time, finish time, loaded record count and error messages.

## Current Database Objects

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

Stores raw Alpha Vantage API responses.

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

### `staging.daily_prices`

Stores parsed daily OHLCV price data.

Main columns:

```text
symbol
price_date
open_price
high_price
low_price
close_price
volume
source_response_id
ingested_at
```

Primary key:

```text
symbol + price_date
```

### `analytics.v_price_history`

Used for historical price charts.

Contains:

```text
symbol
price_date
open_price
high_price
low_price
close_price
volume
```

### `analytics.v_latest_prices`

Used to show the latest available price per symbol.

Contains the most recent price row for every symbol.

### `analytics.v_daily_returns`

Calculates the daily percentage return using the previous close price.

Useful for:

- Daily return charts
- Top movers
- Volatility analysis

### `analytics.v_cumulative_returns`

Calculates cumulative return since the first available date for each symbol.

This is useful because prices between different stocks are not directly comparable, while returns are easier to compare.

## API Provider

The first version uses the Alpha Vantage API.

Current endpoint:

```text
TIME_SERIES_DAILY
```

Example request format:

```text
https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=AAPL&apikey=YOUR_API_KEY
```

The API key is stored in a local `.env` file and should never be committed to GitHub.

## Environment Variables

Create a local `.env` file based on `.env.example`.

Example `.env`:

```env
ALPHA_VANTAGE_API_KEY=your_api_key_here
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=market_data
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```

Example `.env.example`:

```env
ALPHA_VANTAGE_API_KEY=
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=market_data
POSTGRES_USER=
POSTGRES_PASSWORD=
```

## Security Notes

The `.env` file should never be committed to GitHub.

Make sure `.gitignore` contains:

```text
.env
.venv/
__pycache__/
*.pyc
```

Important security lessons:

- Do not print full API request URLs if they contain an API key
- Do not commit `.env` to GitHub
- Use GitHub Secrets for GitHub Actions
- Use Streamlit Secrets for Streamlit Community Cloud
- Rotate the API key if it was accidentally exposed

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/stock_market_analytics_pipeline.git
cd stock_market_analytics_pipeline
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\Activate.ps1
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file based on `.env.example` and add your API key and PostgreSQL credentials.

### 5. Start PostgreSQL and pgAdmin

```bash
docker compose up -d
```

PostgreSQL runs locally on:

```text
localhost:5432
```

pgAdmin runs locally on:

```text
http://localhost:5050
```

When connecting from pgAdmin to PostgreSQL inside Docker, use this host:

```text
postgres
```

When connecting from Python on your machine, use this host:

```text
localhost
```

### 6. Create schemas, tables and views

Run the SQL scripts in order:

```bash
psql -h localhost -U postgres -d market_data -f sql/001_create_schemas.sql
psql -h localhost -U postgres -d market_data -f sql/002_create_tables.sql
psql -h localhost -U postgres -d market_data -f sql/003_create_staging_tables.sql
psql -h localhost -U postgres -d market_data -f sql/004_create_analytics_views.sql
```

Alternatively, run the SQL scripts manually in pgAdmin.

### 7. Configure symbols

Edit:

```text
config/symbols.yaml
```

Example:

```yaml
symbols:
  - AAPL
  - MSFT
  - NVDA
  # - GOOGL
  # - AMZN
  # - SPY
  # - QQQ
```

Only a few symbols are active by default to respect the free Alpha Vantage API limits.

### 8. Run the pipeline

```bash
python src/run_pipeline.py
```

The pipeline will:

- Create a pipeline run record
- Fetch data from Alpha Vantage
- Store raw API responses
- Transform raw JSON into daily price records
- Upsert rows into `staging.daily_prices`
- Update the pipeline run status

### 9. Start the dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard is available locally at:

```text
http://localhost:8501
```

## Dashboard Features

The Streamlit dashboard currently includes:

- Symbol selector in the sidebar
- KPI cards for latest close price, latest date, latest volume and total return
- Latest prices table
- Close price history chart
- Volume history chart
- Cumulative return chart
- Daily returns chart
- Latest rows table for the selected symbol
- Pipeline monitoring table
- Latest pipeline run status cards

## Example Analytics Questions

The analytics layer can answer questions such as:

- What is the latest available price for each symbol?
- How has a symbol's close price evolved over time?
- What is the cumulative return since the first available date?
- What was the daily return for each trading day?
- What was the latest trading volume?
- When was the last successful pipeline run?
- How many records were loaded in the latest pipeline run?

## Useful SQL Checks

Check recent pipeline runs:

```sql
SELECT *
FROM metadata.pipeline_runs
ORDER BY started_at DESC;
```

Check number of records per symbol:

```sql
SELECT symbol, COUNT(*) AS records
FROM staging.daily_prices
GROUP BY symbol
ORDER BY symbol;
```

Check latest prices:

```sql
SELECT *
FROM analytics.v_latest_prices
ORDER BY symbol;
```

Check recent price history:

```sql
SELECT *
FROM analytics.v_price_history
ORDER BY symbol, price_date DESC
LIMIT 20;
```

Check cumulative returns:

```sql
SELECT *
FROM analytics.v_cumulative_returns
ORDER BY symbol, price_date DESC
LIMIT 20;
```

Check daily returns:

```sql
SELECT *
FROM analytics.v_daily_returns
ORDER BY symbol, price_date DESC
LIMIT 20;
```

## Git Commands

Check repository status:

```bash
git status
```

Example commit for the local MVP:

```bash
git add README.md .gitignore .env.example requirements.txt docker-compose.yml config sql src dashboard
git commit -m "Add local market data pipeline MVP"
```

Example commit after dashboard improvements:

```bash
git add src/read_data.py dashboard/app.py README.md
git commit -m "Improve dashboard analytics and documentation"
```

## Roadmap

### Phase 1 — Local MVP and Cleanup

Status: **in progress / mostly complete**

- Set up PostgreSQL with Docker Compose
- Create raw, staging, analytics and metadata schemas
- Connect to Alpha Vantage API using an API key
- Load raw JSON responses into PostgreSQL
- Parse daily price data
- Upsert data into `staging.daily_prices`
- Create analytics views
- Build Streamlit dashboard
- Add KPI cards, volume chart, cumulative returns and daily returns
- Add pipeline monitoring
- Improve README documentation

### Phase 2 — Cloud PostgreSQL

Planned:

- Choose Neon or Supabase Postgres
- Create a cloud PostgreSQL database
- Add cloud database credentials locally
- Run SQL scripts on the cloud database
- Test the local pipeline writing to cloud PostgreSQL
- Test the local dashboard reading from cloud PostgreSQL

### Phase 3 — GitHub Actions

Planned:

- Add GitHub repository secrets
- Create a GitHub Actions workflow
- Add manual `workflow_dispatch` trigger
- Add scheduled daily pipeline run
- Run the pipeline from GitHub Actions
- Write data into the cloud PostgreSQL database

Planned GitHub Secrets:

```text
ALPHA_VANTAGE_API_KEY
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

### Phase 4 — Streamlit Community Cloud

Planned:

- Deploy the dashboard from GitHub
- Set the entry point to `dashboard/app.py`
- Configure Streamlit Secrets
- Connect the dashboard to cloud PostgreSQL
- Test the public dashboard link
- Add the live dashboard link to this README

### Phase 5 — Portfolio Polish

Planned:

- Add dashboard screenshots
- Add an architecture diagram
- Add a LinkedIn-ready project summary
- Add more explanation about the data model
- Add data quality checks
- Add tests
- Add financial disclaimer and limitations

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
- Dashboarding with Streamlit
- Local development with Docker
- Scheduling concepts
- Cloud database deployment
- GitHub Actions automation
- Building portfolio-ready data engineering projects

## Limitations

Current limitations:

- The Alpha Vantage free tier has strict request limits
- The current version uses a small active symbol list
- The local PostgreSQL database is not publicly accessible
- The dashboard currently depends on a running PostgreSQL database
- The first version focuses only on daily prices
- This project does not yet include automated tests or data quality checks

## Financial Disclaimer

This project is for educational and portfolio purposes only.

The data, dashboards and analyses produced by this project should not be considered financial advice or investment recommendations.

## Next Steps

Immediate next steps:

1. Test the improved local dashboard
2. Commit the updated dashboard and README
3. Choose Neon or Supabase for cloud PostgreSQL
4. Run the SQL scripts on the cloud database
5. Test the local pipeline against the cloud database
6. Add GitHub Actions scheduling
7. Deploy the dashboard to Streamlit Community Cloud
