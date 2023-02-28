import asyncio
import logging
import re

from aiogram import Bot, Dispatcher, types, html
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.markdown import text
from aiogram.dispatcher.filters import CommandObject, Text
from googleapiclient.errors import HttpError

from env_reader import config
from config import TRUSTED_ID, DICTIONARY, LOG_LISTNAME, INCOME_LISTNAME, SALARY_LISTNAME
import spreadsheets
import keyboards
import utils

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
    await message.reply("Привет!\nЯ бот от <a href=\"t.me/ecoolge\">eCoolGe</a>!", reply_markup=keyboards.menu_markup())


@dp.message(commands=['help'])
async def process_help_command(message: types.Message):
    """
    Отвечает списком команд и информацией об этих командах на команду /help
    """
    msg = text('<b>Я могу ответить на следующие команды:</b>',
               'Сообщение формата "Родитель Приход Зарплата Преподаватель Комментарий"',
               '/salary [DD.MM.YYYY]', '/income [DD.MM.YYYY]', sep='\n')
    await message.reply(msg)


@dp.message(commands=['now'])
async def process_help_command(message: types.Message):
    """
    Отвечает полной датой и временем на команду /now
    """
    await message.reply(f'<b>Дата и время бота:</b>\n <code>{utils.full_today()}</code>')


@dp.message(commands=["income", "salary"])
async def process_pay_output(message: types.Message, command: CommandObject):
    """
    Выводит на экран приход или зарплату за текущий или указанный день, если таковая имеется,
    если нет - возвращает сообщение об этом
    """
    pay_type = INCOME_LISTNAME if command.command == "income" else SALARY_LISTNAME

    if command.args is not None:
        pay_array = spreadsheets.pay_calculate(pay_type, str(command.args))
        selected_day = f"{html.quote(command.args)}"
    else:
        today = utils.today()
        pay_array = spreadsheets.pay_calculate(pay_type, today)
        selected_day = f"{today}"

    pay_strings = '\n'.join(map(str, pay_array[0])) if len(pay_array) > 1 else pay_array[0]
    total_string = f"<b>Итого:</b> {pay_array[1]}" if len(pay_array) > 1 else ""

    await message.answer(
        f"{pay_type} за <b>{selected_day}</b> \n\n"
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

    try:
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    except TelegramBadRequest:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    await message.answer(
        f"{user_text}",
        reply_markup=keyboards.send_markup()
    )


@dp.callback_query(Text(text_startswith="send_"))
async def process_send_value(callback: types.CallbackQuery):
    """
    Заносит данные в таблицу прихода и зарплаты
    """
    action = callback.data.split("_", maxsplit=1)[1]

    if action == "yesterday" or action == "today" or action == "close":
        await callback.message.edit_text(callback.message.text, reply_markup=keyboards.yesno_markup(callback.data))
        await callback.answer()
    elif action == "close_yes":
        await callback.message.edit_text(callback.message.text)
        await callback.answer()
    elif action == "back":
        await callback.message.edit_text(callback.message.text, reply_markup=keyboards.send_markup())
        await callback.answer()
    elif action == "yesterday_yes" or action == "today_yes":
        user_text = callback.message.text
        user_text = user_text.split(sep=" ", maxsplit=4)

        selected_day = utils.today()
        if action == "yesterday_yes":
            selected_day = utils.yesterday()
        status = f"☁ • {selected_day}"

        try:
            spreadsheets.upload_list_pay(user_text[3], selected_day, int(user_text[1]), INCOME_LISTNAME)
            spreadsheets.upload_list_pay(user_text[3], selected_day, int(user_text[2]), SALARY_LISTNAME)
            await callback.message.edit_text(f"{callback.message.text}\n\n<b>{status}</b>")
            await callback.answer()
        except ValueError or KeyError or HttpError as error:
            header = "Ошибка!\n\n"
            msg = "Данные введены некорректно"
            if error == KeyError:
                msg = "Возможно, таблица пустая - попробуйте внести по одной фамилии и дате"
            elif error == HttpError:
                msg = "Возможно, столбцы и колонки закончились - добавьте их вручную"
            await callback.answer(text=f"{header}{msg}\n\n{error}", show_alert=True)


async def main():
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt as e:
        print("Caught keyboard interrupt. Turning off the bot...")
    finally:
        print("Bot was turned off")

