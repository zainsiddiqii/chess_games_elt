from dagster import EnvVar
from dagster_gcp import BigQueryResource
from ..gcs_resource import GCSCustomResource
from dagster_dbt import DbtCliResource
from ..project import chess_games_project

bigquery_resource = BigQueryResource(
    project=EnvVar("GCP_PROJECT"), 
    gcp_credentials=EnvVar("GCP_CREDS"),
)

gcs_resource = GCSCustomResource(
    project=EnvVar("GCP_PROJECT"),
    gcp_credentials=EnvVar("GCP_CREDS"),
)

dbt_resource = DbtCliResource(project_dir=chess_games_project)