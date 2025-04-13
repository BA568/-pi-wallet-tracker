import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUTHORIZED_USERS = ["@RITAHERNANDEZ001", "@Banky664"]

tracked_wallets = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👑 Welcome to Pi Wallet Tracker Bot!\nUse /addwallet <address> to track your Pi.")

async def add_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.username
    if f"@{user}" not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /addwallet <wallet_address>")
        return
    wallet = context.args[0]
    tracked_wallets[wallet] = 1.001  # Simulated balance
    await update.message.reply_text(f"✅ Wallet {wallet} added. Tracking...")

async def list_wallets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tracked_wallets:
        await update.message.reply_text("📭 No wallets are being tracked.")
    else:
        text = "📍 Tracked Wallets:\n"
        for w, b in tracked_wallets.items():
            text += f"{w} - {b} Pi\n"
        await update.message.reply_text(text)

async def removewallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /removewallet <wallet_address>")
        return
    wallet = context.args[0]
    if wallet in tracked_wallets:
        del tracked_wallets[wallet]
        await update.message.reply_text(f"🗑️ Wallet {wallet} removed.")
    else:
        await update.message.reply_text("Wallet not found in tracking list.")

async def manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
🛠 Bot Manual & Commands:
/start - Start the bot
/addwallet <wallet> - Add wallet to tracker
/removewallet <wallet> - Stop tracking a wallet
/listwallets - List all tracked wallets
/history - View past balance logs
"""
    await update.message.reply_text(help_text)

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📜 (Simulated) No past balance logs available for now.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addwallet", add_wallet))
    app.add_handler(CommandHandler("listwallets", list_wallets))
    app.add_handler(CommandHandler("removewallet", removewallet))
    app.add_handler(CommandHandler("manual", manual))
    app.add_handler(CommandHandler("history", history))

    print("🤖 Bot started. Listening...")
    app.run_polling()

if __name__ == "__main__":
    main()