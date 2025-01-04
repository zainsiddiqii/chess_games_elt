with chesscom_game_info as (
  {{ get_intermediate_model("chesscom") }}
)

select * from chesscom_game_info
where
  result_method is not null
  and total_moves >= 2
