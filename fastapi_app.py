from fastapi import FastAPI, Query
from utils import *
from typing import Optional
import sqlite3

app = FastAPI()

# Список услуг
services = {
    1: {
        "text": '⚡️ BOOST channel | 25-30 DAYS',
        "price": 42,
        "price_text": '42000₽ за 1000',
        "description": 'ССЫЛКУ НУЖНО УКАЗЫВАТЬ НА САМ КАНАЛ<br>ССЫЛКА ДОЛЖНА БЫТЬ БЕЗ ЗАЯВОК<br><br>Бусты на закрытые и открытые каналы.<br>Буст держится 25-30 дней.<br>⚡️ Позволяет публиковать истории.<br>⭐ Личная база аккаунтов, прямой поставщик услуг.',
        "minimum": 1,
        "bt_id": 198
    },
    2: {
        "text": '⚡️ BOOST channel | 1 DAYS',
        "price": 4,
        "price_text": '4000₽ за 1000',
        "description": 'ССЫЛКУ НУЖНО УКАЗЫВАТЬ НА САМ КАНАЛ<br>ССЫЛКА ДОЛЖНА БЫТЬ БЕЗ ЗАЯВОК<br><br>Бусты на закрытые и открытые каналы.<br>Буст держится 1 день.<br><br>⚡️ Позволяет публиковать истории.<br>⭐ Личная база аккаунтов, прямой поставщик услуг.',
        "minimum": 1,
        "bt_id": 181
    },
    3: {
        "text": '🤖 Premium BOT START MIX',
        "price": 0.75,
        "price_text": '750₽ за 1000',
        "description": 'Запуск вашего бота с прем акаунтов.<br><br>NON DROP<br><br>Geo MIX',
        "minimum": 1,
        "bt_id": 205
    },
    4: {
        "text": '🤖 Premium BOT START RU',
        "price": 8.5,
        "price_text": '850₽ за 1000',
        "description": 'Запуск вашего бота с прем акаунтов.<br><br>NON DROPE<br><br>Geo RU',
        "minimum": 1,
        "bt_id": 206
    },
    5: {
        "text": '🤖 BOT START RU',
        "price": 0.2,
        "price_text": '200₽ за 1000',
        "description": 'Запуск вашего бота \n<br><br>аккаунт заходят без прем подписки\n<br><br>Geo RU',
        "minimum": 1,
        "bt_id": 207
    },
    6: {
        "text": '⭐️ 14+ days subscribers',
        "price": 0.045,
        "price_text": '45₽ за 1000',
        "description": 'Ссылка должна быть указана на канал без заявок<br><br>Телеграм подписчики.<br>Отписки через 14+ дней<br>Моментальный запуск',
        "minimum": 1,
        "bt_id": 203
    },
    7: {
        "text": '⭐️ 30+ days subsrcibers',
        "price": 0.08,
        "price_text": '80₽ за 1000',
        "description": 'Ссылка должна быть указана на канал без заявок<br><br>Телеграм подписчики.<br>Отписки через 30+ дней<br>Моментальный запуск',
        "minimum": 1,
        "bt_id": 204
    },
    8: {
        "text": '⭐️ 180+ days subsrcibers',
        "price": 0.3,
        "price_text": '300₽ за 1000',
        "description": 'Без дропа минимум 180 дней!<br><br>🔍Подписчики присоединяются через поиск!<br><br>❤️ У 100% аккаунтов есть фотографии, имена соответствуют аватаркам.<br><br>Гео - МИКС.<br><br>Правила:<br>- Запрещенные каналы: наркотики, лохотрон, порно, пустые каналы.<br>- Каналы должны быть созданы более 2 недель!!!<br>- Должно быть минимум 3 поста на канале. Желательно в разные дни.<br>- Мы не гарантируем возврат средств за ГРУППЫ и ЧАТЫ с датой создания менее года назад.',
        "minimum": 10,
        "bt_id": 75
    },
    9: {
        "text": '👀 Просмотры на 50 постов',
        "price": 0.25,
        "price_text": '250₽ за 1000',
        "description": 'Просмотры из России на последние 50 постов на канале.<br>Попадают в статистику.<br><br>Обратите внимание: если в постах присутствуют изображения, то каждое фото будет определено системой, как отдельный пост.',
        "minimum": 100,
        "bt_id": 166
    },
    10: {
        "text": '👀 Просмотры на 20 постов',
        "price": 0.09,
        "price_text": '90₽ за 1000',
        "description": 'Просмотры из России на последние 20 постов на канале.<br>Попадают в статистику.<br><br>Обратите внимание: если в постах присутствуют изображения, то каждое фото будет определено системой, как отдельный пост.',
        "minimum": 100,
        "bt_id": 165
    },
    11: {
        "text": '👀 Просмотры на 10 постов',
        "price": 0.045,
        "price_text": '45₽ за 1000',
        "description": 'Просмотры из России на последние 5 постов на канале.<br>Попадают в статистику.<br><br>Обратите внимание: если в постах присутствуют изображения, то каждое фото будет определено системой, как отдельный пост.',
        "minimum": 100,
        "bt_id": 164
    },
    12: {
        "text": '👀 Просмотры на 1 пост',
        "price": 0.01,
        "price_text": '10₽ за 1000',
        "description": 'Указывать ссылку на пост.<br>Просмотры добавляются с русских ip адресов',
        "minimum": 100,
        "bt_id": 163
    },
}

# Подключение к базе данных
conn = sqlite3.connect('db.db')
cursor = conn.cursor()

# Загрузка ключей
cursor.execute('SELECT api_key FROM boosttelega')
valid_keys = [row[0] for row in cursor.fetchall()]
conn.close()

# Список допустимых ключей
valid_keys = []  # Загрузите ключи из базы данных

@app.get("/api/v2")
def api_v2(
    action: str = Query(...),
    service: int = Query(...),
    link: str = Query(...),
    quantity: int = Query(...),
    key: str = Query(...)
):
    if key not in valid_keys:
        return {"error": "Недопустимый ключ"}

    if action != "add":
        return {"error": "Неправильное действие"}

    if service not in services:
        return {"error": "Неправильная услуга"}

    if quantity < services[service]["minimum"]:
        return {"error": f"Минимальное количество для услуги {services[service]['text']} равно {services[service]['minimum']}"}

    # Создание заказа
    order_id = create_order(service, link, quantity)
    if order_id:
        return {"message": "Заказ создан", "order_id": order_id}
    else:
        return {"error": "Ошибка при создании заказа"}

def create_order(service_id, link, quantity):
    # Логика создания заказа здесь
    # Например, сохранение в базе данных
    # Для демонстрации просто возвращаем случайный ID
    import random
    return random.randint(1000, 9999)

