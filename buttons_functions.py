# функции
# Расходы в хранилище
def add_expense(msg):
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        text_from_user = str(msg.text)
        dt_from_user = text_from_user.split(' ')[0]
        expense_date(dt_from_user)
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
    with sqlite3.connect(DB) as con:
        cursor = con.cursor()

        text_from_user = str(msg.text)
        dt_from_user = text_from_user.split(' ')[0]
        expense_date(dt_from_user)

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
    with sqlite3.connect(DB) as con:
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
    with sqlite3.connect(DB) as con:
        cursor = con.cursor()

        text_from_user = str(msg.text)
        dt_from_user = text_from_user.split(' ')[0]

        global dt_delete
        expense_date(dt_from_user)

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
    with sqlite3.connect(DB) as con:
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
    with sqlite3.connect(DB) as con:
        cursor = con.cursor()
        cursor.execute("""select strftime('%d', expense_dt)||'.'||strftime('%m', expense_dt) as mnth, sum(amount)
                                from expenses
                               WHERE user_id==? and expense_dt between ? and ? group by mnth""",
                       (msg.from_user.id, week, today))
        expenses, expenses_dt = get_expenses_for_plt(cursor.fetchall())
        build_graph(list(expenses_dt.split(' ')), list(map(float, expenses.split(' '))))

        bot.send_photo(msg.chat.id, photo=open('expenses_by_week_plot.png', 'rb'))
        send_keyboard(msg, "Что делаем дальше?")

def send_file(msg):
    with sqlite3.connect(DB) as con:
        cursor = con.cursor()
        sql = """insert into expenses (user_id, expense, expense_dt, amount)
                    values(?, ?, ?, ?)"""
        try:
            file_id_info = bot.get_file(msg.document.file_id)
            downloaded_file = bot.download_file(file_id_info.file_path)
            # обработка по строкам загруженного файла с тратами
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
