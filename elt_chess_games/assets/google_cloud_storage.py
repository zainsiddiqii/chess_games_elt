from dagster import asset, EnvVar, AssetExecutionContext, BackfillPolicy
from dagster_gcp import BigQueryResource, GCSResource
import polars as pl
from ..resources import GCPAuthResource
import io
from . import constants
from .utils import get_monthly_archive, extract_game_data, BIGQUERY_TABLE_JOB_CONFIG
from ..partitions import monthly_partition

@asset(
    partitions_def=monthly_partition,
    backfill_policy=BackfillPolicy.multi_run(max_partitions_per_run=1),
    group_name="extract_load"
)
def games_dataframe(context: AssetExecutionContext) -> pl.DataFrame:
    """Polars DataFrame containing data about chess games."""
    
    chesscom_username = EnvVar('CHESSCOM_USERNAME').get_value()
    
    partition_date_str = context.partition_key
    year, month = partition_date_str.split('-')[:2]
    
    monthly_data = get_monthly_archive(
        year,
        month,
        username=chesscom_username
    )
    games = monthly_data['games']
    
    df = pl.DataFrame({})
    
    for game in games:
        try:
            game_df = extract_game_data(game)
            df = df.vstack(game_df)
        except pl.exceptions.SchemaError:
            continue
    
    return df
    
@asset(
    partitions_def=monthly_partition,
    backfill_policy=BackfillPolicy.multi_run(max_partitions_per_run=1),
    group_name="extract_load"
)
def gcs_file(context: AssetExecutionContext, games_dataframe: pl.DataFrame, gcp_auth: GCPAuthResource) -> None:
    """The formatted ndjson file containing chess games data for a month."""
    
    partition_date_str = context.partition_key
    year, month = partition_date_str.split('-')[:2]
    
    bucket_name = EnvVar('GCS_BUCKET').get_value()
    gcs_file_path = constants.GCS_FILE_PATH_TEMPLATE.format(year, month)
    full_file_path = f"gs://{bucket_name}/{gcs_file_path}"
    
    client = gcp_auth.get_client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(gcs_file_path)
    print(blob.name)
    
    with io.BytesIO() as stream:
        games_dataframe.write_ndjson(stream)
        stream.seek(0)
        blob.upload_from_file(stream)
        
    print(f"Uploaded {gcs_file_path} to GCS bucket {bucket_name}.")
    
    for blob in client.list_blobs(bucket_name):
        print(blob.name) 
    
@asset(
    partitions_def=monthly_partition,
    backfill_policy=BackfillPolicy.multi_run(max_partitions_per_run=1),
    group_name="extract_load"
)
def bigquery_raw_games_chesscom(games_dataframe: pl.DataFrame, bigquery: BigQueryResource) -> None:
    """Table on BigQuery containing raw data about chess games."""
    
    bq_project = EnvVar('GCP_PROJECT').get_value()
    bq_dataset = EnvVar("BIGQUERY_DATASET").get_value()
    bq_table_name = EnvVar("BIGQUERY_TABLE_NAME").get_value()
    bq_table = f"{bq_project}.{bq_dataset}.{bq_table_name}"
    
    with io.BytesIO() as stream:
        games_dataframe.write_ndjson(stream)
        stream.seek(0)
        with bigquery.get_client() as client:
            job = client.load_table_from_file(
                stream,
                bq_table,
                job_config=BIGQUERY_TABLE_JOB_CONFIG,
            )

    job.result()  # Waits for the job to complete