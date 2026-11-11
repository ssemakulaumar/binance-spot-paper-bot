"""Read-only public Binance market-data client. No API key is required."""
import json
import urllib.parse
import urllib.request
from config import BASE_URL, CANDLE_LIMIT

class MarketDataError(Exception):
    pass

def _get(path, params):
    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(
        f"{BASE_URL}{path}?{query}",
        headers={"User-Agent": "Termux-Paper-Trading-Educational-Bot/1.0"}
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise MarketDataError(f"Binance market-data request failed: {exc}") from exc

def get_klines(symbol, interval):
    raw = _get("/api/v3/klines", {
        "symbol": symbol, "interval": interval, "limit": CANDLE_LIMIT
    })
    if not isinstance(raw, list) or not raw:
        raise MarketDataError(f"No candles returned for {symbol}")
    return [{
        "open_time": int(row[0]),
        "open": float(row[1]),
        "high": float(row[2]),
        "low": float(row[3]),
        "close": float(row[4]),
        "volume": float(row[5]),
        "close_time": int(row[6]),
    } for row in raw]

def get_price(symbol):
    data = _get("/api/v3/ticker/price", {"symbol": symbol})
    return float(data["price"])
