from flask import Flask, render_template, request, redirect, url_for, session, g, jsonify, flash
from fastapi import FastAPI
from urllib.parse import quote
from starlette.middleware.wsgi import WSGIMiddleware
from werkzeug.utils import secure_filename
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram_bot.database import get_user_info
import sqlite3
import hashlib
from capcha import generate_captcha
from config import *
from utils import *
from db import create_db
from ai_bot import generate_response
import datetime
import pytz
import sys
import os
import logging
import requests
from logging.handlers import RotatingFileHandler
import asyncio
import threading


# Инициализация приложения Flask
app = Flask(__name__)
fastapi_app = FastAPI()
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = "static/images/"
LOG_FOLDER = 'logs'
SERVER_LOG_FOLDER = 'server_logs'
NONE_AVATAR_FOLDER = 'static/images/none_avatar.png'


# Настройка политики событийного цикла для Windows
setup_event_loop_policy()
# Создаем папку для логов, если она не существует
create_log_folder(LOG_FOLDER)
# Создаем папку для сервервых логов, если она не существует
create_serverlog_folder(SERVER_LOG_FOLDER)
# Создание базы данных при запуске приложения
create_database()


# Обновляем время последнего онлайна пользователя
def update_online():
    if 'username' in session:
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()

        # Получаем текущее время и добавляем 3 часа
        current_time = datetime.datetime.now()# + datetime.timedelta(hours=3)

        # Форматируем время в строку, совместимую с SQLite
        time_string = current_time.strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute('UPDATE users SET last_online=? WHERE login=?', (time_string, session['username']))
        conn.commit()
        conn.close()

# Маршрут для главной страницы
@app.route("/")
def index():
    write_to_log(message="Зашли на сайт", folder=LOG_FOLDER)
    update_online()
    title = "Dialogia"
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM categories')
    rows = cursor.fetchall()
    categories = []
    for row in rows:
        category = {'id': row[0], 'name': row[1]}
        cursor.execute('SELECT * FROM forums WHERE category_id=?', (row[0],))
        forums_rows = cursor.fetchall()
        forums = []
        for forum_row in forums_rows:
            forum = {'id': forum_row[0], 'name': forum_row[2]}
            forums.append(forum)
        category['forums'] = forums
        categories.append(category)
    conn.close()
    return render_template("index.html", title=title, categories=categories)

# Маршрут для входа в систему
@app.route('/login', methods=['GET', 'POST'])
def login():
    update_online()
    title = "Вход"
    error = None
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        try:
            conn = sqlite3.connect('db.db')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE login=? AND password=?', (login, hashed_password))
            user = cursor.fetchone()
            if user:
                # Проверяем статус блокировки
                cursor.execute('SELECT blocked FROM users WHERE login=?', (login,))
                blocked_status = cursor.fetchone()[0]
                if blocked_status == "YES":
                    conn.close()
                    return render_template('blocked.html', title="Аккаунт заблокирован")

                write_to_log(message=f"Пользователь {login} вошёл в аккаунт", folder=LOG_FOLDER)
                session['logged_in'] = True
                session['username'] = login
                conn.close()
                return redirect(url_for('index'))
            else:
                error = 'Неправильный логин или пароль'
        except sqlite3.Error as e:
            error = 'Ошибка авторизации: ' + str(e)
        finally:
            if conn:
                conn.close()
    return render_template('login.html', title=title, error=error)


