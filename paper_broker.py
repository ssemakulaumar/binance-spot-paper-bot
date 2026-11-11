"""SQLite-backed paper broker. It cannot send orders to Binance."""
import csv
import os
import sqlite3
from datetime import datetime, timezone
from config import DATABASE, TRADE_LOG, STARTING_CASH, FEE_RATE, STOP_LOSS_PCT, TAKE_PROFIT_PCT
from risk import position_budget

class PaperBroker:
    def __init__(self):
        self.db = sqlite3.connect(DATABASE)
        self.db.row_factory = sqlite3.Row
        self._setup()

    def _setup(self):
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS account (
            id INTEGER PRIMARY KEY CHECK(id=1), cash REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS positions (
            symbol TEXT PRIMARY KEY, quantity REAL NOT NULL,
            entry_price REAL NOT NULL, entry_fee REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT, time TEXT, symbol TEXT,
            side TEXT, quantity REAL, price REAL, fee REAL, realized_pnl REAL,
            reason TEXT
        );
        """)
        self.db.execute("INSERT OR IGNORE INTO account(id,cash) VALUES(1,?)", (STARTING_CASH,))
        self.db.commit()
        if not os.path.exists(TRADE_LOG):
            with open(TRADE_LOG, "w", newline="") as f:
                csv.writer(f).writerow(["time","symbol","side","quantity","price","fee","realized_pnl","reason"])

    def cash(self):
        return float(self.db.execute("SELECT cash FROM account WHERE id=1").fetchone()["cash"])

    def positions(self):
        return self.db.execute("SELECT * FROM positions").fetchall()

    def exposure(self, prices):
        total = 0.0
        for p in self.positions():
            total += p["quantity"] * prices.get(p["symbol"], p["entry_price"])
        return total

    def equity(self, prices):
        return self.cash() + self.exposure(prices)

    def _record(self, symbol, side, qty, price, fee, pnl, reason):
        now = datetime.now(timezone.utc).isoformat()
        row = [now, symbol, side, qty, price, fee, pnl, reason]
        self.db.execute(
            "INSERT INTO trades(time,symbol,side,quantity,price,fee,realized_pnl,reason) VALUES(?,?,?,?,?,?,?,?)",
            row
        )
        self.db.commit()
        with open(TRADE_LOG, "a", newline="") as f:
            csv.writer(f).writerow(row)

    def buy(self, symbol, price, prices):
        if any(p["symbol"] == symbol for p in self.positions()):
            return False
        cash = self.cash()
        equity = self.equity(prices)
        budget = position_budget(cash, equity, self.exposure(prices))
        if budget <= 0:
            return False
        fee = budget * FEE_RATE
        qty = (budget - fee) / price
        self.db.execute("UPDATE account SET cash=cash-? WHERE id=1", (budget,))
        self.db.execute(
            "INSERT INTO positions(symbol,quantity,entry_price,entry_fee) VALUES(?,?,?,?)",
            (symbol, qty, price, fee)
        )
        self.db.commit()
        self._record(symbol, "BUY", qty, price, fee, 0.0, "strategy signal")
        return True

    def sell(self, symbol, price, reason="strategy signal"):
        p = self.db.execute("SELECT * FROM positions WHERE symbol=?", (symbol,)).fetchone()
        if not p:
            return False
        gross = p["quantity"] * price
        fee = gross * FEE_RATE
        proceeds = gross - fee
        pnl = proceeds - (p["quantity"] * p["entry_price"]) - p["entry_fee"]
        self.db.execute("UPDATE account SET cash=cash+? WHERE id=1", (proceeds,))
        self.db.execute("DELETE FROM positions WHERE symbol=?", (symbol,))
        self.db.commit()
        self._record(symbol, "SELL", p["quantity"], price, fee, pnl, reason)
        return True

    def check_protective_exits(self, prices):
        for p in list(self.positions()):
            price = prices.get(p["symbol"])
            if price is None:
                continue
            change = price / p["entry_price"] - 1
            if change <= -STOP_LOSS_PCT:
                self.sell(p["symbol"], price, "paper stop-loss")
            elif change >= TAKE_PROFIT_PCT:
                self.sell(p["symbol"], price, "paper take-profit")

    def report(self, prices):
        equity = self.equity(prices)
        realized = self.db.execute("SELECT COALESCE(SUM(realized_pnl),0) AS pnl FROM trades").fetchone()["pnl"]
        print("\\n--- PAPER ACCOUNT ---")
        print(f"Cash:       {self.cash():,.2f} USDT")
        print(f"Equity:     {equity:,.2f} USDT")
        print(f"Realized P/L: {realized:,.2f} USDT")
        print("Open positions:")
        for p in self.positions():
            mark = prices.get(p["symbol"], p["entry_price"])
            unrealized = p["quantity"] * (mark - p["entry_price"]) - p["entry_fee"]
            print(f"  {p['symbol']}: qty={p['quantity']:.8f}, entry={p['entry_price']:.4f}, mark={mark:.4f}, unrealized≈{unrealized:.2f} USDT")
        print("---------------------\\n")

    def close(self):
        self.db.close()
