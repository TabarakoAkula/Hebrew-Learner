from datetime import datetime, timedelta, timezone
import os
import random

from aiogram import F, html, Router
import aiogram.exceptions
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
import dotenv
import keyboards
import states
import utils
import word_formatter

dotenv.load_dotenv()

router = Router()

SEARCH_FILTER = StateFilter(*states.SearchStatesGroup.__all_states__)
BOT_USERNAME = os.getenv("BOT_USERNAME", "")


@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    response = await utils.get_or_create_user(
        message.chat.id,
        {"telegram_username": message.chat.username},
    )
    if not response["success"]:
        return await message.answer(response["message"])
    argument = message.text.split()[-1]
    if argument.startswith("collection_"):
        collection_id = argument.split("_")[-1]
        return await collections_search_id_input_handler(
            message,
            state,
            collection_id=collection_id,
        )
    answer_message = "Привет, в этом боте ты можешь искать перевод слов с иврита"
    if response["data"]["New"]:
        answer_message = "Поздравляю с первым запуском🥳\n\n" + answer_message
    return await message.answer(answer_message, reply_markup=keyboards.main_menu())


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    return await start_handler(callback.message, state)


@router.callback_query(F.data == "search_menu")
async def search_menu_hanlder(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(states.SearchStatesGroup.menu)
    await callback.message.edit_text(
        "Введи слово для поиска:",
        reply_markup=keyboards.return_to_menu(),
    )


@router.message(SEARCH_FILTER)
async def search_result(message: Message, state: FSMContext):
    await state.set_state(states.SearchStatesGroup.result)
    if not utils.check_hebrew_letters(message.text):
        return await message.answer("❗️Введено слово не на иврите")
    response = await utils.get_or_add_word(
        {
            "telegram_id": message.chat.id,
            "word": utils.remove_nekudots(message.text),
        }
    )
    if not response["success"]:
        return await message.answer(response["message"])
    if not response["data"]["new"]:
        await state.update_data(data={"data": response["data"]})
        formatted_message = await utils.get_word_formatting(response["data"])
        await message.answer(
            formatted_message["text"],
            reply_markup=formatted_message["keyboard"],
            parse_mode="Markdown",
        )


@router.callback_query(F.data.startswith("get_imperative_"))
async def get_imperative_form(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    word_data = data.get("data")
    if not word_data:
        await utils.get_by_link(
            {
                "telegram_id": callback.message.chat.id,
                "link": callback.data.split("_")[-1],
                "message_id": callback.message.message_id,
                "imperative": True,
                "passive": False,
            }
        )
    else:
        if word_data.get("multiply"):
            return
        formatted_message = await utils.get_word_formatting(word_data, imperative=True)
        await callback.message.edit_text(
            formatted_message["text"],
            reply_markup=formatted_message["keyboard"],
            parse_mode="Markdown",
        )


@router.callback_query(F.data.startswith("get_passive_"))
async def get_passive_form(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    word_data = data.get("data")
    if not word_data:
        await utils.get_by_link(
            {
                "telegram_id": callback.message.chat.id,
                "link": callback.data.split("_")[-1],
                "message_id": callback.message.message_id,
                "imperative": False,
                "passive": True,
            }
        )
    else:
        if word_data.get("multiply"):
            return
        formatted_message = await utils.get_word_formatting(word_data, passive=True)
        await callback.message.edit_text(
            formatted_message["text"],
            reply_markup=formatted_message["keyboard"],
            parse_mode="Markdown",
        )


@router.callback_query(F.data.startswith("get_by_link_"))
async def get_by_link_form(callback: CallbackQuery, state: FSMContext):
    await state.set_data({})
    await utils.get_by_link(
        {
            "telegram_id": callback.message.chat.id,
            "link": callback.data[callback.data.find("_", 9) + 1 :].replace("_", "-")
            + "/",
            "message_id": callback.message.message_id,
            "imperative": False,
        }
    )


@router.callback_query(F.data.startswith("report"))
async def report_menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SendReportStatesGroup.input)
    await callback.message.answer(
        "📍 Напиши своё предложение ниже, оно будет отправлено разработчику",
        reply_markup=keyboards.return_to_menu(),
    )


@router.message(states.SendReportStatesGroup.input)
async def input_send_report_handler(message: Message, state: FSMContext):
    await state.clear()
    await utils.send_report(
        {
            "telegram_id": message.chat.id,
            "telegram_username": message.chat.username,
            "message": message.text,
        }
    )
    await message.answer(
        "✅ Сообщение успешно отправлено",
        reply_markup=keyboards.return_to_menu(),
    )


@router.callback_query(F.data.startswith("answer_report_"))
async def answer_report_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.AnswerReportStatesGroup.input)
    await state.update_data({"telegram_id": callback.data.split("_")[-1]})
    await callback.message.answer(
        " Введи ответ",
        reply_markup=keyboards.return_to_menu(),
    )


@router.message(states.AnswerReportStatesGroup.input)
async def input_answer_report_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    response = await utils.answer_report(
        {
            "telegram_id": data["telegram_id"],
            "answer": message.text,
        }
    )
    if not response["success"]:
        return await message.answer(response["message"])
    return await message.answer(
        "✅ Ответ успешно отправлен",
        reply_markup=keyboards.return_to_menu(),
    )


@router.callback_query(F.data == "collections_menu")
async def collections_menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Меню коллекций", reply_markup=keyboards.collections_menu()
    )


@router.callback_query(F.data == "collections_search_menu")
async def collections_search_menu_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Выбери метод поиска коллекции",
        reply_markup=keyboards.collections_search_methods(),
    )


@router.callback_query(F.data == "back_to_collections_menu")
async def back_to_collections_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    return await collections_menu_handler(callback, state)


