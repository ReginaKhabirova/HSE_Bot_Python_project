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

bot = telebot.TeleBot("2013562061:AAGi4Dwq_wZwiFzhcqG9tnwUh0kmo6RHRuM")
token = "2013562061:AAGi4Dwq_wZwiFzhcqG9tnwUh0kmo6RHRuM"

# напишем, что делать нашему боту при команде старт
@bot.message_handler(commands=['start'])
def send_keyboard(message, text="Привет, начинается новая финансовая жизнь. С чего начнём?"):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)  # клавиатура
    itembtn1 = types.KeyboardButton('Ввести новые расходы')
    itembtn2 = types.KeyboardButton('Показать список трат')
    itembtn3 = types.KeyboardButton('Удалить траты')
    itembtn4 = types.KeyboardButton('Показать все расходы за сегодня')
    itembtn5 = types.KeyboardButton('График трат')
    itembtn6 = types.KeyboardButton('Обработать файл с тратами')
    itembtn7 = types.KeyboardButton('Отдыхаем!')
    keyboard.add(itembtn1, itembtn2)  # 1 и 2 на первый ряд
    keyboard.add(itembtn3, itembtn4, itembtn5, itembtn6, itembtn7)

    # пришлем это все сообщением и запишем выбранный вариант
    msg = bot.send_message(message.from_user.id,
                           text=text, reply_markup=keyboard)

    # отправим этот вариант в функцию, которая его обработает
    bot.register_next_step_handler(msg, callback_worker)


conn = sqlite3.connect('expenses_hse.db')

# курсор для работы с таблицами
cursor = conn.cursor()

try:
    # sql запрос для создания таблицы
    cursor.execute("""CREATE TABLE IF NOT EXISTS expenses(
       ID INTEGER UNIQUE PRIMARY KEY, user_id INTEGER, expense TEXT,expense_dt DATE,amount REAL);""")
except:
    pass


# функции
# Расходы в хранилище
def add_expense(msg):
    with sqlite3.connect('expenses_hse.db') as conn:
        cursor = conn.cursor()
        text_from_user = str(msg.text)
        dt_from_user = text_from_user.split(' ')[0]

        if len(dt_from_user) == 5 and dt_from_user[2] == '.':
            dt_in = int(dt_from_user[:2])
            month_in = int(dt_from_user[4:5])
            if dt_in > 31 or month_in > 12:
                bot.send_message(msg.chat.id, 'Неверный формат даты')
            else:
                dt_parts = dt_from_user.split('.')
                dt = datetime.strptime('-'.join(['2021', dt_parts[1], dt_parts[0]]), '%Y-%m-%d').date()
        elif dt_from_user.lower() == 'сегодня':
            dt = datetime.strptime(dt_from_user.lower().replace('сегодня', str(today)), '%Y-%m-%d').date()
        elif dt_from_user.lower() == 'вчера':
            dt = datetime.strptime(dt_from_user.lower().replace('вчера', str(today - timedelta(days=1))),
                                   '%Y-%m-%d').date()
        else:
            bot.send_message(msg.chat.id, 'Неверный формат даты')

        expense_txt = text_from_user.split(' ')[1]
        expense_amt = text_from_user.split(' ')[2]
        cursor.execute('INSERT INTO expenses (user_id, expense_dt, expense, amount) VALUES (?, ?, ?, ?)',
                       (msg.from_user.id, dt, expense_txt, expense_amt))
        conn.commit()
    bot.send_message(msg.chat.id, 'Записано!')
    send_keyboard(msg, text="Что дальше?")


# функция, для отправки пользователю expense, amt
def get_expenses_string(expenses):
    expenses_str = []
    for val in list(enumerate(expenses)):
        expenses_str.append(str(val[0] + 1) + '. ' + val[1][0] + ' ' + str(val[1][1]) + '\n')
    return ''.join(expenses_str)


# функция, для отправки пользователю dt, expense, amt
def get_full_expenses(expenses):
    expenses_str = []
    for val in list(enumerate(expenses)):
        expenses_str.append(str(val[0] + 1) + ' ' + val[1][0] + ' ' + str(val[1][1]) + ' ' + str(val[1][2]) + '\n')
    return ''.join(expenses_str)


# отправляем пользователю его расходы за выбранный день
def show_expenses(msg):
    with sqlite3.connect('expenses_hse.db') as con:
        cursor = con.cursor()

        text_from_user = str(msg.text)
        dt_from_user = text_from_user.split(' ')[0]

        if dt_from_user.lower() == 'сегодня':
            dt = datetime.strptime(dt_from_user.lower().replace('сегодня', str(today)), '%Y-%m-%d').date()
        elif dt_from_user.lower() == 'вчера':
            dt = datetime.strptime(dt_from_user.lower().replace('вчера', str(today - timedelta(days=1))),
                                   '%Y-%m-%d').date()
        elif len(dt_from_user) == 5 and dt_from_user[2] == '.':
            dt_parts = dt_from_user.split('.')
            dt = datetime.strptime('-'.join(['2021', dt_parts[1], dt_parts[0]]), '%Y-%m-%d').date()
        else:
            return 'Неверный формат даты'

        cursor.execute("""SELECT 
                        expense, amount
                        FROM expenses 
                        WHERE user_id==? and expense_dt==?""", (msg.from_user.id, dt))
        expenses = get_expenses_string(cursor.fetchall())
        if len(expenses) == 0:
            bot.send_message(msg.chat.id, 'Пока ничего нет. Важно не забывать вносить все расходы')
        else:
            bot.send_message(msg.chat.id, expenses) # TODO: new phrase


