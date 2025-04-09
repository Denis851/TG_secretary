import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.config import BOT_TOKEN, USER_ID
from bot.handlers import register_handlers
from bot.fsm_handlers import register_fsm_handlers
from bot.utils import send_quote, generate_and_send_report

# Логирование
logging.basicConfig(level=logging.INFO)

# Бот и диспетчер
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Планировщик задач
scheduler = AsyncIOScheduler()

def setup_scheduler():
    # Отправка цитаты каждое утро в 6:00
    scheduler.add_job(send_quote, trigger='cron', hour=6, minute=0, args=[bot, USER_ID])

    # Отправка отчета каждое воскресенье в 21:00
    scheduler.add_job(generate_and_send_report, trigger='cron', day_of_week='sun', hour=21, minute=0, args=[bot, USER_ID])

    scheduler.start()

async def main():
    # Регистрация маршрутов
    register_handlers(dp)
    register_fsm_handlers(dp)

    # Запуск планировщика
    setup_scheduler()

    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