@router.callback_query(F.data == "collections_search_by_id")
async def collections_search_id_menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.CollectionsSearchIdStatesGroup.input)
    await callback.message.edit_text(
        "Введи ID коллекции", reply_markup=keyboards.collections_search_by_id()
    )


@router.message(states.CollectionsSearchIdStatesGroup.input)
async def collections_search_id_input_handler(
    message: Message,
    state: FSMContext,
    collection_id: str = None,
):
    user_response = await utils.get_or_create_user(
        message.chat.id,
        {"telegram_id": message.chat.id},
    )
    user_data = user_response.get("data", {})
    new_message = False
    response = await state.get_data()
    if not response:
        new_message = True
        await state.clear()
        response = await utils.collections_search_by_id(
            {
                "collection_id": collection_id if collection_id else message.text,
            }
        )
    if response.get("id", None):
        collection_id = response["id"]
        is_owner = response.get("owner", "0") == str(message.chat.id)
        await state.update_data(response)
        name = response.get("name", "None")
        number_of_words = len(response.get("words", []))
        updated_at = datetime.fromisoformat(
            response.get("updated_at").replace("Z", "+00:00")
        )
        updated_at = updated_at.astimezone(timezone(timedelta(hours=3)))
        text = (
            f"Коллекция: {html.bold(name)}\n\n"
            f"Последнее обновление: {html.bold(updated_at.strftime('%d.%m.%Y %H:%M'))}\n"
            f"Количество слов: {html.bold(number_of_words)}"
        )
        user_collections = user_data.get("collections_saved", [])
        is_saved = bool(any([i["id"] == collection_id for i in user_collections]))
        if new_message and not collection_id:
            await message.answer(
                text=text,
                reply_markup=keyboards.collections_data_menu(
                    response.get("id", "0"),
                    is_owner,
                    is_saved,
                ),
            )
        else:
            try:
                await message.edit_text(
                    text=text,
                    reply_markup=keyboards.collections_data_menu(
                        response.get("id", "0"),
                        is_owner,
                        is_saved,
                    ),
                )
            except aiogram.exceptions.TelegramBadRequest:
                await message.answer(
                    text=text,
                    reply_markup=keyboards.collections_data_menu(
                        response.get("id", "0"),
                        is_owner,
                        is_saved,
                    ),
                )
    else:
        await message.answer(
            "Коллекция с таким ID не найдена",
            reply_markup=keyboards.collections_search_methods(),
        )


@router.callback_query(F.data.startswith("collections_words_"))
async def collections_data_words_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if str(data.get("id")) == callback.data.split("_")[-1]:
        is_owner = data.get("owner", "0") == str(callback.message.chat.id)
        words_data = data.get("words", {})
        words_list = [
            html.bold(words_data[word]["base_form"])
            + " - "
            + words_data[word]["translation"].capitalize()
            for word in words_data.keys()
        ]
        words = "\n".join(words_list)
        if not words_list:
            words = "В этой коллекции пока нет слов"
        words_text = (
            html.bold("Слова в коллекции ") + html.italic(data.get("name", "None")) + ":"
        )
        await callback.message.edit_text(
            text=f"{words_text}\n\n{words}",
            reply_markup=keyboards.collections_data_words(data.get("id", "0"), is_owner),
        )
    return


@router.callback_query(F.data.startswith("back_to_collections_data_"))
async def back_collections_data_words_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if str(data.get("id")) == callback.data.split("_")[-1]:
        await collections_search_id_input_handler(callback.message, state)
    else:
        await back_to_collections_menu(callback, state)


@router.callback_query(F.data.startswith("collections_edit_"))
async def collections_edit_menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.CollectionsEditStatesGroup.menu)
    data = await state.get_data()
    is_correct_collection = str(data.get("id")) == callback.data.split("_")[-1]
    is_owner = data.get("owner", "0") == str(callback.message.chat.id)
    if is_correct_collection and is_owner:
        name = data.get("name", "None")
        words_data = data.get("words", {})
        words_list = [
            html.bold(words_data[word]["base_form"])
            + " - "
            + words_data[word]["translation"].capitalize()
            for word in words_data.keys()
        ]
        words = "\n".join(words_list)
        if not words_list:
            words = "В этой коллекции пока нет слов"
        await callback.message.edit_text(
            text=f"Коллекция: {html.bold(name)}\n\n{words}",
            reply_markup=keyboards.collections_edit_menu(data.get("id", "0"), words_list),
        )


@router.callback_query(F.data.startswith("collections_remove_word_"))
async def collections_remove_word_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    collection_id = callback.data.split("_")[-1]
    is_correct_collection = str(data.get("id")) == collection_id
    is_owner = data.get("owner", "0") == str(callback.message.chat.id)
    if is_correct_collection and is_owner:
        await state.set_state(states.CollectionsRemoveWordStatesGroup.input)
        words_list = data.get("words", {})
        if not words_list:
            await callback.message.edit_text(
                text="В коллекции нет слов для удаления",
                reply_markup=keyboards.back_collections_edit_menu(collection_id),
            )
        else:
            words_text = "\n".join(
                [
                    html.code(word) + " - " + words_list[word]["translation"]
                    for word in words_list.keys()
                ]
            )
            await callback.message.edit_text(
                text=f"Введи слово на иврите для удаления его из коллекции:\n"
                f"(Нажми на слово чтобы его скопировать)\n{words_text}",
                reply_markup=keyboards.back_collections_edit_menu(collection_id),
            )


