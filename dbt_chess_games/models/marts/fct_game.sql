with

joining_dims as (
  select
    cols.game_id,
    dim_game.game_sid,
    dim_opening.opening_sid,
    dim_opponent.opponent_sid,
    dim_result.result_sid,
    dim_time_control.time_control_sid,
    cols.my_rating,
    cols.opponent_rating,
    cols.my_accuracy,
    cols.opponent_accuracy,
    cols.move_number_reached,
    cols.total_moves,
    datetime_diff(
      cols.end_timestamp_utc,
      cols.start_timestamp_utc,
      second
    )                  as game_length,
    lead(cols.my_rating, 1) over (
      partition by cols.source
      order by cols.start_timestamp_utc
    ) - cols.my_rating as rating_change

  from {{ ref("int_game_information") }} as cols

  left join {{ ref("dim_game") }} as dim_game
    on cols.game_id = dim_game.game_id

  left join {{ ref("dim_opening") }} as dim_opening
    on dim_opening.opening_name
    = trim(split(cols.opening_name, ':')[safe_offset(0)])
    and coalesce(dim_opening.opening_variation, '')
    = coalesce(trim(split(cols.opening_name, ':')[safe_offset(1)]), '')
    and dim_opening.white_first_move
    = cols.moves[safe_offset(0)]
    and dim_opening.black_first_move
    = cols.moves[safe_offset(1)]

  left join {{ ref("dim_opponent") }} as dim_opponent
    on cols.opponent_id = dim_opponent.opponent_id

  left join {{ ref("dim_result") }} as dim_result
    on cols.my_result = dim_result.result
    and cols.result_method = dim_result.result_method

  left join {{ ref("dim_time_control") }} as dim_time_control
    on cols.time_control = dim_time_control.time_control
),

fct_game as (
  select
    game_sid,
    opening_sid,
    time_control_sid,
    opponent_sid,
    result_sid,
    my_rating,
    opponent_rating,
    my_accuracy,
    opponent_accuracy,
    move_number_reached,
    total_moves,
    game_length,
    rating_change

  from joining_dims
)

select * from fct_game
