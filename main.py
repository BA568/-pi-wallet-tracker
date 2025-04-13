
import os
import json
import requests
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from threading import Thread
import time

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALERT_USER = os.getenv("ALERT_USER", "@Banky664")

wallets = {}
last_balances = {}

logging.basicConfig(level=logging.INFO)

# Telegram Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [[
        InlineKeyboardButton("💸 Withdraw", callback_data="withdraw"),
        InlineKeyboardButton("📥 Add Wallet", callback_data="addwallet")
    ], [
        InlineKeyboardButton("❌ Remove Wallet", callback_data="removewallet"),
        InlineKeyboardButton("📃 List Wallets", callback_data="listwallets")
    ], [
        InlineKeyboardButton("🕘 History", callback_data="history"),
        InlineKeyboardButton("📚 Help/Manual", callback_data="manual")
    ]]
    await update.message.reply_text("🤖 Welcome to the Pi Wallet Bot", reply_markup=InlineKeyboardMarkup(buttons))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data

    if action == "withdraw":
        await query.edit_message_text("💳 Enter the amount and wallet to withdraw from.")
    elif action == "addwallet":
        await query.edit_message_text("➕ Send your wallet address using /addwallet <wallet>")
    elif action == "removewallet":
        await query.edit_message_text("❌ Send /removewallet <wallet> to stop tracking.")
    elif action == "listwallets":
        text = "📃 Tracked Wallets:
" + "\n".join(wallets.keys()) if wallets else "No wallets added yet."
        await query.edit_message_text(text)
    elif action == "history":
        text = "🕘 History Log:
" + "\n".join([f"{w}: {b} Pi" for w, b in wallets.items()]) if wallets else "No history yet."
        await query.edit_message_text(text)
    elif action == "manual":
        manual_text = "📘 *Bot Commands Manual*\n\n/start - Start bot\n/addwallet - Add wallet to monitor\n/removewallet - Remove a wallet\n/listwallets - Show tracked wallets\n/simulateairdrop - Fake test airdrop\n"
        await query.edit_message_text(manual_text, parse_mode="Markdown")

async def addwallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /addwallet WALLET_ID")
    wallet = context.args[0]
    wallets[wallet] = 0
    await update.message.reply_text(f"✅ Wallet `{wallet}` is now being tracked.", parse_mode="Markdown")

async def removewallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /removewallet WALLET_ID")
    wallet = context.args[0]
    if wallet in wallets:
        del wallets[wallet]
        await update.message.reply_text(f"🗑 Removed wallet `{wallet}`", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Wallet not found.")

async def listwallets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not wallets:
        return await update.message.reply_text("📭 No wallets tracked.")
    msg = "📋 Tracked Wallets:
"
    for w, b in wallets.items():
        msg += f"`{w}` → {b} Pi\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def simulateairdrop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not wallets:
        return await update.message.reply_text("⚠️ Add a wallet first.")
    for w in wallets:
        wallets[w] += 0.1
    await update.message.reply_text("🎭 Simulated airdrop complete. +0.1 Pi to each wallet.")

def check_balances(bot):
    while True:
        for wallet in list(wallets.keys()):
            try:
                url = f"https://blockexplorer.minepi.com/api/accounts/{wallet}"
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    new_balance = float(r.json().get("balance", 0))
                    if wallet in last_balances and new_balance > last_balances[wallet]:
                        diff = round(new_balance - last_balances[wallet], 5)
                        bot.send_message(chat_id=ALERT_USER, text=f"📬 *Airdrop Detected!*
Wallet: `{wallet}`
💸 +{diff} Pi
New Balance: `{new_balance}` Pi", parse_mode="Markdown")
                    last_balances[wallet] = new_balance
                    wallets[wallet] = new_balance
            except Exception as e:
                print(f"Error checking {wallet}: {e}")
        time.sleep(10)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot = app.bot
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("addwallet", addwallet))
    app.add_handler(CommandHandler("removewallet", removewallet))
    app.add_handler(CommandHandler("listwallets", listwallets))
    app.add_handler(CommandHandler("simulateairdrop", simulateairdrop))
    Thread(target=lambda: check_balances(bot), daemon=True).start()
    app.run_polling()

if __name__ == "__main__":
    main()
