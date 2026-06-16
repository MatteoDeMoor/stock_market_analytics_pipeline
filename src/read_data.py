import pandas as pd

from db import get_engine

def read_sql(query: str, params: dict | None = None) -> pd.DataFrame:
    """
    Execute a SQL query and return the result as a pandas DataFrame.

    This helper keeps database reading logic in one place.
    """
    engine = get_engine()

    with engine.connect() as conn:
        return pd.read_sql(query, conn, params=params)

def get_available_symbols() -> list[str]:
    query = """
        SELECT DISTINCT symbol
        FROM analytics.v_symbol_performance
        ORDER BY symbol;
    """

    df = read_sql(query)

    return df["symbol"].tolist()

def get_latest_prices() -> pd.DataFrame:
    query = """
        SELECT
            symbol,
            price_date,
            close_price,
            volume,
            daily_return_pct,
            cumulative_return_pct
        FROM analytics.v_latest_prices
        ORDER BY symbol;
    """

    return read_sql(query)

def get_pipeline_runs() -> pd.DataFrame:
    query = """
        SELECT
            run_id,
            pipeline_name,
            started_at,
            finished_at,
            status,
            records_loaded,
            error_message
        FROM metadata.pipeline_runs
        ORDER BY started_at DESC
        LIMIT 10;
    """

    return read_sql(query)

def get_symbol_performance(symbol: str) -> pd.DataFrame:
    query = """
        SELECT
            symbol,
            price_date,
            open_price,
            high_price,
            low_price,
            close_price,
            volume,
            previous_close_price,
            daily_return_pct,
            cumulative_return_pct
        FROM analytics.v_symbol_performance
        WHERE symbol = %(symbol)s
        ORDER BY price_date;
    """

    return read_sql(query, params={"symbol": symbol})
