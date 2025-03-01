import random
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from flask import Flask, request

# Telegram bot ka token
TOKEN = "7974068784:AAFs-RpxmHrca2OawNHucMxeGhk5jGBXR4A"
WEBHOOK_URL = "https://gaintpro-production.up.railway.app/webhook"  # Update with your actual webhook URL

# Flask app setup
app = Flask(__name__)

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
    try:
        chat_id = context.job.chat_id  # Use job.chat_id to get chat_id
        ad = generate_random_ad()
        await context.bot.send_message(chat_id=chat_id, text=ad)
    except Exception as e:
        print(f"Error in auto_generate: {e}")
        await context.bot.send_message(chat_id=context.job.chat_id, text="There was an error generating the trade signal.")

# Bot start karne ka function
async def main():
    # Create Application object
    app_bot = Application.builder().token(TOKEN).build()

    # Start the auto generation job for every user that starts the bot
    async def start_auto_generation(update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        job_queue = context.application.job_queue

        # Check if a job with this name already exists
        job = job_queue.get_jobs_by_name(str(chat_id))
        if not job:  # Check if the job doesn't already exist
            # Run the repeating job every 5 minutes
            job_queue.run_repeating(auto_generate, interval=300, first=0, chat_id=chat_id, name=str(chat_id))
            await update.message.reply_text("Auto signal generation started. You will receive a signal every 5 minutes.")
        else:
            await update.message.reply_text("Auto signal generation is already running!")

    # Add the auto generation command
    app_bot.add_handler(CommandHandler("start_auto", start_auto_generation))

    # Set webhook URL
    await app_bot.bot.set_webhook(WEBHOOK_URL)

    # Run the application in webhook mode
    await app_bot.run_webhook()

# Webhook route for Flask
@app.route('/webhook', methods=['POST'])
def webhook():
    print(f"Received {request.method} request")  # Logs the request method
    json_str = request.get_data(as_text=True)
    print(f"Webhook received: {json_str}")
    return "OK", 200  # Respond with a success message to Telegram

# Root route to handle requests to "/"
@app.route('/')
def home():
    return "Welcome to the bot webhook service!"

# Handle favicon.ico requests
@app.route('/favicon.ico')
def favicon():
    return '', 404

# 🔹 Event Loop Fix for Running in Async Environments 🔹
if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()  # Fix for environments like Jupyter Notebook
    
    # Run Telegram bot as a background task
    loop = asyncio.get_event_loop()
    loop.create_task(main())

    # Start the Flask app
    from gevent.pywsgi import WSGIServer
    server = WSGIServer(('0.0.0.0', 5000), app)
    server.serve_forever()
