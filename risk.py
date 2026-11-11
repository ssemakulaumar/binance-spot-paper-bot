"""Position sizing and exposure checks for simulated trades only."""
from config import ALLOCATION_PER_TRADE, MAX_TOTAL_EXPOSURE

def position_budget(cash, equity, open_exposure):
    if cash <= 0 or equity <= 0:
        return 0.0
    remaining_capacity = max(0.0, equity * MAX_TOTAL_EXPOSURE - open_exposure)
    return max(0.0, min(cash, equity * ALLOCATION_PER_TRADE, remaining_capacity))
