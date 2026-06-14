import uuid

from psycopg.types.json import Json

from db import get_connection


def create_pipeline_run(pipeline_name: str) -> str:
    run_id = str(uuid.uuid4())

    query = """
        INSERT INTO metadata.pipeline_runs (
            run_id,
            pipeline_name,
            status
        )
        VALUES (%s, %s, %s)
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (run_id, pipeline_name, "RUNNING"))

    return run_id


def insert_raw_api_response(
    run_id: str,
    source_name: str,
    endpoint: str,
    symbol: str,
    request_params: dict,
    response_json: dict,
    status_code: int,
) -> str:
    response_id = str(uuid.uuid4())

    query = """
        INSERT INTO raw.api_responses (
            response_id,
            run_id,
            source_name,
            endpoint,
            symbol,
            request_params,
            response_json,
            status_code
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                query,
                (
                    response_id,
                    run_id,
                    source_name,
                    endpoint,
                    symbol,
                    Json(request_params),
                    Json(response_json),
                    status_code,
                ),
            )

    return response_id


def finish_pipeline_run(
    run_id: str,
    status: str,
    records_loaded: int = 0,
    error_message: str | None = None,
) -> None:
    query = """
        UPDATE metadata.pipeline_runs
        SET
            finished_at = NOW(),
            status = %s,
            records_loaded = %s,
            error_message = %s
        WHERE run_id = %s
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (status, records_loaded, error_message, run_id))