@router.message(states.CollectionsRemoveWordStatesGroup.input)
async def collections_remove_word_input_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    words = data.get("words", {})
    collection_id = data.get("id", "0")
    exists = False
    for word in words.keys():
        if word == message.text:
            exists = True
    if not exists:
        return await message.answer(
            f"✖️ Слова {html.bold(message.text)} нет в коллекции\n\n"
            f"Ты можешь вернуться в меню или ввести еще одно слово, чтобы удалить его",
            reply_markup=keyboards.back_collections_edit_menu(collection_id),
        )

    response = await utils.collections_remove_word(
        {
            "collection_id": collection_id,
            "word": message.text,
            "telegram_id": message.chat.id,
        }
    )

    if response["success"]:
        await message.answer(
            f"✔️ Слово {html.bold(message.text)} успешно удалено из коллекции\n\n"
            f"Ты можешь вернуться в меню или ввести еще одно слово, чтобы удалить его",
            reply_markup=keyboards.back_collections_edit_menu(str(collection_id)),
        )
        del words[message.text]
        data["words"] = words
        await state.set_data(data)
    else:
        await message.answer(
            response["message"],
            reply_markup=keyboards.back_collections_edit_menu(str(collection_id)),
        )


@router.callback_query(F.data.startswith("collections_add_word_"))
async def collections_add_word_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    collection_id = callback.data.split("_")[-1]
    is_correct_collection = str(data.get("id")) == collection_id
    is_owner = data.get("owner", "0") == str(callback.message.chat.id)
    if is_correct_collection and is_owner:
        await state.set_state(states.CollectionsAddWordStatesGroup.input)
        await callback.message.edit_text(
            text="Введи слово на иврите для добавления в коллекцию",
            reply_markup=keyboards.back_collections_edit_menu(collection_id),
        )


@router.message(states.CollectionsAddWordStatesGroup.input)
async def collections_add_word_input_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    word = utils.remove_nekudots(message.text)
    if not utils.check_hebrew_letters(message.text):
        await message.answer(
            text="✖️ Введено слово не на иврите, "
            "ты можешь вернуться в меню или попробовать ввести слово еще раз",
            reply_markup=keyboards.back_collections_edit_menu(data.get("id", "0")),
        )
        return
    response = await utils.get_or_add_word(
        {
            "telegram_id": message.chat.id,
            "word": word,
            "collection_search": True,
        }
    )
    is_success = response.get("success", False)
    response_data = response.get("data", {})
    is_analyzed = response_data.get("analyzed", False)
    is_multiply = response_data.get("multiply", False)
    await state.update_data({"word_to_add": word})

    if is_success:
        if is_analyzed:
            if not is_multiply:
                word = response_data.get("data").get("base_form")
                translation = response_data.get("data").get("translation")
                await message.answer(
                    text=f"Найдено слово: {word} - {translation}",
                    reply_markup=keyboards.collections_add_new_word(
                        response_data.get("id", "0"), data.get("id", "0")
                    ),
                )
            else:
                many_words = word_formatter.get_many_results_message(
                    response.get("data", {}).get("data", [])
                )
                many_words_data = many_words.get("data", [])
                await message.answer(
                    text=many_words.get("text"),
                    reply_markup=keyboards.collections_add_multiple_words(
                        many_words_data, data.get("id", "0")
                    ),
                )
                await state.update_data({"multiple_words_data": many_words_data})
        else:
            pass
    else:
        await message.answer(
            "❕ Неизвестная ошибка при добавлении слова, "
            "попробуй позже или введи новое слово"
        )


@router.callback_query(F.data.startswith("coll_add_existing_"))
async def collections_add_existing_word_handler(
    callback: CallbackQuery, state: FSMContext
):
    data = await state.get_data()
    if not data.get("word_to_add"):
        return
    collection_id = data.get("id", "0")
    response = await utils.collections_add_word(
        {
            "id": callback.data.split("_")[-1],
            "existing": True,
            "collection_id": collection_id,
        }
    )

    if response.get("success", False):
        words_in_collection = data.get("words", {})
        word_data = response.get("data", {})
        words_in_collection[word_data.get("word")] = word_data
        await state.update_data(
            {"words": words_in_collection, "word_to_add": None, "word_id_to_add": None}
        )
        await callback.message.answer(
            text=f"{response.get('message')}\n\n"
            f"Ты можешь вернуться в меню или ввести следующее слово для добавления",
            reply_markup=keyboards.back_collections_edit_menu(collection_id),
        )
    else:
        await callback.message.answer(
            text=f"Ошибка при добавлении слова: {response.get('message')}\n\n"
            f"Ты можешь вернуться в меню или ввести следующее слово для добавления",
            reply_markup=keyboards.back_collections_edit_menu(collection_id),
        )


@router.callback_query(F.data.startswith("coll_existing_custom_translation_"))
async def collections_add_translation_existing_word_handler(
    callback: CallbackQuery, state: FSMContext
):
    data = await state.get_data()
    if not data.get("word_to_add"):
        return
    await state.update_data({"word_id_to_add": callback.data.split("_")[-1]})
    await state.set_state(states.CollectionsAddExistingTranslationWordStatesGroup.input)

    collection_id = data.get("id", "0")
    await callback.message.edit_text(
        text=f"Введи свой перевод для слова {data.get('word_to_add')}",
        reply_markup=keyboards.back_collections_edit_menu(collection_id),
    )


@router.callback_query(F.data.startswith("coll_new_custom_translation_"))
async def collections_add_translation_new_word_handler(
    callback: CallbackQuery, state: FSMContext
):
    data = await state.get_data()
    if not data.get("word_to_add"):
        return

    await state.update_data({"word_id_to_add": None})
    await state.set_state(states.CollectionsAddExistingTranslationWordStatesGroup.input)

    collection_id = data.get("id", "0")
    await callback.message.edit_text(
        text=f"Введи свой перевод для слова {data.get('word_to_add')}",
        reply_markup=keyboards.back_collections_edit_menu(collection_id),
    )


