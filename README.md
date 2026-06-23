# 🤖 Telegram Reminder Bot
[Telegram‑бот](https://t.me/hyperreminderbot), который позволяет создавать, просматривать и удалять напоминания.

## 🕹️ Возможности
- Создание напоминаний
- Просмотр всех активных напоминаний
- Удаление отдельных, ближайших и всех напоминаний
- Установка и отображение часового пояса пользователя
- Подтверждение и отмена действий

## 💬 Список команд
| Команда | Описание |
|:-------:|:--------:|
| show_all_reminders | показать все напоминания |
| set_timezone | задать часовой пояс |
| show_timezone | показать часовой пояс |
| delete_reminder | удалить напоминание |
| delete_nearest_reminder | удалить ближайшее напоминание |
| delete_all_reminders | удалить все напоминания |
| cancel | отменить текущее действие |
| help | справка |

## ⚙️ Технологии
- Python
- AIOgram
- PostgreSQL

## 📁 Структура проекта
```bash
    .
    |
    ├── handlers/
    |   ├── __init__.py
    |   ├── common_handlers.py
    |   ├── delete_reminders_handlers.py
    |   ├── main_handlers.py
    |   └── set_timezone_handlers.py
    |
    ├── keyboards/
    |   ├── __init__.py
    |   └── keyboards.py
    |
    ├── middlewares/
    |   ├── __init__.py
    |   └── db.py
    |
    ├── utils/
    |   ├── __init__.py
    |   ├── db.py
    |   ├── logger.py
    |   ├── misc.py
    |   └── validators.py
    |
    ├── .env
    ├── queries.sql
    ├── receiver.py
    ├── requirements.txt
    ├── sender.py
    |
    └── README.md
```

## 🧠 Идеи для развития
- Повторяющиеся напоминания (ежедневные, еженедельные и т.д.)
- Интеграция с календарями Google/Outlook
- Локализация на разные языки

## 🚀 Как запустить локально
⚠️ Для запуска бота необходимо предварительно создать БД с необходимыми таблицами (запросы для создания таблиц в файле queries.sql). В качестве СУБД выбрана PostgreSQL.

```bash
    # Клонировать репозиторий:
    git clone https://github.com/andrewsalmin/reminder-bot.git
    
    # Прописать credentials в файле .env
    
    # В первой консоли запустить часть, отвечающую за приём сообщений от пользователя
    cd reminder-bot
    python -m venv venv                           # создать виртуальное окружение (один раз)
    source venv/bin/activate                      # активировать окружение (Linux / macOS)
    venv\Scripts\activate                         # активировать окружение (Windows)
    pip install -r requirements.txt               # установить зависимости в это окружение (один раз)
    python receiver.py
    
    # В другой консоли запустить часть, отвечающую за отправку сообщений пользователю
    python sender.py
```

## 📜 Лицензия

Этот проект распространяется по лицензии [MIT](https://opensource.org/licenses/MIT).
