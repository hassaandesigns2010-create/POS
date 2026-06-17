from decimal import Decimal

def format_rs(amount: float | int | Decimal | None) -> str:
    try:
        if amount is None:
            val = Decimal(0)
        else:
            val = amount
        return f"Rs {val:,.2f}"
    except Exception:
        return "Rs 0.00"