@router.message(states.CollectionsAddExistingTranslationWordStatesGroup.input)
async def collection_add_base_form_new_word_menu_handler(
    message: Message, state: FSMContext
):
    data = await state.get_data()
    await state.update_data({"word_translation_to_add": message.text})
    await state.set_state(
        states.CollectionsAddExistingTranslationWordStatesGroup.input_two
    )
    base_form = "None"
    if data.get("word_id_to_add"):
        response = await utils.get_or_add_word(
            {
                "telegram_id": message.chat.id,
                "word": utils.remove_nekudots(data.get("word_to_add")),
            }
        )
        base_form = response["data"]["data"].get("base_form", "")
    await message.answer(
        text=f"Слово: {html.bold(data.get('word_to_add'))}\n"
        f"Перевод: {html.bold(message.text.capitalize())}\n"
        f"Форма с огласовками: {html.bold(base_form)}\n\n"
        f"Форма с огласовками записана правильно?",
        reply_markup=keyboards.collection_add_base_form_menu(data.get("id", "0")),
    )


@router.callback_query(F.data == "collections_add_edit_base_form")
async def collections_edit_base_form_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    collection_id = data.get("id", "0")
    word = data.get("word_to_add")
    await callback.message.edit_text(
        text=f"Введи корректную форму с огласовками для слова {html.bold(word)}",
        reply_markup=keyboards.collection_add_base_form_input(collection_id, word),
    )


@router.callback_query(F.data == "collections_apply_same_base_form")
async def collections_edit_base_form_handler_same_with_word(
    callback: CallbackQuery,
    state: FSMContext,
):
    data = await state.get_data()
    await state.update_data({"base_form": data.get("word_to_add")})
    await collections_add_translation_new_word_input_handler(callback, state, False)


@router.message(states.CollectionsAddExistingTranslationWordStatesGroup.input_two)
async def collections_edit_base_form_input_handler(message: Message, state: FSMContext):
    await state.update_data({"base_form": message.text})
    await collections_add_translation_new_word_input_handler(message, state, True)


@router.callback_query(F.data == "collections_apply_translation")
async def collections_add_translation_new_word_input_handler(
    callback: CallbackQuery | Message,
    state: FSMContext,
    use_message: bool = False,
):
    data = await state.get_data()
    collection_id = data.get("id")
    existing = data.get("word_id_to_add") is not None
    request_data = {
        "id": data.get("word_id_to_add"),
        "existing": existing,
        "collection_id": collection_id,
        "translation": data.get("word_translation_to_add"),
    }
    base_form = data.get("base_form", None)
    if base_form:
        request_data["base_form"] = base_form
    if not existing:
        request_data["base_form"] = data.get("word_to_add")
        request_data["word"] = data.get("word_to_add")

    response = await utils.collections_add_word(request_data)

    await state.set_state(states.CollectionsAddWordStatesGroup.input)
    if response.get("success", False):
        words_in_collection = data.get("words", {})
        word_data = response.get("data", {})
        words_in_collection[word_data.get("word")] = word_data
        await state.update_data(
            {"words": words_in_collection, "word_to_add": None, "word_id_to_add": None}
        )
        if use_message:
            await callback.answer(
                text=f"{response.get('message')}\n\n"
                f"Ты можешь вернуться в меню или ввести следующее слово для добавления",
                reply_markup=keyboards.back_collections_edit_menu(collection_id),
            )
        else:
            await callback.message.edit_text(
                text=f"{response.get('message')}\n\n"
                f"Ты можешь вернуться в меню или ввести следующее слово для добавления",
                reply_markup=keyboards.back_collections_edit_menu(collection_id),
            )
    else:
        if use_message:
            await callback.answer(
                text=f"Ошибка при добавлении слова: {response.get('message')}\n\n"
                f"Ты можешь вернуться в меню или ввести следующее слово для добавления",
                reply_markup=keyboards.back_collections_edit_menu(collection_id),
            )
        else:
            await callback.message.edit_text(
                text=f"Ошибка при добавлении слова: {response.get('message')}\n\n"
                f"Ты можешь вернуться в меню или ввести следующее слово для добавления",
                reply_markup=keyboards.back_collections_edit_menu(collection_id),
            )


@router.callback_query(F.data.startswith("coll_add_multiple_"))
async def collections_add_multiple_translation_existing_word_handler(
    callback: CallbackQuery, state: FSMContext
):
    data = await state.get_data()
    collection_id = data.get("id")
    if not data.get("word_to_add"):
        return
    word_data = list(
        filter(
            lambda x: x.get("id") == callback.data[18:], data.get("multiple_words_data")
        )
    )[0]
    if utils.remove_nekudots(data.get("word_to_add")) != utils.remove_nekudots(
        word_data.get("base_form")
    ):
        return
    response = await utils.collections_add_word(
        {
            "word": data.get("word_to_add"),
            "existing": False,
            "collection_id": collection_id,
            "translation": word_data.get("translation"),
            "link": word_data.get("link"),
            "base_form": word_data.get("base_form"),
        }
    )
    if response.get("success", False):
        words_in_collection = data.get("words", {})
        word_data = response.get("data", {})
        words_in_collection[word_data.get("word")] = word_data
        await state.update_data(
            {
                "words": words_in_collection,
                "word_to_add": None,
                "word_id_to_add": None,
            }
        )
        await callback.message.answer(
            text=f"{response.get('message')}\n\n"
            f"Ты можешь вернуться в меню или ввести следующее слово для добавления",
            reply_markup=keyboards.back_collections_edit_menu(collection_id),
        )
    else:
        await callback.message.answer(
            text=f"Ошибка при добавлении слова: {response.get('message')}\n\n"
            f"Ты можешь вернуться в меню или ввести следующее слово для добавления",
            reply_markup=keyboards.back_collections_edit_menu(collection_id),
        )


