from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from config import *
from db import create_table_users


conn = sqlite3.connect("db.db")
cur = conn.cursor()


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = 'static/images/'
create_table_users()


@app.route('/')
def index():
    title = 'Dialogia'
    return render_template("index.html", title=title)


@app.route('/signin', methods=['GET', 'POST'])
def login():
    title = "Sign In"
    return render_template("login.html", title=title)

@app.route('/signup', methods=['GET', 'POST'])
def register():
    title = "Sign Up"
    return render_template("login.html", title=title)


if __name__ == '__main__':
    app.run(debug=True)
