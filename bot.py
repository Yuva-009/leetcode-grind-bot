import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, MessageHandler,
    filters, ContextTypes
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio

# Set up logging
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "7842828813:AAG7QpuH7JIYDqLFtq66SCVekqoDeIK1lbg"
GROUP_CHAT_ID = -1002556002177  # Replace with actual group chat ID

async def send_daily_reminder(app):
    await app.bot.send_message(chat_id=GROUP_CHAT_ID, text="🌞 6:30 PM – Consistency beats talent — DSA grind mode: ON 🔥 Let’s go!")

async def send_daily_poll(app):
    await app.bot.send_poll(
        chat_id=GROUP_CHAT_ID,
        question="🧠 Midnight Check-in! How many problems did you solve today?",
        options=[
            "0️⃣ - Today’s problems: zero solved, infinite excuses! 😂",
            "1️⃣ - One problem down, thousands to go! 😅",
            "2️⃣ - Two problems done, brain feeling twice as smart! 🤓",
            "3️⃣ - Three today? Someone’s on fire! 🔥",
            "3️⃣+ - Coding legend in the making! Bow down! 👑"
        ],
        is_anonymous=False
    )

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type in ["group", "supergroup"]:
        for user in update.message.new_chat_members:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"👋 Welcome, {user.mention_html()}!\nDrop a quick intro & tell us about your DSA & Development progress!",
                parse_mode='HTML'
            )

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Scheduler setup
    scheduler = AsyncIOScheduler()

    # Because scheduler jobs are sync or async functions without context,
    # we wrap calls so they get 'app' passed correctly
    scheduler.add_job(lambda: asyncio.create_task(send_daily_reminder(app)),
                      CronTrigger(hour=18, minute=30, timezone="Asia/Kolkata"))
    scheduler.add_job(lambda: asyncio.create_task(send_daily_poll(app)),
                      CronTrigger(hour=0, minute=0, timezone="Asia/Kolkata"))
    scheduler.start()

    # Add handler for welcoming new chat members
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    # Run the bot (this will manage event loop correctly)
    await app.run_polling()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
