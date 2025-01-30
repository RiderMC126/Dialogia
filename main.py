from flask import Flask, render_template, request, redirect, url_for, session, g, jsonify
from http.server import HTTPServer, BaseHTTPRequestHandler
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
from logging.handlers import RotatingFileHandler
import asyncio
import threading


# Инициализация приложения Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = 'static/images/'
LOG_FOLDER = 'logs'
NONE_AVATAR_FOLDER = 'static/images/none_avatar.png'

# Настройка политики событийного цикла для Windows
setup_event_loop_policy()
# Создаем папку для логов, если она не существует
create_log_folder(LOG_FOLDER)

# Создание базы данных при запуске приложения
create_database()

# Обновляем время последнего онлайна пользователя
def update_online():
    if 'username' in session:
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET last_online=CURRENT_TIMESTAMP WHERE login=?', (session['username'],))
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
            write_to_log(message=f"Пользователь {login} вошёл в аккаунт", folder=LOG_FOLDER)
            user = cursor.fetchone()
            if user:
                session['logged_in'] = True
                session['username'] = login
                return redirect(url_for('index'))
            else:
                error = 'Неправильный логин или пароль'
        except sqlite3.Error as e:
            error = 'Ошибка авторизации: ' + str(e)
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

                    cursor.execute(
                        'INSERT INTO users (login, password, email, role, registration_time) VALUES (?, ?, ?, ?, ?)',
                        (login, hashed_password, email, 'Пользователь', local_time))
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
    cursor.execute('SELECT * FROM threads WHERE id=?', (thread_id,))
    thread_data = cursor.fetchone()

    cursor.execute('''
        SELECT p.content, p.name, p.created_at, u.avatar
        FROM posts p
        LEFT JOIN users u ON p.user_id = u.login
        WHERE p.thread_id = ?
    ''', (thread_id,))
    posts = cursor.fetchall()

    print("Посты:", posts)  # Отладка

    hashed_login = hashlib.sha256(session['username'].encode()).hexdigest()
    cursor.execute('SELECT avatar FROM users WHERE login=?', (hashed_login,))
    avatar = cursor.fetchone()
    if avatar is not None and avatar[0] is not None:
        avatar = avatar[0]
    else:
        avatar = 'avatar_none.png'
    conn.close()

    if thread_data is None:
        return 'Тема не найдена'
    else:
        return render_template('thread.html', thread=thread_data, posts=posts, avatar=avatar,
                               username=session['username'])

# Маршрут для отправки поста
@app.route('/send_post', methods=['POST'])
def send_post():
    update_online()
    post = request.form['post']
    thread_id = request.args.get('thread_id')
    try:
        conn = sqlite3.connect("db.db")
        cursor = conn.cursor()
        hashed_login = hashlib.sha256(session['username'].encode()).hexdigest()
        utc_time = datetime.datetime.utcnow()
        local_time = utc_time.astimezone(pytz.timezone('Europe/Moscow'))  # Московское время с DST
        local_time = local_time + datetime.timedelta(hours=3)  # Добавить 3 часа
        local_time = local_time.strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('INSERT INTO posts (thread_id, user_id, content, name, created_at) VALUES (?, ?, ?, ?, ?)', (thread_id, hashed_login, post, session['username'], local_time))
        conn.commit()
        conn.close()
        return redirect(url_for('thread', thread_id=thread_id))
    except sqlite3.Error as e:
        return 'Ошибка отправки поста: ' + str(e)

# Маршрут для отображения профиля пользователя
@app.route('/members/<username>')
def profile(username):
    update_online()
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    cursor.execute('SELECT avatar, last_online, role FROM users WHERE login=?', (username,))
    user_data = cursor.fetchone()
    if user_data is not None:
        status = user_data[2]
        avatar = user_data[0]
        last_online_time = user_data[1]
        if username == session['username']:
            cursor.execute('UPDATE users SET last_online=? WHERE login=?',
                           (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), username))
            conn.commit()
        last_online_time = datetime.datetime.strptime(last_online_time, '%Y-%m-%d %H:%M:%S')
        last_online_time = pytz.utc.localize(last_online_time).astimezone(pytz.timezone('Europe/Moscow'))
        now = pytz.timezone('Europe/Moscow').localize(datetime.datetime.now())
        time_diff = now - last_online_time
        if time_diff < datetime.timedelta(minutes=5):
            last_online = "в сети"
        elif time_diff < datetime.timedelta(hours=1):
            last_online = f"Был в сети {time_diff.seconds // 60} минут назад"
        elif time_diff < datetime.timedelta(days=1):
            last_online = f"Был в сети {time_diff.seconds // 3600} часов назад"
        else:
            last_online = f"Был в сети {time_diff.days} дней назад"
    else:
        avatar = NONE_AVATAR_FOLDER  # Если пользователя нет, используем none.png
        last_online = None
    conn.close()
    return render_template('profile.html', username=username, avatar=avatar, last_online=last_online, status=status)

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

# Обработка выхода из аккаунта
@app.route('/logout')
def logout():
    write_to_log(message=f"Пользователь {session['username']} вышел из аккаунта", folder=LOG_FOLDER)
    update_online()
    session['logged_in'] = False
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
    app.run(debug=True)


