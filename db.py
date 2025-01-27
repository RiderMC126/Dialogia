import sqlite3

def get_db():
    conn = sqlite3.connect('db.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_table_users():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    blocked TEXT NOT NULL DEFAULT 'NO'
    );
    ''')
    conn.commit()
    conn.close()
