# import os
# import logging
# from dotenv import load_dotenv
# from telegram import Update
# from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
# from agent_module import run_gmail_agent

# # ఎన్విరాన్‌మెంట్ వేరియబుల్స్ లోడ్ చేయడం
# load_dotenv()
# TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# # ALLOWED_USER_ID ని రీడ్ చేసి Integer కింద మారుస్తున్నాం
# try:
#     ALLOWED_USER_ID = int(os.getenv("ALLOWED_TELEGRAM_USER_ID", "0"))
# except ValueError:
#     ALLOWED_USER_ID = 0

# # లాగింగ్ సెటప్
# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
# )

# # 1. /start కమాండ్ హ్యాండ్లర్ (సెక్యూరిటీ చెక్ తో)
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if not update.effective_user or not update.effective_message:
#         return

#     user_id = update.effective_user.id
    
#     # ఒకవేళ మెసేజ్ పంపిన యూజర్ ఐడీ మన అనుమతించబడిన ఐడీ కాకపోతే:
#     if user_id != ALLOWED_USER_ID:
#         print(f"[SECURITY WARNING] Unauthorized access attempt by User ID: {user_id}")
#         await update.effective_message.reply_text("Sorry!, you don't have access to this bot 🚫")
#         return

#     await update.effective_message.reply_text(
#         "Hello! I am your career assistant. 🌟\n\n"
#         "Send me the HR email ID and job details. "
#         "I will create a professional application email draft in your Gmail!"
#     )

# # 2. యూజర్ పంపే మెసేజ్ హ్యాండ్లర్ (సెక్యూరిటీ చెక్ తో)
# async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if not update.effective_user or not update.effective_message:
#         return

#     user_id = update.effective_user.id
    
#     # ఇక్కడ కూడా యూజర్ ఐడీని వెరిఫై చేస్తున్నాం
#     if user_id != ALLOWED_USER_ID:
#         print(f"[SECURITY WARNING] Unauthorized message from User ID: {user_id}")
#         await update.effective_message.reply_text("Sorry!, you don't have access to this bot 🚫")
#         return

#     user_text = update.effective_message.text
#     if not user_text:
#         return

#     await update.effective_message.reply_text("Please wait while I draft your email... ⏳")
    
#     try:
#         agent_reply = run_gmail_agent(user_text)
#         await update.effective_message.reply_text(agent_reply)
#         await update.effective_message.reply_text("Successfully drafted! Please check your Gmail 'Drafts' folder. 📧")
        
#     except Exception as e:
#         await update.effective_message.reply_text(f"Sorry!, something went wrong: {str(e)}")

# # 3. బోట్ స్టార్ట్ చేసే మెయిన్ ఫంక్షన్
# def main():
#     if not TOKEN:
#         print("[ERROR] Haven't got TELEGRAM_BOT_TOKEN in .env file!")
#         return
#     if ALLOWED_USER_ID == 0:
#         print("[WARNING] ALLOWED_TELEGRAM_USER_ID is not set correctly! The bot will not respond to anyone.")
        
#     print(f"[INFO] Telegram bot is starting only for User ID: {ALLOWED_USER_ID}...")
#     app = Application.builder().token(TOKEN).build()

#     app.add_handler(CommandHandler("start", start))
#     app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

#     app.run_polling()

# if __name__ == "__main__":
#     main()





import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from agent_module import run_gmail_agent

# ఎన్విరాన్‌మెంట్ వేరియబుల్స్ లోడ్ చేయడం
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

try:
    ALLOWED_USER_ID = int(os.getenv("ALLOWED_TELEGRAM_USER_ID", "0"))
except ValueError:
    ALLOWED_USER_ID = 0

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# 1. /start కమాండ్ హ్యాండ్లర్
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.effective_message:
        return

    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        await update.effective_message.reply_text("క్షమించండి, మీకు ఈ బోట్‌ను ఉపయోగించే అనుమతి లేదు! 🚫")
        return

    await update.effective_message.reply_text(
        "హలో! నేను మీ పర్సనల్ AI అసిస్టెంట్ ని. 🌟\n\n"
        "నాకు HR ఈమెయిల్ ఐడి మరియు జాబ్ వివరాలు పంపండి. "
        "నేను మీ కోసం Gmail లో ఒక చక్కటి అప్లికేషన్ ఈమెయిల్ డ్రాఫ్ట్ క్రియేట్ చేస్తాను!"
    )

# 2. యూజర్ పంపే మెసేజ్ హ్యాండ్లర్
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not update.effective_message:
        return

    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        await update.effective_message.reply_text("క్షమించండి, మీకు ఈ బోట్‌ను ఉపయోగించే అనుమతి లేదు! 🚫")
        return

    user_text = update.effective_message.text
    if not user_text:
        return

    # హార్డ్ కోడెడ్ మెసేజ్ కి బదులుగా ఒక తాత్కాలిక "ఆలోచిస్తున్నాను..." మెసేజ్ ని పంపుతున్నాం
    status_message = await update.effective_message.reply_text("ఆలోచిస్తున్నాను... ⏳")
    
    try:
        # ఏజెంట్ కి యూజర్ ఐడీ మరియు మెసేజ్ ని పంపుతున్నాం
        agent_reply = run_gmail_agent(user_id, user_text)
        
        # ఆలోచిస్తున్నాను మెసేజ్ ని డిలీట్ చేసి కరెక్ట్ రిప్లై ని పోస్ట్ చేస్తున్నాం
        await status_message.delete()
        await update.effective_message.reply_text(agent_reply)
        
    except Exception as e:
        # ఏదైనా ఎర్రర్ వస్తే స్టేటస్ మెసేజ్ ని ఎర్రర్ టెక్స్ట్ గా మారుస్తాం
        await status_message.edit_text(f"అయ్యో! ఏదో పొరపాటు జరిగింది: {str(e)}")

# 3. బోట్ స్టార్ట్ చేసే మెయిన్ ఫంక్షన్
def main():
    if not TOKEN:
        print("[ERROR] .env ఫైల్ లో TELEGRAM_BOT_TOKEN లభించలేదు!")
        return
    if ALLOWED_USER_ID == 0:
        print("[WARNING] ALLOWED_TELEGRAM_USER_ID కరెక్ట్ గా సెట్ చేయబడలేదు!")
        
    print(f"[INFO] టెలిగ్రామ్ బోట్ User ID: {ALLOWED_USER_ID} కోసం స్టార్ట్ అవుతోంది...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()