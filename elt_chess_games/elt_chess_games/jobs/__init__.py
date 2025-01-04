from dagster import define_asset_job, AssetSelection
from ..partitions import monthly_partition

monthly_el_update_job = define_asset_job(
    name="monthly_update_job",
    partitions_def=monthly_partition,
    selection=AssetSelection.groups("extracting_loading")
)

monthly_transform_serve_job = define_asset_job(
    name="monthly_transform_serve_job",
    selection=AssetSelection.groups("transformation_serving")
)