import asyncio
import os

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
import dotenv
import requests
import word_formatter

dotenv.load_dotenv()

DOCKER_URL = os.getenv("DOCKER_URL")
API_KEY = os.getenv("API_KEY")

DEFAULT_BUTTONS = [
    InlineKeyboardButton(
        text="🔙 В меню",
        callback_data="back_to_menu",
    ),
]


def check_success(function_name):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            if isinstance(result, dict) and result.get("success") is False:
                print(
                    f"Error at {function_name} function. "
                    f"Message: {result.get('message')}. "
                    f"Data: {result.get('data')}"
                )
            return result

        return wrapper

    return decorator


def get_imperative_button(word: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text="➕ Повелительное наклонение",
        callback_data=f"get_imperative_{word}",
    )


def get_passive_button(word: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text="➕ Страдательный залог",
        callback_data=f"get_passive_{word}",
    )


async def simple_post_request(data: dict) -> None:
    telegram_id = data["telegram_id"]
    await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + f"users/{telegram_id}",
        json=data,
        headers={"x-api-key": API_KEY},
    )


@check_success("get_or_create_user")
async def get_or_create_user(telegram_id: int, data: dict) -> None:
    response = await asyncio.to_thread(
        requests.post,
        url=DOCKER_URL + f"users/{telegram_id}",
        headers={"x-api-key": API_KEY},
        params=data,
    )
    return response.json()


@check_success("get_or_add_word")
async def get_or_add_word(data: dict) -> None:
    response = await asyncio.to_thread(
        requests.get,
        url=DOCKER_URL + "storage/words",
        headers={"x-api-key": API_KEY},
        params=data,
    )
    return response.json()


@check_success("get_by_link")
async def get_by_link(data: dict) -> None:
    response = await asyncio.to_thread(
        requests.get,
        url=DOCKER_URL + "storage/words/by-link",
        headers={"x-api-key": API_KEY},
        params=data,
    )
    return response.json()


async def get_word_formatting(
    data: dict, imperative: bool = False, passive: bool = False
) -> dict:
    await asyncio.sleep(0)
    reply_markup = []
    type = data["data"]["type"]
    if type == "verb":
        answer_text = word_formatter.verb_create_words_form_message(
            data["data"], imperative, passive
        )
        if (
            answer_text["imperative_mode"]
            and answer_text["passive_voice"]
            and not passive
            and not imperative
        ):
            reply_markup.append(
                [
                    get_imperative_button(data["data"]["link"]),
                    get_passive_button(data["data"]["link"]),
                ]
            )
        elif answer_text["imperative_mode"] and not imperative:
            reply_markup.append([get_imperative_button(data["data"]["link"])])
        elif answer_text["passive_voice"] and not passive:
            reply_markup.append([get_passive_button(data["data"]["link"])])
    elif type in ["noun", "adj"]:
        answer_text = word_formatter.noun_create_words_form_message(data["data"])
    elif type in ["adv", "union", "pronoun", "interjection"]:
        answer_text = word_formatter.basic_create_words_from_message(data["data"])
    elif type == "pretext":
        answer_text = word_formatter.pretext_create_words_form_message(data["data"])
    else:
        answer_text = "Неизвестная ошибка"
    return {
        "text": answer_text["text"],
        "keyboard": InlineKeyboardMarkup(
            inline_keyboard=[*reply_markup, DEFAULT_BUTTONS]
        ),
    }
