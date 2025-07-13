from aiogram import html, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import dotenv

dotenv.load_dotenv()

router = Router()


@router.message(Command("start"))
async def example_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(html.quote("Your message:") + message.text)
