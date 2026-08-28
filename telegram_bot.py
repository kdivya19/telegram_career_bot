import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from agent_module import run_gmail_agent

# loading env variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

try:
    ALLOWED_USER_ID = int(os.getenv("ALLOWED_TELEGRAM_USER_ID", "0"))
except ValueError:
    ALLOWED_USER_ID = 0

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# 1. /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.effective_message:
        return

    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        await update.effective_message.reply_text("Sorry! You don't have access to this bot! 🚫")
        return

    await update.effective_message.reply_text(
        "Hello! I am your personal AI assistant.🌟\n\n"
        "Send me the HR email ID and job details. "
        "I will create a neat application email draft for you in Gmail!"
    )

# 2. User message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.effective_message:
        return

    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        await update.effective_message.reply_text("Sorry! You don't have access to this bot! 🚫")
        return

    user_text = update.effective_message.text
    if not user_text:
        return

    # Instead of a hard‑coded message, I’m sending a temporary ‘Drafting…’ message.
    status_message = await update.effective_message.reply_text("Drafting... ⏳")
    
    try:
        # I am sending the user ID and the message to the agent.
        agent_reply = run_gmail_agent(user_id, user_text)
        
        # Deleting the ‘Drafting…’ message and posting the correct reply.
        await status_message.delete()
        await update.effective_message.reply_text(agent_reply)
        
    except Exception as e:
        # If any error occurs, I will change the status message to the error text.
        await status_message.edit_text(f"Ohh! Something went wrong!: {str(e)}")

# 3. Main function that starts the bot.
def main():
    if not TOKEN:
        print("[ERROR] TELEGRAM_BOT_TOKEN not found in the .env file!")
        return
    if ALLOWED_USER_ID == 0:
        print("[WARNING] ALLOWED_TELEGRAM_USER_ID is set correctly!")
        
    print(f"[INFO] Telegram bot User ID: {ALLOWED_USER_ID} starting for...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
