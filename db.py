import sqlite3


conn = sqlite3.connect('db.db')
cur = conn.cursor()


# Создание "users"
def create_table_users():
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            email TEXT,
            date DATE NOT NULL DEFAULT CURRENT_DATE,
            blocked TEXT NOT NULL DEFAULT NO
        );
    ''')