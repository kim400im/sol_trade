import os
import requests
import hmac
import hashlib
import base64
import json
from dotenv import load_dotenv
import time

load_dotenv()


def get_bitget_chart(symbol="SOLUSDT", granularity="3m", limit=50, product_type="usdt-futures"):
    print('[Function] 차트 데이터 요청중 -> '+granularity+' candles')
    url = "https://api.bitget.com/api/v2/mix/market/candles"
    params = {
        "symbol": symbol,
        "granularity": granularity,
        "limit": limit,
        "productType": product_type
    }
    res = requests.get(url, params=params)
    return res.json().get('data', [])


def get_bitget_position():
    print('[Function] 내 포지션 긁어오기 실행')
    access_key = os.getenv("BG_ACCESS_KEY")
    secret_key = os.getenv("BG_SECRET_KEY")
    passphrase = os.getenv("BG_PASSPHARASE")

    server_time_res = requests.get("https://api.bitget.com/api/v2/public/time")
    timestamp = server_time_res.json()['data']['serverTime']

    method = "GET"
    path = "/api/v2/mix/position/single-position"
    query = "symbol=solusdt&productType=USDT-FUTURES&marginCoin=USDT"
    url = f"https://api.bitget.com{path}?{query}"

    sign_data = timestamp + method + path + "?" + query
    signature = hmac.new(secret_key.encode(),
                         sign_data.encode(), hashlib.sha256).digest()
    access_sign = base64.b64encode(signature).decode()

    headers = {
        "ACCESS-KEY": access_key,
        "ACCESS-SIGN": access_sign,
        "ACCESS-PASSPHRASE": passphrase,
        "ACCESS-TIMESTAMP": timestamp,
        "locale": "en-US",
        "Content-Type": "application/json"
    }

    res = requests.get(url, headers=headers)
    return res.json()


def close_all_positions(symbol="SOLUSDT", product_type="USDT-FUTURES"):
    print("[Function] 포지션 전부 청산 시도중...")

    access_key = os.getenv("BG_ACCESS_KEY")
    secret_key = os.getenv("BG_SECRET_KEY")
    passphrase = os.getenv("BG_PASSPHARASE")

    # 서버 시간
    server_time_res = requests.get("https://api.bitget.com/api/v2/public/time")
    timestamp = str(server_time_res.json().get('data', {}).get('serverTime'))

    method = "POST"
    path = "/api/v2/mix/order/close-positions"
    url = "https://api.bitget.com" + path

    body_dict = {
        "symbol": symbol,
        "productType": product_type
        # hedge-mode에서 long/short 따로 닫으려면 "holdSide": "long" 또는 "short"
    }
    body = json.dumps(body_dict)

    # 서명
    sign_data = timestamp + method + path + body
    signature = hmac.new(secret_key.encode('utf-8'),
                         sign_data.encode('utf-8'), hashlib.sha256).digest()
    access_sign = base64.b64encode(signature).decode()

    headers = {
        "ACCESS-KEY": access_key,
        "ACCESS-SIGN": access_sign,
        "ACCESS-PASSPHRASE": passphrase,
        "ACCESS-TIMESTAMP": timestamp,
        "locale": "en-US",
        "Content-Type": "application/json"
    }

    # 요청 전송
    res = requests.post(url, headers=headers, data=body)
    result = res.json()

    print("[Bitget] 포지션 종료 응답:", result)
    return result


