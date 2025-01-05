from dagster_gcp import BigQueryResource
from gcs_auth_resource import GCSAuthResource
from dagster import EnvVar
from dagster_dbt import DbtCliResource
from ..project import chess_games_project

bigquery_resource = BigQueryResource(
    project=EnvVar("GCP_PROJECT"), 
    gcp_credentials=EnvVar("GCP_CREDS"),
)

gcs_auth_resource = GCSAuthResource(
    project=EnvVar("GCP_PROJECT"),
    gcp_credentials=EnvVar("GCP_CREDS"),
)

dbt_resource = DbtCliResource(project_dir=chess_games_project)