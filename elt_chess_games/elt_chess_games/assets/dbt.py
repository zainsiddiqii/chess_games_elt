from dagster import AssetExecutionContext
from dagster_dbt import dbt_assets
from ..project import chess_games_project
from ..resources import dbt_resource

@dbt_assets(
    manifest=chess_games_project.manifest_path,
)
def chess_dbt_assets(context: AssetExecutionContext):
    yield from dbt_resource.cli(["build"], context=context).stream()