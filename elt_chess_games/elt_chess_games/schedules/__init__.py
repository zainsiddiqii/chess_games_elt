from dagster import ScheduleDefinition
from ..jobs import monthly_el_update_job

monthly_update_schedule = ScheduleDefinition(
    job=monthly_el_update_job,
    cron_schedule="0 0 1 * *", # every 1st of the month at midnight
)