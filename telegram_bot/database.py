import sqlite3
from config import DATABASE_URL


def get_user_info():
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute('SELECT login FROM users')
    users = cursor.fetchall()
    user_count = len(users)
    user_list = "\n".join([user[0] for user in users])

    cursor.execute('SELECT login FROM users WHERE role = ?', ('Администрация',))
    admins = cursor.fetchall()
    admin_count = len(admins)
    admin_list = "\n".join([admin[0] for admin in admins])

    conn.close()

    return user_list, user_count, admin_list, admin_count


def get_categories():
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM categories')
    categories = cursor.fetchall()
    return categories

def create_categories(name):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()


def create_forums(category_id, name):
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO forums (category_id, name) VALUES (?, ?)', (category_id, name))
        conn.commit()
        new_id = cursor.lastrowid
        return new_id
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        conn.close()
