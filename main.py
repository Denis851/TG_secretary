import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.config import BOT_TOKEN, USER_ID
from bot.handlers import register_handlers
from bot.fsm_handlers import register_fsm_handlers
from bot.utils import generate_report_pdf

from aiogram.types import InputFile

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Задача по расписанию — АВТООТЧЁТ в PDF по воскресеньям
async def weekly_report():
    path = generate_report_pdf()
    if path:
        await bot.send_document(chat_id=USER_ID, document=InputFile(path), caption="📊 Твой недельный отчёт")

async def main():
    # Регистрация хендлеров
    register_handlers(dp)
    register_fsm_handlers(dp)

    # Планировщик задач
    scheduler = AsyncIOScheduler()
    scheduler.add_job(weekly_report, "cron", day_of_week="sun", hour=21, minute=0)
    scheduler.start()

    await bot.delete_webhook(drop_pending_updates=True)
    register_fsm_handlers(dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
git add .
git commit -m "fix: clear webhook conflict"
git push origin main
