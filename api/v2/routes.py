from flask import Blueprint, request, jsonify
from utils import get_db_connection
from config import BT_API_KEY
import requests
import json

# Загрузка данных из services.json
with open('services.json', 'r', encoding='utf-8') as file:
    services = json.load(file)

v2_blueprint = Blueprint('v2', __name__)

# Пример данных (в реальном проекте используйте базу данных)
orders = []
order_id_counter = 1

def create_order_on_external_api(service_id, link, quantity):
    url = "https://boosttelega.online/api/v2"
    params = {
        "action": "add",
        "service": service_id,
        "link": link,
        "quantity": quantity,
        "key": BT_API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка запроса: {response.text}")  # Вывод текста ошибки
        return {"error": f"Request failed with status code {response.status_code}"}


@v2_blueprint.route('/create_order', methods=['GET'])
def create_order():
    global order_id_counter

    # Получаем данные из параметров строки запроса
    service_id = request.args.get('id', type=int)
    link = request.args.get('link')
    quantity = request.args.get('quantity', type=int)
    key = request.args.get('key')

    # Проверяем, что все параметры переданы
    if not all([service_id, link, quantity, key]):
        return jsonify({"error": "Missing parameters"}), 400

    # Проверяем API-ключ в базе данных
    conn = get_db_connection()
    cursor = conn.cursor()

    # Выполняем запрос к базе данных
    cursor.execute('SELECT * FROM boosttelega WHERE api_key = ?', (key,))
    user = cursor.fetchone()  # Получаем первую строку результата
    conn.close()

    # Если ключ не найден
    if not user:
        return jsonify({"error": "Invalid API key"}), 401

    # Проверяем, что услуга существует
    service = services.get(str(service_id))

    if not service:
        return jsonify({"error": "Service not found"}), 404

    # Проверяем минимальное количество
    if quantity < service['minimum']:
        return jsonify({"error": f"Minimum quantity is {service['minimum']}"}), 400

    # Создаем заказ
    order = {
        "id": order_id_counter,
        "service_id": service_id,
        "link": link,
        "quantity": quantity,
        "price": service['price'] * quantity
    }
    orders.append(order)
    order_id_counter += 1

    # Создаем заказ на внешнем API
    external_service_id = service['bt_id']  # Это будет 204 для id=7
    external_order_response = create_order_on_external_api(external_service_id, link, quantity)

    # Возвращаем ответ
    return jsonify({"order": order["id"], "external_order": external_order_response}), 200



