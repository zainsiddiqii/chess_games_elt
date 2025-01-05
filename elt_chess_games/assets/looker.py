from dagster import asset, EnvVar
from dagster_gcp import BigQueryResource
from dagster_dbt import get_asset_key_for_model
from datetime import datetime
from google.cloud import bigquery as bq
from .utils import bigquery_view_query
from .dbt import chess_dbt_assets

@asset(
    deps=get_asset_key_for_model([chess_dbt_assets], "fct_game"),
    group_name="serve"
)
def bigquery_view_monthly_summary(bigquery: BigQueryResource):
    """A view on BigQuery that will be fed into a Looker dashboard."""
    
    bigquery_project = EnvVar("GCP_PROJECT").get_value()
    bigquery_dataset = EnvVar("BIGQUERY_DATASET").get_value()
    print(f"Using dataset: {bigquery_dataset}")
    
    view_id = f"{bigquery_project}.{bigquery_dataset}.view_monthly_summary"

    curr_month = datetime.now().month
    curr_year = datetime.now().year

    formatted_query = bigquery_view_query.format(
        dataset=bigquery_dataset,
        month=curr_month,
        year=curr_year
    )
    print(formatted_query)
    
    view = bq.Table(view_id)
    view.mview_query = formatted_query

    with bigquery.get_client() as client:
        # Make an API request to create the materialized view.
        view = client.create_table(view, exists_ok=True)
        print(f"Created {view.table_type}: {str(view.reference)}")