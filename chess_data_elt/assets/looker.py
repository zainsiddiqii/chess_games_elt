from dagster import asset
from dagster_dbt import get_asset_key_for_model
from .dbt import chess_dbt_assets
from ..resources import bigquery_resource
from .utils import bigquery_view_query

@asset(
    deps=[get_asset_key_for_model([chess_dbt_assets], "fct_game")]
)
def bigquery_view():
    """A view on BigQuery that will be fed into a Looker dashboard."""
    
    with bigquery_resource.get_client() as client:
        query = client.query(bigquery_view_query)
        
    return query.result()