from dagster import Definitions, load_assets_from_modules
from .resources import bigquery_resource, dbt_resource
from .assets import google_cloud_storage, dbt

gcs_assets = load_assets_from_modules(
    [google_cloud_storage],
    group_name='Extract Load')
dbt_assets = load_assets_from_modules(
    [dbt],
    "Transform"
)

defs = Definitions(
    assets=[*gcs_assets, *dbt_assets],
    resources={
        "bigquery": bigquery_resource,
        "dbt": dbt_resource,
    },
)