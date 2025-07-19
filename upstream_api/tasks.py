from celery import shared_task

from .synchronize import synchronize


@shared_task
def sync_up_user():
    synchronize()
