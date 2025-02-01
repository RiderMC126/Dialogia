import sqlite3

def create_db():
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        login TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        balance INTEGER NOT NULL DEFAULT 0,
        avatar TEXT,
        last_online DATETIME,
        registration_time DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP),
        role TEXT NOT NULL DEFAULT 'Пользователь',
        blocked TEXT NOT NULL DEFAULT 'NO'
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS forums (
        id INTEGER PRIMARY KEY,
        category_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS threads (
        id INTEGER PRIMARY KEY,
        forum_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (forum_id) REFERENCES forums (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY,
        thread_id INTEGER NOT NULL,
        user_id TEXT,
        content TEXT,
        name TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (thread_id) REFERENCES threads (id),
        FOREIGN KEY (user_id) REFERENCES users (login)
        );
    ''')

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    sender TEXT NOT NULL,
    recipient TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender) REFERENCES users (login),
    FOREIGN KEY (recipient) REFERENCES users (login)
        );
    """)

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS boosttelega (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        api_key VARCHAR(255) NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

create_db()