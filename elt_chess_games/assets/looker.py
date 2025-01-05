from dagster import asset, EnvVar
from dagster_gcp import BigQueryResource
from dagster_dbt import get_asset_key_for_model
from .utils import bigquery_view_query
from .dbt import chess_dbt_assets

@asset(
    deps=get_asset_key_for_model([chess_dbt_assets], "fct_game"),
    group_name="serve"
)
def bigquery_dashboard_view(bigquery: BigQueryResource):
    """A view on BigQuery that will be fed into a Looker dashboard."""
    
    bigquery_dataset = EnvVar("BIGQUERY_DATASET").get_value()
    
    with bigquery.get_client() as client:
        query = client.query(
            bigquery_view_query.format(bigquery_dataset)
        )
        
    return query.result()