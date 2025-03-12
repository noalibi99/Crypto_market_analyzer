from binance.client import Client
import logging
from typing import Optional, List, Dict, Any
import config

logger = logging.getLogger(__name__)

class BinanceAPI:
    def __init__(self):
        try:
            self.client = Client(config.BINANCE_API_KEY, config.BINANCE_API_SECRET)
        except Exception as e:
            logger.error(f"Error initializing Binance client: {str(e)}")
            raise e

    def get_account_info(self) -> Optional[List[Dict[str, Any]]]:
        try:
            account = self.client.get_account()
            return account['balances']
        except Exception as e:
            logger.error(f"Error fetching account info: {str(e)}")
            return None
    
    def get_ticker(self, symbol: str) -> Optional[Dict[str, Any]]:
        try:
            return self.client.get_ticker(symbol=symbol)
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {str(e)}")
            return None
    
    def get_klines(self, symbol: str, interval: str, limit: int) -> List:
        try:
            return self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
        except Exception as e:
            logger.error(f"Error fetching klines for {symbol} at {interval}: {str(e)}")
            return []
    
    def get_historical_klines(self, symbol: str, interval: str, start_str: str, end_str: str, limit: int) -> List:
        try:
            return self.client.get_historical_klines(
                symbol=symbol,
                interval=interval,
                start_str=start_str,
                end_str=end_str,
                limit=limit
            )
        except Exception as e:
            logger.error(f"Error fetching historical klines: {str(e)}")
            return []
