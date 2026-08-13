#!/usr/bin/env python3
"""
Crypto Price Alert Bot
Monitors token prices via CoinGecko and fires Telegram alerts when targets are hit.
Author: Maduka Treasure
"""

import os
import logging
import aiohttp
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# In-memory store: {user_id: {symbol: {target, direction, chat_id}}}
alerts: dict = {}

# Ticker symbol → CoinGecko coin ID
COIN_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "BNB": "binancecoin",
    "SOL": "solana",
    "DOGE": "dogecoin",
    "SHIB": "shiba-inu",
    "PEPE": "pepe",
    "WIF": "dogwifhat",
    "BONK": "bonk",
    "FLOKI": "floki",
    "XRP": "ripple",
    "ADA": "cardano",
    "AVAX": "avalanche-2",
    "LINK": "chainlink",
    "TRX": "tron",
    "TON": "the-open-network",
    "MATIC": "matic-network",
    "DOT": "polkadot",
    "UNI": "uniswap",
    "LTC": "litecoin",
}


async def fetch_price(symbol: str) -> float | None:
    """Fetch current USD price from CoinGecko (free tier, no API key needed)."""
    coin_id = COIN_MAP.get(symbol.upper(), symbol.lower())
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get(coin_id, {}).get("usd")
    except Exception as e:
        logger.error(f"Price fetch error for {symbol}: {e}")
    return None


# ── Commands ──────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 *Crypto Price Alert Bot*\n\n"
        "Track any token and get notified the moment it hits your target price.\n\n"
        "*Commands:*\n"
        "• `/price BTC` — get current price\n"
        "• `/alert BTC 50000` — alert when BTC hits $50,000\n"
        "• `/alerts` — view your active alerts\n"
        "• `/remove BTC` — delete an alert\n\n"
        "Supports: BTC, ETH, SOL, DOGE, SHIB, PEPE, WIF, BONK, FLOKI, XRP, ADA, and more.",
        parse_mode="Markdown"
    )


async def cmd_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/price BTC`", parse_mode="Markdown")
        return

    symbol = context.args[0].upper()
    await update.message.reply_text(f"⏳ Fetching price for *{symbol}*...", parse_mode="Markdown")

    price = await fetch_price(symbol)

    if price is None:
        await update.message.reply_text(
            f"❌ Couldn't find *{symbol}*. Check the ticker symbol and try again.",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            f"💰 *{symbol}* — `${price:,.6f}`",
            parse_mode="Markdown"
        )


async def cmd_alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: `/alert BTC 50000`", parse_mode="Markdown")
        return

    symbol = context.args[0].upper()

    try:
        target = float(context.args[1].replace(",", ""))
    except ValueError:
        await update.message.reply_text("❌ Invalid price. Example: `/alert SOL 200`", parse_mode="Markdown")
        return

    current = await fetch_price(symbol)
    if current is None:
        await update.message.reply_text(f"❌ Couldn't find *{symbol}*.", parse_mode="Markdown")
        return

    direction = "above" if target > current else "below"
    user_id = update.effective_user.id

    alerts.setdefault(user_id, {})[symbol] = {
        "target": target,
        "direction": direction,
        "chat_id": update.effective_chat.id,
    }

    emoji = "📈" if direction == "above" else "📉"
    await update.message.reply_text(
        f"✅ *Alert set!*\n\n"
        f"{emoji} *{symbol}* → notify when {direction} `${target:,.4f}`\n"
        f"Current price: `${current:,.6f}`",
        parse_mode="Markdown"
    )


async def cmd_list_alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_alerts = alerts.get(user_id, {})

    if not user_alerts:
        await update.message.reply_text(
            "You have no active alerts.\nSet one with `/alert BTC 50000`",
            parse_mode="Markdown"
        )
        return

    lines = ["📋 *Your Active Alerts:*\n"]
    for symbol, data in user_alerts.items():
        emoji = "📈" if data["direction"] == "above" else "📉"
        lines.append(f"{emoji} *{symbol}*: `${data['target']:,.4f}` ({data['direction']})")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def cmd_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/remove BTC`", parse_mode="Markdown")
        return

    symbol = context.args[0].upper()
    user_id = update.effective_user.id

    if user_id in alerts and symbol in alerts[user_id]:
        del alerts[user_id][symbol]
        await update.message.reply_text(f"✅ Removed alert for *{symbol}*", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"No active alert found for *{symbol}*", parse_mode="Markdown")


# ── Background job ─────────────────────────────────────────────────────────────

async def check_alerts_job(context: ContextTypes.DEFAULT_TYPE):
    """Runs every 60 seconds — checks all alerts and fires notifications."""
    triggered = []

    for user_id, user_alerts in list(alerts.items()):
        for symbol, data in list(user_alerts.items()):
            current = await fetch_price(symbol)
            if current is None:
                continue

            hit = (
                (data["direction"] == "above" and current >= data["target"]) or
                (data["direction"] == "below" and current <= data["target"])
            )

            if hit:
                emoji = "🚀" if data["direction"] == "above" else "🔻"
                await context.bot.send_message(
                    chat_id=data["chat_id"],
                    text=(
                        f"🚨 *ALERT TRIGGERED!*\n\n"
                        f"{emoji} *{symbol}* hit your target!\n"
                        f"Current price: `${current:,.6f}`\n"
                        f"Your target: `${data['target']:,.4f}`"
                    ),
                    parse_mode="Markdown"
                )
                triggered.append((user_id, symbol))

    # Remove triggered alerts
    for user_id, symbol in triggered:
        if user_id in alerts:
            alerts[user_id].pop(symbol, None)


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set. Check your .env file.")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("price", cmd_price))
    app.add_handler(CommandHandler("alert", cmd_alert))
    app.add_handler(CommandHandler("alerts", cmd_list_alerts))
    app.add_handler(CommandHandler("remove", cmd_remove))

    # Check all price alerts every 60 seconds
    app.job_queue.run_repeating(check_alerts_job, interval=60, first=15)

    logger.info("✅ Bot is running and polling for updates...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()