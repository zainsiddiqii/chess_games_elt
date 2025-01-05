from dagster import AssetExecutionContext, AssetKey
from dagster_dbt import dbt_assets, DbtCliResource, DagsterDbtTranslator
from ..project import chess_games_project
from .utils import store_service_account_key
import os

class CustomizedDagsterDbtTranslator(DagsterDbtTranslator):
    def get_asset_key(self, dbt_resource_props):
        resource_type = dbt_resource_props["resource_type"]
        name = dbt_resource_props["name"]
        if resource_type == "source":
            return AssetKey(f"bigquery_{name}")
        else:
            return super().get_asset_key(dbt_resource_props)

@dbt_assets(
    manifest=chess_games_project.manifest_path,
)
def chess_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    service_account_key_path = store_service_account_key(context)
    # Set the environment variable for dbt to use the file path
    os.environ["GCP_SERVICE_ACCOUNT_KEYFILE"] = service_account_key_path
    yield from dbt.cli(["build"], context=context).stream()