from ..jobs import monthly_transform_serve_job
from dagster import (
    AssetKey,
    EventLogEntry,
    RunConfig,
    SensorEvaluationContext,
    RunRequest,
    asset_sensor,
)

# AssetKey for the asset to monitor
BIGQUERY_RAW_TABLE_ASSET = AssetKey("bigquery_raw_games_chesscom")

@asset_sensor(asset_key=BIGQUERY_RAW_TABLE_ASSET, job=monthly_transform_serve_job)
def bigquery_raw_table_sensor(context: SensorEvaluationContext, asset_event: EventLogEntry):
    assert asset_event.dagster_event and asset_event.dagster_event.asset_key
    yield RunRequest(
        run_key=context.cursor,
        run_config={
            "ops": {
                "read_materialization": {
                    "config": {
                        "asset_key": asset_event.dagster_event.asset_key.path,
                    }
                }
            }
        },
    )
