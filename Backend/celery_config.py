from celery.schedules import crontab

broker_url = "redis://localhost:6379/0"
result_backend = "redis://localhost:6379/1"
timezone = "Asia/Kolkata"
enable_utc = False
broker_connection_retry_on_startup = True

imports = ("application.tasks",)

beat_schedule = {
    "send-monthly-doctor-report-every-2-minutes-dev": {
        "task": "monthly_doctor_report",  
        "schedule": crontab(minute='*/2'),  # runs every 2 minutes
        #1st of every month at 10am (enable the filters in tasks.py)
        #"schedule": crontab(day_of_month=1, hour=10, minute=0),
    },
    
    "send-daily-appointment-reminders": {
        "task": "daily_appointment_reminder",
        "schedule": crontab(minute='*/2')  # run every day at 10AM
    }
}