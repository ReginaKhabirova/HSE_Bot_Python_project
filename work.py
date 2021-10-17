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
        dt = datetime.strptime(text_from_user.split(' ')[0].replace('Сегодня', str(today)), '%Y-%m-%d').date()
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
        expenses_str.append(str(val[0] + 1) + '. ' + val[1][0] + '\n')
    return ''.join(expenses_str)

# отправляем пользователю его расходы за сегодня
def show_expenses(msg):
    with sqlite3.connect('expenses_hse.db') as con:
        cursor = con.cursor()
        cursor.execute('SELECT expense FROM expenses WHERE user_id=={}'.format(msg.from_user.id))
        expenses = get_expenses_string(cursor.fetchall())
        bot.send_message(msg.chat.id, expenses)
        send_keyboard(msg, "Чем еще могу помочь?") # TODO: new phrase

'''
# выыделяет одно дело, которое пользователь хочет удалить
def delete_one_plan(msg):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    with sqlite3.connect('planner_hse.db') as con:
        cursor = con.cursor()
        # достаем все задачи пользователя
        cursor.execute('SELECT plan FROM planner WHERE user_id=={}'.format(msg.from_user.id))
        # достанем результат запроса
        tasks = cursor.fetchall()
        for value in tasks:
            markup.add(types.KeyboardButton(value[0]))
        msg = bot.send_message(msg.from_user.id,
                               text="Выбери одно дело из списка",
                               reply_markup=markup)
        bot.register_next_step_handler(msg, delete_one_plan_)


# удаляет это дело
def delete_one_plan_(msg):
    with sqlite3.connect('planner_hse.db') as con:
        cursor = con.cursor()
        cursor.execute('DELETE FROM planner WHERE user_id==? AND plan==?', (msg.from_user.id, msg.text))
        bot.send_message(msg.chat.id, 'Ура, минус одна задача!')
        send_keyboard(msg, "Чем еще могу помочь?")


# удаляет все планы для конкретного пользователя
def delete_all_plans(msg):
    with sqlite3.connect('planner_hse.db') as con:
        cursor = con.cursor()
        cursor.execute('DELETE FROM planner WHERE user_id=={}'.format(msg.from_user.id))
        con.commit()
        bot.send_message(msg.chat.id, 'Удалены все дела. Хорошего отдыха!')
        send_keyboard(msg, "Чем еще могу помочь?")
'''

# привязываем функции к кнопкам на клавиатуре
def callback_worker(call):
    if call.text == "Ввести новые расходы":
        msg = bot.send_message(call.chat.id, 'Введи расход в формате дата (пока только сегодня), позиция, сумма')
        bot.register_next_step_handler(msg, add_expense)

    elif call.text == "Показать список трат":
        try:
            show_expenses(call)
        except:
            bot.send_message(call.chat.id, 'Пока ничего нет. Очень важно не забывать все расходы')
            send_keyboard(call, "Чем еще могу помочь?") # TODO: new phrase
    '''
    elif call.text == "Удалить дело из списка":
        try:
            delete_one_plan(call)
        except:
            bot.send_message(call.chat.id, 'Здесь пусто. Можно отдыхать :-)')
            send_keyboard(call, "Чем еще могу помочь?")

    elif call.text == "Удалить все дела из списка":
        try:
            delete_all_plans(call)
        except:
            bot.send_message(call.chat.id, 'Здесь пусто. Можно отдыхать :-)')
            send_keyboard(call, "Чем еще могу помочь?")

    elif call.text == "Другое":
        bot.send_message(call.chat.id, 'Больше я пока ничего не умею :-(')
        send_keyboard(call, "Чем еще могу помочь?")

    elif call.text == "Пока все!":
        bot.send_message(call.chat.id, 'Хорошего дня! Когда захотите продолжнить нажмите на команду /start')
'''

bot.polling(none_stop=True)