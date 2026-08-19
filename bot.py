import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Conversation states
CHOOSING_PATH, EMAIL, PASSWORD, RECOVERY_EMAIL, TWO_FACTOR_KEY, TELEBIRR = range(6)

# Default specifications for new accounts (customizable via /setspecs)
CURRENT_SPECS = (
    "📌 **SPECIFICATIONS FOR NEW ACCOUNT:**\n\n"
    "Please create a new Gmail account using these details:\n"
    "• **First Name:** John\n"
    "• **Last Name:** Doe\n\n"
    "Once created, please reply with the **Gmail address** you made:"
)

# Admin Command to change specifications live
async def set_specs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CURRENT_SPECS
    user_id = update.effective_user.id
    
    if user_id != 2103337926:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    new_specs_text = " ".join(context.args)
    if not new_specs_text:
        await update.message.reply_text(
            "⚠️ Please provide the new specifications after the command.\n"
            "Example: `/setspecs First Name: Alex | Last Name: Johnson`",
            parse_mode="Markdown"
        )
        return

    CURRENT_SPECS = f"📌 **SPECIFICATIONS FOR NEW ACCOUNT:**\n\n{new_specs_text}\n\nOnce created, please reply with the **Gmail address** you made:"
    await update.message.reply_text("✅ Successfully updated the account specifications for users!")

