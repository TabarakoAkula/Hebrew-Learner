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
        "title": "🔙 В меню",
        "callback": "back_to_menu",
    },
]


def get_imperative_button(word: str) -> dict:
    return {
        "title": "➕ Повелительное наклонение",
        "callback": f"get_imperative_{word}",
    }


def get_passive_button(word: str) -> dict:
    return {
        "title": "➕ Страдательный залог",
        "callback": f"get_passive_{word}",
    }


def manager_analyze_word(data: dict) -> None:
    if USE_CELERY:
        return celery_analyze_word.delay(data, data.get("link", ""))
    return celery_analyze_word(data, data.get("link", ""))


@shared_task()
def celery_analyze_word(data: dict, link="") -> None:
    message_text = "💫 Загрузка схемы"
    if data["new"]:
        message_text = "🎉 Это слово введено в первый раз\n\n" + message_text
    if not data.get("message_id"):
        message = manager_send_message(
            {
                "telegram_id": data["telegram_id"],
                "data": {"message": message_text, "inline_reply_markup": []},
            },
            use_celery=False,
        )
    answer_text = "an error"
    reply_markup = []
    word_links = {"link": "/ru/dict/" + link}
    word = None
    if not link:
        word_links = parse_pealim.get_word_page(data["word"])
        word = Word.objects.get(hebrew_word=data["word"])
    if (isinstance(word_links, list) and len(word_links) == 1) or link:
        if not link and word:
            word_links = word_links[0]
            word.pealim_link = BASE_PEALIM_LINK + word_links["link"]
        analysis = parse_pealim.get_word(word_links["link"])
        if not link and word:
            word.data = analysis
            word.analyzed = True
            word.save()
        hebrew_link = analysis["link"]
        if analysis["type"] == "verb":
            answer_text = utils.verb_create_words_form_message(
                analysis,
                data.get("imperative", False),
                data.get("passive", False),
            )
            if (
                answer_text["imperative_mode"]
                and answer_text["passive_voice"]
                and not data.get("imperative", False)
                and not data.get("passive", False)
            ):
                reply_markup.append(
                    [
                        get_imperative_button(hebrew_link),
                        get_passive_button(hebrew_link),
                    ]
                )
            elif answer_text["imperative_mode"] and not data.get("imperative", False):
                reply_markup.append([get_imperative_button(hebrew_link)])
            elif answer_text["passive_voice"] and not data.get("passive", False):
                reply_markup.append([get_passive_button(hebrew_link)])
        elif analysis["type"] in ["noun", "adj"]:
            answer_text = utils.noun_create_words_form_message(analysis)
        elif analysis["type"] in ["adv", "union", "pronoun", "interjection"]:
            answer_text = utils.basic_create_words_from_message(analysis)
        elif analysis["type"] == "pretext":
            answer_text = utils.pretext_create_words_form_message(analysis)
        else:
            answer_text = {"text": "Тип речи не определен"}

    elif isinstance(word_links, list):
        word.multiply = True
        word.new = True
        word.analyzed = True
        word.data = word_links
        word.save()
        answer_text = utils.get_many_results_message(word_links)
        for i in answer_text["buttons"]:
            reply_markup.append(
                [{"title": i["label"], "callback": "get_by_link_" + i["link"]}]
            )
    elif not word_links:
        answer_text = {"text": "Не удалось ничего найти"}
    return asyncio.run(
        edit_message(
            data["telegram_id"],
            {
                "message": utils.normalize_text(answer_text["text"]),
                "message_id": (
                    data["message_id"] if data.get("message_id") else message.message_id
                ),
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