# Маршрут для регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    update_online()
    title = "Регистрация"
    error = None
    if request.method == 'GET':
        captcha_text, _ = generate_captcha()
        session['captcha_text'] = captcha_text
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        email = request.form['email']
        user_captcha = request.form['captcha']

        # Проверка капчи
        if user_captcha != session['captcha_text']:
            error = 'Неправильная капча'
            captcha_text, _ = generate_captcha()
            session['captcha_text'] = captcha_text
        # Проверка подтверждения пароля
        elif password != confirm_password:
            error = 'Пароли не совпадают'
            captcha_text, _ = generate_captcha()
            session['captcha_text'] = captcha_text
        else:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            try:
                conn = sqlite3.connect('db.db')
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE login=?', (login,))
                write_to_log(message=f"Пользователь {login} зарегистрировался", folder=LOG_FOLDER)
                user = cursor.fetchone()
                if user:
                    error = 'Логин уже существует'
                    captcha_text, _ = generate_captcha()
                    session['captcha_text'] = captcha_text
                else:
                    utc_time = datetime.datetime.utcnow()
                    local_time = utc_time.astimezone(pytz.timezone('Europe/Moscow'))
                    local_time = local_time + datetime.timedelta(hours=3)
                    local_time = local_time.strftime('%Y-%m-%d %H:%M:%S')

                    # Генерируем API-ключ
                    api_key = generate_api_key()

                    # Вставляем данные пользователя в таблицу users
                    cursor.execute(
                        'INSERT INTO users (login, password, email, role, registration_time) VALUES (?, ?, ?, ?, ?)',
                        (login, hashed_password, email, 'Пользователь', local_time))
                    conn.commit()

                    # Получаем ID только что зарегистрированного пользователя
                    user_id = cursor.lastrowid

                    # Вставляем API-ключ в таблицу bt_api
                    cursor.execute('INSERT INTO boosttelega (user_id, api_key) VALUES (?, ?)', (user_id, api_key))
                    conn.commit()
                    conn.close()

                    session['logged_in'] = True
                    session['username'] = login

                    return redirect(url_for('index'))
            except sqlite3.Error as e:
                error = 'Ошибка регистрации: ' + str(e)
                captcha_text, _ = generate_captcha()
                session['captcha_text'] = captcha_text
    return render_template('register.html', title=title, error=error)


# Маршрут для отображения категории
@app.route('/category/<int:category_id>')
def category(category_id):
    update_online()
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM categories WHERE id=?', (category_id,))
    category = cursor.fetchone()
    cursor.execute('SELECT * FROM forums WHERE category_id=?', (category_id,))
    forums = cursor.fetchall()
    cursor.execute('SELECT * FROM threads WHERE forum_id IN (SELECT id FROM forums WHERE category_id=?)', (category_id,))
    threads = cursor.fetchall()
    conn.close()
    return render_template('category.html', category=category, forums=forums, threads=threads)

# Маршрут для отображения форума
@app.route('/forum/<int:forum_id>')
def forum(forum_id):
    update_online()
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    cursor.execute('PRAGMA table_info(forums)')
    cursor.execute('SELECT * FROM forums WHERE id=?', (forum_id,))
    forum_data = cursor.fetchone()
    cursor.execute('SELECT * FROM threads WHERE forum_id=?', (forum_id,))
    threads = cursor.fetchall()
    conn.close()
    if forum_data is None:
        return 'Форум не найден'
    else:
        return render_template('forum.html', forum=forum_data, threads=threads)

# Маршрут для отображения тем
@app.route('/thread/<int:thread_id>')
def thread(thread_id):
    update_online()
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()

    # Получаем данные темы
    cursor.execute('SELECT * FROM threads WHERE id=?', (thread_id,))
    thread_data = cursor.fetchone()

    # Получаем посты для темы
    cursor.execute('''
        SELECT p.content, p.name, p.created_at, COALESCE(u.avatar, 'none_avatar.png') as avatar
        FROM posts p
        LEFT JOIN users u ON p.user_id = u.id  
        WHERE p.thread_id = ?
    ''', (thread_id,))
    posts = cursor.fetchall()

    # Получаем аватарку текущего пользователя
    avatar = 'none_avatar.png'
    if 'username' in session:
        username = session['username']
        cursor.execute('SELECT avatar FROM users WHERE login=?', (username,))
        avatar_result = cursor.fetchone()
        if avatar_result and avatar_result[0]:
            avatar = avatar_result[0]

    conn.close()

    if thread_data is None:
        return 'Тема не найдена'
    else:
        return render_template('thread.html', thread=thread_data, posts=posts, avatar=avatar,
                               username=session.get('username', 'Гость'))



