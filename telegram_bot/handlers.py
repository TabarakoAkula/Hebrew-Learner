from aiogram import F, html, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
import dotenv
import utils
import keyboards
import states

dotenv.load_dotenv()

router = Router()

SEARCH_FILTER = StateFilter(*states.SearchStatesGroup.__all_states__)


@router.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    response = await utils.get_or_create_user(message.chat.id, {"telegram_username": message.chat.username})
    answer_message = "Привет, в этом боте ты можешь искать перевод слов с иврита"
    if response["data"]["New"]:
        answer_message = "Поздравляю с первым запуском🥳\n\n" + answer_message
    await message.answer(answer_message, reply_markup=keyboards.keyboard_example())
    if response["data"]["moderator"]:
        await message.answer("⚠️ У вас есть права модератора:\n\n- Редактировать категории")


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
        await message.answer(str(response["data"]))
