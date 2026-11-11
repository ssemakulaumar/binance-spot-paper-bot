"""Small dependency-free technical indicator calculations."""

def sma(values, period):
    if len(values) < period:
        return None
    return sum(values[-period:]) / period

def ema_series(values, period):
    if len(values) < period:
        return []
    multiplier = 2 / (period + 1)
    seed = sum(values[:period]) / period
    result = [seed]
    current = seed
    for value in values[period:]:
        current = (value * multiplier) + (current * (1 - multiplier))
        result.append(current)
    return result

def rsi(values, period=14):
    if len(values) <= period:
        return None
    changes = [values[i] - values[i-1] for i in range(1, len(values))]
    gains = [max(change, 0) for change in changes]
    losses = [max(-change, 0) for change in changes]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for i in range(period, len(changes)):
        avg_gain = ((avg_gain * (period - 1)) + gains[i]) / period
        avg_loss = ((avg_loss * (period - 1)) + losses[i]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def macd(values, fast=12, slow=26, signal=9):
    fast_line = ema_series(values, fast)
    slow_line = ema_series(values, slow)
    if not fast_line or not slow_line:
        return None
    # Align the EMA series at the point where the slow EMA begins.
    offset = slow - fast
    aligned_fast = fast_line[offset:]
    line = [a - b for a, b in zip(aligned_fast, slow_line)]
    signal_line = ema_series(line, signal)
    if not signal_line:
        return None
    return line[-1], signal_line[-1]