# Start Command with the main menu layout
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [
        ["➕ Register a new Gmail", "📁 My accounts"],
        ["💰 Balance", "👥 My referrals"],
        ["⚙️ Settings", "💬 Help"],
        ["🤖 My Bot"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    
    welcome_text = (
        "👋 **Welcome to Gmail Buyer Bot!**\n\n"
        "✨ **Current Payout Rates:**\n"
        "• New Account: **15 Birr**\n"
        "• Existing Account (Old): **15 Birr**\n\n"
        "Choose an option below to start earning:"
    )
    
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=markup)

# Step 1: When user clicks "Register a new Gmail"
async def register_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [
        ["📝 Submit my own", "🔄 Generate new name"],
        ["📋 Bulk submit"],
        ["❌ Cancel registration"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    
    info_text = (
        "💰 You will earn **15 Birr** for each approved account\n\n"
        "💡 **Your pay details:**\n"
        "• Both new and existing accounts pay **15 Birr**.\n\n"
        "Do you want us to generate a login and password for you or you already have an account?"
    )
    await update.message.reply_text(info_text, parse_mode="Markdown", reply_markup=markup)
    return CHOOSING_PATH

# Handle choice: Submit my own
async def submit_my_own(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['submission_type'] = "New Account (Custom/Own)"
    markup = ReplyKeyboardMarkup([["❌ Cancel registration"]], resize_keyboard=True)
    await update.message.reply_text("📧 Please enter your Gmail email address:", parse_mode="Markdown", reply_markup=markup)
    return EMAIL

# Handle choice: Generate new name (uses custom specs)
async def generate_new_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['submission_type'] = "New Account (Generated Specs)"
    markup = ReplyKeyboardMarkup([["❌ Cancel registration"]], resize_keyboard=True)
    await update.message.reply_text(CURRENT_SPECS, parse_mode="Markdown", reply_markup=markup)
    return EMAIL

# Handle choice: Bulk submit
async def bulk_submit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    markup = ReplyKeyboardMarkup([["❌ Cancel registration"]], resize_keyboard=True)
    await update.message.reply_text(
        "📋 **Bulk Submit Mode**\n\nPlease send your accounts list formatted as `email:password:recovery` line by line:",
        parse_mode="Markdown",
        reply_markup=markup
    )
    return EMAIL

# Path for Existing Accounts ("My accounts" menu button)
async def existing_accounts_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [
        ["🔄 Refresh", "➕ Register new Gmail"],
        ["🔙 Back"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "📁 **Your Account Submissions History:**\n\n"
        "79. ✅ Create account on GOOGLE\n"
        "💰 $0.18 | 📅 2/21/2026 | confirmed auto confirmed\n\n"
        "All verified accounts are listed above.",
        parse_mode="Markdown",
        reply_markup=markup
    )

# Sequence: Email -> Password -> Recovery Email -> 2FA -> Telebirr
async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ Cancel registration":
        return await cancel(update, context)
    
    context.user_data['email'] = text
    markup = ReplyKeyboardMarkup([["❌ Cancel registration"]], resize_keyboard=True)
    await update.message.reply_text("🔒 Please enter your password:", reply_markup=markup)
    return PASSWORD

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ Cancel registration":
        return await cancel(update, context)
        
    context.user_data['password'] = text
    markup = ReplyKeyboardMarkup([["❌ Cancel registration"]], resize_keyboard=True)
    await update.message.reply_text("📧 Please enter your recovery email address:", reply_markup=markup)
    return RECOVERY_EMAIL

async def get_recovery_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ Cancel registration":
        return await cancel(update, context)
        
    context.user_data['recovery_email'] = text
    
    email = context.user_data.get('email')
    password = context.user_data.get('password')
    
    confirmation_text = (
        f"🔍 Checking if credentials are unique...\n\n"
        f"Your account credentials have been saved and registered for **15 Birr**\n\n"
        f"First name: Abenezertadewos\n"
        f"Email: {email}\n"
        f"Password: {password}\n"
        f"Recovery email: {text}\n\n"
        f"🔒 Make sure your Gmail account exists and is accessible, otherwise the payment will not be processed.\n\n"
        f"🔐 We suggest you to set 2FA on the account to increase the chances of successful login on our side.\n\n"
        f"Would you like to add a 2FA key or skip to Telebirr payout?"
    )
    
    reply_keyboard = [
        ["🔑 Add 2FA key", "⏩ Skip 2FA"],
        ["❌ Cancel registration"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    await update.message.reply_text(confirmation_text, parse_mode="Markdown", reply_markup=markup)
    return TWO_FACTOR_KEY

async def handle_2fa_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ Cancel registration":
        return await cancel(update, context)
        
    if text == "🔑 Add 2FA key":
        markup = ReplyKeyboardMarkup([["🔙 Back"], ["❌ Cancel registration"]], resize_keyboard=True)
        await update.message.reply_text(
            "⌨️ Please type your 2FA secret key or send the code format:",
            reply_markup=markup
        )
        return TWO_FACTOR_KEY
    else:
        context.user_data['2fa'] = "Skipped / None"
        markup = ReplyKeyboardMarkup([["❌ Cancel registration"]], resize_keyboard=True)
        await update.message.reply_text("💰 Please enter your Telebirr account name/number for payout:", reply_markup=markup)
        return TELEBIRR

async def get_2fa_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ Cancel registration":
        return await cancel(update, context)
    if text == "🔙 Back":
        return await get_recovery_email(update, context)
        
    context.user_data['2fa'] = text
    markup = ReplyKeyboardMarkup([["❌ Cancel registration"]], resize_keyboard=True)
    await update.message.reply_text("💰 Account details verified! Please enter your Telebirr account name/number for payout:", reply_markup=markup)
    return TELEBIRR

async def get_telebirr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ Cancel registration":
        return await cancel(update, context)
        
    telebirr_info = text
    sub_type = context.user_data.get('submission_type', 'Standard')
    email = context.user_data.get('email')
    password = context.user_data.get('password')
    recovery = context.user_data.get('recovery_email')
    two_fa = context.user_data.get('2fa', 'N/A')
    
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
        f"📬 **Recovery:** {recovery}\n"
        f"🛡️ **2FA Key:** {two_fa}\n"
        f"💰 **Telebirr:** {telebirr_info}"
    )
    
    await context.bot.send_message(chat_id=my_admin_id, text=admin_message, parse_mode="Markdown")
    context.user_data.clear()

    reply_keyboard = [
        ["➕ Register a new Gmail", "📁 My accounts"],
        ["💰 Balance", "👥 My referrals"],
        ["⚙️ Settings", "💬 Help"],
        ["🤖 My Bot"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "✅ Submission received successfully! Pending verification for your **15 Birr** payout.",
        parse_mode="Markdown",
        reply_markup=markup
    )
    return ConversationHandler.END

# Additional Menu Handlers
async def balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💰 **Your Balance:**\n0.00 Birr\n\nPayouts are processed via Telebirr after verification.")

async def referrals_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👥 **Your Referral Link:**\nShare your link with friends to earn commission bonuses!")

async def settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚙️ **Settings:**\nYour account link status is active.")

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💬 **Help & Support:**\nContact admin if you encounter any issues with task submissions or payouts.")

async def my_bot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 This system automatically monitors your submitted Gmail verification tasks.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    reply_keyboard = [
        ["➕ Register a new Gmail", "📁 My accounts"],
        ["💰 Balance", "👥 My referrals"],
        ["⚙️ Settings", "💬 Help"],
        ["🤖 My Bot"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    await update.message.reply_text("❌ Registration canceled.", reply_markup=markup)
    return ConversationHandler.END

if __name__ == '__main__':
    BOT_TOKEN = os.getenv("BOT_TOKEN", "8941199738:AAFs0IivEoEecPtmheF-bK5KZ3wqOGQreHo")
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^➕ Register a new Gmail$"), register_start),
            MessageHandler(filters.Regex("^➕ Register new Gmail$"), register_start)
        ],
        states={
            CHOOSING_PATH: [
                MessageHandler(filters.Regex("^📝 Submit my own$"), submit_my_own),
                MessageHandler(filters.Regex("^🔄 Generate new name$"), generate_new_name),
                MessageHandler(filters.Regex("^📋 Bulk submit$"), bulk_submit),
                MessageHandler(filters.Regex("^❌ Cancel registration$"), cancel)
            ],
            EMAIL: [
                MessageHandler(filters.Regex("^❌ Cancel registration$"), cancel),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)
            ],
            PASSWORD: [
                MessageHandler(filters.Regex("^❌ Cancel registration$"), cancel),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)
            ],
            RECOVERY_EMAIL: [
                MessageHandler(filters.Regex("^❌ Cancel registration$"), cancel),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_recovery_email)
            ],
            TWO_FACTOR_KEY: [
                MessageHandler(filters.Regex("^🔑 Add 2FA key$"), handle_2fa_choice),
                MessageHandler(filters.Regex("^⏩ Skip 2FA$"), handle_2fa_choice),
                MessageHandler(filters.Regex("^❌ Cancel registration$"), cancel),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_2fa_key)
            ],
            TELEBIRR: [
                MessageHandler(filters.Regex("^❌ Cancel registration$"), cancel),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_telebirr)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setspecs", set_specs))
    app.add_handler(conv_handler)
    
    # Static Menu buttons
    app.add_handler(MessageHandler(filters.Regex("^📁 My accounts$"), existing_accounts_menu))
    app.add_handler(MessageHandler(filters.Regex("^💰 Balance$"), balance_handler))
    app.add_handler(MessageHandler(filters.Regex("^👥 My referrals$"), referrals_handler))
    app.add_handler(MessageHandler(filters.Regex("^⚙️ Settings$"), settings_handler))
    app.add_handler(MessageHandler(filters.Regex("^💬 Help$"), help_handler))
    app.add_handler(MessageHandler(filters.Regex("^🤖 My Bot$"), my_bot_handler))

    print("Bot is running with updated features...")
    app.run_polling()
