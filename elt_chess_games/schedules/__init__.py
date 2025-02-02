from dagster import ScheduleDefinition, build_schedule_from_partitioned_job
from ..jobs import monthly_el_update_job

monthly_update_schedule = build_schedule_from_partitioned_job(
    job=monthly_el_update_job,
    cron_schedule="0 0 1 * *", # every 1st of the month at midnight
)