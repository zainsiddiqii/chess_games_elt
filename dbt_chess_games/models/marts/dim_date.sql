with

dates_series as (
  select *
  from
    unnest(
      generate_date_array('2020-01-01', '2030-01-01', interval 1 day)
    ) as d
),

dim_date as (
  select
    d                                     as date_id,
    cast(format_date('%Q', d) as integer) as quarter,
    cast(format_date('%w', d) as integer) as week_day,
    extract(year from d)                  as year,
    extract(week from d)
      as year_week,
    extract(day from d)
      as month_day,
    extract(dayofyear from d)             as year_day,
    extract(month from d)                 as month,
    format_date('%B', d)
      as month_name,
    format_date('%A', d)                  as day_name,
    coalesce (format_date('%A', d) in ('Sunday', 'Saturday'),
    false)                                as day_is_weekend

  from dates_series
)

select * from dim_date