@router.callback_query(F.data == "coll_multiple_custom_translation")
async def collections_add_translation_multiple_word_handler(
    callback: CallbackQuery,
    state: FSMContext,
):
    data = await state.get_data()
    if not data.get("word_to_add"):
        return

    await state.update_data({"word_id_to_add": None})
    await state.set_state(states.CollectionsAddMultipleTranslationWordStatesGroup.input)

    collection_id = data.get("id", "0")
    await callback.message.edit_text(
        text=f"Введи свой перевод для слова {data.get('word_to_add')}",
        reply_markup=keyboards.back_collections_edit_menu(collection_id),
    )


@router.message(states.CollectionsAddMultipleTranslationWordStatesGroup.input)
async def collections_add_translation_multiple_word_input_handler(
    message: Message,
    state: FSMContext,
):
    data = await state.get_data()
    collection_id = data.get("id")

    response = await utils.collections_add_word(
        {
            "existing": False,
            "collection_id": collection_id,
            "translation": message.text,
            "word": data.get("word_to_add"),
            "base_form": data.get("word_to_add"),
        }
    )

    if response.get("success", False):
        words_in_collection = data.get("words", {})
        word_data = response.get("data", {})
        words_in_collection[word_data.get("word")] = word_data
        await state.update_data(
            {
                "words": words_in_collection,
                "word_to_add": None,
                "word_id_to_add": None,
            }
        )
        await message.answer(
            text=f"{response.get('message')}\n\n"
            f"Ты можешь вернуться в меню или ввести следующее слово для добавления",
            reply_markup=keyboards.back_collections_edit_menu(collection_id),
        )
    else:
        await message.answer(
            text=f"Ошибка при добавлении слова: {response.get('message')}\n\n"
            f"Ты можешь вернуться в меню или ввести следующее слово для добавления",
            reply_markup=keyboards.back_collections_edit_menu(collection_id),
        )


@router.callback_query(F.data.startswith("coll_add_new_multiple_"))
async def collections_add_translation_new_multiple_word_handler(
    callback: CallbackQuery,
    state: FSMContext,
):
    data = await state.get_data()
    collection_id = data.get("id")

    response = await utils.collections_add_word(
        {
            "existing": True,
            "is_multiple": True,
            "word": data.get("word_to_add"),
            "base_form": data.get("word_to_add"),
            "collection_id": collection_id,
            "id": callback.data[22:],
        }
    )

    if response.get("success", False):
        words_in_collection = data.get("words", {})
        word_data = response.get("data", {})
        words_in_collection[word_data.get("word")] = word_data
        await state.update_data(
            {
                "words": words_in_collection,
                "word_to_add": None,
                "word_id_to_add": None,
            }
        )
        await callback.message.edit_text(
            text=f"{response.get('message')}\n\n"
            f"Ты можешь вернуться в меню или ввести следующее слово для добавления",
            reply_markup=keyboards.back_collections_edit_menu(collection_id),
        )
    else:
        await callback.message.edit_text(
            text=f"Ошибка при добавлении слова: {response.get('message')}\n\n"
            f"Ты можешь вернуться в меню или ввести следующее слово для добавления",
            reply_markup=keyboards.back_collections_edit_menu(collection_id),
        )


@router.callback_query(F.data == "collections_add_menu")
async def create_collection_menu_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(states.CreateCollectionStatesGroup.input)
    await callback.message.edit_text(
        text="Введи название для новой коллекции",
        reply_markup=keyboards.create_collection_menu(),
    )


@router.message(states.CreateCollectionStatesGroup.input)
async def create_collection_menu_input_handler(message: Message, state: FSMContext):
    response = await utils.create_collection(
        {
            "telegram_id": message.chat.id,
            "name": message.text,
        }
    )
    await state.clear()

    if response.get("success", False):
        await message.answer(
            text=f"Коллекция {html.bold(message.text)} успешно создана. "
            f"ID: {response.get('data').get('id')}",
            reply_markup=keyboards.new_created_collection_menu(
                str(response.get("data", {}).get("id", "0"))
            ),
        )
    else:
        await message.answer(
            text=response.get("message"),
            reply_markup=keyboards.create_collection_menu(),
        )


@router.callback_query(F.data.startswith("open_collection_by_id_"))
async def open_collection_by_id_handler(callback: CallbackQuery, state: FSMContext):
    return await collections_search_id_input_handler(
        callback.message,
        state,
        collection_id=callback.data.split("_")[-1],
    )


@router.callback_query(F.data.startswith("collections_training_"))
async def collections_training_menu_handler(
    callback: CallbackQuery,
    state: FSMContext,
    first_launch=True,
):
    if first_launch:
        await state.update_data({"training_mode_translation": False})
        await state.update_data({"training_mode_nekudot": True})
        await state.update_data({"training_mode_training": 1})
        await state.update_data({"training_n_options": 3})
    data = await state.get_data()
    if callback.data.split("_")[-1] != str(data.get("id")) and first_launch:
        return await callback.answer(
            text="Запрещено запускать тренировку из старого сообщения",
        )
    training_mode = data.get("training_mode_training")
    display_mode = data.get("training_mode_translation")
    nekudot_mode = data.get("training_mode_nekudot")
    n_options = data.get("training_n_options")
    training_mode_text = "Выбор опции" if training_mode == 1 else "Ввод вручную"
    display_mode_text = "Слово на иврите" if display_mode else "Перевод слова"
    nekudot_mode_text = "Да" if nekudot_mode else "Нет"
    settings_text = (
        f"Выбери настройки:\n\nРежим: {html.bold(training_mode_text)}\n"
        f"В вопросе: {html.bold(display_mode_text)}\n"
        f"Отображать некудот: {html.bold(nekudot_mode_text)}"
    )
    if training_mode == 1:
        settings_text += f"\nКоличество опций: {html.bold(n_options)}"
    else:
        n_options = 0
    return await callback.message.edit_text(
        text=settings_text,
        reply_markup=keyboards.collection_training_settings_menu(
            data.get("id", "0"),
            n_options != 0,
        ),
    )


