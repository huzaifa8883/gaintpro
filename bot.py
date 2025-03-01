import logging
import random
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
)
from threading import Thread
import aiohttp  # Importing aiohttp for making HTTP requests
import asyncio  # We will use asyncio to manage both Flask and Telegram bot

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

TOKEN = "7930820356:AAFiicSUzpUx2E2_KCaUOzkbETqUI5hvm-I"
WEBHOOK_URL = "https://gaintpro-production.up.railway.app/webhook"
WEBHOOK_SECRET = "nothing"

app = Flask(__name__)

# Initialize Telegram bot application
application = Application.builder().token(TOKEN).build()

# ✅ **Function to Generate Random Trade Signals**
def generate_random_signal():
    signals = [
        "🔵 Buy EUR/USD at 1.0850, TP: 1.0900, SL: 1.0800",
        "🔴 Sell GBP/USD at 1.2750, TP: 1.2700, SL: 1.2800",
        "🟢 Buy BTC/USD at 45,000, TP: 46,500, SL: 43,500",
        "🔴 Sell ETH/USD at 3,200, TP: 3,100, SL: 3,300"
    ]
    return random.choice(signals)

# ✅ **Auto Generate Trade Signals Every 5 Minutes**
async def auto_generate(context: CallbackContext):
    try:
        chat_id = context.job.chat_id
        signal = generate_random_signal()
        logging.info(f"✅ Generating signal for chat {chat_id}: {signal}")
        await context.bot.send_message(chat_id=chat_id, text=signal)
    except Exception as e:
        logging.error(f"❌ Error in auto_generate: {e}")

# ✅ **Start Auto Signal Generation**
async def start_auto_generation(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    job_queue = context.application.job_queue
    job = job_queue.get_jobs_by_name(str(chat_id))

    if not job:
        logging.info(f"✅ Job started for chat ID: {chat_id}")
        job_queue.run_repeating(auto_generate, interval=300, first=5, chat_id=chat_id, name=str(chat_id))
        await update.message.reply_text("🚀 Auto signal generation started! You'll receive signals every 5 minutes.")
    else:
        await update.message.reply_text("⚠ Auto signal generation is already running!")

# ✅ **Stop Auto Signal Generation**
async def stop_auto_generation(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    job_queue = context.application.job_queue
    jobs = job_queue.get_jobs_by_name(str(chat_id))

    if jobs:
        for job in jobs:
            job.schedule_removal()
        logging.info(f"❌ Job stopped for chat ID: {chat_id}")
        await update.message.reply_text("🛑 Auto signal generation stopped.")
    else:
        await update.message.reply_text("⚠ No active signal generation found.")

# ✅ **Webhook Handler for Telegram Messages**
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # Verify secret token
        if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
            return "Unauthorized", 401

        data = request.json
        logging.info(f"📩 Received Webhook Data: {data}")
        update = Update.de_json(data, application.bot)
        application.update_queue.put_nowait(update)
        return "OK", 200
    except Exception as e:
        logging.error(f"❌ Webhook Error: {e}")
        return "ERROR", 400

# ✅ **Set Webhook on Startup**
async def set_webhook():
    webhook_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}"
    async with aiohttp.ClientSession() as session:  # Using aiohttp for the POST request
        async with session.post(webhook_url) as response:
            logging.info(await response.json())

# ✅ **Run Flask App**
def run_flask():
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)

# ✅ **Main Function to Start Flask and Telegram Bot**
async def main():
    # Set the webhook before running the bot
    await set_webhook()

    # Run Flask app in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Add Telegram bot handlers
    application.add_handler(CommandHandler("start_auto", start_auto_generation))
    application.add_handler(CommandHandler("stop_auto", stop_auto_generation))

    # Run Telegram bot
    await application.run_polling()

# ✅ **Run the asyncio event loop to manage both Flask and the Telegram bot**
if __name__ == "__main__":
    try:
        loop = asyncio.get_running_loop()  # Use get_running_loop()
    except RuntimeError:  # If no event loop is running
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(main())  # Ensures that everything is running inside an event loop
