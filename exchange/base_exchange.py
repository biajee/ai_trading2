"""Base exchange interface"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from models import Trade, MarketData


class BaseExchange(ABC):
    """Base exchange interface"""
    
    @abstractmethod
    async def get_market_data(self, symbol: str) -> MarketData:
        """Get current market data for a symbol"""
        pass
    
    @abstractmethod
    async def get_multiple_market_data(self, symbols: List[str]) -> Dict[str, MarketData]:
        """Get market data for multiple symbols"""
        pass
    
    @abstractmethod
    async def execute_trade(self, trade: Trade) -> Trade:
        """Execute a trade"""
        pass
    
    @abstractmethod
    async def get_balance(self, currency: str = "USDT") -> float:
        """Get account balance"""
        pass
    
    @abstractmethod
    async def cancel_trade(self, trade_id: str) -> bool:
        """Cancel a pending trade"""
        pass
    
    @abstractmethod
    def is_mock(self) -> bool:
        """Check if this is a mock exchange"""
        pass
