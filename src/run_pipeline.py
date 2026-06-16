import time

from api_client import fetch_daily_prices
from config import load_symbols
from load_raw import (
    create_pipeline_run,
    finish_pipeline_run,
    insert_raw_api_response,
)
from transform_prices import transform_raw_response_to_staging


def main():
    symbols = load_symbols()
    pipeline_name = "daily_market_data_pipeline"

    run_id = create_pipeline_run(pipeline_name)
    total_records_loaded = 0
    failed_symbols = []

    try:
        print(f"Starting pipeline for {len(symbols)} symbols.")

        for symbol in symbols:
            print(f"\nProcessing symbol: {symbol}")

            try:
                data = fetch_daily_prices(symbol)
            except ValueError as error:
                error_message = str(error)
                failed_symbols.append(symbol)

                print(f"Skipping {symbol}: {error_message}")

                request_params = {
                    "function": "TIME_SERIES_DAILY",
                    "symbol": symbol,
                }

                insert_raw_api_response(
                    run_id=run_id,
                    source_name="Alpha Vantage",
                    endpoint="TIME_SERIES_DAILY",
                    symbol=symbol,
                    request_params=request_params,
                    response_json={"error": error_message},
                    status_code=429,
                )

                continue

            request_params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
            }

            response_id = insert_raw_api_response(
                run_id=run_id,
                source_name="Alpha Vantage",
                endpoint="TIME_SERIES_DAILY",
                symbol=symbol,
                request_params=request_params,
                response_json=data,
                status_code=200,
            )

            records_loaded = transform_raw_response_to_staging(response_id)
            total_records_loaded += records_loaded

            print(f"Loaded {records_loaded} records for {symbol}.")

            time.sleep(12)

        if failed_symbols:
            status = "PARTIAL_SUCCESS"
            error_message = f"Failed symbols: {', '.join(failed_symbols)}"
        else:
            status = "SUCCESS"
            error_message = None

        finish_pipeline_run(
            run_id=run_id,
            status=status,
            records_loaded=total_records_loaded,
            error_message=error_message,
        )

        print(
            f"\nPipeline finished with status {status}. "
            f"Loaded {total_records_loaded} records in total."
        )

        if failed_symbols:
            print(f"Failed symbols: {', '.join(failed_symbols)}")

    except Exception as error:
        finish_pipeline_run(
            run_id=run_id,
            status="FAILED",
            records_loaded=total_records_loaded,
            error_message=str(error),
        )

        print(f"Pipeline failed: {error}")
        raise


if __name__ == "__main__":
    main()