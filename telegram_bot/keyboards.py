from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Поиск 🔎",
                    callback_data="search_menu",
                ),
            ],
        ]
    )


def return_to_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙 В меню",
                    callback_data="back_to_menu",
                )
            ]
        ]
    )
