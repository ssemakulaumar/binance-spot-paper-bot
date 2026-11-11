"""Run the Binance Spot paper-trading bot from Termux."""
import argparse
import time
from config import SYMBOLS, INTERVAL, POLL_SECONDS, LIVE_TRADING_ENABLED
from market_data import get_klines, get_price, MarketDataError
from strategy import get_signal
from paper_broker import PaperBroker

def run_once(broker):
    prices = {}
    candles_by_symbol = {}
    for symbol in SYMBOLS:
        try:
            candles = get_klines(symbol, INTERVAL)
            price = get_price(symbol)
            candles_by_symbol[symbol] = candles
            prices[symbol] = price
        except MarketDataError as exc:
            print(f"[DATA ERROR] {symbol}: {exc}")
    if not prices:
        print("No market prices available; skipping this cycle.")
        return

    broker.check_protective_exits(prices)
    for symbol, candles in candles_by_symbol.items():
        signal, details = get_signal(candles)
        price = prices[symbol]
        print(f"{symbol} | {signal} | price={price:.4f} | {details}")
        if signal == "BUY":
            broker.buy(symbol, price, prices)
        elif signal == "SELL":
            broker.sell(symbol, price, "strategy sell signal")
    broker.report(prices)

def main():
    parser = argparse.ArgumentParser(description="Binance Spot paper-trading bot (no live orders)")
    parser.add_argument("--once", action="store_true", help="run one market scan and exit")
    args = parser.parse_args()

    if LIVE_TRADING_ENABLED:
        raise RuntimeError("Safety check failed: live trading must remain disabled.")
    if not SYMBOLS:
        raise RuntimeError("Set BOT_SYMBOLS to at least one Binance Spot symbol.")

    broker = PaperBroker()
    print("Binance Spot PAPER mode. Live order execution is disabled.")
    print(f"Pairs: {', '.join(SYMBOLS)} | interval: {INTERVAL}")
    try:
        while True:
            run_once(broker)
            if args.once:
                break
            time.sleep(max(10, POLL_SECONDS))
    except KeyboardInterrupt:
        print("\\nStopped by user.")
    finally:
        broker.close()

if __name__ == "__main__":
    main()
