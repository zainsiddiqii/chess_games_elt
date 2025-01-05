import polars as pl
import requests
from polars.exceptions import SchemaError
from datetime import datetime
import os
import base64
import tempfile

from google.cloud.bigquery import (
    LoadJobConfig,
    SchemaField,
    SourceFormat,
    WriteDisposition,
    TimePartitioning,
    TimePartitioningType,
    SchemaUpdateOption
)

headers = {'User-Agent': 'Mozilla/5.0'}

def get_archives(username: str) -> dict:
    
    base_url = "https://api.chess.com/pub/player"
    url = f"{base_url}/{username}/games/archives"
    response = requests.get(url, headers=headers).json()
    
    return response

def get_monthly_archive(year: str, month: str, username: str) -> dict:
    
    base_url = f"https://api.chess.com/pub/player/{username}/games/"
    url = f"{base_url}{year}/{month}"
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch data from Chess.com API. Status code: {response.status_code}, URL: {url}")

    try:
        response_json = response.json()
    except requests.exceptions.JSONDecodeError:
        raise ValueError(f"Invalid JSON response from Chess.com API. URL: {url}, Response: {response.text}")
    
    return response_json

def extract_game_data(game: dict) -> pl.DataFrame:
    
    url = game['url']
    print('Extracting data from:', url)
    game_id = game['uuid']
    time_class = game['time_class'] # rapid, blitz, bullet
    time_control = game['time_control'] # in seconds
    is_rated = game['rated'] # boolean
    white_rating = game['white']['rating']
    black_rating = game['black']['rating']
    white_result = game['white']['result']
    black_result = game['black']['result']
    
    try:
        white_accuracy = game['accuracies']['white']
        black_accuracy = game['accuracies']['black']
    except KeyError:
        white_accuracy = None
        black_accuracy = None

    if game['white']['username'] == 'zainsiddiqii':
        colour = 'white'
        opponent_api_link = game['black']['@id']

    else:
        colour = 'black'
        opponent_api_link = game['white']['@id']

    opponent_data = requests.get(opponent_api_link, headers=headers).json()
    opponent_username = opponent_data['username']
    opponent_country = requests.get(opponent_data['country'], headers=headers).json()['name']
    opponent_is_verified = opponent_data['verified']
    opponent_status = opponent_data['status']
    opponent_id = opponent_data['player_id']
    
    pgn_data = game['pgn'].split('\n')
    
    start_date = pgn_data[2].strip('[]').split(' ')[1].strip('"')
    start_time = pgn_data[17].strip('[]').split(' ')[1].strip('"')
    end_date = pgn_data[18].strip('[]').split(' ')[1].strip('"')
    
    try:
        end_time = pgn_data[19].strip('[]').split(' ')[1].strip('"')
    except IndexError:
        end_time = None
        print('Game was not started. Skipping...')
    
    if end_time is None:
        start_datetime = None
        end_datetime = None
        opening_code = None
        opening_url = None
        opening_name = None
        move_times = None
        moves = None
        total_moves = None
    else:
        start_datetime = start_date.replace('.', '-') + ' ' + start_time
        end_datetime = end_date.replace('.', '-') + ' ' + end_time
        opening_code = pgn_data[9].strip('[]').split(' ')[1].strip('"')
        opening_url = pgn_data[10].strip('[]').split(' ')[1].strip('"')
        opening_name = pgn_data[10].strip('[]').split(' ')[1].strip('"').split('/')[-1].replace('-', ' ')
        
        pgn = game['pgn'].split('\n')[-2]
        pgn = pgn.split('}')
        moves = [moves.split('{')[0].strip() for moves in pgn]
        move_times = [moves.split('{')[-1] for moves in pgn]
        move_times = [move_times.split(' ')[-1].strip(']') for move_times in move_times]

        moves_list = [move.split(' ')[-1] for move in moves]
        move_times_list = [move.split(' ')[-1] for move in move_times]

        move_times = ','.join(move_times_list[:-1])
        moves = ','.join(moves_list[:-1])

        total_moves = len(moves_list) // 2

    row = {
        'game_id': game_id,
        'url': url,
        'time_class': time_class,
        'time_control': time_control,
        'is_rated': is_rated,
        'white_rating': white_rating,
        'black_rating': black_rating,
        'white_accuracy': white_accuracy,
        'black_accuracy': black_accuracy,
        'white_result': white_result,
        'black_result': black_result,
        'colour': colour,
        'opponent_id': opponent_id,
        'opponent_username': opponent_username,
        'opponent_country': opponent_country,
        'opponent_is_verified': opponent_is_verified,
        'opponent_status': opponent_status,
        'start_datetime': start_datetime,
        'end_datetime': end_datetime,
        'opening_code': opening_code,
        'opening_url': opening_url,
        'opening_name': opening_name,
        'total_moves': total_moves,
        'moves': moves,
        'move_times': move_times
    }
    
    df = pl.DataFrame(row).with_columns(
        pl.col('moves').str.split(','),
        pl.col('move_times').str.split(',')
    ).select(
        pl.col('game_id').cast(pl.Utf8),
        pl.col('url').cast(pl.Utf8),
        pl.col('time_class').cast(pl.Utf8),
        pl.col('time_control').cast(pl.Utf8),
        pl.col('is_rated').cast(pl.Boolean),
        pl.col('white_rating').cast(pl.Utf8),
        pl.col('black_rating').cast(pl.Utf8),
        pl.col('white_accuracy').cast(pl.Utf8),
        pl.col('black_accuracy').cast(pl.Utf8),
        pl.col('white_result').cast(pl.Utf8),
        pl.col('black_result').cast(pl.Utf8),
        pl.col('colour').cast(pl.Utf8),
        pl.col('opponent_id').cast(pl.Utf8),
        pl.col('opponent_username').cast(pl.Utf8),
        pl.col('opponent_country').cast(pl.Utf8),
        pl.col('opponent_is_verified').cast(pl.Boolean),
        pl.col('opponent_status').cast(pl.Utf8),
        pl.col('start_datetime').cast(pl.Utf8),
        pl.col('end_datetime').cast(pl.Utf8),
        pl.col('opening_code').cast(pl.Utf8),
        pl.col('opening_url').cast(pl.Utf8),
        pl.col('opening_name').cast(pl.Utf8),
        pl.col('total_moves').cast(pl.Utf8),
        pl.col('moves').cast(pl.List(pl.Utf8)),
        pl.col('move_times').cast(pl.List(pl.Utf8)),
        pl.lit(datetime.now()).alias("_extracted_at")
    )
    
    return df