# Маршрут для отправки поста
@app.route('/send_post', methods=['POST'])
def send_post():
    update_online()
    post_content = request.form['post']
    thread_id = request.args.get('thread_id')
    if 'username' not in session:
        return render_template("register.html", title="Регистрация"), 401

    try:
        conn = sqlite3.connect("db.db")
        cursor = conn.cursor()

        # Получаем user_id на основе имени пользователя
        username = session['username']
        cursor.execute('SELECT id FROM users WHERE login=?', (username,))
        user_result = cursor.fetchone()
        if user_result is None:
            return 'Пользователь не найден', 404
        user_id = user_result[0]

        utc_time = datetime.datetime.utcnow()
        local_time = pytz.utc.localize(utc_time).astimezone(pytz.timezone('Europe/Moscow'))
        local_time = local_time.strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute('INSERT INTO posts (thread_id, user_id, content, name, created_at) VALUES (?, ?, ?, ?, ?)',
                       (thread_id, user_id, post_content, username, local_time))
        conn.commit()
        conn.close()
        write_to_log(message=f"Пользователь {username} написал пост", folder=LOG_FOLDER)
        return redirect(url_for('thread', thread_id=thread_id))
    except sqlite3.Error as e:
        return 'Ошибка отправки поста: ' + str(e)

# Маршрут для отображения профиля пользователя
@app.route('/members/<username>')
def profile(username):
    update_online()
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    cursor.execute('SELECT avatar, last_online, role, registration_time, email FROM users WHERE login=?', (username,))
    user_data = cursor.fetchone()

    if user_data is None:
        conn.close()
        return render_template('404.html'), 404

    avatar, last_online_time, role, registration_date, email = user_data

    # Преобразуем строку времени в объект datetime
    last_online_time = datetime.datetime.strptime(last_online_time, '%Y-%m-%d %H:%M:%S')

    # Получаем текущее время
    now = datetime.datetime.now()
    print(f"ВРЕМЯ СЕЙЧАС - {now}")

    # Вычисляем разницу
    time_diff = now - last_online_time

    if time_diff < datetime.timedelta(minutes=5):
        last_online = "в сети"
    elif time_diff < datetime.timedelta(hours=1):
        minutes = time_diff.seconds // 60
        last_online = f"Был в сети {pluralize_russian(minutes, 'минуту', 'минуты', 'минут')} назад"
    elif time_diff < datetime.timedelta(days=1):
        hours = time_diff.seconds // 3600
        last_online = f"Был в сети {pluralize_russian(hours, 'час', 'часа', 'часов')} назад"
    elif time_diff < datetime.timedelta(days=30):
        days = time_diff.days
        last_online = f"Был в сети {pluralize_russian(days, 'день', 'дня', 'дней')} назад"
    else:
        last_online = last_online_time.strftime('%d.%m.%Y %H:%M')

    registered_datetime = datetime.datetime.strptime(registration_date, '%Y-%m-%d %H:%M:%S')
    days_registered = (datetime.datetime.now() - registered_datetime).days
    if days_registered == 0:
        days_registered = 1

    conn.close()

    is_own_profile = 'username' in session and username == session['username']

    return render_template('profile.html',
                           username=username,
                           avatar=avatar,
                           last_online=last_online,
                           role=role,
                           days_registered=days_registered,
                           email=email,
                           is_own_profile=is_own_profile)



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

# Маршрут для изменения пароля
@app.route('/change_password', methods=['POST'])
def change_password():
    if 'username' not in session:
        return 'Вы должны быть авторизованы для изменения пароля', 401

    new_password = request.form['new-password']
    confirm_password = request.form['confirm-password']

    if new_password != confirm_password:
        return 'Пароли не совпадают', 400

    hashed_password = hashlib.sha256(new_password.encode()).hexdigest()

    try:
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET password=? WHERE login=?', (hashed_password, session['username']))
        conn.commit()
        conn.close()
        write_to_log(message=f"Пользователь {session['username']} сменил пароль", folder=LOG_FOLDER)
        return redirect(url_for('profile', username=session['username']))
    except sqlite3.Error as e:
        return 'Ошибка изменения пароля: ' + str(e)

# Маршрут для изменения email
@app.route('/change_email', methods=['POST'])
def change_email():
    if 'username' not in session:
        return 'Вы должны быть авторизованы для изменения email', 401

    new_email = request.form['email']

    try:
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET email=? WHERE login=?', (new_email, session['username']))
        conn.commit()
        conn.close()
        write_to_log(message=f"Пользователь {session['username']} сменил почту", folder=LOG_FOLDER)
        return redirect(url_for('profile', username=session['username']))
    except sqlite3.Error as e:
        return 'Ошибка изменения email: ' + str(e)

