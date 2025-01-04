from dagster import Definitions, load_assets_from_package_module
from .resources import bigquery_resource, dbt_resource
from .assets.dbt import chess_dbt_assets
from .assets.google_cloud_storage import games_dataframe, gcs_file, bigquery_raw_games_chesscom
from .assets.looker import bigquery_dashboard_view
from .jobs import monthly_el_update_job, monthly_transform_serve_job
from .schedules import monthly_update_schedule
from .sensors import bigquery_raw_table_sensor

defs = Definitions(
    assets=[games_dataframe, gcs_file, bigquery_raw_games_chesscom, chess_dbt_assets, bigquery_dashboard_view],
    resources={
        "bigquery": bigquery_resource,
        "dbt": dbt_resource,
    },
    jobs=[monthly_el_update_job, monthly_transform_serve_job],
    schedules=[monthly_update_schedule],
    sensors=[bigquery_raw_table_sensor],
)