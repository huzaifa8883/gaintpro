import logging
import asyncio
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.ext import CallbackContext

# Set up logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage for chat IDs of users who started the bot (You can store this in a database if needed)
chat_ids = set()

# Function to generate random trade signal
async def send_signal(context):
    # Define possible trade types for 'Buy'
    buy_options = ["Big", "Small", "Single", "Double"]
    buy = random.choice(buy_options)  # Randomly select one

    # Generate the signal message
    period = str(int(asyncio.get_event_loop().time() * 1000))  # Get current timestamp in milliseconds
    message = f"⏰Trade Type: 5 Minute⏰\n\n"
    message += f"👉Period:{period}\n"
    message += f"👉Buy: {buy}\n"
    message += f"💰Bet: 1 USDT\n\n"
    message += "🔥Earn 30% interest on each bet.\n"
    message += "🔥The higher the stage, the more profit you make."

    # Send message to all chat IDs in the list
    for chat_id in chat_ids:
        await context.bot.send_message(chat_id=chat_id, text=message)

# Function to handle /start command and store the user's chat_id
async def start(update: Update, context: CallbackContext):
    user_chat_id = update.message.chat_id
    # Store the user's chat_id if not already in the list
    chat_ids.add(user_chat_id)
    await update.message.reply_text('Bot is running and will send trade signals every 5 minutes.')

# Main function to set up the bot
async def main():
    application = Application.builder().token("7930820356:AAFiicSUzpUx2E2_KCaUOzkbETqUI5hvm-I").build()  # Replace with your bot token

    # Register the start command handler
    application.add_handler(CommandHandler("start", start))

    # Set up the job to send a signal every 5 minutes (300 seconds)
    job_queue = application.job_queue
    job_queue.run_repeating(send_signal, interval=300, first=0)  # first=0 will send the first message immediately

    # Start the bot
    await application.run_polling()

# Run the bot
if __name__ == '__main__':
    asyncio.run(main())
