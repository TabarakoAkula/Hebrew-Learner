from datetime import datetime, timedelta, timezone

from aiogram import F, html, Router
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


@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    response = await utils.get_or_create_user(
        message.chat.id,
        {"telegram_username": message.chat.username},
    )
    if not response["success"]:
        return await message.answer(response["message"])
    answer_message = "Привет, в этом боте ты можешь искать перевод слов с иврита"
    if response["data"]["New"]:
        answer_message = "Поздравляю с первым запуском🥳\n\n" + answer_message

    if response["data"]["moderator"]:
        await message.answer("⚠️ У вас есть права модератора")

    await message.answer(answer_message, reply_markup=keyboards.main_menu())


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
        if new_message and not collection_id:
            await message.answer(
                text=text,
                reply_markup=keyboards.collections_data_menu(
                    response.get("id", "0"), is_owner
                ),
            )
        else:
            await message.edit_text(
                text=text,
                reply_markup=keyboards.collections_data_menu(
                    response.get("id", "0"), is_owner
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
            + words_data[word]["translation"]
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
            + words_data[word]["translation"]
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
async def collections_add_translation_new_word_input_handler(
    message: Message, state: FSMContext
):
    data = await state.get_data()
    collection_id = data.get("id")
    existing = data.get("word_id_to_add") is not None
    request_data = {
        "id": data.get("word_id_to_add"),
        "existing": existing,
        "collection_id": collection_id,
        "translation": message.text,
    }
    if not existing:
        request_data["base_form"] = data.get("word_to_add")
        request_data["word"] = data.get("word_to_add")

    response = await utils.collections_add_word(request_data)

    if response.get("success", False):
        words_in_collection = data.get("words", {})
        word_data = response.get("data", {})
        words_in_collection[word_data.get("word")] = word_data
        await state.update_data(
            {"words": words_in_collection, "word_to_add": None, "word_id_to_add": None}
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
            text=f"Коллекция {html.bold(message.text)} успешно создана",
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
