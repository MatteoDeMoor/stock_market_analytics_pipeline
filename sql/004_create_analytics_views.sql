CREATE OR REPLACE VIEW analytics.v_latest_prices AS
SELECT DISTINCT ON (symbol)
    symbol,
    price_date,
    open_price,
    high_price,
    low_price,
    close_price,
    volume,
    ingested_at
FROM staging.daily_prices
ORDER BY symbol, price_date DESC;


CREATE OR REPLACE VIEW analytics.v_daily_returns AS
SELECT
    symbol,
    price_date,
    close_price,
    LAG(close_price) OVER (
        PARTITION BY symbol
        ORDER BY price_date
    ) AS previous_close_price,
    ROUND(
        (
            (close_price - LAG(close_price) OVER (
                PARTITION BY symbol
                ORDER BY price_date
            ))
            / NULLIF(LAG(close_price) OVER (
                PARTITION BY symbol
                ORDER BY price_date
            ), 0)
        ) * 100,
        4
    ) AS daily_return_pct
FROM staging.daily_prices;


CREATE OR REPLACE VIEW analytics.v_cumulative_returns AS
WITH base AS (
    SELECT
        symbol,
        price_date,
        close_price,
        FIRST_VALUE(close_price) OVER (
            PARTITION BY symbol
            ORDER BY price_date
        ) AS first_close_price
    FROM staging.daily_prices
)
SELECT
    symbol,
    price_date,
    close_price,
    ROUND(
        ((close_price - first_close_price) / NULLIF(first_close_price, 0)) * 100,
        4
    ) AS cumulative_return_pct
FROM base;

------------

SELECT *
FROM analytics.v_latest_prices
ORDER BY symbol;

SELECT *
FROM analytics.v_daily_returns
ORDER BY symbol, price_date DESC
LIMIT 20;

SELECT *
FROM analytics.v_cumulative_returns
ORDER BY symbol, price_date DESC
LIMIT 20;