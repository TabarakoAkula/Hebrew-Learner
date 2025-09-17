from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
import dotenv
import keyboards
import states
import utils

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
    await message.answer(answer_message, reply_markup=keyboards.main_menu())
    if response["data"]["moderator"]:
        await message.answer(
            "⚠️ У вас есть права модератора:\n\n- Редактировать категории"
        )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    return await start_handler(callback.message, state)


@router.callback_query(F.data == "search_menu")
async def search_menu_hanlder(callback: CallbackQuery, state: FSMContext):
    await state.set_state(states.SearchStatesGroup.menu)
    await callback.message.edit_text(
        "Введи слово для поиска:",
        reply_markup=keyboards.return_to_menu(),
    )


@router.message(SEARCH_FILTER)
async def search_result(message: Message, state: FSMContext):
    await state.set_state(states.SearchStatesGroup.result)
    response = await utils.get_or_add_word(
        {
            "telegram_id": message.chat.id,
            "word": message.text,
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