# отправляем пользователю его расходы за сегодня
def show_expenses_today(msg):
    with sqlite3.connect('expenses_hse.db') as con:
        cursor = con.cursor()
        cursor.execute("""SELECT 
                                expense, amount
                                FROM expenses 
                                WHERE user_id==? and expense_dt==?""",
                       (msg.from_user.id, today))  # TODO show sum for day
        expenses = get_expenses_string(cursor.fetchall())
        if len(expenses) == 0:
            bot.send_message(msg.chat.id, 'Пока ничего нет. Важно не забывать вносить все расходы')
        else:
            bot.send_message(msg.chat.id, expenses)
            send_keyboard(msg, "Что делаем дальше?")

# выыделяет одно дело, которое пользователь хочет удалить
def choose_expense_to_delete(msg):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    with sqlite3.connect('expenses_hse.db') as con:
        cursor = con.cursor()

        text_from_user = str(msg.text)
        dt_from_user = text_from_user.split(' ')[0]

        global dt_delete
        if dt_from_user == 'Сегодня':
            dt_delete = datetime.strptime(dt_from_user.replace('Сегодня', str(today)), '%Y-%m-%d').date()
        elif dt_from_user == 'Вчера':
            dt_delete = datetime.strptime(dt_from_user.replace('Вчера', str(today - timedelta(days=1))),
                                          '%Y-%m-%d').date()
        elif len(dt_from_user) == 5 and dt_from_user[2] == '.':
            dt_parts = dt_from_user.split('.')
            dt_delete = datetime.strptime('-'.join(['2021', dt_parts[1], dt_parts[0]]), '%Y-%m-%d').date()
        else:
            return 'Неверный формат даты'

        # достаем все траты пользователя
        cursor.execute("""SELECT 
                                expense_dt, expense, amount
                                        FROM expenses 
                                        WHERE user_id==? and expense_dt==?""",
                       (msg.from_user.id, dt_delete))
        expenses = cursor.fetchall()

        for val in expenses:
            markup.add(types.KeyboardButton(val[1] + ' ' + str(val[2])))
        msg = bot.send_message(msg.from_user.id,
                               text="Выбери одну трату из списка",
                               reply_markup=markup)
        bot.register_next_step_handler(msg, delete_expense) # TODO добавить - ничего не удалять

def delete_expense(msg):
    with sqlite3.connect('expenses_hse.db') as con:
        cursor = con.cursor()
        cursor.execute('DELETE FROM expenses WHERE user_id==? AND expense==? and expense_dt ==? and amount==?',
                       (msg.from_user.id, msg.text.split(' ')[0], dt_delete, msg.text.split(' ')[1]))
        bot.send_message(msg.chat.id, 'Выбранная трата удалена')
        send_keyboard(msg, "Что делаем дальше?")


# параметры для графика
def get_expenses_for_plt(expenses):
    values = []
    exp_dt = []
    for val in expenses:
        values.append(str(val[1]))
        exp_dt.append(str(val[0]))
    return ' '.join(values), ' '.join(exp_dt)


# График трат
def send_plot(msg):
    with sqlite3.connect('expenses_hse.db') as con:
        cursor = con.cursor()
        cursor.execute("""select strftime('%d', expense_dt)||'.'||strftime('%m', expense_dt) as mnth, sum(amount)
                                from expenses
                               WHERE user_id==? and expense_dt between ? and ? group by mnth""",
                       (msg.from_user.id, week, today))
        expenses, expenses_dt = get_expenses_for_plt(cursor.fetchall())

        x = list(expenses_dt.split(' '))
        y = list(map(float, expenses.split(' ')))

        plt.title('Траты за неделю')
        plt.xlabel('Дни трат')
        plt.ylabel('Сумма за день')
        plt.bar(x, y)

        plt.savefig('expenses_by_week_plot.png', dpi=300)
        bot.send_photo(msg.chat.id, photo=open('expenses_by_week_plot.png', 'rb'))
        send_keyboard(msg, "Что делаем дальше?")

def send_file(msg):
    with sqlite3.connect('expenses_hse.db') as con:
        cursor = con.cursor()
        sql = """insert into expenses (user_id, expense, expense_dt, amount)
                    values(?, ?, ?, ?)"""
        try:
            file_id_info = bot.get_file(msg.document.file_id)
            downloaded_file = bot.download_file(file_id_info.file_path)

            text = downloaded_file.decode('utf-8')
            text = text.split('\n')

            file_lines = []
            for r in text:
                #r = r.replace('\n', '')
                if len(r) > 14:
                    file_lines.append(r.split(' '))

            for line in file_lines:
                cursor.execute(sql, (msg.from_user.id, line[1], line[0], line[2]))
        except:
            bot.send_message(msg.chat.id, "Ошибка загрузки файла")

        bot.send_message(msg.chat.id, "Приветики. Файл загружен")

def send_sticker(msg):
    bot.send_message(msg.chat.id, smile)

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