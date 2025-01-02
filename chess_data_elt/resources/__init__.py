from dagster_gcp import BigQueryResource, GCSResource
from dagster import EnvVar
from ..project import my_project
from dagster_dbt import DbtCliResource

bigquery_resource = BigQueryResource(
    project=EnvVar("GCP_PROJECT"), 
    gcp_credentials=EnvVar("GCP_CREDS"),
)

dbt_resource = DbtCliResource(project_dir=my_project)