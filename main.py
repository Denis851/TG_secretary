import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.config import BOT_TOKEN, USER_ID
from handlers import register_handlers
from fsm_handlers import register_fsm_handlers
from utils import generate_report_pdf

from aiogram.enums import ParseMode
bot = Bot(token="YOUR_TOKEN", parse_mode=ParseMode.HTML)


dp = Dispatcher()

# Задача по расписанию — автоотчёт в PDF по воскресеньям
async def weekly_report():
    path = generate_report_pdf()
    if path:
        await bot.send_document(chat_id=USER_ID, document=path, caption="📊 Еженедельный отчёт")

async def main():
    # Расписание задач
    scheduler = AsyncIOScheduler()
    scheduler.add_job(weekly_report, "cron", day_of_week="sun", hour=21, minute=0)
    scheduler.start()

    # Регистрация хендлеров
    register_handlers(dp)
    register_fsm_handlers(dp)

    print("Бот запущен ✅")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
