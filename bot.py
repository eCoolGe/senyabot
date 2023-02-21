import asyncio
import logging
import re

from aiogram import Bot, Dispatcher, types, html
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.markdown import text
from googleapiclient.errors import HttpError

from env_reader import config
from aiogram.dispatcher.filters import CommandObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import TRUSTED_ID, DICTIONARY, LOG_LISTNAME, INCOME_LISTNAME, SALARY_LISTNAME
import spreadsheets

logging.basicConfig(format=u'%(filename)s [ LINE:%(lineno)+3s ]#%(levelname)+8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)
bot = Bot(token=config.bot_token.get_secret_value(), parse_mode="HTML")
dp = Dispatcher()


@dp.message(lambda message: message.from_user.id not in TRUSTED_ID)
async def process_verify_user(message: types.Message):
    """
    Запрещает использовать все возможные команды в том случае, если id пользователя не относится к одному из доверенных
    """
    return await message.reply("Вы не относитесь к списку доверенных пользователей!")


@dp.message(commands=['start'])
async def process_start_command(message: types.Message):
    """
    Отвечает приветственным сообщением на команду /start
    """
    buttons = [
        [types.KeyboardButton(text="/income")],
        [types.KeyboardButton(text="/salary")]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="*родитель* *приход* *зарплата* *преподаватель* *комментарий*"
    )
    await message.reply("Привет!\nЯ бот от <a href=\"t.me/ecoolge\">eCoolGe</a>!", reply_markup=keyboard)


@dp.message(commands=['help'])
async def process_help_command(message: types.Message):
    """
    Отвечает списком команд и информацией об этих командах на команду /help
    """
    msg = text('<b>Я могу ответить на следующие команды:</b>',
               'Сообщение формата "Родитель Приход Зарплата Преподаватель Комментарий"',
               '/salary [DD.MM.YYYY]', '/income [DD.MM.YYYY]', sep='\n')
    await message.reply(msg)


@dp.message(commands=["income", "salary"])
async def process_pay_output(message: types.Message, command: CommandObject):
    """
    Выводит на экран приход или зарплату за текущий или указанный день, если таковая имеется,
    если нет - возвращает сообщение об этом
    """
    if command.command == "income":
        pay_type = INCOME_LISTNAME
    else:
        pay_type = SALARY_LISTNAME

    if command.args:
        pay_array = spreadsheets.pay_calculate(pay_type, str(command.args))

        if len(pay_array) > 1:
            pay_strings = '\n'.join(map(str, pay_array[0]))
            total_string = f"<b>Итого:</b> {pay_array[1]}"
        else:
            pay_strings = pay_array[0]
            total_string = ""

        await message.answer(
            f"{pay_type} за <b>{html.quote(command.args)}</b> \n\n"
            f"{pay_strings}\n\n"
            f"{total_string}"
        )
    else:
        pay_array = spreadsheets.pay_calculate(pay_type)

        if len(pay_array) > 1:
            pay_strings = '\n'.join(map(str, pay_array[0]))
            total_string = f"<b>Итого:</b> {pay_array[1]}"
        else:
            pay_strings = pay_array[0]
            total_string = ""

        await message.answer(
            f"{pay_type} за <b>сегодня</b>\n\n"
            f"{pay_strings}\n\n"
            f"{total_string}"
        )


@dp.message(content_types="text")
async def process_extract_data(message: types.Message):
    """
    Записывает полученное сообщение определенного формата в таблицу, по нажатию кнопки активирует событие занесения
    данных в таблицу прихода и зарплаты
    """
    user_text = message.text
    user_text = re.sub(r"[([{})\]]", " ", user_text)
    user_text = re.sub(r"\s((\s)(\s+)?)?", " ", user_text)
    user_split_text = user_text.split(sep=" ", maxsplit=4)

    if len(user_split_text) < 4 or user_split_text[0] in DICTIONARY:
        return

    spreadsheets.upload_log_message(LOG_LISTNAME, user_split_text)

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="Подтвердить отправку в таблицу",
        callback_data="send_value")
    )

    try:
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    except TelegramBadRequest:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    await message.answer(
        f"{user_text}",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(text="send_value")
async def process_send_value(callback: types.CallbackQuery):
    """
    Заносит данные в таблицу прихода и зарплаты
    """
    user_text = callback.message.text
    user_text = user_text.split(sep=" ", maxsplit=4)

    try:
        spreadsheets.upload_list_pay(user_text[3], int(user_text[1]), INCOME_LISTNAME)
        spreadsheets.upload_list_pay(user_text[3], int(user_text[2]), SALARY_LISTNAME)

        await callback.message.edit_text(callback.message.text)

        await callback.answer(
            text="Данные успешно отправлены в таблицу",
            show_alert=True
        )
        # или просто await call.answer()
    except ValueError:
        await callback.answer(
            text="Произошла ошибка или данные были введены некорректно, попробуйте еще раз",
            show_alert=True
        )
    except KeyError:
        await callback.answer(
            text="Произошла ошибка - возможно, ваша таблица полностью пустая - попробуйте внести одну фамилию и одну "
                 "дату",
            show_alert=True
        )
    except HttpError:
        await callback.answer(
            text="Произошла ошибка - возможно, в вашей таблице закончились столбцы или колонки - создайте их в ручном "
                 "режиме",
            show_alert=True
        )


async def main():
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
