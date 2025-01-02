select
    total_moves

from {{ ref("fct_game") }}

where total_moves < 2