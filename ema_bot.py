from binance.client import Client
import pandas as pd
import requests
import time

# 🔐 본인 텔레그램 정보 입력
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

client = Client()

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=data)

print("🔍 4H EMA21 > EMA50 + 가격 > EMA200 체크 시작")

exchange_info = client.futures_exchange_info()
symbols = [s['symbol'] for s in exchange_info['symbols']
           if s['quoteAsset'] == 'USDT' and s['status'] == 'TRADING']

matched = []

for symbol in symbols:
    try:
        klines = client.futures_klines(symbol=symbol, interval='4h', limit=250)

        df = pd.DataFrame(klines, columns=[
            'open_time','open','high','low','close','volume',
            'close_time','qav','num_trades','taker_base_vol',
            'taker_quote_vol','ignore'
        ])

        df['close'] = df['close'].astype(float)

        # EMA 계산
        df['ema21'] = df['close'].ewm(span=21).mean()
        df['ema50'] = df['close'].ewm(span=50).mean()
        df['ema200'] = df['close'].ewm(span=200).mean()

        curr_21 = df['ema21'].iloc[-1]
        curr_50 = df['ema50'].iloc[-1]
        curr_200 = df['ema200'].iloc[-1]
        curr_price = df['close'].iloc[-1]

        # 조건 2개
        if curr_21 > curr_50 and curr_price > curr_200:
            matched.append(symbol)

        time.sleep(0.3)

    except Exception as e:
        time.sleep(1)

if matched:
    message = "📈 4H 조건 충족 코인\n\nEMA21 > EMA50\n가격 > EMA200\n\n" + "\n".join(matched)
    send_telegram(message)
    print("텔레그램 전송 완료")
else:
    print("조건 충족 코인 없음")

input("엔터 누르면 종료됩니다...")
