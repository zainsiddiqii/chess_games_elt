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

import os
import base64
from google.cloud import storage
from pydantic import Field
from typing import Optional
from dagster import ConfigurableResource


class GCPAuthResource(ConfigurableResource):
    """
    A Dagster resource that wraps around the google.cloud.storage.Client class,
    adding support for credential management during instantiation.

    Example:
        .. code-block:: python

            @asset
            def upload_to_gcs(gcp_auth: GCPAuthResource):
                client = gcp_auth.get_client()
                bucket = client.bucket("my-bucket")
                blob = bucket.blob("example.txt")
                blob.upload_from_string("Hello, World!")
    """

    project: str = Field(
        default=None,
        description="Project ID for the GCP project. If not provided, inferred from credentials.",
    )
    gcp_credentials: Optional[str] = Field(
        default=None,
        description=(
            "Base64-encoded GCP authentication credentials. If provided, a temporary file "
            "will be created with the credentials, and GOOGLE_APPLICATION_CREDENTIALS will "
            "be set to the temporary file for authentication."
        ),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = None

    def _setup_credentials(self):
        """
        Sets up GCP credentials by decoding the base64-encoded credentials and creating
        a temporary file to be used by GOOGLE_APPLICATION_CREDENTIALS.
        """
        if self.gcp_credentials:
            # Decode the credentials
            creds_json = base64.b64decode(self.gcp_credentials).decode("utf-8")
            self._temp_credentials_path = "/tmp/gcp_creds.json"

            # Write to a temporary file
            with open(self._temp_credentials_path, "w") as f:
                f.write(creds_json)

            # Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self._temp_credentials_path

    def _cleanup_credentials(self):
        """Cleans up the temporary credentials file and unsets the environment variable."""
        if hasattr(self, "_temp_credentials_path") and os.path.exists(self._temp_credentials_path):
            os.remove(self._temp_credentials_path)
            del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

    def get_client(self) -> storage.Client:
        """
        Returns a google.cloud.storage.Client instance. Sets up credentials if provided.
        """
        if self._client is None:
            try:
                self._setup_credentials()
                self._client = storage.Client(project=self.project)
            finally:
                self._cleanup_credentials()
        return self._client


gcp_auth_resource = GCPAuthResource(
    project=EnvVar("GCP_PROJECT"),
    gcp_credentials=EnvVar("GCP_CREDS"),
)