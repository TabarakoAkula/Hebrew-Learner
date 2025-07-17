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
    answer_message = "Привет, в этом боте ты можешь искать перевод слов с иврита"
    if response["data"]["New"]:
        answer_message = "Поздравляю с первым запуском🥳\n\n" + answer_message
    await message.answer(answer_message, reply_markup=keyboards.keyboard_example())
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
    await callback.message.edit_text("Введи слово для поиска:")


@router.message(SEARCH_FILTER)
async def search_result(message: Message, state: FSMContext):
    await state.set_state(states.SearchStatesGroup.result)
    response = await utils.get_or_add_word(
        {
            "telegram_id": message.chat.id,
            "word": message.text,
            "message_id": message.message_id,
        }
    )
    if not response["success"]:
        return await message.answer("⚠️ Неизвестная ошибка!")
    if not response["data"]["new"]:
        await state.set_data(data=response["data"])
        await message.answer(str(response["data"]))


@router.callback_query(F.data.startswith("get_imperative_"))
async def get_imperative_form(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data["data"]:
        await callback.message.answer("we already have it")
    else:
        await callback.message.answer("нужно отправить запрос")
    await callback.message.answer(callback.data)


@router.callback_query(F.data.startswith("get_passive_"))
async def get_imperative_form(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data["data"]:
        await callback.message.answer("we already have it")
    else:
        await callback.message.answer("нужно отправить запрос")
        data = await utils.get_or_add_word(
            {
                "telegram_id": message.chat.id,
                "word": message.text,
                "message_id": message.message_id,
            }
        )
    await callback.message.answer(str(data["data"]))
