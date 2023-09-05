from os import getenv

from aiogram import Bot
from aiogram.types import FSInputFile
from dotenv import load_dotenv

load_dotenv()
bot = Bot(token=getenv('BOT_TOKEN'), parse_mode='HTML')
template = '🗞 <i>Новое уведомление</i>\n\n{}'


async def send_text(chat_id: int, text: str):
    await bot.send_message(chat_id, template.format(text))


async def send_files(chat_id: int, text: str, files: list[str]):
    await bot.send_message(chat_id, template.format(text))
    for f in files:
        await bot.send_document(chat_id, document=FSInputFile(f))
