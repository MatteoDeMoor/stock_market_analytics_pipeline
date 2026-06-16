DROP VIEW IF EXISTS analytics.v_latest_prices;
DROP VIEW IF EXISTS analytics.v_symbol_performance;

CREATE OR REPLACE VIEW analytics.v_symbol_performance AS
WITH base AS (
    SELECT
        symbol,
        price_date,
        open_price,
        high_price,
        low_price,
        close_price,
        volume,
        LAG(close_price) OVER (
            PARTITION BY symbol
            ORDER BY price_date
        ) AS previous_close_price,
        FIRST_VALUE(close_price) OVER (
            PARTITION BY symbol
            ORDER BY price_date
        ) AS first_close_price
    FROM staging.daily_prices
)
SELECT
    symbol,
    price_date,
    open_price,
    high_price,
    low_price,
    close_price,
    volume,
    previous_close_price,
    ROUND(
        (
            (close_price - previous_close_price)
            / NULLIF(previous_close_price, 0)
        ) * 100,
        4
    ) AS daily_return_pct,
    ROUND(
        (
            (close_price - first_close_price)
            / NULLIF(first_close_price, 0)
        ) * 100,
        4
    ) AS cumulative_return_pct
FROM base;

CREATE OR REPLACE VIEW analytics.v_latest_prices AS
SELECT DISTINCT ON (symbol)
    symbol,
    price_date,
    open_price,
    high_price,
    low_price,
    close_price,
    volume,
    daily_return_pct,
    cumulative_return_pct
FROM analytics.v_symbol_performance
ORDER BY symbol, price_date DESC;

------------

SELECT *
FROM analytics.v_symbol_performance
ORDER BY symbol, price_date DESC
LIMIT 10;

SELECT *
FROM analytics.v_latest_prices
ORDER BY symbol;
