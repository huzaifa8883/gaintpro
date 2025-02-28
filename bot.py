from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import random

# Yahan apna Telegram bot ka token daalo
TOKEN = "7974068784:AAFs-RpxmHrca2OawNHucMxeGhk5jGBXR4A"

# Random ad type generate karne ka function
def generate_random_ad():
    ad_types = ["Single", "Double"]
    is_big = random.random() > 0.5
    main_ad = "Big" if is_big else "Small"
    random_ad_type = random.choice(ad_types)
    return f"{main_ad} {random_ad_type}"

# /start command ka response
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Welcome! Send /generate to get a random ad type.")

# /generate command ka response
async def generate(update: Update, context: CallbackContext):
    ad = generate_random_ad()
    await update.message.reply_text(f"Generated: {ad}")

# Bot setup aur start karne ka function
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("generate", generate))

    print("🤖 Bot is running...")
    app.run_polling()

# Run the bot
if __name__ == "__main__":
    main()
