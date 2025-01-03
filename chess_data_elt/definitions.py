from dagster import Definitions, load_assets_from_modules
from .resources import bigquery_resource, dbt_resource
from .assets import dbt_and_looker, google_cloud_storage, looker
from .jobs import monthly_el_update_job, monthly_transform_serve_job
from .schedules import monthly_update_schedule
from .sensors import bigquery_raw_table_sensor

gc_assets = load_assets_from_modules(
    [google_cloud_storage],
    group_name="extracting_loading"
)
dbt_and_looker_assets = load_assets_from_modules(
    [dbt_and_looker],
    group_name="transformation_serving"
)
looker_assets = load_assets_from_modules(
    [looker],
    group_name="serving"
)

defs = Definitions(
    assets=[*gc_assets, *dbt_and_looker_assets],
    resources={
        "bigquery": bigquery_resource,
        "dbt": dbt_resource,
    },
    jobs=[monthly_el_update_job, monthly_transform_serve_job],
    schedules=[monthly_update_schedule],
    sensors=[bigquery_raw_table_sensor],
)