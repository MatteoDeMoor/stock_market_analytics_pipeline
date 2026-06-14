CREATE TABLE IF NOT EXISTS metadata.pipeline_runs (
    run_id UUID PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    status TEXT NOT NULL,
    records_loaded INTEGER DEFAULT 0,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS raw.api_responses (
    response_id UUID PRIMARY KEY,
    run_id UUID REFERENCES metadata.pipeline_runs(run_id),
    source_name TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    symbol TEXT NOT NULL,
    request_params JSONB,
    response_json JSONB NOT NULL,
    status_code INTEGER,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
