from dagster_gcp import BigQueryResource, GCSResource
from dagster import EnvVar
from ..project import chess_games_project
from dagster_dbt import DbtCliResource

bigquery_resource = BigQueryResource(
    project=EnvVar("GCP_PROJECT"), 
    gcp_credentials=EnvVar("GCP_CREDS"),
)

gcs_resource = GCSResource(
    project=EnvVar("GCP_PROJECT"),
)

dbt_resource = DbtCliResource(project_dir=chess_games_project)