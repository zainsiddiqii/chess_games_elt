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
from contextlib import contextmanager
from typing import Optional, Iterator
from google.cloud import storage
from dagster import ConfigurableResource
from pydantic import Field

class GCPAuthResource(ConfigurableResource):
    """
    A Dagster resource for authenticated interactions with GCP services, such as GCS,
    using credentials provided during instantiation.

    Example:
        .. code-block:: python

            @asset
            def my_asset(gcp_auth: GCPAuthResource):
                with gcp_auth.get_gcs_client() as client:
                    bucket = client.bucket("my-bucket")
                    blob = bucket.blob("my-object")
                    blob.upload_from_string("Hello, World!")
    """

    project: Optional[str] = Field(
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

    @contextmanager
    def _setup_credentials(self):
        """Temporarily sets up GCP credentials for the resource."""
        if self.gcp_credentials:
            # Decode the base64-encoded credentials
            creds_json = base64.b64decode(self.gcp_credentials).decode("utf-8")
            temp_credentials_path = "/tmp/gcp_creds.json"

            # Write credentials to a temporary file
            with open(temp_credentials_path, "w") as f:
                f.write(creds_json)

            # Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_credentials_path

            try:
                yield  # Yield control back to the caller
            finally:
                # Cleanup: Remove the temporary file and unset the environment variable
                os.remove(temp_credentials_path)
                del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
        else:
            yield  # Proceed without modifying credentials if none are provided

    @contextmanager
    def get_gcs_client(self) -> Iterator[storage.Client]:
        """
        Returns an authenticated GCS client (google.cloud.storage.Client) using the provided credentials.

        Example:
            .. code-block:: python

                with gcp_auth.get_gcs_client() as client:
                    bucket = client.bucket("my-bucket")
                    ...
        """
        with self._setup_credentials():
            yield storage.Client(project=self.project)

gcp_auth_resource = GCPAuthResource(
    project=EnvVar("GCP_PROJECT"),
    gcp_credentials=EnvVar("GCP_CREDS"),
)