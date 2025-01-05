with

openings as (
  select
    game_id,
    opening_code,
    opening_name,
    opening_url

  from {{ source("chesscom", "raw_games_chesscom") }}

  where
    -- 1st letter alphabet, 2nd letter digit
    regexp_contains(
      left(opening_code, 2),
      r'^[A-Z][0-9]'
    )
)

select * from openings
