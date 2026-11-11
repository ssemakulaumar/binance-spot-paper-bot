"""Combined SMA + MACD + RSI educational signal strategy."""
from indicators import sma, rsi, macd

def get_signal(candles):
    closes = [c["close"] for c in candles]
    if len(closes) < 60:
        return "HOLD", {"reason": "Not enough candle history"}

    sma20 = sma(closes, 20)
    sma50 = sma(closes, 50)
    rsi14 = rsi(closes, 14)
    macd_values = macd(closes)

    if rsi14 is None or macd_values is None:
        return "HOLD", {"reason": "Indicators are not ready"}

    macd_line, signal_line = macd_values
    price = closes[-1]
    details = {
        "price": price, "sma20": sma20, "sma50": sma50,
        "rsi14": rsi14, "macd": macd_line, "macd_signal": signal_line
    }

    if price > sma20 > sma50 and macd_line > signal_line and 50 <= rsi14 <= 70:
        return "BUY", details
    if price < sma20 or rsi14 >= 75 or (macd_line < signal_line and price < sma20):
        return "SELL", details
    return "HOLD", details
