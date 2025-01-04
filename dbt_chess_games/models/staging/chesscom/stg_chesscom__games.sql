{% set my_opponent_columns = ["accuracy", "rating"] %}
{% set my_or_opponent = ["my", "opponent"] %}

with games as (

  select
    game_id,
    url as game_url,
    is_rated,
    -- create my_accuracy, opponent_accuracy, my_rating, opponent_rating
    {{ map_white_black_to_my_opponent(my_opponent_columns, my_or_opponent) }}
    colour,
    opponent_id,
    opponent_username,
    opponent_country,
    opponent_is_verified,
    opponent_status,
    total_moves as move_number_reached,
    array_length(moves) as total_moves,
    moves

  from {{ source("dagster", "bigquery_raw_games_chesscom") }}

)

select * from games
