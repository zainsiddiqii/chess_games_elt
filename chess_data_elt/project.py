from pathlib import Path

from dagster_dbt import DbtProject

RELATIVE_PATH_TO_MY_DBT_PROJECT = "../dbt_chess_games"

my_project = DbtProject(
    project_dir=Path(__file__)
    .joinpath("..", RELATIVE_PATH_TO_MY_DBT_PROJECT)
    .resolve(),
)
my_project.prepare_if_dev()
