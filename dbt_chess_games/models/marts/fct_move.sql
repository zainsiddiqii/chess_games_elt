with still_arrays as (
  select
    game_id,
    colour as my_colour,
    moves,
    move_times,
    increment_amount,
    minutes

  from {{ ref("int_game_information") }}
),

moves_flattened as (
  select
    game_id,
    moves_flat,
    number,
    my_colour,
    increment_amount,
    minutes

  from still_arrays
  cross join
    unnest(still_arrays.moves) as moves_flat
    with offset as number
),

move_times_flattened as (
  select
    game_id,
    move_times_flat,
    number

  from still_arrays
  cross join
    unnest(still_arrays.move_times) as move_times_flat
    with offset as number
),

flattened as (
  select
    moves.game_id,
    moves.moves_flat           as move,
    move_times.move_times_flat as move_ts,
    moves.my_colour,

    moves.increment_amount,
    moves.minutes,
    moves.number + 1           as number

  from moves_flattened as moves

  inner join move_times_flattened as move_times
    on moves.game_id = move_times.game_id
    and moves.number = move_times.number

),

colours_added as (
  select
    *,
    case
      when mod(flattened.number, 2) = 1
        then 'white'
      else 'black'
    end as move_colour

  from flattened
),

joins_and_mappings as (
  select
    *,
    coalesce(move_colour = my_colour, false) as is_my_move,
    row_number() over (
      partition by game_id, move_colour
      order by number
    )                                        as move_number,
    case
      when move like '%#'
        then 'checkmate'
      when move like '%+'
        then 'check'
      when move like '_x%'
        then 'capture'
      when move like 'O%'
        then 'castles'
      else 'move'
    end                                      as move_type

  from colours_added

  left join {{ ref("letter_to_piece_mapping") }} as lpc
    on lpc.letter = left(colours_added.move, 1)
),

final_transforms as (
  select
    *,
    lag(move_ts, 1)
      over (
        partition by game_id, move_colour
        order by number
      )
      as move_ts_previous,
    parse_time('%M:%S', concat(cast(minutes as string), ':00')) as start_time

  from joins_and_mappings
),

time_taken_calculated as (
  select
    *,
    generate_uuid()      as move_sid,
    time_diff(
      -- coalesce because first move time is calculated
      -- from the start time of the game
      coalesce(move_ts_previous, start_time),
      move_ts,
      second
    ) + increment_amount as time_taken

  from final_transforms
),

fct_move as (
  select
    final.move_sid,
    dim_game.game_sid,
    final.move_number,
    final.number as move_number_raw,
    final.move,
    final.is_my_move,
    final.move_colour,
    final.piece  as move_piece,
    final.move_type,
    final.move_ts,
    final.time_taken,
    final.increment_amount

  from time_taken_calculated as final

  left join {{ ref("dim_game") }} as dim_game
    on final.game_id = dim_game.game_id
)

select * from fct_move
order by game_sid, move_number_raw
