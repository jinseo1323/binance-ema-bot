import os
import requests
import pandas as pd

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

BASE_KLINE_URL = "https://api.binance.com/api/v3/klines"
BASE_INFO_URL = "https://api.binance.com/api/v3/exchangeInfo"


def get_all_usdt_symbols():
    data = requests.get(BASE_INFO_URL).json()
    symbols = []

    for s in data["symbols"]:
        if s["quoteAsset"] == "USDT" and s["status"] == "TRADING":
            symbols.append(s["symbol"])

    return symbols


def get_klines(symbol):
    params = {
        "symbol": symbol,
        "interval": "4h",
        "limit": 250
    }

    response = requests.get(BASE_KLINE_URL, params=params)
    data = response.json()

    if isinstance(data, dict):
        return None

    df = pd.DataFrame(data)
    df = df.iloc[:, 0:6]
    df.columns = ["time", "open", "high", "low", "close", "volume"]
    df["close"] = df["close"].astype(float)

    return df


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=payload)


def main():
    symbols = get_all_usdt_symbols()
    result = []

    for symbol in symbols:
        try:
            df = get_klines(symbol)
            if df is None or len(df) < 200:
