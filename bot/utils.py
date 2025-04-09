import os
import json
import random
from datetime import datetime
from aiogram import Bot
from aiogram.types import FSInputFile

from reportlab.pdfgen import canvas


# === Общие функции ===

def load_json(path: str, default=None):
    if default is None:
        default = []
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def save_json(path: str, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# === Цитата дня ===

def get_random_quote():
    try:
        with open("data/quotes.txt", encoding="utf-8") as f:
            quotes = [line.strip() for line in f if line.strip()]
        return random.choice(quotes)
    except Exception:
        return "Каждый день — шанс начать заново."


async def send_quote(bot: Bot, user_id: int):
    quote = get_random_quote()
    await bot.send_message(user_id, f"💬 Цитата дня:\n<em>{quote}</em>")


# === Генерация и отправка PDF отчета ===

def generate_report_text() -> str:
    today = datetime.today().strftime("%Y-%m-%d")
    checklist = load_json("data/checklist.json", [])
    goals = load_json("data/goals.json", [])
    mood = load_json("data/mood.json", [])

    report = f"📝 Отчёт за {today}\n\n"

    # Задачи
    completed = [task for task in checklist if task.get("done")]
    report += "✅ Выполненные задачи:\n"
    report += "\n".join(f" - {task['task']}" for task in completed) or " - нет\n"

    # Цели
    report += "\n🎯 Цели:\n"
    report += "\n".join(f" - {g['text']} ✅" if g.get("done") else f" - {g['text']} ❌" for g in goals) or " - нет\n"

    # Настроение
    today_mood = next((m['mood'] for m in reversed(mood) if today in m['time']), "—")
    report += f"\n😌 Настроение: {today_mood}"

    return report


def create_pdf_report(report_text: str, file_path: str):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    c = canvas.Canvas(file_path)
    y = 800
    for line in report_text.split('\n'):
        c.drawString(40, y, line)
        y -= 20
    c.save()


async def generate_and_send_report(bot: Bot, user_id: int):
    today = datetime.today().strftime("%Y-%m-%d")
    report_text = generate_report_text()
    file_path = f"data/reports/report_{today}.pdf"
    create_pdf_report(report_text, file_path)

    await bot.send_document(user_id, FSInputFile(file_path), caption="📤 Твой отчёт за неделю")
