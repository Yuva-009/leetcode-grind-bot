from datetime import time, datetime, timedelta
import pytz
import os
import logging
import pickle
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ChatMemberHandler, PollAnswerHandler
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8443))
TIMEZONE = pytz.timezone("Asia/Kolkata")
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")

# Set up data storage
DATA_FILE = "poll_data.pkl"
os.makedirs("data", exist_ok=True)

logging.basicConfig(level=logging.INFO)

# === DATA HANDLING FUNCTIONS ===
def save_data(data):
    with open(DATA_FILE, "wb") as f:
        pickle.dump(data, f)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "rb") as f:
            return pickle.load(f)
    return {"weekly_scores": {}, "last_reset": datetime.now()}

def next_sunday_at_night():
    now = datetime.now(TIMEZONE)
    next_sunday = now + timedelta(days=(6 - now.weekday()))
    return next_sunday.replace(hour=23, minute=59, second=0)

# === POST INITIALIZATION ===
async def post_init(application):
    job_queue = application.job_queue

    # Existing jobs
    job_queue.run_daily(
        callback=daily_reminder,
        time=time(18, 30, 0, tzinfo=TIMEZONE),
        name="daily_reminder"
    )
    
    job_queue.run_daily(
        callback=send_poll,
        time=time(0, 0, 0, tzinfo=TIMEZONE),
        name="midnight_poll"
    )
    
    # New weekly reset job
    job_queue.run_repeating(
        reset_leaderboard,
        interval=timedelta(weeks=1),
        first=next_sunday_at_night(),
        name="weekly_reset"
    )

# === NEW LEADERBOARD FUNCTIONS ===
async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = load_data()
    answer = update.poll_answer
    user_id = answer.user.id
    option_chosen = answer.option_ids[0]  # 0=1 problem, 1=2 problems, etc.
    
    points = option_chosen + 1  # Convert to 1-based count
    
    if str(user_id) not in user_data["weekly_scores"]:
        user_data["weekly_scores"][str(user_id)] = 0
    
    user_data["weekly_scores"][str(user_id)] += points
    save_data(user_data)

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = load_data()
    
    if not user_data["weekly_scores"]:
        await update.message.reply_text("🚧 No data yet! Answer today's poll to get on the board.")
        return
    
    sorted_scores = sorted(
        user_data["weekly_scores"].items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    message = "🏆 <b>Weekly Leaderboard</b> 🏆\n\n"
    for rank, (user_id, score) in enumerate(sorted_scores[:10], 1):
        try:
            user = await context.bot.get_chat(user_id)
            name = user.full_name
        except:
            name = f"User #{user_id}"
        message += f"{rank}. {name}: <b>{score}</b> problems\n"
    
    await update.message.reply_text(message, parse_mode="HTML")

async def reset_leaderboard(context: ContextTypes.DEFAULT_TYPE):
    user_data = load_data()
    
    if not user_data["weekly_scores"]:
        return
    
    top5 = sorted(
        user_data["weekly_scores"].items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    announcement = "🎉 <b>Weekly Results</b> 🎉\n\n"
    for rank, (user_id, score) in enumerate(top5, 1):
        try:
            user = await context.bot.get_chat(user_id)
            name = user.full_name
        except:
            name = f"User #{user_id}"
        announcement += f"{rank}. {name}: <b>{score}</b> problems\n"
    
    announcement += "\nLeaderboard has been reset! New week starts now 💪"
    
    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=announcement,
        parse_mode="HTML"
    )
    
    user_data["weekly_scores"] = {}
    save_data(user_data)

# === EXISTING HANDLERS (unchanged) ===
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
                "Please introduce yourself and tell us how your DSA and Java/Spring Boot journey is going! 🚀"
            ),
            parse_mode="HTML"
        )

async def send_to_group(context: ContextTypes.DEFAULT_TYPE, text: str):
    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=text
    )

async def sendpublic(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    
    # New leaderboard handlers
    app.add_handler(PollAnswerHandler(handle_poll_answer))
    app.add_handler(CommandHandler("leaderboard", leaderboard))

    # Run in webhook mode
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"https://leetcode-grind-bot-1.onrender.com/{BOT_TOKEN}"
    )
