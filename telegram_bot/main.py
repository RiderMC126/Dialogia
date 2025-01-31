from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.fsm.state import State, StatesGroup
from config import TELEGRAM_BOT_TOKEN, admin_id, DATABASE_URL
from keyboards.keyboards_admins import index_keyboard_admins, gohome_keyboard_admins
import logging
import asyncio
import sys
import sqlite3
import os


bot = Bot(TELEGRAM_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher()
router = Router()

@dp.message(Command('start'))
async def index(message: types.Message):
    if message.from_user.id == admin_id:
        await bot.send_message(message.chat.id, text="Привет, Админ! Что нужно?", reply_markup=index_keyboard_admins())
    else:
        await bot.send_message(message.chat.id, text="Доступ заблокирован!")


@dp.callback_query(F.data == "count_users")
async def price(callback: types.CallbackQuery):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute('SELECT login FROM users')
    users = cursor.fetchall()
    user_count = len(users)
    user_list = "\n".join([user[0] for user in users])
    cursor.execute('SELECT login FROM users WHERE role = ?', ('Администрация',))
    admins = cursor.fetchall()
    admin_count = len(admins)
    admin_list = "\n".join([admin[0] for admin in admins])
    conn.close()

    await bot.send_message(callback.message.chat.id,
                           text=f"---------------------------\nСписок всех пользователей:\n{user_list}\n---------------------------\nОбщее количество пользователей - {user_count} человек\n---------------------------\nСписок Администрации:\n{admin_list}\n---------------------------\nОбщее количество администраторов - {admin_count} человек",
                           reply_markup=gohome_keyboard_admins())
    await callback.answer()

@dp.callback_query(F.data == "gohome")
async def price(call: types.CallbackQuery):
    await bot.send_message(call.message.chat.id, text="Привет, Админ! Что нужно?", reply_markup=index_keyboard_admins())
    await callback.answer()



async def main() -> None:
    bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

