from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def menu_markup():
    buttons = [
        [KeyboardButton(text="/income")],
        [KeyboardButton(text="/salary")]
    ]
    markup = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="*родитель* *приход* *зарплата* *преподаватель* *комментарий*"
    )
    return markup


def send_markup():
    markup = InlineKeyboardBuilder()
    btn1 = InlineKeyboardButton(text="Вчера", callback_data="send_yesterday")
    btn2 = InlineKeyboardButton(text="Сегодня", callback_data="send_today")
    btn3 = InlineKeyboardButton(text="Отмена", callback_data="send_close")
    markup.add(btn1, btn2, btn3)
    return markup.as_markup()


def yesno_markup(callback):
    back = callback.split("_")
    markup = InlineKeyboardBuilder()
    btn1 = InlineKeyboardButton(text="Подтвердить", callback_data=f"{callback}_yes")
    btn2 = InlineKeyboardButton(text="Назад", callback_data=f"{back[0]}_back")
    markup.add(btn1, btn2)
    return markup.as_markup()
