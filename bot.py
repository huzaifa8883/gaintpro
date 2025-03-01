import asyncio
import random
import nest_asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Telegram bot ka token
TOKEN = "7974068784:AAFs-RpxmHrca2OawNHucMxeGhk5jGBXR4A"

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
    chat_id = context.job.chat_id  # Use job.chat_id to get chat_id
    ad = generate_random_ad()
    await context.bot.send_message(chat_id=chat_id, text=ad)

# Bot start karne ka function
async def main():
    app = Application.builder().token(TOKEN).build()

    # Start polling the bot
    app.add_handler(CommandHandler("start", start))

    # Start the auto generation job for every user that starts the bot
    async def start_auto_generation(update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        job_queue = context.application.job_queue  # Ensure job queue is initialized

        # Check if a job with this name already exists
        job = job_queue.get_jobs_by_name(str(chat_id))
        if not job:  # Check if the job doesn't already exist
            # Run the repeating job every 5 minutes
            job_queue.run_repeating(auto_generate, interval=300, first=0, chat_id=chat_id, name=str(chat_id))
            await update.message.reply_text("Auto signal generation started. You will receive a signal every 5 minutes.")
        else:
            await update.message.reply_text("Auto signal generation is already running!")

    # Add the auto generation command
    app.add_handler(CommandHandler("start_auto", start_auto_generation))

    # Start the job queue and start polling
    await app.run_polling()

# 🔹 Event Loop Fix for Running in Async Environments 🔹
if __name__ == "__main__":
    nest_asyncio.apply()  # Jupyter Notebook aur similar environments ke liye
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(main())
