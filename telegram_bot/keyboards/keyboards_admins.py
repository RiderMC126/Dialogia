from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

def index_keyboard_admins():
    buttons = [
        [InlineKeyboardButton(text="Пользователи", callback_data="count_users")],
        [InlineKeyboardButton(text="Заблокировать", callback_data="blocked_users"), InlineKeyboardButton(text="Разблокировать", callback_data="unblocked_users")],
        [InlineKeyboardButton(text="Создать", callback_data="create")]
    ]
    inline_kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return inline_kb

def gohome_keyboard_admins():
    buttons = [
        [InlineKeyboardButton(text="На главную", callback_data="gohome")],
    ]
    inline_kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    return inline_kb