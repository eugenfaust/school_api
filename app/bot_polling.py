import asyncio
import datetime
import logging
import random
import string
import sys
from os import getenv

import pytz
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, WebAppInfo, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from dotenv import load_dotenv

from sql_app.crud import get_user_by_tg_hash, get_active_schedules_with_tg
from sql_app.database import SessionLocal

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()


def generate_tg_hash():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(12))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def check_schedules(bot):
    db = next(get_db())
    tzdata = pytz.timezone('Europe/Moscow')
    while True:
        await asyncio.sleep(60)
        cur_date = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
        schedules = get_active_schedules_with_tg(db, cur_date)
        for s in schedules:
            if s.scheduled_at - cur_date < datetime.timedelta(hours=1):
                await bot.send_message(s.user.tg_id, "⏰ Скоро занятие!\n\n"
                                                     "На сегодня запланировано занятие в <b>{}</b>"
                                       .format(s.scheduled_at.astimezone(tzdata).strftime("%H:%M")))
                s.tg_notified = True
        db.commit()

@dp.callback_query()
async def clb_game(clb: CallbackQuery):
    await clb.answer(url="https://eugenfaust.github.io/react-slots/")

@dp.message(Command('test'))
async def command_test(message: Message):
    builder = InlineKeyboardBuilder()
    url = "https://eugenfaust.github.io/react-slots/"

    builder.button(text="Slots!", web_app=WebAppInfo(url=url))
    await message.answer("Test",
                         reply_markup=builder.as_markup())
    await message.answer_game('JockerSloots')


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    args = message.text.split(' ')
    if len(args) > 1:
        tg_hash = args[1]
        db = next(get_db())
        user = get_user_by_tg_hash(db, tg_hash)
        if user:
            user.tg_id = message.from_user.id
            user.tg_hash = generate_tg_hash()
            db.commit()
            await message.answer(
                "{} теперь подключен к Telegram. Уведомления о занятиях и заданиях будут приходить сюда\n\n"
                "<b>Если</b> возникнет необходимость подключить другой Telegram, перейдите по новой ссылке "
                "в личном кабинете на сайте"
                .format(user.full_name))


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    asyncio.create_task(check_schedules(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
