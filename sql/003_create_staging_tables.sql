CREATE TABLE IF NOT EXISTS staging.daily_prices (
    symbol TEXT NOT NULL,
    price_date DATE NOT NULL,
    open_price NUMERIC(18, 6),
    high_price NUMERIC(18, 6),
    low_price NUMERIC(18, 6),
    close_price NUMERIC(18, 6),
    volume BIGINT,
    source_response_id UUID,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (symbol, price_date)
);
