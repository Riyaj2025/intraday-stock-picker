from angel_api import get_intraday_candles

def check_trade_score(symbol, token):
    df = get_intraday_candles(token)

    if df.empty or len(df) < 5:
        return None  # skip if insufficient data

    score = 0
    reasons = []
    direction = None

    c1 = df.iloc[0]
    c2 = df.iloc[1]
    c3 = df.iloc[2]
    volume_avg = df["volume"].astype(float).iloc[1:6].mean()
    vol_current = float(c1["volume"])

    # --- Buy Conditions ---
    if c1["open"] == c1["low"]:
        score += 1
        reasons.append("Open = Low")
        direction = "BUY"

    if c1["close"] > c1["open"] and c2["close"] > c2["open"]:
        score += 1
        reasons.append("2 Green Candles")
        direction = "BUY"

    if vol_current > 2 * volume_avg:
        score += 1
        reasons.append("Volume Spike")
        direction = "BUY"

    # --- Short Conditions ---
    if c1["open"] == c1["high"]:
        score += 1
        reasons.append("Open = High")
        direction = "SHORT"

    if c1["close"] < c1["open"] and c2["close"] < c2["open"]:
        score += 1
        reasons.append("2 Red Candles")
        direction = "SHORT"

    if vol_current > 2 * volume_avg and direction == "SHORT":
        score += 1
        reasons.append("Volume Spike")
        direction = "SHORT"

    if direction:
        return {
            "symbol": symbol,
            "token": token,
            "score": score,
            "direction": direction,
            "reasons": ", ".join(reasons)
        }

    return None
