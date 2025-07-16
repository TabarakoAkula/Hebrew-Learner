import asyncio
import html

from apps.words.notifier import edit_message, logs_snitch, send_message
from apps.words.utils import parse_pealim, parse_iris, utils
from apps.words.models import Word
from celery import shared_task
from django.conf import settings

USE_CELERY = settings.USE_CELERY
BASE_PEALIM_LINK = "https://www.pealim.com"


def manager_analyze_word(data: dict) -> None:
    if USE_CELERY:
        return celery_analyze_word.delay(data)
    return celery_analyze_word(data)


@shared_task()
def celery_analyze_word(data: dict) -> None:
    message = manager_send_message(
        {
            "telegram_id": data["telegram_id"],
            "data": {"message": "Wait", "inline_reply_markup": []}
        },
        use_celery=False,
    )
    word = Word.objects.get(hebrew_word=data["word"])
    word_links = parse_pealim.get_word_page(data["word"])
    answer_text = "an error"
    if isinstance(word_links, dict):
        word.pealim_link = BASE_PEALIM_LINK + word_links["link"]
        analysis = parse_pealim.get_word(word_links["link"])
        word.data = analysis

        # word.analyzed = True # ONLY FOR DEV

        word.save()
        answer_text = utils.create_words_form_message(analysis)
    elif isinstance(word_links, list):
        answer_text = "найдено несколько слов"
    elif not word_links:
        answer_text = "not found"

    return asyncio.run(
        edit_message(
            data["telegram_id"],
            {
                "message": utils.normalize_text(answer_text),
                "message_id": message.message_id,
                "inline_reply_markup": [
                    [
                        {
                            "title": "Search in IRIS",
                            "callback": "ask_question",
                        },
                        {
                            "title": "🔙 В меню",
                            "callback": "back_to_menu",
                        },
                    ],
                ],
            },
        ),
    )


def manager_send_message(data: dict, use_celery=True):
    if USE_CELERY and use_celery:
        return celery_send_message.delay(data).get()
    return celery_send_message(data)


@shared_task
def celery_send_message(data: dict):
    return asyncio.run(send_message(data["telegram_id"], data["data"]))
