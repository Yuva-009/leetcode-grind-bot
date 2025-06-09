import asyncio
import logging
from telegram import Update, Poll
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, ChatMemberHandler, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# === CONFIG ===
BOT_TOKEN = "7842828813:AAG7QpuH7JIYDqLFtq66SCVekqoDeIK1lbg"
GROUP_CHAT_ID = -1002556002177  # Replace with your group ID

# === DAILY REMINDER ===
async def send_daily_reminder(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text="🌟 It's 6:30 PM! Time to kick off your LeetCode grind! 🚀 Let's goooo! 💪"
    )

# === DAILY POLL ===
async def send_daily_poll(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_poll(
        chat_id=GROUP_CHAT_ID,
        question="🧠 How many problems did you solve today?",
        options=["1", "2", "3", "3+"],
        is_anonymous=False,
        explanation="Don't lie 😤, we got LeetCode open 👀"
    )

# === WELCOME NEW MEMBER ===
async def welcome_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.chat_member.new_chat_members:
        name = member.first_name
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                f"👋 Welcome *{name}* to the LeetCode Grind group!\n\n"
                "1. Drop a quick intro (name, college/year if you're a student).\n"
                "2. Are you working on development? If yes, what tech stack?\n"
                "3. What's your current DSA progress?\n"
                "4. Are you learning Java/Spring Boot? What's your status?"
            ),
            parse_mode="Markdown"
        )

# === MAIN FUNCTION ===
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Scheduler setup
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_daily_reminder, CronTrigger(hour=18, minute=30, timezone="Asia/Kolkata"), args=[app.bot])
    scheduler.add_job(send_daily_poll, CronTrigger(hour=0, minute=0, timezone="Asia/Kolkata"), args=[app.bot])
    scheduler.start()

    # Handlers
    app.add_handler(ChatMemberHandler(welcome_user, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: None))  # Placeholder if needed

    await app.run_polling()

# === ENTRY POINT FIX FOR RENDER ===
if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
