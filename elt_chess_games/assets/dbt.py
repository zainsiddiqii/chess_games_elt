from dagster import AssetExecutionContext
from dagster_dbt import dbt_assets, DbtCliResource
from ..project import chess_games_project

@dbt_assets(
    manifest=chess_games_project.manifest_path,
)
def chess_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()