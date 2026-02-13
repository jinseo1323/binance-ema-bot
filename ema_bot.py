import os
import requests
import pandas as pd

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

BASE_URL = "https://api.binance.com/api/v3/klines"

def get_klines(symbol):
    params = {
        "symbol": symbol,
        "interval": "4h",
        "limit": 250
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    df = pd.DataFrame(data)
    df = df.iloc[:, 0:6]
    df.columns = ["time", "open", "high", "low", "close", "volume"]
    df["close"] = df["close"].astype(float)
    return df

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)

symbols = ["BTCUSDT","ETHUSDT","SOLUSDT","XRPUSDT"]

result = []

for symbol in symbols:
    try:
        df = get_klines(symbol)

        df["ema21"] = df["close"].ewm(span=21).mean()
        df["ema50"] = df["close"].ewm(span=50).mean()
        df["ema200"] = df["close"].ewm(span=200).mean()

        last = df.iloc[-1]

        if last["ema21"] > last["ema50"] and last["close"] > last["ema200"]:
            result.append(symbol)

    except:
        pass

if result:
    message = "조건 충족 코인:\n" + "\n".join(result)
    send_telegram(message)
else:
    print("조건 충족 코인 없음")

