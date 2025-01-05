from dagster import AssetExecutionContext
from dagster_dbt import dbt_assets, DbtCliResource
from ..project import chess_games_project
from .utils import store_service_account_key
import os

@dbt_assets(
    manifest=chess_games_project.manifest_path,
)
def chess_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    service_account_key_path = store_service_account_key(context)
    # Set the environment variable for dbt to use the file path
    os.environ["GCP_SERVICE_ACCOUNT_KEYFILE"] = service_account_key_path
    yield from dbt.cli(["build"], context=context).stream()