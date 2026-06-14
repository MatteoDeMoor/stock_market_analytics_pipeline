from db import get_connection


def transform_raw_response_to_staging(response_id: str) -> int:
    select_query = """
        SELECT response_id, symbol, response_json
        FROM raw.api_responses
        WHERE response_id = %s
          AND endpoint = 'TIME_SERIES_DAILY'
    """

    upsert_query = """
        INSERT INTO staging.daily_prices (
            symbol,
            price_date,
            open_price,
            high_price,
            low_price,
            close_price,
            volume,
            source_response_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (symbol, price_date)
        DO UPDATE SET
            open_price = EXCLUDED.open_price,
            high_price = EXCLUDED.high_price,
            low_price = EXCLUDED.low_price,
            close_price = EXCLUDED.close_price,
            volume = EXCLUDED.volume,
            source_response_id = EXCLUDED.source_response_id,
            ingested_at = NOW()
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(select_query, (response_id,))
            row = cur.fetchone()

            if row is None:
                print(f"No raw API response found for response_id: {response_id}")
                return 0

            source_response_id, symbol, response_json = row

            time_series = response_json.get("Time Series (Daily)")

            if not time_series:
                raise ValueError(
                    f"Missing 'Time Series (Daily)' in raw response for symbol {symbol}."
                )

            records_loaded = 0

            for price_date, values in time_series.items():
                cur.execute(
                    upsert_query,
                    (
                        symbol,
                        price_date,
                        values.get("1. open"),
                        values.get("2. high"),
                        values.get("3. low"),
                        values.get("4. close"),
                        values.get("5. volume"),
                        source_response_id,
                    ),
                )

                records_loaded += 1

    return records_loaded