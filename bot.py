import nest_asyncio
import asyncio
from datetime import time
import pytz

from telegram import Update, Poll
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    ChatMemberHandler,
    filters,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# === PATCH THE EVENT LOOP ===
nest_asyncio.apply()

# === Replace these ===
TOKEN = "YOUR_BOT_TOKEN"  # Replace with your bot token
GROUP_CHAT_ID = -123456789  # Replace with your group ID

IST = pytz.timezone("Asia/Kolkata")

# === Handlers ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is live and ready to grind 💪")

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.chat_member.new_chat_members:
        await context.bot.send_message(
            chat_id=update.chat_member.chat.id,
            text=(
                f"👋 Welcome {member.mention_html()} to the DSA & Dev grind group!\n"
                f"🚀 Drop a quick intro and tell us how far you're in DSA and Java/Spring Boot."
            ),
            parse_mode="HTML"
        )

# === Scheduled Jobs ===

async def send_reminder(bot):
    await bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text="⏰ It's 6:30 PM! Time to wrap up distractions and grind some LeetCode 💻"
    )

async def send_midnight_poll(bot):
    await bot.send_poll(
        chat_id=GROUP_CHAT_ID,
        question="🌙 Midnight Check: How many problems did you solve today?",
        options=["1", "2", "3", "3+ 🔥"],
        is_anonymous=False,
        allows_multiple_answers=False,
    )

# === Main ===

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(ChatMemberHandler(welcome, ChatMemberHandler.CHAT_MEMBER))

    scheduler = AsyncIOScheduler(timezone=IST)

    scheduler.add_job(send_reminder, 'cron', hour=18, minute=30, args=[app.bot])
    scheduler.add_job(send_midnight_poll, 'cron', hour=0, minute=0, args=[app.bot])

    scheduler.start()
    print("✅ Bot and scheduler started successfully")
    await app.run_polling()

# Run without crashing event loop
asyncio.get_event_loop().run_until_complete(main())
