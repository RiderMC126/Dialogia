"""
Этот файл создан для основных основных функций и действий
"""
from db import create_db
import asyncio
import sqlite3
import datetime
from datetime import datetime
import sys
import os

# Настройка политики событийного цикла для Windows
def setup_event_loop_policy():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def create_log_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f'Папка "LOG_FOLDER" создана')
    else:
        print(f'Папка "LOG_FOLDER" уже существует')

def create_serverlog_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f'Папка "SERVER_LOG_FOLDER" создана')
    else:
        print(f'Папка "SERVER_LOG_FOLDER" уже существует')


def create_database():
    try:
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="users"')
        if cursor.fetchone() is None:
            create_db()
            print("База данных создана")
        else:
            print("База данных уже существует")
    except sqlite3.Error as e:
        print(f"Ошибка создания базы данных: {e}")


def write_to_log(message, folder):
    # Генерируем имя файла с текущей датой
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"log.{current_date}.txt"

    # Путь к файлу
    filepath = os.path.join(folder, filename)

    # Записываем сообщение в файл
    with open(filepath, 'a') as file:
        file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def write_to_serverlog(message, folder):
    # Генерируем имя файла с текущей датой
    current_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"log.{current_date}.txt"

    # Путь к файлу
    filepath = os.path.join(folder, filename)

    # Записываем сообщение в файл
    with open(filepath, 'a') as file:
        file.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")


def pluralize_russian(number, one, few, many):
    if number % 10 == 1 and number % 100 != 11:
        return f"{number} {one}"
    elif 2 <= number % 10 <= 4 and (number % 100 < 10 or number % 100 >= 20):
        return f"{number} {few}"
    else:
        return f"{number} {many}"


# Функция для получения баланса пользователя
def get_user_balance(username):
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE login = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

# Функция для обновления баланса пользователя
def update_user_balance(username, new_balance):
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = ROUND(?, 2) WHERE login = ?', (new_balance, username))
    conn.commit()
    conn.close()