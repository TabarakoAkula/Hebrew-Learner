import asyncio

from apps.words.models import Word
from apps.words.notifier import edit_message, send_message
from apps.words.utils import parse_pealim, utils
from celery import shared_task
from django.conf import settings

USE_CELERY = settings.USE_CELERY
BASE_PEALIM_LINK = "https://www.pealim.com"
DEFAULT_BUTTONS = [
    {
        "title": "Search in IRIS",
        "callback": "ask_question",
    },
    {
        "title": "🔙 В меню",
        "callback": "back_to_menu",
    },
]


def get_imperative_button(word: str) -> dict:
    return {"title": "➕ Повелительное наклонение", "callback": f"get_imperative_{word}"},


def get_passive_button(word: str) -> dict:
    return {"title": "➕ Страдательный залог", "callback": f"get_passive_{word}"}


def manager_analyze_word(data: dict) -> None:
    if USE_CELERY:
        return celery_analyze_word.delay(data)
    return celery_analyze_word(data)


@shared_task()
def celery_analyze_word(data: dict) -> None:
    message = manager_send_message(
        {
            "telegram_id": data["telegram_id"],
            "data": {"message": "Wait", "inline_reply_markup": []},
        },
        use_celery=False,
    )

    reply_markup = []

    word = Word.objects.get(hebrew_word=data["word"])
    word_links = parse_pealim.get_word_page(data["word"])
    answer_text = "an error"
    if isinstance(word_links, list) and len(word_links) == 1:
        word_links = word_links[0]
        word.pealim_link = BASE_PEALIM_LINK + word_links["link"]
        analysis = parse_pealim.get_word(word_links["link"])
        word.data = analysis

        # word.analyzed = True # ONLY FOR DEV

        word.save()
        if analysis["type"] == "verb":
            answer_text = utils.verb_create_words_form_message(analysis)
            if answer_text["imperative_mode"] and answer_text["passive_voice"]:
                reply_markup.append(get_imperative_button(word.hebrew_word))
                reply_markup.append(get_passive_button(word.hebrew_word))
            elif answer_text["imperative_mode"]:
                reply_markup.append(get_imperative_button(word.hebrew_word))
            elif answer_text["passive_voice"]:
                reply_markup.append(get_passive_button(word.hebrew_word))
        elif analysis["type"] in ["noun", "adj"]:
            answer_text = utils.noun_create_words_form_message(analysis)
        elif analysis["type"] in ["adv", "union", "pronoun", "interjection"]:
            answer_text = utils.basic_create_words_from_message(analysis)
        elif analysis["type"] == "pretext":
            answer_text = utils.pretext_create_words_form_message(analysis)
        else:
            answer_text = {"text": "Тип речи не определен"}

    elif isinstance(word_links, list):
            answer_text = {"text": "Найдено несколько результатов"}
    elif not word_links:
            answer_text = {"text": "Не удалось ничего найти"}
    return asyncio.run(
        edit_message(
            data["telegram_id"],
            {
                "message": utils.normalize_text(answer_text["text"]),
                "message_id": int(message.message_id),
                "inline_reply_markup": [*reply_markup, DEFAULT_BUTTONS],
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
