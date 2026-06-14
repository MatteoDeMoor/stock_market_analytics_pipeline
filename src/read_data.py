import pandas as pd

from db import get_engine


def get_available_symbols() -> list[str]:
    query = """
        SELECT DISTINCT symbol
        FROM analytics.v_price_history
        ORDER BY symbol;
    """

    engine = get_engine()

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return df["symbol"].tolist()


def get_price_history(symbol: str) -> pd.DataFrame:
    query = """
        SELECT
            symbol,
            price_date,
            open_price,
            high_price,
            low_price,
            close_price,
            volume
        FROM analytics.v_price_history
        WHERE symbol = %(symbol)s
        ORDER BY price_date;
    """

    engine = get_engine()

    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"symbol": symbol})

    return df

def get_latest_prices() -> pd.DataFrame:
    query = """
        SELECT
            symbol,
            price_date,
            close_price,
            volume
        FROM analytics.v_latest_prices
        ORDER BY symbol;
    """

    engine = get_engine()

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return df

def get_cumulative_returns(symbol: str) -> pd.DataFrame:
    query = """
        SELECT
            symbol,
            price_date,
            close_price,
            cumulative_return_pct
        FROM analytics.v_cumulative_returns
        WHERE symbol = %(symbol)s
        ORDER BY price_date;
    """

    engine = get_engine()

    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"symbol": symbol})

    return df

def get_pipeline_runs() -> pd.DataFrame:
    query = """
        SELECT
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

    engine = get_engine()

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return df