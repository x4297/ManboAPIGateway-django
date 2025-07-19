import os

from celery import Celery
from celery.schedules import crontab

from . import private_settings


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ManboAPIGateway.settings")

app = Celery("ManboAPIGateway")

app.conf.broker_url = private_settings.CELERY_BROKER_URL  # type: ignore
app.conf.result_backend = private_settings.CELERY_RESULT_BACKEND  # type: ignore
app.conf.enable_utc = False

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "sync_up_user": {
        "task": "upstream_api.tasks.sync_up_user",
        "schedule": crontab(minute=0, hour=1)
    }
}
