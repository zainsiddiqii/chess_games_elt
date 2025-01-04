from setuptools import find_packages, setup

setup(
    name="elt_chess_games",
    version="0.0.1",
    packages=find_packages(),
    package_data={
        "elt_chess_games": [
            "dbt-project/**/*",
        ],
    },
    install_requires=[
        "dagster",
        "dagster-cloud",
        "dagster-dbt",
        "dagster-gcp",
        "dagster-polars",
        "dbt-bigquery<1.9",
        "dbt-bigquery<1.9",
        "polars==1.18.0",
        "google-cloud",
        "gcsfs",
    ],
    extras_require={
        "dev": [
            "dagster-webserver",
        ]
    },
)