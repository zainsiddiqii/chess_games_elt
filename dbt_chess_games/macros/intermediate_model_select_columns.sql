{% macro get_intermediate_model(platform) %}

    select
        games.game_id,
        games.game_url,
        start_end_timestamps.start_timestamp_utc,
        start_end_timestamps.start_datetime_actual,
        start_end_timestamps.end_timestamp_utc,
        start_end_timestamps.end_datetime_actual,
        games.is_rated,
        time_class_control.time_class,
        time_class_control.time_control,
        time_class_control.minutes,
        time_class_control.seconds,
        time_class_control.is_increment,
        time_class_control.increment_amount,
        openings.opening_code,
        openings.opening_name,
        games.colour,
        games.my_rating,
        games.opponent_rating,
        cast(games.opponent_id as string) as opponent_id,
        games.opponent_username,
        games.opponent_country,
        games.opponent_is_verified,
        games.opponent_status,
        games.my_accuracy,
        games.opponent_accuracy,
        games.move_number_reached,
        games.total_moves,
        games.moves,
        move_times.move_times,
        results.my_result,
        results.opponent_result,
        results.result_method,
        '{{ platform }}' as source

    from {{ ref('stg_' ~ platform ~ '__games') }} as games

    inner join {{ ref('stg_' ~ platform ~ '__start_end_timestamps') }} as start_end_timestamps
        on games.game_id = start_end_timestamps.game_id

    inner join {{ ref('stg_' ~ platform ~ '__time_class_control') }} as time_class_control
        on games.game_id = time_class_control.game_id

    inner join {{ ref('stg_' ~ platform ~ '__openings') }} as openings
        on games.game_id = openings.game_id

    inner join {{ ref('stg_' ~ platform ~ '__move_times') }} as move_times
        on games.game_id = move_times.game_id

    inner join {{ ref('stg_' ~ platform ~ '__results') }} as results
        on games.game_id = results.game_id

{% endmacro %}
