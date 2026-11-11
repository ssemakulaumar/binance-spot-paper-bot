# Binance Spot Paper-Trading Bot (Termux)

This is an educational **paper-trading** project. It reads public Binance Spot market data and simulates trades locally. It does not place real orders.

## Safety boundary

- `LIVE_TRADING_ENABLED = False` is fixed in `config.py`.
- There is no Binance signed-order endpoint, API-key handling, or live order function.
- Do not add exchange trading credentials to this project.
- Simulated balances and trades are stored locally in SQLite and CSV.

## Termux installation

```bash
pkg update && pkg upgrade -y
pkg install python git -y
```

Download and extract the project ZIP into your Termux home folder. For example, if the ZIP is in Downloads:

```bash
termux-setup-storage
cp ~/storage/downloads/binance_spot_paper_bot.zip ~/
cd ~
unzip binance_spot_paper_bot.zip
cd binance_spot_paper_bot
```

No third-party Python packages are required.

## Run

One scan only:

```bash
python main.py --once
```

Continuous paper monitoring:

```bash
python main.py
```

Stop continuous monitoring with `CTRL+C`.

## Optional settings

Set environment variables before running, for example:

```bash
export BOT_SYMBOLS="BTCUSDT,ETHUSDT"
export BOT_INTERVAL="5m"
export BOT_STARTING_CASH="1000"
export BOT_POLL_SECONDS="60"
python main.py
```

Supported settings are in `config.py`. The first run creates `paper_trading.db` and `paper_trades.csv`.

**Important:** The starting balance is used only when the database is first created. To restart a paper account from scratch, stop the bot and manually back up then remove `paper_trading.db`; this also removes its stored trade history. Keep a copy of the CSV first.

## Project layout

- `config.py` — symbols and risk settings
- `market_data.py` — read-only public Binance data
- `indicators.py` — SMA, EMA, RSI and MACD calculations
- `strategy.py` — combined signal rules
- `risk.py` — simulated position sizing and exposure limit
- `paper_broker.py` — local simulated execution, SQLite and CSV
- `main.py` — monitoring loop

## Testing notes

This project is a starting architecture, not a validated profitable strategy. Test indicator calculations, candle timing, API outages, persistence, fees, and risk behavior before relying on any performance report. Backtests and paper results do not predict future results.
