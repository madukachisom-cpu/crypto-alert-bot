# 🚨 Crypto Price Alert Bot

A Telegram bot that tracks cryptocurrency prices in real time and sends you an instant notification the moment a token hits your target price. Built with Python, python-telegram-bot, and the CoinGecko API.

---

## Features

- 💰 **Live price checks** — fetch the current USD price of any major token
- 🎯 **Custom price alerts** — set a target and get notified automatically
- 📋 **Alert management** — view and remove your active alerts
- 🔁 **Background polling** — checks prices every 60 seconds automatically
- ⚡ **No API key required** — uses CoinGecko's free public API

---

## Supported Tokens

BTC, ETH, SOL, BNB, DOGE, SHIB, PEPE, WIF, BONK, FLOKI, XRP, ADA, AVAX, LINK, TRX, TON, MATIC, DOT, UNI, LTC — and any other token listed on CoinGecko.

---

## Commands

| Command | Description |
|---|---|
| `/start` | Show help and available commands |
| `/price BTC` | Get current price of a token |
| `/alert BTC 50000` | Alert when BTC reaches $50,000 |
| `/alerts` | View your active alerts |
| `/remove BTC` | Delete an alert |

---

## Tech Stack

- **Python 3.11+**
- **python-telegram-bot v20** (async)
- **aiohttp** — async HTTP for CoinGecko API calls
- **CoinGecko API** — free, no key required
- **python-dotenv** — environment variable management

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/madukachisom-cpu/crypto-alert-bot.git
cd crypto-alert-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a Telegram bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow the prompts
3. Copy the token BotFather gives you

### 4. Configure environment

```bash
cp .env.example .env
```

Open `.env` and paste your token:

```
TELEGRAM_BOT_TOKEN=your_token_here
```

### 5. Run the bot

```bash
python bot.py
```

---

## How It Works

1. User sets an alert with `/alert SOL 200`
2. Bot fetches the current price and determines if the target is above or below it
3. A background job runs every 60 seconds, checking all active alerts
4. When a token hits its target price, the bot sends an instant Telegram notification and removes the alert

---

## Author

Built by **Maduka Treasure** — Web3 developer and digital entrepreneur.

- Blog: [cashsuccess.online](https://cashsuccess.online)
- GitHub: [@madukachisom-cpu](https://github.com/madukachisom-cpu)

---

## License

MIT