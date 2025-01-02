from dagster import AssetExecutionContext, asset, EnvVar
from dagster_dbt import dbt_assets, get_asset_key_for_model
from ..resources import dbt_resource, bigquery_resource
from .utils import bigquery_view_query
from ..project import my_project

@dbt_assets(
    manifest=my_project.manifest_path,
)
def chess_dbt_assets(context: AssetExecutionContext):
    yield from dbt_resource.cli(["build"], context=context).stream()

@asset(
    deps=get_asset_key_for_model([chess_dbt_assets], "fct_game")
)
def bigquery_view():
    """A view on BigQuery that will be fed into a Looker dashboard."""
    
    bigquery_dataset = EnvVar("BIGQUERY_DATASET").get_value()
    
    with bigquery_resource.get_client() as client:
        query = client.query(
            bigquery_view_query.format(bigquery_dataset)
        )
        
    return query.result()