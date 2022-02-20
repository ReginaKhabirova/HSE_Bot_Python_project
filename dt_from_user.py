def expense_date (dt_from_user):
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
