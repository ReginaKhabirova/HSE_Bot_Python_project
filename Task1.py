import telebot
from telebot import types
import sqlite3
from datetime import date, timedelta
from datetime import datetime
today = date.today()
yesterday = today - timedelta(days=1)

bot = telebot.TeleBot("2013562061:AAGi4Dwq_wZwiFzhcqG9tnwUh0kmo6RHRuM")


# напишем, что делать нашему боту при команде старт
@bot.message_handler(commands=['start'])
def send_keyboard(message, text="Привет, начинается новая финансовая жизнь. С чего начнём?"):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)  # клавиатура
    itembtn1 = types.KeyboardButton('Ввести новые расходы')
    itembtn2 = types.KeyboardButton('Показать список трат')
    itembtn3 = types.KeyboardButton('Удалить траты')
    itembtn4 = types.KeyboardButton('Показать все расходы за день')
    itembtn5 = types.KeyboardButton('График трат')
    itembtn6 = types.KeyboardButton('Обработать файл с тратами')
    itembtn7 = types.KeyboardButton('Отдыхаем!')
    keyboard.add(itembtn1, itembtn2)  #1 и 2 на первый ряд
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

        if dt_from_user == 'Сегодня': # TODO lower
            dt = datetime.strptime(dt_from_user.replace('Сегодня', str(today)), '%Y-%m-%d').date()
        elif dt_from_user == 'Вчера': # TODO lower
            dt = datetime.strptime(dt_from_user.replace('Вчера', str(today - timedelta(days=1))), '%Y-%m-%d').date()
        elif len(dt_from_user) == 5 and dt_from_user[2] == '.':
            dt_parts = dt_from_user.split('.')
            dt = datetime.strptime('-'.join(['2021', dt_parts[1], dt_parts[0]]), '%Y-%m-%d').date()
        else:
            return 'Неверный формат даты'

        expense_txt = text_from_user.split(' ')[1]
        expense_amt = text_from_user.split(' ')[2]
        cursor.execute('INSERT INTO expenses (user_id, expense_dt, expense, amount) VALUES (?, ?, ?, ?)',
                       (msg.from_user.id, dt, expense_txt, expense_amt))
        conn.commit()
    bot.send_message(msg.chat.id, 'Записано!')
    send_keyboard(msg, text="Что дальше?")

# просто функция, которая делает нам красивые строки для отправки пользователю
def get_expenses_string(expenses):
    expenses_str = []
    for val in list(enumerate(expenses)):
        expenses_str.append(str(val[0] + 1) + '. ' + val[1][0] +' ' + str(val[1][1]) + '\n')
    return ''.join(expenses_str)

# отправляем пользователю его расходы за сегодня
def show_expenses(msg):
    with sqlite3.connect('expenses_hse.db') as con:
        cursor = con.cursor()

        text_from_user = str(msg.text)
        dt_from_user = text_from_user.split(' ')[0]

        if dt_from_user == 'Сегодня':
            dt = datetime.strptime(dt_from_user.replace('Сегодня', str(today)), '%Y-%m-%d').date()
        elif dt_from_user == 'Вчера':
            dt = datetime.strptime(dt_from_user.replace('Вчера', str(today - timedelta(days=1))), '%Y-%m-%d').date()
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
        bot.send_message(msg.chat.id, expenses)
        send_keyboard(msg, "Чем еще могу помочь?") # TODO: new phrase


# привязываем функции к кнопкам на клавиатуре
def callback_worker(call):
    if call.text == "Ввести новые расходы":
        msg = bot.send_message(call.chat.id, 'Введи расход в формате дата (пока только сегодня), позиция, сумма')
        bot.register_next_step_handler(msg, add_expense)

    elif call.text == "Показать список трат":
        try:
            msg = bot.send_message(call.chat.id, 'Введи дату, за которую показать траты: сегодня, вчера или дд.мм')
            bot.register_next_step_handler(msg, show_expenses)
        except:
            bot.send_message(call.chat.id, 'Пока ничего нет. Очень важно не забывать все расходы')
            send_keyboard(call, "Чем еще могу помочь?") # TODO: new phrase


bot.polling(none_stop=True)