from pathlib import Path
import os
from dagster_dbt import DbtProject

RELATIVE_PATH_TO_MY_DBT_PROJECT = "../dbt_chess_games"

def get_env():
    if os.getenv("DAGSTER_CLOUD_IS_BRANCH_DEPLOYMENT", "") == "1":
        return "test"
    if os.getenv("DAGSTER_CLOUD_DEPLOYMENT_NAME", "") == "prod":
        return "prod"

my_project = DbtProject(
    project_dir=Path(__file__)
    .joinpath("..", RELATIVE_PATH_TO_MY_DBT_PROJECT)
    .resolve(),
    target=get_env(),
)
my_project.prepare_if_dev()
