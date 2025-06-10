from datetime import time
import pytz
import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ChatMemberHandler
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8443))
TIMEZONE = pytz.timezone("Asia/Kolkata")
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")

logging.basicConfig(level=logging.INFO)

# === POST INITIALIZATION ===
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
        time=time(0, 0, 0, tzinfo=TIMEZONE),
        name="midnight_poll"
    )

# === HANDLERS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Bot is live with Webhook mode!")

async def daily_reminder(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text="🧩 Reminder: One LeetCode a day keeps the regrets away! Start solving now!!!"
    )

async def send_poll(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_poll(
        chat_id=GROUP_CHAT_ID,
        question="🧠 How many problems did you solve today?",
        options=["1️⃣ - One problem down, thousands to go! 😅", 
                "2️⃣ - Two problems done, brain feeling twice as smart! 🤓", 
                "3️⃣ - Three today? Someone's on fire! 🔥", 
                "3️⃣+ - Coding legend in the making! Bow down! 👑"],
        is_anonymous=False
    )

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_member = update.chat_member.new_chat_member
    if new_member.status == "member":
        await context.bot.send_message(
            chat_id=update.chat_member.chat.id,
            text=(
                f"👋 Welcome, {new_member.user.mention_html()}!\n"
                "Please introduce yourself and tell us how your DSA and Java/Spring Boot journey is going! �"
            ),
            parse_mode="HTML"
        )

async def send_to_group(context: ContextTypes.DEFAULT_TYPE, text: str):
    """Helper to send messages to the group."""
    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=text
    )

async def sendpublic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /sendpublic command: Broadcast user's message to group."""
    if update.message.chat.type != "private":
        await update.message.reply_text("❌ This command only works in private chat!")
        return
    
    if not context.args:
        context.user_data['awaiting_broadcast'] = True
        await update.message.reply_text("📝 Please send me the message you want to broadcast now!")
    else:
        message = " ".join(context.args)
        await send_to_group(context, message)
        await update.message.reply_text("✅ Message sent to the group!")

async def handle_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Capture follow-up messages after /sendpublic."""
    user_data = context.user_data
    
    if user_data.get('awaiting_broadcast') and update.message.chat.type == "private":
        await send_to_group(context, update.message.text)
        user_data['awaiting_broadcast'] = False
        await update.message.reply_text("✅ Message sent to the group!")

# === MAIN FUNCTION ===
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(ChatMemberHandler(welcome, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(CommandHandler("sendpublic", sendpublic))
    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND,
            handle_broadcast_message
        )
    )

    # Run in webhook mode
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"https://leetcode-grind-bot-1.onrender.com/{BOT_TOKEN}"
    )
