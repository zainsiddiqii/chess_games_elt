with

unique_games as (
  select
    game_id,
    game_url,
    source,
    is_rated,
    colour,
    date(start_timestamp_utc)   as start_date_utc,
    date(start_datetime_actual) as start_date_actual,
    time(start_timestamp_utc)   as start_time_utc,
    time(start_datetime_actual) as start_time_actual,
    date(end_timestamp_utc)     as end_date_utc,
    date(end_datetime_actual)   as end_date_actual,
    time(end_timestamp_utc)     as end_time_utc,
    time(end_datetime_actual)   as end_time_actual

  from {{ ref("int_game_information") }}
),

generate_id as (
  select
    *,
    generate_uuid() as game_sid

  from unique_games
),

dim_game as (
  select
    game_sid,
    game_id,
    game_url,
    source,
    is_rated,
    start_date_utc,
    start_date_actual,
    start_time_utc,
    start_time_actual,
    end_date_utc,
    end_date_actual,
    end_time_utc,
    end_time_actual,
    colour

  from generate_id
)

select * from dim_game
