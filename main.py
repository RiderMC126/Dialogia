from flask import Flask, render_template, request, redirect, url_for, session, g
from http.server import HTTPServer, BaseHTTPRequestHandler
import sqlite3
import hashlib
from capcha import generate_captcha
from config import *
from db import create_db
import datetime
import pytz
import os
import logging
import asyncio


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = 'static/images/'


# Создание базы данных при запуске приложения
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

# Обновляем онлайн пользователей
def update_online():
    if 'username' in session:
        conn = sqlite3.connect('db.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET last_online=CURRENT_TIMESTAMP WHERE login=?', (session['username'],))
        conn.commit()
        conn.close()

@app.route('/')
def index():
    title = 'Dialogia'
    user = None
    if 'user_id' in session:
        user = session['username']
    return render_template("index.html", title=title, user=user)



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
                session['logged_in'] = True
                session['username'] = login
                return redirect(url_for('index'))
            else:
                error = 'Неправильный логин или пароль'
        except sqlite3.Error as e:
            error = 'Ошибка авторизации: ' + str(e)
    return render_template('login.html', title=title, error=error)

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



@app.route('/logout')
def logout():
    update_online()
    session['logged_in'] = False
    return redirect(url_for('index'))

@app.context_processor
def inject_user():
    user = None
    if 'user_id' in session:
        user = session['username']
    return dict(user=user)

@app.route('/refresh_captcha')
def refresh_captcha():
    captcha_text, _ = generate_captcha()
    session['captcha'] = captcha_text
    return redirect(url_for('register'))



if __name__ == '__main__':
    app.run(debug=True)
