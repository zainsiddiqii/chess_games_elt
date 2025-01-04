from pathlib import Path
from dagster_dbt import DbtProject

chess_games_project = DbtProject(
    project_dir=Path(__file__).joinpath("..", "..", "dbt_chess_games").resolve(),
    packaged_project_dir=Path(__file__).joinpath("..", "..", "dbt-project").resolve(),
)
chess_games_project.prepare_if_dev()