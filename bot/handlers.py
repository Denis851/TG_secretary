from aiogram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, Router

router = Router()

# Главное меню (Reply Keyboard)
main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Расписание")],
        [KeyboardButton(text="✅ Чек-лист")],
        [KeyboardButton(text="🎯 Цели")],
        [KeyboardButton(text="💬 Цитата")],
    ],
    resize_keyboard=True
)

# Inline-кнопка для цитаты
quote_inline_kb = InlineKeyboardButton(
    text="🔁 Обновить цитату",
    callback_data="update_quote"
)

# Inline-кнопка для отчета
report_inline_kb = InlineKeyboardButton(
    text="📊 Получить отчет",
    callback_data="weekly_report"
)

# Клавиатура для целей
goals_inline_kb = [
    [
        InlineKeyboardButton(text="➕ Добавить цель", callback_data="add_goal"),
        InlineKeyboardButton(text="📋 Показать цели", callback_data="show_goals")
    ]
]

# Клавиатура для задач
tasks_inline_kb = [
    [
        InlineKeyboardButton(text="➕ Добавить задачу", callback_data="add_task"),
        InlineKeyboardButton(text="📋 Показать задачи", callback_data="show_tasks")
    ]
]

# Клавиатура для чек-листа
checklist_inline_kb = [
    [
        InlineKeyboardButton(text="☑️ Отметить выполненное", callback_data="mark_done"),
        InlineKeyboardButton(text="📋 Показать чек-лист", callback_data="show_checklist")
    ]
]
def register_handlers(dp: Router):
    dp.include_router(router)