@router.callback_query(F.data == "collection_training_change_display_mode")
async def collections_training_change_display_mode_handler(
    callback: CallbackQuery,
    state: FSMContext,
):
    data = await state.get_data()
    await state.update_data(
        {
            "training_mode_translation": not data.get("training_mode_translation"),
        }
    )
    return await collections_training_menu_handler(callback, state, first_launch=False)


@router.callback_query(F.data == "collection_training_change_nekudot_mode")
async def collections_training_change_nekudot_mode_handler(
    callback: CallbackQuery,
    state: FSMContext,
):
    data = await state.get_data()
    await state.update_data(
        {
            "training_mode_nekudot": not data.get("training_mode_nekudot"),
        }
    )
    return await collections_training_menu_handler(callback, state, first_launch=False)


@router.callback_query(F.data == "collection_training_change_training_mode")
async def collections_training_change_training_mode_handler(
    callback: CallbackQuery,
    state: FSMContext,
):
    data = await state.get_data()
    training_mode_now = data.get("training_mode_training")
    if training_mode_now == 1:
        new_training_mode = 2
    else:
        new_training_mode = 1
    await state.update_data(
        {
            "training_mode_training": new_training_mode,
            "training_mode_translation": False,
        }
    )
    return await collections_training_menu_handler(callback, state, first_launch=False)


@router.callback_query(F.data == "collection_training_change_options_number")
async def collections_training_change_options_number_handler(
    callback: CallbackQuery,
    state: FSMContext,
):
    data = await state.get_data()
    words = data.get("words", {})
    n_options = data.get("training_n_options", 3)
    if n_options == 3 and len(words) > 3:
        n_options = 4
    elif n_options == 4 and len(words) > 4:
        n_options = 5
    elif n_options == 5:
        n_options = 3
    elif n_options == 4 and len(words) <= 4:
        n_options = 3
    await state.update_data(
        {
            "training_n_options": n_options,
        }
    )
    return await collections_training_menu_handler(callback, state, first_launch=False)


@router.callback_query(F.data == "collection_training_start")
async def collections_training_start_handler(
    callback: CallbackQuery,
    state: FSMContext,
):
    data = await state.get_data()
    collection_words_dict = data.get("words", {})
    n_options = data.get("training_n_options", 0)
    collection_words_list = [
        collection_words_dict[word] for word in collection_words_dict.keys()
    ]
    questions = []
    for item in collection_words_list:
        correct_word = item["word"]
        other_words = [w for w in collection_words_list if w != item]
        sampled = random.sample(other_words, min(n_options - 1, len(other_words)))
        options = sampled + [item]
        random.shuffle(options)

        options_dict = {i + 1: opt["word"] for i, opt in enumerate(options)}
        correct_index = [k for k, v in options_dict.items() if v == correct_word]
        correct_index = correct_index[0]
        questions.append(
            {
                "options": options_dict,
                "correct_answer": correct_index,
            }
        )
    random.shuffle(questions)
    await state.update_data(
        {
            "training_questions": questions,
            "training_question_number": 0,
            "training_correct_answers": 0,
            "training_not_correct_answers": [],
        }
    )
    await collections_training_question_handler(callback, state)


async def collections_training_question_handler(
    callback: CallbackQuery,
    state: FSMContext,
):
    data = await state.get_data()
    collection_id = data.get("id", "0")
    questions = data.get("training_questions", [])
    question_now_number = data.get("training_question_number")
    correct_answers = data.get("training_correct_answers")
    not_correct_answers = data.get("training_not_correct_answers")

    if len(questions) == 0 or len(questions) == question_now_number:
        words_to_repeat = "\n".join([f"• {i}" for i in not_correct_answers])
        words_to_repeat = "Слова для повторения:\n" + words_to_repeat
        if len(not_correct_answers) == 0:
            words_to_repeat = ""
        answers_percentage = round(correct_answers / question_now_number * 100, 1)
        answers_percentage_text = f"{answers_percentage}%"
        return await callback.message.edit_text(
            text=f"Тренировка завершена\n\n"
            f"Верных ответов: {html.bold(answers_percentage_text)}\n\n"
            f"{words_to_repeat}",
            reply_markup=keyboards.collections_training_finish(data.get("id")),
        )

    question_now = questions[question_now_number]
    training_mode = data.get("training_mode_training")
    display_mode = data.get("training_mode_translation")
    nekudot_mode = data.get("training_mode_nekudot")
    collection_words = data.get("words", {})
    correct_word_data_word = question_now["options"].get(
        str(question_now["correct_answer"])
    )
    correct_word_data = collection_words.get(correct_word_data_word)
    word_to_display = correct_word_data.get("translation")
    if display_mode:
        if nekudot_mode:
            word_to_display = correct_word_data.get("base_form")
        else:
            word_to_display = correct_word_data.get("word")

    correct_percentage = 100
    if question_now_number != 0:
        correct_percentage = correct_answers / question_now_number * 100
    if training_mode == 1:
        question_text = (
            f"Выбери правильный перевод: {html.bold(word_to_display.capitalize())}"
        )
    else:
        question_text = f"Введи перевод слова: {html.bold(word_to_display.capitalize())}"
    await state.update_data({"training_question_text": question_text})

    stats_string = (
        f"{question_now_number + 1}/{len(questions)} "
        f"{round(correct_percentage, 1)}%\n\n"
    )
    question_text = html.italic(stats_string) + question_text
    if training_mode == 1:
        await state.set_state(states.TrainingStatesGroup.choose)
        await callback.message.edit_text(
            text=question_text,
            reply_markup=keyboards.create_training_options(
                question_now,
                display_mode,
                nekudot_mode,
                data.get("id", "0"),
                collection_words,
            ),
        )
    else:
        await state.set_state(states.TrainingStatesGroup.input)
        await callback.message.edit_text(
            text=question_text,
            reply_markup=keyboards.collection_data(collection_id),
        )
    return None


