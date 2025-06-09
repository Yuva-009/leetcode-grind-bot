import logging
import datetime
import pytz
from telegram import Update, Poll
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler, ChatMemberHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- Config ---
BOT_TOKEN = "7842828813:AAG7QpuH7JIYDqLFtq66SCVekqoDeIK1lbg"
GROUP_ID = -1002556002177  # your group ID

# --- Logging ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Scheduler ---
scheduler = AsyncIOScheduler()

# --- Reminder message ---
async def send_daily_reminder(app):
    try:
        await app.bot.send_message(
            chat_id=GROUP_ID,
            text="🚀 Time to grind LeetCode! Let’s make today count! 💪"
        )
        logger.info("Sent daily reminder")
    except Exception as e:
        logger.error(f"Error sending daily reminder: {e}")

# --- Poll with banter ---
async def send_daily_poll(app):
    try:
        poll_message = await app.bot.send_poll(
            chat_id=GROUP_ID,
            question="How many problems did you solve today?",
            options=["1", "2", "3", "3+"],
            is_anonymous=False
        )
        logger.info("Sent daily poll")

        # Banter reply after poll (a short delay to avoid flooding)
        await app.bot.send_message(
            chat_id=GROUP_ID,
            text="👀 Be honest... or LeetCode will haunt your dreams 😈"
        )
    except Exception as e:
        logger.error(f"Error sending daily poll: {e}")

# --- Welcome new members ---
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        welcome_text = (
            f"👋 Welcome, {member.first_name}!\n\n"
            "Drop a quick intro:\n"
            "- What’s your DSA progress?\n"
            "- Are you working on development? If yes, what tech stack?"
        )
        await context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_text)

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your LeetCode grind bot. Let's code!")

async def log_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Just log the group ID if you want
    chat = update.effective_chat
    logger.info(f"Message in chat {chat.id} ({chat.type})")

# --- Main ---
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.ALL, log_group_id))  # Optional

    # Scheduler jobs (using Asia/Kolkata timezone)
    tz = pytz.timezone('Asia/Kolkata')

    scheduler.add_job(send_daily_reminder, 'cron', hour=18, minute=30, timezone=tz, args=[app])
    scheduler.add_job(send_daily_poll, 'cron', hour=0, minute=0, timezone=tz, args=[app])

    scheduler.start()

    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
