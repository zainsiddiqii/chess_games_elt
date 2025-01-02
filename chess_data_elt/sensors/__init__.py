from dagster import sensor, AssetKey, RunRequest
from ..jobs import monthly_transform_serve_job

# AssetKey for the asset to monitor
BIGQUERY_RAW_ASSET = AssetKey("bigquery_raw_games_chesscom")

@sensor(job=monthly_transform_serve_job)  # Reference the job to trigger
def transformation_sensor(context):
    # Check if the specific asset was materialized
    events = context.instance.get_asset_materialization_events(BIGQUERY_RAW_ASSET)

    # If no materialization events, do nothing
    if not events:
        return

    # Get the most recent materialization
    latest_event = events[0]

    # Check if this materialization is new
    if not context.instance.has_seen_event(latest_event.event_log_entry_id):
        context.instance.mark_event_as_seen(latest_event.event_log_entry_id)

        # Trigger the job with a RunRequest
        return RunRequest(run_key=str(latest_event.event_log_entry_id))
