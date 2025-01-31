from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.fsm.state import State, StatesGroup
from config import TELEGRAM_BOT_TOKEN, admin_id, DATABASE_URL
from keyboards.keyboards_admins import index_keyboard_admins, gohome_keyboard_admins, create_admins
from database import get_user_info, create_categories
import logging
import asyncio
import sys
import sqlite3
import os


bot = Bot(TELEGRAM_BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher()
router = Router()


class Create(StatesGroup):
    categories = State()
    forums = State()
    threads = State()



@dp.message(Command('start'))
async def index(message: types.Message):
    if message.from_user.id == admin_id:
        await bot.send_message(message.chat.id, text="Привет, Админ! Что нужно?", reply_markup=index_keyboard_admins())
    else:
        await bot.send_message(message.chat.id, text="Доступ заблокирован!")


@dp.callback_query(F.data == "count_users")
async def price(callback: types.CallbackQuery):
    user_list, user_count, admin_list, admin_count = get_user_info()

    await bot.send_message(callback.message.chat.id,
                           text=f"---------------------------\nСписок всех пользователей:\n{user_list}\n---------------------------\nОбщее количество пользователей - {user_count} человек\n---------------------------\nСписок Администрации:\n{admin_list}\n---------------------------\nОбщее количество администраторов - {admin_count} человек",
                           reply_markup=gohome_keyboard_admins())
    await callback.answer()

@dp.callback_query(F.data == "gohome")
async def price(callback: types.CallbackQuery):
    await bot.send_message(callback.message.chat.id, text="Привет, Админ! Что нужно?", reply_markup=index_keyboard_admins())
    await callback.answer()

@dp.callback_query(F.data == "create")
async def create(callback: types.CallbackQuery):
    await bot.send_message(callback.message.chat.id, text=f"Выбери то, что нужно создать: ", reply_markup=create_admins())
    await callback.answer()


@dp.callback_query(F.data == "create_category")
async def create(callback: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback.message.chat.id, text=f"Введите название категории: ", reply_markup=gohome_keyboard_admins())
    await callback.answer()
    await state.set_state(Create.categories)

@dp.message(StateFilter(Create.categories))
async def categories_name(message: types.Message, state: FSMContext):
    await state.update_data(categories_name=message.text)
    try:
        create_categories(message.text)
        await bot.send_message(message.chat.id, text=f"Успешно! Создана категория с названием: {message.text}")
    except sqlite3.Error as error:
        await bot.send_message(message.chat.id, text=f"Произошла ошибка: {error}")






async def main() -> None:
    bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

