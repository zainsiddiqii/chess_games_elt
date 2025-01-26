## Background and Overview

I have been an avid chess player since I watched the Queen's Gambit back in the winter of 2020. I've played over 10000 games over the course of my career, and I got into data into 2022. This project is a culmination of my two passions, chess and data. I wanted to analyse my performance over the course of my career and have my data stored somewhere so I can easily answer questions about my games.

This is thus a full-stack data project, from ingestion, to loading, storage, transformation, and serving. I use Python to call the chess.com API to retrieve my games data, which it returns as a JSON object. I then transform this data slightly so that it is as clean as possible when I load it into Google BigQuery. I then use dbt to transform the data into a STAR schema, and eventually create a VIEW which I feed into a dashboard on Looker Studio. This report gives me some performance metrics over the past month of my play, so I can see which areas to improve and address in my game. All of these steps are orchestrated on a monthly schedule using Dagster. Everything is also version controlled using Git and deployed via GitHub Actions, using a CI/CD pipeline.

### Tech Stack

- `Python` for Extract and Load
- `Google BigQuery` for Storage
- `dbt` for Transformation
- `Looker Studio` for Data Visualization
- `Dagster` for Orchestration
- `GitHub Actions` for CI/CD

### Folder Structure

```
chess_games_elt
├── README.md
├── .gitignore
├── .github
│   └── deploy.yml
    └── branch_deployments.yml
├── .env
├── dagster_cloud.yaml
├── pyproject.toml
├── setup.py
├── dbt_chess_games/
├── elt_chess_games/
```

The project is structured as follows:
- `dbt_chess_games/` contains the dbt project
- `elt_chess_games/` contains the Dagster project, which includes scripts for extracting and loading data, as well as the orchestration of the pipeline, and the view creation in BigQuery that feeds into Looker Studio.

### Pipeline

![Pipeline](Global_Asset_Lineage.svg)

Since everything is orchestrated in Dagster, the pipeline is as organised into asset_groups as follows:

1. extract_load
   
   This asset group extract the data from the chesscom API, lightly transforms it, and loads it into BigQuery, as well as creating a backup in Google Cloud Storage.
2. transform (default)
   
    This asset group transforms the data in BigQuery using dbt.
3. serve
   
    This asset group creates a view in BigQuery that feeds into Looker Studio.

### Dashboard

The [dashboard](https://lookerstudio.google.com/reporting/ea86985e-f6a3-4ece-899b-5ba78a987e0e) can be accessed on Looker Studio. It shows me
- Where my opponents are located and how much I've played against opponents from each country
- The number of games I have played over the course of the month
- My Win percentage by colour (White vs Black) and then drilled down by opening, this shows me which openings I am most successful with, and which I need to improve on
- My average accuracy vs my opponent's average accuracy by each opening, this shows me which openings I am most successful with, and which I need to improve on
- Summary statistics such as Minutes Played, Wins, Losses, Number of Games Player, Highest Rating, and Lowest Rating.