BIGQUERY_TABLE_JOB_CONFIG = LoadJobConfig(
    schema=[
        # SchemaField("name", "field_type", "mode", "default_value_expression", "description")
        SchemaField("game_id", "STRING", "Required", None, "uuid provided by chess.com"),
        SchemaField("url", "STRING", "NULLABLE", None, "game url on chess.com"),
        SchemaField("time_class", "STRING", "NULLABLE", None, "time class of the game"),
        SchemaField("time_control", "STRING", "NULLABLE", None, "time control of the game"),
        SchemaField("is_rated", "BOOLEAN", "NULLABLE", None, "whether the game is rated or not"),
        SchemaField("white_rating", "INTEGER", "NULLABLE", None, "white player's rating"),
        SchemaField("black_rating", "INTEGER", "NULLABLE", None, "black player's rating"),
        SchemaField("white_accuracy", "FLOAT", "NULLABLE", None, "white player's accuracy"),
        SchemaField("black_accuracy", "FLOAT", "NULLABLE", None, "black player's accuracy"),
        SchemaField("white_result", "STRING", "NULLABLE", None, "white player's result"),
        SchemaField("black_result", "STRING", "NULLABLE", None, "black player's result"),
        SchemaField("colour", "STRING", "NULLABLE", None, "colour of the player"),
        SchemaField("opponent_id", "INTEGER", "NULLABLE", None, "opponent's ID"),
        SchemaField("opponent_username", "STRING", "NULLABLE", None, "opponent's username"),
        SchemaField("opponent_country", "STRING", "NULLABLE", None, "opponent's country"),
        SchemaField("opponent_is_verified", "BOOLEAN", "NULLABLE", None, "whether the opponent is verified or not"),
        SchemaField("opponent_status", "STRING", "NULLABLE", None, "opponent's status"),
        SchemaField("start_datetime", "STRING", "NULLABLE", None, "start datetime of the game in UTC"),
        SchemaField("end_datetime", "STRING", "NULLABLE", None, "end datetime of the game in UTC"),
        SchemaField("opening_code", "STRING", "NULLABLE", None, "opening code of the game"),
        SchemaField("opening_name", "STRING", "NULLABLE", None, "opening name of the game"),
        SchemaField("opening_url", "STRING", "NULLABLE", None, "url for the opening"),
        SchemaField("total_moves", "INTEGER", "NULLABLE", None, "total moves in the game"),
        SchemaField("moves", "STRING", "REPEATED", None, "moves of the game"),
        SchemaField("move_times", "STRING", "REPEATED", None, "move times of the game"),
        SchemaField("_extracted_at", "DATETIME", "NULLABLE", None, "datetime when the data was extracted")
    ],
    source_format=SourceFormat.NEWLINE_DELIMITED_JSON,
    write_disposition=WriteDisposition.WRITE_APPEND,
    time_partitioning=TimePartitioning(
        type_=TimePartitioningType.MONTH
    ),
    schema_update_options=[
        SchemaUpdateOption.ALLOW_FIELD_RELAXATION
    ]
)

