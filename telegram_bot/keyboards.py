from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


def keyboard_example() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="button 1",
                    callback_data="button1",
                ),
                InlineKeyboardButton(
                    text="button 2",
                    callback_data="button2",
                ),
            ],
        ]
    )
