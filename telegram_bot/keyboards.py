from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def keyboard_example() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Поиск 🔎",
                    callback_data="search_menu",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Словарь 📖",
                    callback_data="dictionary_menu",
                ),
            ],
        ]
    )
