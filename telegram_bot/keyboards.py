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
            [
                InlineKeyboardButton(
                    text="Коллекции 📚",
                    callback_data="collections_menu",
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


def collections_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔎 Поиск",
                    callback_data="collections_search_menu",
                ),
                InlineKeyboardButton(
                    text="➕ Создать",
                    callback_data="collections_add_menu",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="💾 Сохраненные",
                    callback_data="collections_saved_menu",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔙 В меню",
                    callback_data="back_to_menu",
                )
            ],
        ]
    )


def collections_search_methods() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Поиск по ID",
                    callback_data="collections_search_by_id",
                ),
                InlineKeyboardButton(
                    text="Поиск по названию",
                    callback_data="collections_search_by_name",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="back_to_collections_menu",
                ),
            ],
        ]
    )


def collections_search_by_id() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Поиск по названию",
                    callback_data="collections_search_by_name",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="back_to_collections_menu",
                ),
            ],
        ]
    )


def collections_data_menu(collection_id: str, is_owner: bool) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="📋 Слова",
                callback_data=f"collections_words_{collection_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🧠 Тренировка",
                callback_data=f"collections_training_{collection_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data="back_to_collections_menu",
            ),
        ],
    ]
    if is_owner:
        keyboard[0].append(
            InlineKeyboardButton(
                text="✏️ Редактировать",
                callback_data=f"collections_edit_{collection_id}",
            ),
        )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def collections_data_words(collection_id: str, is_owner: bool) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data=f"back_to_collections_data_{collection_id}",
            ),
        ]
    ]
    if is_owner:
        keyboard.insert(
            0,
            [
                InlineKeyboardButton(
                    text="✏️ Редактировать",
                    callback_data=f"collections_edit_{collection_id}",
                ),
            ],
        )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def back_collections_edit_menu(collection_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data=f"collections_edit_{collection_id}",
                ),
            ]
        ]
    )


def collections_edit_menu(collection_id: str, words_list: list) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="➕ Слово",
                callback_data=f"collections_add_word_{collection_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🗑️ Удалить коллекцию",
                callback_data=f"collections_delete_{collection_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data=f"back_to_collections_data_{collection_id}",
            ),
        ],
    ]
    if words_list:
        keyboard[0].append(
            InlineKeyboardButton(
                text="➖ Слово",
                callback_data=f"collections_remove_word_{collection_id}",
            )
        )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def collections_add_new_word(
    id: str, collection_id: str, add_existing: bool = True
) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="🖊️ Свой перевод",
                callback_data=(
                    f"coll_existing_custom_translation_{id}"
                    if add_existing
                    else f"coll_new_custom_translation_{id}"
                ),
            ),
        ],
        [
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data=f"collections_edit_{collection_id}",
            ),
        ],
    ]
    if add_existing:
        keyboard[0].insert(
            0,
            InlineKeyboardButton(
                text="➕ Добавить", callback_data=f"coll_add_existing_{id}"
            ),
        )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def collections_add_multiple_words(
    data: list[dict], collection_id: str
) -> InlineKeyboardMarkup:
    keyboard = []
    for word in data:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=word.get("label", ""),
                    callback_data="coll_add_multiple_" + word.get("id", ""),
                ),
            ]
        )
    keyboard.append(
        [
            InlineKeyboardButton(
                text="🖊️ Свой перевод",
                callback_data="coll_multiple_custom_translation",
            ),
        ],
    )
    keyboard.append(
        [
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data=f"collections_edit_{collection_id}",
            ),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_collection_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="collections_menu",
                )
            ]
        ]
    )


def new_created_collection_menu(collection_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📂 Открыть коллекцию",
                    callback_data=f"open_collection_by_id_{collection_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад",
                    callback_data="collections_menu",
                )
            ],
        ]
    )
