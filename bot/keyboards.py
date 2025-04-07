from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

# 🔹 Главное меню (reply)
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🗓️ Расписание")],
        [KeyboardButton(text="🧠 Цели")],
        [KeyboardButton(text="✅ Чеклист")],
        [KeyboardButton(text="📊 Прогресс")]
    ],
    resize_keyboard=True
)

# 🔹 Инлайн-кнопки для задач и целей
inline_actions_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Выполнено", callback_data="done")],
        [InlineKeyboardButton(text="❌ Не выполнено", callback_data="not_done")],
        [InlineKeyboardButton(text="➕ Добавить задачу", callback_data="add_task")],
        [InlineKeyboardButton(text="➕ Добавить цель", callback_data="add_goal")]
    ]
)
