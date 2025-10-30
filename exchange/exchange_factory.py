"""Exchange factory to create appropriate exchange instance"""
from .base_exchange import BaseExchange
from .mock_exchange import MockExchange
from .real_exchange import RealExchange
from config import Config


class ExchangeFactory:
    """Factory to create exchange instances"""
    
    @staticmethod
    def create_exchange() -> BaseExchange:
        """Create exchange based on configuration"""
        if Config.MOCK_TRADING:
            print(f"🎮 Using MOCK EXCHANGE (Paper Trading)")
            return MockExchange()
        else:
            print(f"⚠️  Using REAL EXCHANGE - Real money at risk! ⚠️")
            return RealExchange()
