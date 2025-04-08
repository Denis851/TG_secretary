# 📁 config.py — Загрузка переменных окружения и базовая настройка
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = int(os.getenv("USER_ID", 0))

if not BOT_TOKEN or USER_ID == 0:
    raise ValueError("BOT_TOKEN или USER_ID не заданы корректно в .env!")

