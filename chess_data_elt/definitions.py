from dagster import Definitions, load_assets_from_modules
from .resources import bigquery_resource, dbt_resource
from .assets import google_cloud_storage, dbt, looker

gc_assets = load_assets_from_modules(
    [google_cloud_storage],
    group_name="extract_load"
)
dbt_assets = load_assets_from_modules(
    [dbt],
    group_name="transform"
)
# dashboard_assets = load_assets_from_modules(
#     [looker],
#     group_name="dashboard"
# )

defs = Definitions(
    assets=[*gc_assets, *dbt_assets,],
    resources={
        "bigquery": bigquery_resource,
        "dbt": dbt_resource,
    },
)