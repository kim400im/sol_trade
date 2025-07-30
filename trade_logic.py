import os
from bitget_api import place_bitget_order


def execute_trade_based_on_gpt(trade_direction, chart_data):
    trade_direction = trade_direction.strip().lower()
    symbol = "SOLUSDT"
    order_amount_usd = float(os.getenv("ORDER_AMOUNT_USD"))

    latest_close_price = float(chart_data[-1][4])
    size = round(order_amount_usd / latest_close_price, 4)

    if trade_direction == "buy":
        print("[Action] BUY")
        res = place_bitget_order(symbol=symbol, side="buy", size=str(
            size), price=str(latest_close_price), order_type="market")

    elif trade_direction == "sell":
        print("[Action] SELL")
        res = place_bitget_order(symbol=symbol, side="sell", size=str(
            size), price=str(latest_close_price), order_type="market")

    else:
        print(
            f"[Error] file trade_logic - Unknown trade_direction: {trade_direction}")

    print("[Response] "+res["msg"])

