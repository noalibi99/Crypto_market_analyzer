from typing import Tuple

def format_currency(value: float, precision: int = 2) -> str:
    if value is None:
        return "N/A"
    
    if value >= 1e12:
        return f"${value/1e12:.3f}T"
    elif value >= 1e9:
        return f"${value/1e9:.2f}B"
    elif value >= 1e6:
        return f"${value/1e6:.2f}M"
    elif value >= 1e3:
        return f"${value:,.2f}"
    else:
        return f"${value:.2f}"

def format_price_change(value: float) -> Tuple[str, str, str]:
    if value is None:
        return "N/A", "gray", None
    color = "green" if value >= 0 else "red"
    arrow = "↑" if value >= 0 else "↓"
    return f"{value:+.2f}%", color, arrow

def format_number(value: float, suffix: str = "") -> str:
    if value is None:
        return "N/A"
    if value >= 1e6:
        formatted = f"{value/1e6:.2f}M"
    elif value >= 1e3:
        formatted = f"{value/1e3:.2f}K"
    else:
        formatted = f"{value:.2f}"
    return f"{formatted}{suffix}"