@router.callback_query(
    F.data.startswith("training_choose_"),
    states.TrainingStatesGroup.choose,
)
async def collections_training_question_choose_handler(
    callback: CallbackQuery,
    state: FSMContext,
):
    data = await state.get_data()
    collection_words = data.get("words", {})
    questions = data.get("training_questions", [])
    display_mode = data.get("training_mode_translation")
    nekudot_mode = data.get("training_mode_nekudot")
    question_now_number = data.get("training_question_number")
    question_now = questions[question_now_number]
    correct_answer_number = str(question_now["correct_answer"])
    user_answer_number = callback.data.split("_")[-1]
    user_answer_data_word = question_now["options"][user_answer_number]
    user_answer_data = collection_words.get(user_answer_data_word)
    correct_answer_data_word = question_now["options"][correct_answer_number]
    correct_answer_data = collection_words.get(correct_answer_data_word)
    question_text = data.get("training_question_text")
    correct_answers = data.get("training_correct_answers")
    not_correct_answers = data.get("training_not_correct_answers")

    question_now_number += 1
    if correct_answer_number == user_answer_number:
        correct_answers += 1

    correct_percentage = 1
    if question_now_number != 0:
        correct_percentage = correct_answers / question_now_number * 100

    stats_string = (
        f"{question_now_number}/{len(questions)} {round(correct_percentage, 1)}%\n\n"
    )
    result_text = html.italic(stats_string) + question_text

    if correct_answer_number != user_answer_number:
        word = user_answer_data["word"]
        base_form = user_answer_data["base_form"]
        translation = user_answer_data["translation"].capitalize()
        if display_mode:
            part_one = html.bold(base_form) + " - " + html.italic(translation)

        else:
            if nekudot_mode:
                part_one = html.bold(base_form) + " - " + html.italic(translation)
            else:
                part_one = html.bold(word) + " - " + html.italic(translation)
        result_text += f"\n\nТы ответил: {part_one}"

        correct_word = correct_answer_data["base_form" if nekudot_mode else "word"]
        correct_translation = correct_answer_data["translation"].capitalize()
        correct_text = f"{html.bold(correct_word)} - {correct_translation}"
        not_correct_answers.append(correct_text)
        await state.update_data({"training_not_correct_answers": not_correct_answers})
    else:
        await state.update_data({"training_correct_answers": correct_answers})

    result_text += html.italic(
        "\n\nНажми на любую кнопку для перехода к следующему вопросу"
    )
    await state.set_state(states.TrainingStatesGroup.answers)
    await callback.message.edit_text(
        text=result_text,
        reply_markup=keyboards.create_training_options(
            question_now,
            display_mode,
            nekudot_mode,
            data.get("id", "0"),
            collection_words,
            True,
            user_answer_number,
        ),
    )


@router.callback_query(
    F.data.startswith("training_choose_"),
    states.TrainingStatesGroup.answers,
)
async def collections_training_next_question_handler(
    callback: CallbackQuery,
    state: FSMContext,
):
    data = await state.get_data()
    await state.update_data(
        {
            "training_question_number": data.get("training_question_number") + 1,
            "training_question_text": "",
        }
    )
    await collections_training_question_handler(callback, state)


@router.callback_query(F.data == "collections_saved_menu")
async def saved_collections_menu_handler(callback: CallbackQuery, state: FSMContext):
    response = await utils.get_or_create_user(
        callback.message.chat.id,
        {"telegram_id": callback.message.chat.id},
    )
    if response.get("success", False):
        response_data = response.get("data", {})
        collections_list = response_data.get("collections_saved", [])
        is_empty = len(collections_list) == 0
        answer_text = "Список сохраненных коллекций:"
        if len(collections_list) == 0:
            answer_text = "Ты пока не сохранил ни одной коллекции"
        await callback.message.edit_text(
            text=answer_text,
            reply_markup=keyboards.my_collections_menu(collections_list, not is_empty),
        )
    else:
        await callback.message.answer(
            text=f"Ошибка при получении списка сохраненных коллекций: "
            f"{response.get('message')}",
        )


@router.callback_query(F.data == "collections_my_menu")
async def my_collections_menu_handler(callback: CallbackQuery, state: FSMContext):
    response = await utils.get_or_create_user(
        callback.message.chat.id,
        {"telegram_id": callback.message.chat.id},
    )
    if response.get("success", False):
        response_data = response.get("data", {})
        collections_list = response_data.get("collections_owner", [])
        answer_text = "Список моих коллекций:"
        if len(collections_list) == 0:
            answer_text = "Ты пока не создал ни одной коллекции"
        await callback.message.edit_text(
            text=answer_text,
            reply_markup=keyboards.my_collections_menu(collections_list),
        )
    else:
        await callback.message.answer(
            text=f"Ошибка при получении списка сохраненных коллекций: "
            f"{response.get('message')}",
        )


@router.callback_query(F.data.startswith("collections_share_"))
async def share_collections_handler(callback: CallbackQuery, state: FSMContext):
    collection_id = callback.data.split("_")[-1]
    data = await state.get_data()
    if collection_id != str(data.get("id")):
        return await callback.answer(
            text="Открой коллекцию в новом сообщении, чтобы поделиться ею",
        )
    share_link = f"t.me/{BOT_USERNAME}?start=collection_{collection_id}"
    part_one = html.italic("Поделись этой ссылкой, чтобы открыть коллекцию ")
    part_two = html.italic(" на другом устройстве:")
    share_text = part_one + data.get("name") + part_two
    await callback.message.edit_text(
        text=f"{share_text}\n\n{share_link}",
        reply_markup=keyboards.share_keyboard(share_link, collection_id),
    )


