from setuptools import find_packages, setup

setup(
    name="chess_data_elt",
    packages=find_packages(exclude=["chess_data_elt_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud",
        "dagster-gcp",
        "dagster-polars",
        "dagster-dbt",
        "polars==1.18.0",
        "google-cloud",
        "gcsfs",
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
