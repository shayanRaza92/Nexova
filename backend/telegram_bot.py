import logging
import os
import sys
import asyncio
from dotenv import load_dotenv

# Add project root to sys.path to allow imports from backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from backend.chat_engine import chat_engine

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command"""
    await update.message.reply_text(
        "Hello! I am the Nexova AI Agent. Ask me anything about our services!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages"""
    user_text = update.message.text
    user_id = update.effective_user.id
    
    print(f"Received from {user_id}: {user_text}")

    # Get response from AI
    try:
        response_data = await chat_engine.get_response(user_text)
        
        # Extract the reply text 
        reply_text = response_data.get("reply", "Sorry, I didn't understand.")
        
        # Check if it was an order (Log it for now)
        if response_data.get("type") == "order":
            print(f"ORDER RECEIVED: {response_data.get('order_details')}")
            # Here you could save to database/sheets
            
        await update.message.reply_text(reply_text)
    except Exception as e:
        print(f"Error generating response: {e}")
        await update.message.reply_text("I'm having a little trouble thinking right now. Please try again.")

if __name__ == '__main__':
    token = os.getenv("TELEGRAM_TOKEN")
    
    if not token:
        print("ERROR: TELEGRAM_TOKEN is missing in .env")
        sys.exit(1)

    print("Starting Telegram Bot...")
    
    # Build the Application
    application = ApplicationBuilder().token(token).build()

    # Add Handlers
    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)

    application.add_handler(start_handler)
    application.add_handler(message_handler)

    # Run the bot (Polling mode)
    application.run_polling()
