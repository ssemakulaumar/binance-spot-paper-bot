"""Configuration for the educational Binance Spot paper-trading bot."""
import os

BASE_URL = "https://api.binance.com"
SYMBOLS = [s.strip().upper() for s in os.getenv("BOT_SYMBOLS", "BTCUSDT,ETHUSDT,SOLUSDT").split(",") if s.strip()]
INTERVAL = os.getenv("BOT_INTERVAL", "5m")
CANDLE_LIMIT = int(os.getenv("BOT_CANDLE_LIMIT", "120"))
POLL_SECONDS = int(os.getenv("BOT_POLL_SECONDS", "60"))

STARTING_CASH = float(os.getenv("BOT_STARTING_CASH", "1000"))
ALLOCATION_PER_TRADE = float(os.getenv("BOT_ALLOCATION", "0.10"))
MAX_TOTAL_EXPOSURE = float(os.getenv("BOT_MAX_EXPOSURE", "0.50"))
STOP_LOSS_PCT = float(os.getenv("BOT_STOP_LOSS", "0.02"))
TAKE_PROFIT_PCT = float(os.getenv("BOT_TAKE_PROFIT", "0.04"))
FEE_RATE = float(os.getenv("BOT_FEE_RATE", "0.001"))

DATABASE = os.getenv("BOT_DATABASE", "paper_trading.db")
TRADE_LOG = os.getenv("BOT_TRADE_LOG", "paper_trades.csv")

# This project intentionally has no live-order implementation.
LIVE_TRADING_ENABLED = False
