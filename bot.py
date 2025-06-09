from datetime import time
import pytz
import os
import pytz
import logging
from telegram import Update, Poll
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ChatMemberHandler
)
from telegram.ext import JobQueue

BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8443))
TIMEZONE = pytz.timezone("Asia/Kolkata")

logging.basicConfig(level=logging.INFO)

# === HANDLERS ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Bot is live with Webhook mode!")

async def daily_reminder(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=os.getenv("GROUP_CHAT_ID"),
        text="🧩 Reminder: One LeetCode a day keeps the regrets away!"
        
        
    )

async def send_poll(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_poll(
        chat_id=os.getenv("GROUP_CHAT_ID"),
        question="🧠 How many problems did you solve today?",
        options=["1️⃣ - One problem down, thousands to go! 😅", "2️⃣ - Two problems done, brain feeling twice as smart! 🤓", "3️⃣ - Three today? Someone’s on fire! 🔥", "3️⃣+ - Coding legend in the making! Bow down! 👑"],
        is_anonymous=False
    )

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_member = update.chat_member.new_chat_member
    if new_member.status == "member":
        await context.bot.send_message(
            chat_id=update.chat_member.chat.id,
            text=(
                f"👋 Welcome, {new_member.user.mention_html()}!\n"
                "Please introduce yourself and tell us how your DSA and Java/Spring Boot journey is going! 🚀"
            ),
            parse_mode="HTML"
        )

# === MAIN FUNCTION ===

async def post_init(application):
    job_queue = application.job_queue

    # Schedule 6:30 PM reminder
    job_queue.run_daily(
        callback=daily_reminder,
        time=time(18, 30, 0, tzinfo=TIMEZONE),
        name="daily_reminder"
    )
    
    

    # Schedule 12:00 AM poll
    job_queue.run_daily(
        callback=send_poll,
        time=time(22, 52, 0, tzinfo=TIMEZONE),
        name="midnight_poll"
    )


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(ChatMemberHandler(welcome, ChatMemberHandler.CHAT_MEMBER))

    # Run in webhook mode
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"https://leetcode-grind-bot-1.onrender.com/{BOT_TOKEN}"
    )
