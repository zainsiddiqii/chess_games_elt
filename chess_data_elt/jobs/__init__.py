from dagster import define_asset_job, AssetSelection
from ..partitions import monthly_partition

monthly_update_job = define_asset_job(
    name="monthly_update_job",
    partitions_def=monthly_partition,
    selection=AssetSelection.all()
)