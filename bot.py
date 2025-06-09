from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Replace these
TOKEN = "7842828813:AAG7QpuH7JIYDqLFtq66SCVekqoDeIK1lbg"
GROUP_CHAT_ID = -1002556002177  # Replace with your Telegram group chat ID

# 1. Daily reminder at 6:30 PM IST
async def send_daily_reminder(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text="⏰ It's 6:30 PM! Time to grind, you awesome coders 💻🔥")

# 2. Daily poll at 12:00 AM IST
async def send_daily_poll(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_poll(
        chat_id=GROUP_CHAT_ID,
        question="🌙 How many DSA problems did you crush today?",
        options=["1", "2", "3", "3+"],
        is_anonymous=False,
        allows_multiple_answers=False,
    )

# 3. Welcome new members
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user in update.message.new_chat_members:
        await update.message.reply_text(
            f"👋 Welcome {user.first_name}!\n"
            "Please introduce yourself and let us know your DSA or Spring Boot progress! 🚀"
        )

# Create app and run it
app = ApplicationBuilder().token(TOKEN).build()

# Schedule jobs
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")
scheduler.add_job(send_daily_reminder, CronTrigger(hour=18, minute=30), kwargs={"context": app})
scheduler.add_job(send_daily_poll, CronTrigger(hour=0, minute=0), kwargs={"context": app})
scheduler.start()

# Add handlers
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new_member))

# Start bot
app.run_polling()
