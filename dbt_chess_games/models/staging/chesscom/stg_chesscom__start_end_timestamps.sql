with

start_end_timestamps as (
  select
    game_id,
    safe.timestamp(
      end_datetime, 'UTC'
    ) as end_timestamp_utc,
    safe.timestamp(
      start_datetime, 'UTC'
    ) as start_timestamp_utc

  from {{ source("dagster", "bigquery_raw_games_chesscom") }}

  where
    safe.timestamp(start_datetime, 'UTC') is not null
    and safe.timestamp(end_datetime, 'UTC') is not null

),

all_timestamps as (
  select
    timestamps.game_id,
    timestamps.end_timestamp_utc,
    timestamps.start_timestamp_utc,
    datetime(timestamps.start_timestamp_utc, tzdb_timezone)
      as start_datetime_actual,
    datetime(timestamps.end_timestamp_utc, tzdb_timezone)
      as end_datetime_actual

  from start_end_timestamps as timestamps

  left join {{ ref("timezones") }} as timezones
    on timestamps.start_timestamp_utc
    between
    timestamp(
      timezones.datetime_start
    ) and
    timestamp(
      timezones.datetime_end
    )
    and timestamps.end_timestamp_utc
    between
    timestamp(
      timezones.datetime_start
    ) and
    timestamp(
      timezones.datetime_end
    )
)

select * from all_timestamps
