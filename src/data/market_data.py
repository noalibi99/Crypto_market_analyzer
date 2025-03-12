import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import logging
from src.api.binance_client import BinanceAPI
import config

logger = logging.getLogger(__name__)

def get_market_info(client: BinanceAPI, symbol: str) -> Optional[Dict[str, Any]]:
    try:
        stats = client.get_ticker(symbol=symbol)
        
        klines_1h = client.get_klines(symbol=symbol, interval=client.client.KLINE_INTERVAL_1HOUR, limit=2)
        klines_7d = client.get_klines(symbol=symbol, interval=client.client.KLINE_INTERVAL_1DAY, limit=8)
        klines_all = client.get_klines(symbol=symbol, interval=client.client.KLINE_INTERVAL_1DAY, limit=1000)
        
        price_change_1h = ((float(klines_1h[-1][4]) - float(klines_1h[-2][4])) / float(klines_1h[-2][4])) * 100
        price_change_7d = ((float(klines_7d[-1][4]) - float(klines_7d[0][4])) / float(klines_7d[0][4])) * 100
        
        current_price = float(stats['lastPrice'])
        
        if symbol.startswith('BTC'):
            max_supply = config.SYMBOL_DATA.get("BTCUSDT", {}).get("max_supply")
            circulation_supply = config.SYMBOL_DATA.get("BTCUSDT", {}).get("circulation_supply")
            market_cap = current_price * circulation_supply if circulation_supply else None
        else:
            max_supply = None
            circulation_supply = None
            market_cap = None

        return {
            'low_24h': float(stats['lowPrice']),
            'high_24h': float(stats['highPrice']),
            'price_change_1h': price_change_1h,
            'price_change_24h': float(stats['priceChangePercent']),
            'price_change_7d': price_change_7d,
            'volume_24h': float(stats['volume']) * float(stats['weightedAvgPrice']),
            'market_cap': market_cap,
            'circulation_supply': circulation_supply,
            'max_supply': max_supply,
            'all_time_high': max([float(k[2]) for k in klines_all])
        }
    except Exception as e:
        logger.error(f"Error fetching market info: {str(e)}")
        return None

def get_price_change_for_interval(client: BinanceAPI, symbol: str, interval: str) -> float:
    interval_mapping = {
        "1m": (client.client.KLINE_INTERVAL_1MINUTE, 2),
        "5m": (client.client.KLINE_INTERVAL_5MINUTE, 2),
        "15m": (client.client.KLINE_INTERVAL_15MINUTE, 2),
        "30m": (client.client.KLINE_INTERVAL_30MINUTE, 2),
        "1h": (client.client.KLINE_INTERVAL_1HOUR, 2),
        "4h": (client.client.KLINE_INTERVAL_4HOUR, 2),
        "1d": (client.client.KLINE_INTERVAL_1DAY, 2),
        "1w": (client.client.KLINE_INTERVAL_1DAY, 8),
        "1M": (client.client.KLINE_INTERVAL_1DAY, 31)
    }

    if interval not in interval_mapping:
        return 0.0

    interval_str, limit = interval_mapping[interval]
    klines = client.get_klines(symbol=symbol, interval=interval_str, limit=limit)
    
    if len(klines) < 2:
        return 0.0

    current_price = float(klines[-1][4])
    previous_price = float(klines[0][4])
    return ((current_price - previous_price) / previous_price) * 100

def fetch_candlesticks(
    client: BinanceAPI,
    symbol: str,
    interval: str = "15m",
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Optional[pd.DataFrame]:
    try:
        interval_time_map = {
            "1w": 52,  # 52 weeks
            "1M": 12   # 12 months
        }
        
        if interval in interval_time_map:
            weeks_or_months = interval_time_map[interval]
            if interval == "1w":
                start_date = end_date - timedelta(weeks=weeks_or_months)
            else:  # 1M
                start_date = end_date - timedelta(days=weeks_or_months * 30)

        start_ts = int(start_date.timestamp() * 1000) if start_date else None
        end_ts = int(end_date.timestamp() * 1000) if end_date else None
        
        data = client.get_historical_klines(
            symbol=symbol,
            interval=interval,
            start_str=str(start_ts),
            end_str=str(end_ts),
            limit=1000
        )
        
        columns = [
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base", "taker_buy_quote", "ignore"
        ]
        
        df = pd.DataFrame(data, columns=columns)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        
        numeric_cols = ["open", "high", "low", "close", "volume"]
        df[numeric_cols] = df[numeric_cols].astype(float)
        
        return calculate_moving_averages(df)
    
    except Exception as e:
        logger.error(f"Error fetching candlestick data: {str(e)}")
        return None

def calculate_moving_averages(df: pd.DataFrame, periods: List[int] = [20, 50, 200]) -> pd.DataFrame:
    for period in periods:
        df[f'MA_{period}'] = df['close'].rolling(window=period).mean()
    return df
