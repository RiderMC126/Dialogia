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
from database import get_user_info, create_categories, get_categories, create_forums, get_forums, create_threads, block_user_by_nickname, get_user_list, get_blocked_user_list, unblock_user_by_nickname
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

class Users(StatesGroup):
    blocked_nickname = State()
    unblock_nickname = State()


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
    await bot.send_message(callback.message.chat.id, text="Введите название категории:", reply_markup=gohome_keyboard_admins())
    await callback.answer()
    await state.set_state(Create.categories)

@dp.message(StateFilter(Create.categories))
async def categories_name(message: types.Message, state: FSMContext):
    await state.update_data(categories_name=message.text)
    try:
        new_category_id = create_categories(message.text)
        if new_category_id:
            await message.reply(f"Категория '{message.text}' успешно создана с ID: {new_category_id}")
        else:
            await message.reply("Произошла ошибка при создании категории.")
    except sqlite3.Error as error:
        await message.reply(f"Произошла ошибка: {error}")

    await state.clear()
    await message.answer("Что дальше?", reply_markup=index_keyboard_admins())

@dp.callback_query(F.data == "create_forums")
async def create(callback: types.CallbackQuery, state: FSMContext):
    categories = get_categories()
    if categories:
        category_list = "\n".join([f"{cat[0]} | {cat[1]}\n----------------------" for cat in categories])
        await bot.send_message(callback.message.chat.id, text=f"Список категорий:\n{category_list}")
    else:
        await bot.send_message(callback.message.chat.id, text=f"Не удалось получить список категорий")
    await bot.send_message(callback.message.chat.id, text=f"Введите category_id и название для forum:\nПример: 1 Название", reply_markup=gohome_keyboard_admins())
    await callback.answer()
    await state.set_state(Create.forums)

@dp.message(StateFilter(Create.forums))
async def forums_name(message: types.Message, state: FSMContext):
    await state.update_data(forums_name=message.text)
    try:
        category_id, forum_name = message.text.split(' ', 1)
        category_id = int(category_id)

        new_forum_id = create_forums(category_id, forum_name)

        if new_forum_id:
            await message.reply(f"Форум '{forum_name}' успешно создан с ID: {new_forum_id}")
        else:
            await message.reply("Произошла ошибка при создании форума.")
    except ValueError:
        await message.reply(
            "Неправильный формат. Пожалуйста, введите ID категории и название форума, разделенные пробелом.")

    await state.clear()
    await message.answer("Что дальше?", reply_markup=index_keyboard_admins())

@dp.callback_query(F.data == "create_threads")
async def create(callback: types.CallbackQuery, state: FSMContext):
    forums = get_forums()
    if forums:
        forum_list = "\n".join([f"{forum[0]} | {forum[2]}" for forum in forums])
        await bot.send_message(callback.message.chat.id, text=f"Список форумов:\n{forum_list}")
    else:
        await bot.send_message(callback.message.chat.id, text="Не удалось получить список форумов")
    await bot.send_message(callback.message.chat.id, text="Введите forum_id и название для threads:\nПример: 1 Название темы", reply_markup=gohome_keyboard_admins())
    await callback.answer()
    await state.set_state(Create.threads)

@dp.message(StateFilter(Create.threads))
async def threads_name(message: types.Message, state: FSMContext):
    await state.update_data(threads_name=message.text)
    try:
        forum_id, thread_name = message.text.split(' ', 1)
        forum_id = int(forum_id)

        new_thread_id = create_threads(forum_id, thread_name)

        if new_thread_id:
            await message.reply(f"Тема '{thread_name}' успешно создана с ID: {new_thread_id}")
        else:
            await message.reply("Произошла ошибка при создании темы.")
    except ValueError:
        await message.reply(
            "Неправильный формат. Пожалуйста, введите ID форума и название темы, разделенные пробелом.")

    await state.clear()
    await message.answer("Что дальше?", reply_markup=index_keyboard_admins())

@dp.callback_query(F.data == "blocked_users")
async def blocked_users(callback: types.CallbackQuery, state: FSMContext):
    user_list = get_user_list()  # Новая функция
    await bot.send_message(callback.message.chat.id, text=f"Список пользователей:\n{user_list}")
    await bot.send_message(callback.message.chat.id, text="Напишите ник пользователя, которого нужно заблокировать:", reply_markup=gohome_keyboard_admins())
    await callback.answer()
    await state.set_state(Users.blocked_nickname)


@dp.message(StateFilter(Users.blocked_nickname))
async def block_user(message: types.Message, state: FSMContext):
    nickname = message.text
    result = block_user_by_nickname(nickname)  # Новая функция, которую нужно создать
    if result:
        await message.reply(f"Пользователь {nickname} успешно заблокирован.")
    else:
        await message.reply(
            f"Не удалось заблокировать пользователя {nickname}. Возможно, пользователь не существует или уже заблокирован.")

    await state.clear()
    await message.answer("Что дальше?", reply_markup=index_keyboard_admins())


@dp.callback_query(F.data == "unblocked_users")
async def unblocked_users(callback: types.CallbackQuery, state: FSMContext):
    blocked_user_list = get_blocked_user_list()
    if blocked_user_list:
        await bot.send_message(callback.message.chat.id,
                               text=f"Список заблокированных пользователей:\n{blocked_user_list}")
        await bot.send_message(callback.message.chat.id,
                               text="Напишите ник пользователя, которого нужно разблокировать:",
                               reply_markup=gohome_keyboard_admins())
        await state.set_state(Users.unblock_nickname)
    else:
        await bot.send_message(callback.message.chat.id, text="Нет заблокированных пользователей.",
                               reply_markup=gohome_keyboard_admins())
    await callback.answer()


@dp.message(StateFilter(Users.unblock_nickname))
async def unblock_user(message: types.Message, state: FSMContext):
    nickname = message.text
    result = unblock_user_by_nickname(nickname)
    if result:
        await message.reply(f"Пользователь {nickname} успешно разблокирован.")
    else:
        await message.reply(
            f"Не удалось разблокировать пользователя {nickname}. Возможно, пользователь не существует или уже разблокирован.")

    await state.clear()
    await message.answer("Что дальше?", reply_markup=index_keyboard_admins())


async def main() -> None:
    bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

