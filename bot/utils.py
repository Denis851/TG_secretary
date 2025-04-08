import os
import json
import random
from datetime import datetime

from aiogram import Bot
from aiogram.types import FSInputFile
from dotenv import load_dotenv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")

# ---------- JSON УТИЛИТЫ ----------

def load_json(path, default=[]):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---------- ЦИТАТА ДНЯ ----------

def get_random_quote():
    try:
        with open("data/quotes.txt", encoding="utf-8") as f:
            quotes = [line.strip() for line in f if line.strip()]
        return random.choice(quotes)
    except Exception:
        return "Каждый день — шанс начать заново."

# ---------- PDF ОТЧЁТ ----------

def generate_report_pdf(filename="data/weekly_report.pdf"):
    goals = load_json("data/goals.json", [])
    tasks = load_json("data/checklist.json", [])
    completed_goals = [g for g in goals if g.get("done")]
    completed_tasks = [t for t in tasks if t.get("done")]

    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    c.setTitle("Weekly Progress Report")

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "📊 Weekly Progress Report")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Дата: {datetime.now().strftime('%d.%m.%Y')}")

    # Goals
    c.drawString(50, height - 120, f"🎯 Цели выполнены: {len(completed_goals)} / {len(goals)}")
    for i, goal in enumerate(goals, start=1):
        status = "✅" if goal.get("done") else "❌"
        c.drawString(70, height - 140 - i * 20, f"{status} {goal.get('text', 'Цель без текста')}")

    y_offset = height - 160 - len(goals) * 20 - 20
    c.drawString(50, y_offset, f"📋 Задачи выполнены: {len(completed_tasks)} / {len(tasks)}")
    for i, task in enumerate(tasks, start=1):
        status = "✅" if task.get("done") else "❌"
        c.drawString(70, y_offset - i * 20, f"{status} {task.get('text', 'Задача без текста')}")

    c.save()
    return filename

# ---------- ОТПРАВКА ОТЧЁТА ----------

async def send_weekly_report_pdf():
    try:
        user_data = load_json("data/user.json", {})
        user_id = user_data.get("id")
        if not user_id:
            print("❗ Telegram ID пользователя не найден.")
            return

        path = generate_report_pdf()
        await bot.send_document(chat_id=user_id, document=FSInputFile(path), caption="📄 Твой еженедельный отчёт готов!")
        print("✅ Отчёт отправлен.")
    except Exception as e:
        print(f"❌ Ошибка отправки отчёта: {e}")

