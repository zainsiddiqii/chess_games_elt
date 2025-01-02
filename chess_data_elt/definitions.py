from dagster import Definitions, load_assets_from_modules
from .resources import bigquery_resource, dbt_resource
from .assets import dbt_and_looker, google_cloud_storage
from .jobs import monthly_el_update_job
from .schedules import monthly_update_schedule
from .sensors import transformation_sensor

gc_assets = load_assets_from_modules(
    [google_cloud_storage],
    group_name="extracting_loading"
)
dbt_and_looker_assets = load_assets_from_modules(
    [dbt_and_looker],
    group_name="transformation_serving"
)

defs = Definitions(
    assets=[*gc_assets, *dbt_and_looker_assets,],
    resources={
        "bigquery": bigquery_resource,
        "dbt": dbt_resource,
    },
    jobs=[monthly_el_update_job],
    schedules=[monthly_update_schedule],
    sensors=[transformation_sensor],
)