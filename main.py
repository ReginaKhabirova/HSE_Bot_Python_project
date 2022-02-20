import telebot
from telebot import types
import sqlite3
from datetime import date, timedelta
from datetime import datetime
import matplotlib
import emoji
from emoji import emojize
import requests

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

today = date.today()
yesterday = today - timedelta(days=1)
week = today - timedelta(days=7)
smile = emojize('😊', use_aliases=True)
DB = 'expenses_hse.db'

bot = telebot.TeleBot("")

from keyboard import send_keyboard
from dt_from_user import expense_date
from build_graph import build_graph
from buttons_functions import add_expense
from buttons_functions import show_expenses
from buttons_functions import show_expenses_today
from buttons_functions import choose_expense_to_delete
from buttons_functions import send_plot
from buttons_functions import send_file
from buttons_functions import send_sticker
from buttons_functions import delete_expense
from buttons_functions import get_expenses_string
from buttons_functions import get_full_expenses
from buttons_functions import get_expenses_for_plt

# напишем, что делать нашему боту при команде старт
@bot.message_handler(commands=['start'])


conn = sqlite3.connect(DB)

# курсор для работы с таблицами
cursor = conn.cursor()

try:
    # sql запрос для создания таблицы
    cursor.execute("""CREATE TABLE IF NOT EXISTS expenses(
       ID INTEGER UNIQUE PRIMARY KEY, user_id INTEGER, expense TEXT,expense_dt DATE,amount REAL);""")
except:
    pass

# привязываем функции к кнопкам на клавиатуре
def callback_worker(call):
    if call.text == "Ввести новые расходы":
        try:
            msg = bot.send_message(call.chat.id, 'Введи расход в формате Сегодня, Вчера или дд.мм, позиция, сумма')
            bot.register_next_step_handler(msg, add_expense)
        except:
            bot.send_message(call.chat.id, 'wrong format')

    elif call.text == "Показать список трат":
        try:
            msg = bot.send_message(call.chat.id, 'Введи дату, за которую показать траты: Сегодня, Вчера или дд.мм')
            bot.register_next_step_handler(msg, show_expenses)
        except:
            bot.send_message(call.chat.id, 'Пока ничего нет. Очень важно не забывать вносить все расходы')
            send_keyboard(call, "Что делаем дальше?")

    elif call.text == "Показать все расходы за сегодня":
        try:
            show_expenses_today(call)
        except:
            bot.send_message(call.chat.id, 'Пока ничего нет. Очень важно не забывать все расходы')
            send_keyboard(call, "Что делаем дальше?")

    elif call.text == "Удалить траты":
        try:
            msg = bot.send_message(call.chat.id, 'Введи дату, за которую показать траты: Сегодня, Вчера или дд.мм')
            bot.register_next_step_handler(msg, choose_expense_to_delete)
        except:
            bot.send_message(call.chat.id, 'В этот день не было трат')
            send_keyboard(call, "Что делаем дальше?")

    elif call.text == "График трат":
        try:
            send_plot(call)
        except:
            bot.send_message(call.chat.id, 'Нет трат за неделю')
            send_keyboard(call, "Что делаем дальше?")

    elif call.text == "Обработать файл с тратами":
        try:
            msg = bot.send_message(call.chat.id, 'Загрузи файл в формате дата, название расхода, сумма')
            bot.register_next_step_handler(msg, send_file)
        except:
            bot.send_message(call.chat.id, "Файл не загрузился")
            send_keyboard(call, "Что делаем дальше?")

    elif call.text == "Отдыхаем!":
        try:
            send_sticker(call)
        except:
            bot.send_message(call.chat.id, 'Прекрасно :)')


bot.polling(none_stop=True)