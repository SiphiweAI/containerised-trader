import requests
import os
import sys
from typing import Optional

def validate_env_vars():
    required_vars = ["DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD", "twelvedataAPI_KEY", "CELERY_BROKER_URL"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print(f"Missing environment variables: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

def fetch_candles(symbol: str, period: list[str], outputsize: int = 5) -> list[dict[str, str]]:
    """
    Fetch the last `outputsize` candlesticks for a given symbol and interval.
    """
    apikey = os.getenv("twelvedataAPI_KEY")
    if not apikey:
        raise ValueError("API_KEY not set in environment variables")

    url = "https://api.twelvedata.com/time_series"
    interval = period[0]

    params = {
        "symbol": symbol,
        "interval": interval,
        "start_date": period[1].strip() if len(period) > 1 else None,
        "end_date": period[2].strip() if len(period) > 2 else None,
        "outputsize": outputsize,
        "apikey": apikey
    }

    # remove None values if any
    params = {k: v for k, v in params.items() if v is not None}

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise Exception(f"Request failed: {response.status_code} - {response.text}")

    data = response.json()

    if data.get("status") == "error" or "values" not in data:
        raise Exception(f"API Error: {data.get('message', 'Unknown error')}")

    return data["values"]

def evaluate_trade(candles, entry_price, tp, sl, position_size=1.0):
    """
    Evaluates a trade based on candlestick data and returns verdict and PnL.

    Parameters:
        candles (list): List of candlestick dicts with 'low', 'high', 'open', and 'close' keys.
        entry_price (float): Entry price for the trade.
        tp (float): Take profit level.
        sl (float): Stop loss level.
        position_size (float): Size of the position (e.g., lot size, units). Default is 1.0.

    Returns:
        verdict (str): 'win' | 'loss' | 'holding' | 'no entry'
        pnl (float): profit or loss as float (0.0 if holding or no entry)
    """
    entry_triggered = False
    verdict = "no entry"
    pnl = 0.0

    # Buffer to tolerate slight price misses due to noise/slippage
    buffer = (tp - entry_price) * 0.01 if tp > entry_price else (entry_price - tp) * 0.01

    for i, candle in enumerate(candles):
        low = float(candle["low"])
        high = float(candle["high"])
        open_ = float(candle.get("open", (low + high) / 2))
        close = float(candle.get("close", (low + high) / 2))

        # Check if entry is triggered (using high-low-open-close for confirmation)
        if not entry_triggered:
            # Entry triggered if entry price is within candle range (with buffer)
            if low <= entry_price <= high or open_ <= entry_price <= close or close <= entry_price <= open_:
                entry_triggered = True
                entry_candle_index = i
            else:
                continue

        # After entry triggered, check for TP or SL with buffer
        if (low <= tp + buffer <= high) or (open_ <= tp + buffer <= close) or (close <= tp + buffer <= open_):
            verdict = "win"
            pnl = (tp - entry_price) * position_size
            break
        elif (low <= sl - buffer <= high) or (open_ <= sl - buffer <= close) or (close <= sl - buffer <= open_):
            verdict = "loss"
            pnl = (sl - entry_price) * position_size
            break

    # If entry triggered but no TP or SL hit yet, verify holding status with a couple of follow-up candles
    if entry_triggered and verdict == "no entry":
        # Simple extension: confirm if price is moving favorably or flat in next few candles
        follow_up_candles = candles[entry_candle_index + 1 : entry_candle_index + 3]
        favorable_move = False
        for candle in follow_up_candles:
            high = float(candle["high"])
            low = float(candle["low"])
            if tp > entry_price and high >= entry_price:  # bullish move on long
                favorable_move = True
                break
            elif tp < entry_price and low <= entry_price:  # bearish move on short
                favorable_move = True
                break
        verdict = "holding" if favorable_move else "no entry"
        pnl = 0.0

    return verdict, round(pnl, 5)
