from flask import Flask, request
import asyncio
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

TOKEN = "7930820356:AAFiicSUzpUx2E2_KCaUOzkbETqUI5hvm-I"
WEBHOOK_URL = "https://gaintpro-production.up.railway.app/webhook"

app = Flask(__name__)

# Function to generate a random ad
def generate_random_ad():
    ad_types = ["Single", "Double", "Small", "Big"]
    random_ad_type = random.choice(ad_types)
    bet_amount = random.choice([1, 3, 5, 10, 27])
    period = random.randint(1520250301100, 1520250301200)
    return f"""⏰Trade Type: 5 Minute⏰

👉Period: {period}
👉Buy: {random_ad_type}
💰Bet: {bet_amount} USDT

🔥Earn 30% interest on each bet.
🔥The higher the stage, the more profit you make."""

# Function to send auto-generated signals
async def auto_generate(context: CallbackContext):
    try:
        chat_id = context.job.chat_id
        ad = generate_random_ad()
        print(f"Sending signal to {chat_id}: {ad}")
        await context.bot.send_message(chat_id=chat_id, text=ad)
    except Exception as e:
        print(f"Error in auto_generate: {e}")
        await context.bot.send_message(chat_id=context.job.chat_id, text="Error generating trade signal.")

# Telegram bot main function
async def main():
    app_bot = Application.builder().token(TOKEN).build()

    # Command to start auto signal generation
    async def start_auto_generation(update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        job_queue = context.application.job_queue
        job = job_queue.get_jobs_by_name(str(chat_id))
        if not job:
            print(f"Starting auto generation for chat_id: {chat_id}")
            job_queue.run_repeating(auto_generate, interval=300, first=0, chat_id=chat_id, name=str(chat_id))
            await update.message.reply_text("Auto signal generation started. You will receive a signal every 5 minutes.")
        else:
            await update.message.reply_text("Auto signal generation is already running!")

    app_bot.add_handler(CommandHandler("start_auto", start_auto_generation))
    await app_bot.bot.set_webhook(WEBHOOK_URL)
    await app_bot.run_webhook()

# Flask webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    print(f"Webhook received: {json_str}")
    return "OK", 200  # Success response to Telegram

# Home route
@app.route('/')
def home():
    return "Welcome to the bot webhook service!"

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()

    loop = asyncio.get_event_loop()
    loop.create_task(main())

    from gevent.pywsgi import WSGIServer
    server = WSGIServer(('0.0.0.0', 5000), app)
    server.serve_forever()
