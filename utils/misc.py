from datetime import date, timedelta

reminder_creation_message_example = (
    f'- Сегодня 12:00 позвонить другу\n'
    f'- Завтра 12:30 сходить в магазин\n'
    f'- {(date.today() + timedelta(days=3)).strftime("%d.%m.%Y")} 13:00 отправить письмо\n'
    '- Через 2 часа проверить почту\n'
    '- 16:00 забрать посылку'
)

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