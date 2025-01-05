from dagster import define_asset_job, AssetSelection
from dagster_dbt import build_dbt_asset_selection
from ..assets.dbt import chess_dbt_assets
from ..partitions import monthly_partition

monthly_el_update_job = define_asset_job(
    name="monthly_extract_load_job",
    partitions_def=monthly_partition,
    selection=AssetSelection.groups("extract_load")
)

transform_serve_assets = build_dbt_asset_selection(
    dbt_assets=[chess_dbt_assets],
    dbt_select="fqn:*"
).downstream()

monthly_transform_serve_job = define_asset_job(
    name="monthly_transform_serve_job",
    selection=transform_serve_assets
)