with

move_times_parsed as (
  select
    game_id,
    array(
      select
        coalesce(
          safe.parse_time(
            '%M:%E1S',
            concat(
              -- times given as hh:mm:ss
              split(move_time, ':')[safe_offset(1)],
              ':',
              split(move_time, ':')[safe_offset(2)]
            )
          ),
          '00:00:00'
        )
      from unnest(move_times) as move_time
    )                         as move_times

  from {{ source("dagster", "bigquery_raw_games_chesscom") }}
)

select * from move_times_parsed
