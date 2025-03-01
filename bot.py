import asyncio
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Telegram bot ka token
TOKEN = "7974068784:AAFs-RpxmHrca2OawNHucMxeGhk5jGBXR4A"

# Scheduler initialize kar rahe hain
scheduler = AsyncIOScheduler()

# Random ad type generate karne ka function
def generate_random_ad():
    ad_types = ["Single", "Double", "Small", "Big"]
    random_ad_type = random.choice(ad_types)
    bet_amount = random.choice([1, 3, 5, 10, 27])  # Random bet amount
    period = random.randint(1520250301100, 1520250301200)  # Random period number
    return f"""⏰Trade Type: 5 Minute⏰

👉Period: {period}
👉Buy: {random_ad_type}
💰Bet: {bet_amount} USDT

🔥Earn 30% interest on each bet.
🔥The higher the stage, the more profit you make."""

# /start command ka response
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome! The bot will automatically generate trade signals every 5 minutes.")

# Har 5 minute bad auto generate hone wala function
async def auto_generate(context: CallbackContext):
    chat_id = context.job.chat_id  # Jis chat se /start command aayi thi
    ad = generate_random_ad()
    await context.bot.send_message(chat_id=chat_id, text=ad)

# /generate command ka response
async def generate(update: Update, context: CallbackContext):
    ad = generate_random_ad()
    await update.message.reply_text(f"Generated:\n\n{ad}")

# Auto signal generation start karne ka function
async def start_auto_generation(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    job = context.job_queue.get_jobs_by_name(str(chat_id))
    if not job:
        context.job_queue.run_repeating(auto_generate, interval=300, first=0, chat_id=chat_id, name=str(chat_id))
        await update.message.reply_text("Auto signal generation started. You will receive a signal every 5 minutes.")
    else:
        await update.message.reply_text("Auto signal generation is already running!")

# Bot aur scheduler start karne ka function
async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("generate", generate))
    app.add_handler(CommandHandler("start_auto", start_auto_generation))  # Start auto signals

    # Scheduler ko proper async execution ke liye start karna
    scheduler.start()

    print("🤖 Bot is running...")
    await app.run_polling()

# Run the bot using asyncio.run()
if __name__ == "__main__":
    asyncio.run(main())
