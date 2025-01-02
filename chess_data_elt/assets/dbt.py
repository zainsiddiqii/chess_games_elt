from dagster import AssetExecutionContext
from dagster_dbt import dbt_assets
from ..resources import dbt_resource

from ..project import my_project

@dbt_assets(
    manifest=my_project.manifest_path
)
def chess_dbt_assets(context: AssetExecutionContext):
    yield from dbt_resource.cli(["build"], context=context).stream()