def place_bitget_order(symbol="SOLUSDT", side="buy", size="0.01", price="200", order_type="limit"):
    print("[Action] PLACING ORDER")
    access_key = os.getenv("BG_ACCESS_KEY")
    secret_key = os.getenv("BG_SECRET_KEY")
    passphrase = os.getenv("BG_PASSPHARASE")

    server_time_res = requests.get("https://api.bitget.com/api/v2/public/time")
    timestamp = str(server_time_res.json()['data']['serverTime'])

    method = "POST"
    path = "/api/v2/mix/order/place-order"
    url = "https://api.bitget.com" + path

    body_dict = {
        "symbol": symbol,
        "marginCoin": "USDT",
        "side": side,
        "orderType": order_type,
        "size": size,
        "price": price,
        "timeInForceValue": "normal",
        "productType": "USDT-FUTURES",
        "marginMode": "isolated",
        "tradeSide": "open"
    }
    body = json.dumps(body_dict)

    sign_data = timestamp + method + path + body
    signature = hmac.new(secret_key.encode(),
                         sign_data.encode(), hashlib.sha256).digest()
    access_sign = base64.b64encode(signature).decode()

    headers = {
        "ACCESS-KEY": access_key,
        "ACCESS-SIGN": access_sign,
        "ACCESS-PASSPHRASE": passphrase,
        "ACCESS-TIMESTAMP": timestamp,
        "locale": "en-US",
        "Content-Type": "application/json"
    }

    res = requests.post(url, headers=headers, data=body)
    return res.json()


def get_bitget_balance(symbol="SOLUSDT", margin_coin="USDT"):
    access_key = os.getenv("BG_ACCESS_KEY")
    secret_key = os.getenv("BG_SECRET_KEY")
    passphrase = os.getenv("BG_PASSPHARASE")

    # 서버 시간
    server_time_res = requests.get("https://api.bitget.com/api/v2/public/time")
    timestamp = str(server_time_res.json().get('data', {}).get('serverTime'))

    method = "GET"
    path = "/api/v2/mix/account/account"
    query = f"symbol={symbol.lower()}&productType=USDT-FUTURES&marginCoin={margin_coin}"
    url = f"https://api.bitget.com{path}?{query}"

    sign_data = timestamp + method + path + "?" + query
    signature = hmac.new(secret_key.encode(),
                         sign_data.encode(), hashlib.sha256).digest()
    access_sign = base64.b64encode(signature).decode()

    headers = {
        "ACCESS-KEY": access_key,
        "ACCESS-SIGN": access_sign,
        "ACCESS-PASSPHRASE": passphrase,
        "ACCESS-TIMESTAMP": timestamp,
        "locale": "en-US",
        "Content-Type": "application/json"
    }

    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data = res.json()
        if data.get("code") == "00000" and data.get("data"):
            account_data = data["data"]
            available_balance = float(account_data.get("available", 0))
            equity = float(account_data.get("accountEquity", 0))
            return {"available": available_balance, "equity": equity}
        else:
            print(f"[Error] 잔고 조회 실패: {data}")
            return None
    except Exception as e:
        print(f"[Error] 잔고 조회 실패: {e}")
        return None


def get_all_positions():
    print('[Function] 모든 포지션 조회 중...')
    access_key = os.getenv("BG_ACCESS_KEY")
    secret_key = os.getenv("BG_SECRET_KEY")
    passphrase = os.getenv("BG_PASSPHARASE")

    server_time_res = requests.get("https://api.bitget.com/api/v2/public/time")
    timestamp = str(server_time_res.json()['data']['serverTime'])

    method = "GET"
    path = "/api/v2/mix/position/all-position"
    query = "productType=USDT-FUTURES&marginCoin=USDT"
    url = f"https://api.bitget.com{path}?{query}"

    sign_data = timestamp + method + path + "?" + query
    signature = hmac.new(secret_key.encode(),
                         sign_data.encode(), hashlib.sha256).digest()
    access_sign = base64.b64encode(signature).decode()

    headers = {
        "ACCESS-KEY": access_key,
        "ACCESS-SIGN": access_sign,
        "ACCESS-PASSPHRASE": passphrase,
        "ACCESS-TIMESTAMP": timestamp,
        "locale": "en-US",
        "Content-Type": "application/json"
    }

    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data = res.json()
        if data.get("code") == "00000":
            return data.get("data", [])
        else:
            print(f"[Error] 포지션 조회 실패: {data}")
            return []
    except Exception as e:
        print(f"[Error] 포지션 조회 실패: {e}")
        return []
