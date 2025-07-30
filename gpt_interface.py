import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# GPT 호출 카운터
gpt_call_count = 0

# 자연어 설명용 (프롬프트에 사용)
granularity_human_readable = {
    "1m": "1-minute", "3m": "3-minute", "5m": "5-minute", "15m": "15-minute", "30m": "30-minute",
    "1H": "1-hour", "4H": "4-hour", "6H": "6-hour", "12H": "12-hour", "1D": "1-day",
    "3D": "3-day", "1W": "1-week", "1M": "1-month",
    "6Hutc": "6-hour UTC", "12Hutc": "12-hour UTC",
    "1Dutc": "1-day UTC", "3Dutc": "3-day UTC", "1Wutc": "1-week UTC", "1Mutc": "1-month UTC"
}



def ask_gpt(chart_data, granularity, calnum, delta):
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    global gpt_call_count
    gpt_call_count += 1
    print(f"현재 세션에서 GPT 호출한 횟수 : {gpt_call_count}")

    # 차트 데이터 압축: [open, high, low, close, volume]
    trimmed_data = [[c[1], c[2], c[3], c[4], c[5]] for c in chart_data]
    chart_text = "\n".join([",".join(map(str, row)) for row in trimmed_data])

    granularity_label = granularity_human_readable.get(
        granularity, granularity)

    prompt = (
        f"Each row below is a candlestick in format [open, high, low, close, volume].\n"
        f"Based on this {granularity_label} chart, respond with ONLY ONE WORD: buy or sell.\n"
        f"(buy means long, sell means short.)\n"
        f"if it moves more than {delta} dollar, position is going to close.\n"
        f"You have to check all the {calnum} candles from from beginning to end.\n"
        f"\n"
        f"IMPORTANT:\n"
        f"- No explanation, no punctuation, just one word.\n"
        f"{chart_text}"
    )

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a BTC futures professional trader."},
            {"role": "user", "content": prompt}
        ]
    )

    answer = response.choices[0].message.content.strip().lower()
    print(f"[GPT:{granularity}] {answer}")
    if answer == "BUY":
        answer = "buy"
    if answer == "SELL":
        answer = "sell"
    if answer in ["buy", "sell"]:
        return answer
    else:
        print("[Error] @@@@@ GPT 응답이 buy/sell이 아님:", answer)
        return "error"
    