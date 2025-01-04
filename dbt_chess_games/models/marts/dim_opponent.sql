with

unique_opponents as (
  select distinct
    opponent_id,
    opponent_username    as username,
    opponent_country     as country,
    opponent_status      as status,
    opponent_is_verified as is_verified

  from {{ ref("int_game_information") }}
),

generate_id as (
  select
    *,
    generate_uuid() as opponent_sid

  from unique_opponents
),

dim_opponent as (
  select
    opponent_sid,
    opponent_id,
    username,
    country,
    status,
    is_verified

  from generate_id
)

select * from dim_opponent
