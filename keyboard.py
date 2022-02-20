
def send_keyboard(message, text="Привет, начинается новая финансовая жизнь. С чего начнём?"):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)  # клавиатура
    btn_new_expenses = types.KeyboardButton('Ввести новые расходы')
    btn_show_list_of_expenses = types.KeyboardButton('Показать список трат')
    btn_delete_expenses = types.KeyboardButton('Удалить траты')
    btn_show_expenses_today = types.KeyboardButton('Показать все расходы за сегодня')
    btn_graph = types.KeyboardButton('График трат')
    btn_file_with_expenses = types.KeyboardButton('Обработать файл с тратами')
    btn_message = types.KeyboardButton('Отдыхаем!')
    keyboard.add(btn_new_expenses, btn_show_list_of_expenses)  # 1 и 2 на первый ряд
    keyboard.add(btn_delete_expenses, btn_show_expenses_today, btn_graph, btn_file_with_expenses, btn_message)

    # пришлем это все сообщением и запишем выбранный вариант
    msg = bot.send_message(message.from_user.id,
                           text=text, reply_markup=keyboard)

    # отправим этот вариант в функцию, которая его обработает
    bot.register_next_step_handler(msg, callback_worker)
