import asyncio

from apps.words.notifier import logs_snitch
from celery import shared_task
from django.conf import settings

USE_CELERY = settings.USE_CELERY


def manager_snitch_logs(data: dict):
    if USE_CELERY:
        return celery_snitch_logs.delay(data)
    return celery_snitch_logs(data)


@shared_task
def celery_snitch_logs(data: dict):
    message = f"""📍 New report\n
    Telegram id: {data['telegram_id']}
    Telegram username: {data['telegram_username']}\n\n{data['message']}"""
    return asyncio.run(logs_snitch(message))
