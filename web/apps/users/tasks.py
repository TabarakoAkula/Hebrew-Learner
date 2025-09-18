import asyncio

from apps.users.notifier import send_report
from apps.users.utils import get_report_answer_keyboard, get_report_keyboard
from apps.words.notifier import send_message
from celery import shared_task
from django.conf import settings

USE_CELERY = settings.USE_CELERY


def manager_send_report(data: dict):
    if USE_CELERY:
        return celery_send_report.delay(data)
    return celery_send_report(data)


@shared_task
def celery_send_report(data: dict):
    data[
        "message"
    ] = f"""📍 New report\n
Telegram id: {data['telegram_id']}
Telegram username: {data['telegram_username']}\n\n{data['message']}"""
    data["inline_reply_markup"] = get_report_keyboard(data["telegram_id"])
    return asyncio.run(send_report(data))


def manager_answer_report(data: dict):
    if USE_CELERY:
        return celery_answer_report.delay(data)
    return celery_answer_report(data)


@shared_task
def celery_answer_report(data: dict):
    data["inline_reply_markup"] = get_report_answer_keyboard()
    return asyncio.run(send_message(data["telegram_id"], data))
