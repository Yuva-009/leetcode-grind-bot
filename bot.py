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
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")  # Ensure this is set
TIMEZONE = pytz.timezone("Asia/Kolkata")

# ... [Keep existing code] ...

# === NEW HELPER FUNCTION ===
async def send_to_group(context: ContextTypes.DEFAULT_TYPE, text: str):
    """Helper to send messages to the group."""
    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=text
    )

# === NEW HANDLERS ===
async def sendpublic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /sendpublic command: Broadcast user's message to group."""
    if update.message.chat.type != "private":
        await update.message.reply_text("❌ This command only works in private chat!")
        return
    
    # Check if text exists after command
    if not context.args:
        context.user_data['awaiting_broadcast'] = True  # Set state
        await update.message.reply_text("📝 Please send me the message you want to broadcast now!")
    else:
        message = " ".join(context.args)
        await send_to_group(context, message)
        await update.message.reply_text("✅ Message sent to the group!")

async def handle_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Capture follow-up messages after /sendpublic."""
    user_data = context.user_data
    
    # Check if user is in "awaiting broadcast" state
    if user_data.get('awaiting_broadcast') and update.message.chat.type == "private":
        await send_to_group(context, update.message.text)
        user_data['awaiting_broadcast'] = False  # Clear state
        await update.message.reply_text("✅ Message sent to the group!")

# === UPDATED MAIN ===
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    # Existing handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(ChatMemberHandler(welcome, ChatMemberHandler.CHAT_MEMBER))
    
    # NEW: Add handlers for broadcast feature
    app.add_handler(CommandHandler("sendpublic", sendpublic))
    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND,
            handle_broadcast_message
        )
    )

    # ... [Keep webhook setup] ...

    # Run in webhook mode
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"https://leetcode-grind-bot-1.onrender.com/{BOT_TOKEN}"
    )
