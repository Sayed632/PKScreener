import os
import yfinance as yf
import pandas as pd
import requests

# Load your secure Telegram keys from GitHub Secrets
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# The stocks we want to scan (Top Nifty Heavyweights)
STOCKS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "BHARTIARTL.NS", "SBIN.NS", "ITC.NS", "HINDUNILVR.NS", "LT.NS"
]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

print("Fetching live market data...")
alerts = []

for ticker in STOCKS:
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="2d")
        if len(df) < 2: continue
        
        close_today = df['Close'].iloc[-1]
        close_yesterday = df['Close'].iloc[-2]
        pct_change = ((close_today - close_yesterday) / close_yesterday) * 100
        
        # Signal condition: If stock moves up or down more than 1.5%
        if abs(pct_change) >= 1.5:
            direction = "🚀 Up" if pct_change > 0 else "💥 Down"
            alerts.append(f"{direction} *{ticker.split('.')[0]}*: {pct_change:.2f}% (Price: ₹{close_today:.2f})")
    except Exception as e:
        print(f"Error scanning {ticker}: {e}")

if alerts:
    message = "📊 *LIVE NIFTY SIGNALS*\n\n" + "\n".join(alerts)
    send_telegram(message)
    print("Alert sent to Telegram!")
else:
    print("No major price movements found.")
