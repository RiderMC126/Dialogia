from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
import hashlib
from datetime import datetime
from capcha import generate_captcha
from config import *
from db import create_table_users
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = 'static/images/'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("db.db")
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_db(error):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.before_request
def before_request():
    g.db = get_db()

create_table_users()

@app.route('/')
def index():
    title = 'Dialogia'
    user = None
    if 'user_id' in session:
        user = session['username']
    return render_template("index.html", title=title, user=user)



@app.route('/signin', methods=['GET', 'POST'])
def login():
    title = "Sign In"
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Хеширование введенного пароля
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Проверка пользователя в базе данных
        cur = g.db.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_password))
        user = cur.fetchone()

        if user:
            # Если пользователь найден, создаем сессию
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))  # Перенаправление на главную страницу после успешного входа
        else:
            error = "Неправильное имя пользователя или пароль"

    return render_template("login.html", title=title, error=error)

@app.route('/signup', methods=['GET', 'POST'])
def register():
    title = "Регистрация"
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        email = request.form['email']
        captcha = request.form['captcha']

        if captcha != session['captcha']:
            error = "Неверный код капчи."
        elif not username or not password or not email:
            error = "Все поля обязательны для заполнения."
        elif password != confirm_password:
            error = "Пароли не совпадают."
        else:
            # Проверка, существует ли уже пользователь с таким именем или email
            cur = g.db.execute("SELECT * FROM users WHERE username=? OR email=?", (username, email))
            user = cur.fetchone()
            if user:
                error = "Пользователь с таким именем или email уже существует."
            else:
                # Хеширование пароля
                hashed_password = hashlib.sha256(password.encode()).hexdigest()

                # Добавление нового пользователя в базу данных
                current_date = datetime.now().strftime("%Y-%m-%d")
                g.db.execute("""
                    INSERT INTO users (username, password, email ,date, blocked)
                    VALUES (?, ?, ?, ?, ?)
                """, (username, hashed_password, email, current_date, "NO"))
                g.db.commit()

                # Перенаправление на страницу входа после успешной регистрации
                return redirect(url_for('login'))
    # Генерация новой капчи
    captcha_text, _ = generate_captcha()
    session['captcha'] = captcha_text

    return render_template("register.html", title=title, error=error)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
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