# Обработчик изменение аватара
@app.route('/change_avatar', methods=['POST'])
def change_avatar():
    if 'avatar' in request.files:
        avatar_file = request.files['avatar']
        if avatar_file.filename:
            # Получаем имя пользователя из сессии
            username = session['username']

            # Создаем папку для аватаров, если она не существует
            avatar_dir = os.path.join(app.root_path, 'static', 'images')
            if not os.path.exists(avatar_dir):
                os.makedirs(avatar_dir)

            # Сохраняем файл с именем пользователя
            filename = f"{username}.jpg"  # Используем формат .jpg, но можно сохранять в исходном формате
            avatar_path = os.path.join(avatar_dir, filename)

            # Проверка типа файла
            if allowed_file(avatar_file.filename):
                avatar_file.save(avatar_path)

                # Обновляем аватар в базе данных
                conn = sqlite3.connect('db.db')
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET avatar=? WHERE login=?', (filename, username))
                conn.commit()
                conn.close()
                write_to_log(message=f"Пользователь {session['username']} сменил аватарку", folder=LOG_FOLDER)

                return redirect(url_for('profile', username=username))
            else:
                return 'Недопустимый тип файла', 400
        else:
            return 'Файл не выбран', 400
    else:
        return 'Файл не передан в запросе', 400




# Маршрут для чата с ИИ
@app.route('/ai-chat', methods=['GET', 'POST'])
def ai_chat():
    update_online()
    title = "AI Chat"
    if request.method == 'POST':
        # Получаем текст запроса от пользователя
        prompt = request.form.get('prompt')
        write_to_log(message=f"Пользователь {session['username']} спросил у ИИ: {prompt}", folder=LOG_FOLDER)
        # Генерируем ответ с помощью ИИ
        answer = generate_response(f"Всегда отвечай на русском!\nЗапрос: {prompt}")
        # Возвращаем ответ в формате JSON
        return jsonify({'answer': answer})
    else:
        # Если это GET-запрос, просто отображаем страницу
        return render_template('ai-chat.html', title=title, answer="")

# Обработка списка админов
@app.route('/admin_list')
def admin_list():
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    # Получаем логин администраторов
    cursor.execute('SELECT login FROM users WHERE role = ?', ('Администратор',))
    admins = cursor.fetchall()
    # Получаем логин модераторов
    cursor.execute('SELECT login FROM users WHERE role = ?', ('Модератор',))
    moderators = cursor.fetchall()
    # Получаем логин программистов
    cursor.execute('SELECT login FROM users WHERE role = ?', ('Программист',))
    programmers = cursor.fetchall()
    conn.close()
    title = "Admin List"
    return render_template("admin_list.html", title=title, admins=admins, moderators=moderators, programmers=programmers)

@app.route('/services')
def services():
    title = "Сервисы"
    return render_template('services.html', title=title)


@app.route('/telegram-boost')
def telegram_boost():
    title = "Telegram Boost"
    if 'username' in session:
        username = session['username']
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE login=?', (username,))
        user_id = cursor.fetchone()[0]

        cursor.execute('SELECT api_key FROM boosttelega WHERE user_id=?', (user_id,))
        api_key = cursor.fetchone()

        if api_key:
            api_key = api_key[0]
        else:
            api_key = "API-ключ не найден"

        conn.close()
    else:
        return redirect(url_for('login'))  # Если пользователь не авторизован, перенаправляем на страницу входа

    return render_template("telegram-boost.html", title=title, api_key=api_key)

@app.route('/change_api_token', methods=['POST'])
def change_api_token():
    if 'username' not in session:
        return jsonify({'error': 'Пользователь не авторизован'}), 401

    username = session['username']
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    # Получаем ID пользователя
    cursor.execute('SELECT id FROM users WHERE login=?', (username,))
    user_id = cursor.fetchone()

    # Генерируем новый API-ключ
    new_api_key = generate_api_key()

    if user_id:
        # Проверяем, есть ли уже запись в boosttelega
        cursor.execute('SELECT * FROM boosttelega WHERE user_id=?', (user_id[0],))
        existing_record = cursor.fetchone()

        if existing_record:
            # Обновляем существующую запись
            cursor.execute('UPDATE boosttelega SET api_key=? WHERE user_id=?', (new_api_key, user_id[0]))
        else:
            # Создаем новую запись
            cursor.execute('INSERT INTO boosttelega (user_id, api_key) VALUES (?, ?)', (user_id[0], new_api_key))

        conn.commit()
        conn.close()
        return jsonify({'api_key': new_api_key}), 200
    else:
        conn.close()
        return jsonify({'error': 'Пользователь не найден'}), 404


