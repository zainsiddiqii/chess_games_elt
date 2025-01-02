with

unique_time_formats as (
  select distinct
    time_class,
    time_control,
    minutes,
    seconds,
    is_increment,
    increment_amount

  from {{ ref("int_game_information") }}
),

generate_id as (
  select
    *,
    generate_uuid() as time_control_sid

  from unique_time_formats
),

dim_time_control as (
  select
    time_control_sid,
    time_control,
    time_class,
    minutes,
    seconds,
    is_increment,
    increment_amount

  from generate_id
)

select * from dim_time_control
