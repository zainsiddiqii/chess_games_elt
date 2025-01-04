with

unique_openings as (
  select distinct
    split(opening_name, ':') as split_opening,
    moves[safe_offset(0)]    as white_first_move,
    moves[safe_offset(1)]    as black_first_move

  from {{ ref("int_game_information") }}
),

transformations_and_id as (
  select
    white_first_move,
    black_first_move,
    generate_uuid()                     as opening_sid,
    trim(split_opening[safe_offset(0)]) as opening_name,
    trim(split_opening[safe_offset(1)]) as opening_variation

  from unique_openings
),

dim_games as (
  select
    opening_sid,
    opening_name,
    opening_variation,
    white_first_move,
    black_first_move

  from transformations_and_id
)

select * from dim_games