@app.route('/create_order', methods=['POST'])
def create_order():
    if 'username' not in session:
        return jsonify({'error': 'Пользователь не авторизован'}), 401

    username = session['username']
    data = request.json
    service_id = data.get('service_id')
    link = data.get('link')
    quantity = data.get('quantity')
    price = data.get('price')  # Общая стоимость заказа

    if not all([service_id, link, quantity, price]):
        return jsonify({'error': 'Не все данные предоставлены'}), 400

    # Преобразуйте цену в float
    try:
        price = float(price)
    except ValueError:
        return jsonify({'error': 'Неправильный формат цены'}), 400

    # Получаем текущий баланс пользователя
    current_balance = get_user_balance(username)

    # Проверяем, достаточно ли средств
    if current_balance < price:
        return jsonify({'error': 'Недостаточно средств на балансе'}), 400

    # Снимаем средства с баланса
    new_balance = round(current_balance - price, 2)
    update_user_balance(username, new_balance)

    # Создаем заказ через API
    api_key = 'heJeyxWJLszVV2oAy4CPbcFOVWwXj14ZQoUZpYgbJfWHzDXMms5rMeAjKPrz'
    api_url = f'https://boosttelega.online/api/v2?action=add&service={service_id}&link={quote(link)}&quantity={quantity}&key={api_key}'

    try:
        response = requests.get(api_url)
        response_data = response.json()

        if response_data.get('order'):
            return jsonify({'message': 'Заказ успешно создан', 'order_id': response_data['order'], 'new_balance': f"{new_balance:.2f}"}), 200
        else:
            # Если заказ не создан, возвращаем средства
            update_user_balance(username, current_balance)
            return jsonify({'error': 'Ошибка при создании заказа'}), 500

    except Exception as e:
        # В случае ошибки возвращаем средства
        update_user_balance(username, current_balance)
        return jsonify({'error': str(e)}), 500



@app.route("/admin-panel")
def admin_panel():
    if 'username' not in session:
        return redirect(url_for('login'))  # Если пользователь не авторизован, перенаправляем на страницу входа

    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    cursor.execute('SELECT role FROM users WHERE login=?', (session['username'],))
    user_role = cursor.fetchone()
    conn.close()

    if user_role and user_role[0] == 'Администратор':
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()

        cursor.execute('SELECT login FROM users')
        users = cursor.fetchall()
        user_count = len(users)
        title = "Admin Panel"
        return render_template('admin_panel.html', title=title, user_count=user_count)
    else:
        return render_template("403.html"), 403  # Если пользователь не является администратором, показываем ошибку 403

@app.route('/search_threads')
def search_threads():
    query = request.args.get('query', '')
    if len(query) < 1:
        return jsonify([])

    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM threads WHERE title LIKE ? LIMIT 5", ('%' + query + '%',))
    results = cursor.fetchall()
    conn.close()

    threads = [{'id': row[0], 'title': row[1]} for row in results]
    return jsonify(threads)


# Обработка выхода из аккаунта
@app.route('/logout')
def logout():
    write_to_log(message=f"Пользователь {session.get('username', 'Unknown')} вышел из аккаунта", folder=LOG_FOLDER)
    update_online()
    #session['logged_in'] = False # Так было раньше
    session.clear()  # Полностью очищаем сессию
    return redirect(url_for('index'))


# Добавление пользователя в контекст шаблона
@app.context_processor
def inject_user():
    user = None
    if 'user_id' in session:
        user = session['username']
    return dict(user=user)

# Обновляет капчу при регистрации
@app.route('/refresh_captcha')
def refresh_captcha():
    captcha_text, _ = generate_captcha()
    session['captcha'] = captcha_text
    return redirect(url_for('register'))

# Обрабатываем ошибку 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Запуск приложения
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    write_to_serverlog("Сервер запущен!", SERVER_LOG_FOLDER)
    try:
        # Код запуска вашего сервера
        app.run(debug=True, host="127.0.0.1", port=5000)
        #app.wsgi_app = WSGIMiddleware(fastapi_app ,app.wsgi_app)
    except Exception as e:
        write_to_serverlog(f'Ошибка при запуске сервера: {e}', SERVER_LOG_FOLDER)
    finally:
        write_to_serverlog('Сервер остановлен', SERVER_LOG_FOLDER)


