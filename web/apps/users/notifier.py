from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from apps.words.notifier import build_inline_keyboard
from django.conf import settings

BOT_TOKEN = settings.BOT_TOKEN
LOGS_GROUP_ID = settings.LOGS_GROUP_ID


async def send_report(data: dict) -> str:
    async with AiohttpSession() as async_session:
        notify_bot = Bot(
            token=BOT_TOKEN,
            session=async_session,
            default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2),
        )
        try:
            await notify_bot.send_message(
                chat_id=LOGS_GROUP_ID,
                text=data["message"],
                reply_markup=build_inline_keyboard(data["inline_reply_markup"]),
            )
        except Exception as error:
            return f"Reporter error: {error}"
    return "Successfully sent report"