bigquery_view_query = """
  select
    fct_game.game_sid,
    dim_game.colour,
    dim_game.source,
    dim_game.start_date_actual,
    dim_game.start_time_actual,
    dim_game.end_date_actual,
    dim_game.end_time_actual,
    dim_date.day_name,
    dim_date.month_name,
    dim_time.time_control,
    dim_time.time_class,
    dim_time.is_increment,
    dim_opponent.country as opponent_country,
    dim_opening.opening_name,
    dim_opening.opening_variation,
    dim_opening.white_first_move,
    dim_opening.black_first_move,
    dim_result.result,
    dim_result.result_method,
    fct_game.game_length,
    fct_game.move_number_reached,
    fct_game.total_moves,
    fct_game.my_rating,
    fct_game.opponent_rating,
    fct_game.my_accuracy,
    fct_game.opponent_accuracy

  from `{dataset}.fct_game` as fct_game

  left join `{dataset}.dim_game` as dim_game
    on dim_game.game_sid = fct_game.game_sid

  left join `{dataset}.dim_opening` as dim_opening
    on dim_opening.opening_sid = fct_game.opening_sid

  left join `{dataset}.dim_opponent` as dim_opponent
    on dim_opponent.opponent_sid = fct_game.opponent_sid

  left join `{dataset}.dim_result` as dim_result
    on dim_result.result_sid = fct_game.result_sid

  left join `{dataset}.dim_time_control` as dim_time
    on dim_time.time_control_sid = fct_game.time_control_sid

  left join `{dataset}.dim_date` as dim_date
    on dim_date.date_id between dim_game.start_date_actual and dim_game.end_date_actual

  where
    dim_game.is_rated = TRUE
    and dim_date.month = if({month} = 1, 12, {month} - 1)
    and dim_date.year = if({month} = 1, {year} - 1, {year})
"""

def store_service_account_key(context):
    # Retrieve the Base64-encoded key from the environment variable
    encoded_key = os.getenv("GCP_CREDS")
    if not encoded_key:
        context.log.error("GCP_CREDS environment variable is not set.")
        raise ValueError("GCP_CREDS environment variable is not set.")
    
    # Decode the Base64-encoded service account key
    decoded_key = base64.b64decode(encoded_key)

    # Create a temporary file to store the decoded JSON key
    with tempfile.NamedTemporaryFile(delete=False, mode='wb', suffix='.json') as temp_file:
        temp_file.write(decoded_key)
        temp_file_path = temp_file.name
    
    # Log the file path for debugging (can be removed later for security reasons)
    context.log.info(f"Service account key saved to temporary file: {temp_file_path}")
    
    return temp_file_path