@router.callback_query(F.data.startswith("collections_save_"))
async def collections_save_add_handler(callback: CallbackQuery, state: FSMContext):
    collection_id = callback.data.split("_")[-1]
    response = await utils.users_saved_add(
        {
            "telegram_id": callback.message.chat.id,
            "collection_id": collection_id,
        }
    )
    if response.get("success", False):
        await callback.answer("✅ Коллекция успешно сохранена")
    else:
        await callback.message.answer(
            text=f"Ошибка при сохранении коллекции {response.get('message')}",
        )


@router.callback_query(F.data == "collections_saved_edit")
async def saved_collections_edit_menu_handler(callback: CallbackQuery, state: FSMContext):
    response = await utils.get_or_create_user(
        callback.message.chat.id,
        {"telegram_id": callback.message.chat.id},
    )
    if response.get("success", False):
        response_data = response.get("data", {})
        collections_list = response_data.get("collections_saved", [])
        answer_text = (
            "Список сохраненных коллекций:\n\n"
            "Нажми на название коллекции, чтобы убрать её из списка сохранённых"
        )
        await callback.message.edit_text(
            text=answer_text,
            reply_markup=keyboards.my_collections_menu(collections_list, False, True),
        )
    else:
        await callback.message.answer(
            text=f"Ошибка при получении списка сохраненных коллекций: "
            f"{response.get('message')}",
        )


@router.callback_query(F.data.startswith("collections_remove_saved_"))
async def collections_save_remove_handler(callback: CallbackQuery, state: FSMContext):
    collection_id = callback.data.split("_")[-1]
    response = await utils.users_saved_remove(
        {
            "telegram_id": callback.message.chat.id,
            "collection_id": collection_id,
        }
    )
    if response.get("success", False):
        await callback.answer(f"✅ Коллекция №{collection_id} удалена из сохраненных")
        await saved_collections_edit_menu_handler(callback, state)
    else:
        await callback.message.answer(
            text=f"Ошибка при сохранении коллекции {response.get('message')}",
        )


@router.callback_query(F.data.startswith("collections_rename_"))
async def collections_rename_menu_handler(callback: CallbackQuery, state: FSMContext):
    collection_id = callback.data.split("_")[-1]
    data = await state.get_data()
    if collection_id != str(data.get("id", 0)):
        return await callback.answer(
            text="Запрещено редактировать коллекцию из старого сообщения",
        )
    await state.set_state(states.RenameCollectionStatesGroup.input)
    return await callback.message.edit_text(
        text="Введи новое название для коллекции",
        reply_markup=keyboards.back_collections_edit_menu(collection_id),
    )


@router.message(states.RenameCollectionStatesGroup.input)
async def collections_rename_menu_input_handler(message: Message, state: FSMContext):
    collection_name = message.text
    data = await state.get_data()
    collection_id = data.get("id")
    response = await utils.rename_collection(
        {
            "collection_id": collection_id,
            "name": collection_name,
        }
    )
    if response.get("id", None):
        await message.answer(
            text=f"✔️ Коллекция успешно переименована в {html.bold(collection_name)}",
            reply_markup=keyboards.back_collections_edit_menu(collection_id),
        )
        await state.update_data({"name": collection_name})
    else:
        await message.answer(
            text="Ошибка при обновлении имени коллекции",
            reply_markup=keyboards.back_collections_edit_menu(collection_id),
        )


@router.callback_query(F.data.startswith("collections_other_"))
async def collections_other_menu_handler(callback: CallbackQuery, state: FSMContext):
    collection_id = callback.data.split("_")[-1]
    await callback.message.edit_reply_markup(
        reply_markup=keyboards.collections_other_menu(collection_id),
    )


@router.callback_query(F.data == "not_realized_feature")
async def not_realized_feature_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Эта функция еще не добавлена :)")


@router.message(states.TrainingStatesGroup.input)
async def collections_training_question_input_handler(
    message: Message,
    state: FSMContext,
):
    user_answer = message.text

    data = await state.get_data()
    collection_words = data.get("words", {})
    collection_id = data.get("id", "0")
    questions = data.get("training_questions", [])
    question_now_number = data.get("training_question_number")
    question_now = questions[question_now_number]
    correct_answer_number = str(question_now["correct_answer"])
    correct_answer_data_word = question_now["options"][correct_answer_number]

    clear_correct_answer = utils.remove_nekudots(correct_answer_data_word)
    is_correct = clear_correct_answer == utils.remove_nekudots(user_answer)

    correct_answer_data = collection_words.get(correct_answer_data_word)
    question_text = data.get("training_question_text")
    correct_answers = data.get("training_correct_answers")
    not_correct_answers = data.get("training_not_correct_answers")

    question_now_number += 1
    if is_correct:
        correct_answers += 1

    correct_percentage = 1
    if question_now_number != 0:
        correct_percentage = correct_answers / question_now_number * 100

    stats_string = (
        f"{question_now_number}/{len(questions)} {round(correct_percentage, 1)}%\n\n"
    )
    result_text = html.italic(stats_string) + question_text

    if not is_correct:
        result_text += html.bold("\n\n️❌ Не верно")
        correct_word = correct_answer_data["word"]
        result_text += (
            f"\n\nТы ответил: {html.bold(user_answer)}\n"
            f"Правильный ответ: {html.bold(correct_word)}"
        )

        correct_translation = correct_answer_data["translation"].capitalize()
        correct_text = f"{html.bold(correct_word)} - {correct_translation}"
        not_correct_answers.append(correct_text)
        await state.update_data({"training_not_correct_answers": not_correct_answers})
    else:
        result_text += html.bold("\n\n️✅ Верно") + f" - {user_answer}"
        await state.update_data({"training_correct_answers": correct_answers})

    result_text += html.italic(
        "\n\nНажми на кнопку ниже для перехода к следующему вопросу"
    )
    await state.set_state(states.TrainingStatesGroup.answers)
    await message.answer(
        text=result_text,
        reply_markup=keyboards.training_next_question(collection_id),
    )
