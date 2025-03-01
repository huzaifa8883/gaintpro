import logging
import asyncio
import random
from flask import Flask, request
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Flask app initialize
app = Flask(__name__)

# Telegram Bot Token (Replace with your own)
TOKEN = "7930820356:AAFiicSUzpUx2E2_KCaUOzkbETqUI5hvm-I"

# Store users who started the bot
subscribed_users = set()

# Set up logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to send trade signals
async def send_signal(context: CallbackContext):
    buy_options = ["Big", "Small", "Single", "Double"]
    buy = random.choice(buy_options)

    period = str(int(asyncio.get_event_loop().time() * 1000))  # Generate period
    message = (
        f"⏰Trade Type: 5 Minute⏰\n\n"
        f"👉Period:{period}\n"
        f"👉Buy: {buy}\n"
        f"💰Bet: 1 USDT\n\n"
        f"🔥Earn 30% interest on each bet.\n"
        f"🔥The higher the stage, the more profit you make."
    )

    # Send message to all subscribed users
    for chat_id in subscribed_users:
        try:
            await context.bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            logger.error(f"Failed to send message to {chat_id}: {e}")

# Handle /start command
async def start(update: Update, context):
    chat_id = update.message.chat_id
    if chat_id not in subscribed_users:
        subscribed_users.add(chat_id)
        await update.message.reply_text("✅ You have subscribed to trade signals. You'll receive updates every 5 minutes.")
    else:
        await update.message.reply_text("🔔 You are already subscribed!")

# Main function to set up the bot
async def main():
    application = Application.builder().token(TOKEN).build()
    
    # Add /start command handler
    application.add_handler(CommandHandler("start", start))
    
    # Schedule job to send messages every 5 minutes
    job_queue = application.job_queue
    job_queue.run_repeating(send_signal, interval=300, first=5)

    # Start bot polling
    await application.run_polling()

# Flask route for testing
@app.route('/')
def home():
    return "Bot is running!"

# Fix for Webhook 404 error
@app.route('/webhook', methods=['POST'])
def webhook():
    return "Webhook received!", 200

# Function to start the bot
def start_bot():
    asyncio.run(main())

# Start Flask and Telegram bot
if __name__ == "__main__":
    # Run Telegram bot in main thread
    bot_thread = Thread(target=start_bot, daemon=True)
    bot_thread.start()

    # Start Flask app
    app.run(host="0.0.0.0", port=5000, debug=False)
