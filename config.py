import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")

# Email Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")

# Default symbols
DEFAULT_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", 
    "ADAUSDT", "DOGEUSDT", "XRPUSDT"
]

# Time intervals
INTERVALS = ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"]

# Symbol specific data
SYMBOL_DATA = {
    "BTCUSDT": {
        "max_supply": 21_000_000,
        "circulation_supply": 19_801_356
    }
}
