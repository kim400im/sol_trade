import os
import time
from dotenv import load_dotenv
from bitget_api import get_bitget_chart, get_bitget_position, place_bitget_order, close_all_positions, get_bitget_balance, get_all_positions
from gpt_interface import ask_gpt
from logger import log_trade_decision, update_trade_exit
from utils import get_current_ip, get_current_time
from collections import Counter
from utils import *


load_dotenv()

# ==========================
# CONFIG
# ==========================
symbol = "SOLUSDT"
product_type = "usdt-futures"
granularities = ["3m", "5m", "1m"]
candlenum = 100
order_amount_usd = float("1000")
check_interval_sec = 30
price_change_threshold = float("2")  # Adjusted for Solana price range
TP_DELTA = SL_DELTA = 5  # 고정 이익 목표 (Solana price range)

# ==========================
# INIT
# ==========================
beeplow()
beep()
beeplow()
beep()
beeplow()
beep()

# Display startup information
print("=" * 60)
print("CRYPTO TRADING BOT - STARTUP INFORMATION")
print("=" * 60)

current_ip = get_current_ip()
print(f"현재 IP 주소: {current_ip}")

# Get and display account balance
print("\n[계정 정보]")
balance_info = get_bitget_balance()
if balance_info:
    print(f"사용 가능 잔고: ${balance_info['available']:.2f} USDT")
    print(f"총 자산: ${balance_info['equity']:.2f} USDT")
else:
    print("잔고 정보를 가져올 수 없습니다.")

# Get and display all positions
print("\n[현재 포지션]")
all_positions = get_all_positions()
if all_positions:
    active_positions = [pos for pos in all_positions if float(pos.get('total', 0)) != 0]
    if active_positions:
        for pos in active_positions:
            symbol = pos.get('symbol', 'Unknown')
            side = pos.get('holdSide', 'Unknown')
            size = pos.get('total', '0')
            unrealized_pnl = pos.get('unrealizedPL', '0')
            margin = pos.get('margin', '0')
            avg_price = pos.get('averageOpenPrice', '0')
            print(f"  {symbol}: {side.upper()} | Size: {size} | Avg Price: ${avg_price}")
            print(f"    미실현 손익: ${float(unrealized_pnl):.2f} | 마진: ${float(margin):.2f}")
    else:
        print("활성 포지션이 없습니다.")
else:
    print("포지션 정보를 가져올 수 없습니다.")

print("\n" + "=" * 60)
print("트레이딩 시작...")
print("=" * 60 + "\n")

previous_price = None
target_price = None
stop_loss_price = None
timestamp = None

# ==========================
# MAIN LOOP
# ==========================
while True:
    try:
        print(f"현재 시간: {get_current_time()}")
        position_data = get_bitget_position()
        position_active = bool(position_data.get("data"))

        chart_data = get_bitget_chart()
        beeploww()
        current_price = float(chart_data[-1][4])

        if position_active:
            hold_side = position_data.get("data", [])[0].get(
                "holdSide")  # "long" or "short"
            print(
                f"[Monitor] Position active ({hold_side.upper()}) | Current: {current_price} | TP: {target_price} | SL: {stop_loss_price}")
            beeploww()
            if hold_side == "long":
                if target_price and current_price >= target_price:
                    print("[Action] TAKE PROFIT (LONG)")
                    close_all_positions()
                    balance = get_bitget_balance()
                    update_trade_exit(
                        timestamp, "closed", exit_reason="take_profit", exit_balance=balance)
                    target_price = stop_loss_price = timestamp = None
                    beep()
                    # 코드 유지보수 시간 벌기 위해 공백기를 설정
                    time.sleep(check_interval_sec*2)

                elif stop_loss_price and current_price <= stop_loss_price:
                    print("[Action] STOP LOSS (LONG)")
                    close_all_positions()
                    balance = get_bitget_balance()
                    update_trade_exit(
                        timestamp, "closed", exit_reason="stop_loss", exit_balance=balance)
                    target_price = stop_loss_price = timestamp = None
                    beeplow()
                    # 코드 유지보수 시간 벌기 위해 공백기를 설정
                    time.sleep(check_interval_sec*2)

            elif hold_side == "short":
                if target_price and current_price <= target_price:
                    print("[Action] TAKE PROFIT (SHORT)")
                    close_all_positions()
                    balance = get_bitget_balance()
                    update_trade_exit(
                        timestamp, "closed", exit_reason="take_profit", exit_balance=balance)
                    target_price = stop_loss_price = timestamp = None
                elif stop_loss_price and current_price >= stop_loss_price:
                    print("[Action] STOP LOSS (SHORT)")
                    close_all_positions()
                    balance = get_bitget_balance()
                    update_trade_exit(
                        timestamp, "closed", exit_reason="stop_loss", exit_balance=balance)
                    target_price = stop_loss_price = timestamp = None

        else:
            if previous_price and abs(current_price - previous_price) < price_change_threshold:
                print("[Skip] 가격 변화 부족")
                beeploww()
                time.sleep(check_interval_sec)
                continue
            previous_price = current_price

            directions = []

            for g in granularities:
                chart_data = get_bitget_chart(
                    symbol, g, candlenum, product_type)
                direction = ask_gpt(chart_data, g, candlenum, TP_DELTA)
                directions.append(direction)

            if all(d == "buy" for d in directions):
                trade_direction = "buy"
            elif all(d == "sell" for d in directions):
                trade_direction = "sell"
            else:
                print(
                    f"[Decision] 혼합 방향 → HOLD | 분포: {dict(Counter(directions))}")
                beepshort()
                time.sleep(check_interval_sec)
                continue

            # 고정된 TP/SL 설정
            if trade_direction == "buy":
                avg_tp = current_price + TP_DELTA
                avg_sl = current_price - SL_DELTA
            elif trade_direction == "sell":  # sell
                avg_tp = current_price - TP_DELTA
                avg_sl = current_price + SL_DELTA

            size = round(order_amount_usd / current_price, 4)

            print(
                f"[Action] {trade_direction.upper()} / TP: {avg_tp} / SL: {avg_sl}")
            place_bitget_order(symbol, trade_direction, str(
                size), str(current_price), order_type="market")

            if (trade_direction == "buy"):
                beep()
            else:
                beeplow()

            target_price = avg_tp
            stop_loss_price = avg_sl
            timestamp = log_trade_decision(
                price=current_price,
                granularity_list=granularities,
                trade_direction=trade_direction,
                tp=avg_tp,
                sl=avg_sl
            )

        time.sleep(check_interval_sec)

    except Exception as e:
        print(f"[Error] {e}")
        time.sleep(10)
