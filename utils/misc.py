from datetime import date, timedelta

reminder_creation_message_example = f'Сегодня 12:00 Позвонить другу\nЗавтра 15:00 Сходить в магазин\n{(date.today() + timedelta(weeks=1)).strftime("%Y-%m-%d")} 18:00 Отправить письмо'

commands = {
    'send_location': '📍 Отправить геолокацию',
    'choose_city': '🌍 Выбрать город',
    'choose_timezone': '🌐 Выбрать часовой пояс',
    'use_utc': '🕓 Использовать UTC',
    'create': '✅ Да, создать',
    'delete': '🗑️ Да, удалить',
    'cancel': '❌ Отменить',
}

cities = {
    'Moscow': '🇷🇺 Москва',
    'Yekaterinburg': '🇷🇺 Екатеринбург',
    'Yerevan': '🇦🇲 Ереван',
    'Tbilisi': '🇬🇪 Тбилиси',
    'Minsk': '🇧🇾 Минск',
    'no_city': '🚫 Нет моего города',
}

timezones = {
    'no_timezone': '🚫 Нет моего пояса',
}