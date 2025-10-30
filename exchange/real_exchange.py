"""Real exchange integration using CCXT"""
import ccxt
from typing import Dict, List
from models import Trade, MarketData, TradeStatus, TradeType
from .base_exchange import BaseExchange
from config import Config


class RealExchange(BaseExchange):
    """Real exchange implementation using CCXT"""
    
    def __init__(self):
        # Initialize exchange connection
        exchange_class = getattr(ccxt, Config.EXCHANGE_NAME)
        self.exchange = exchange_class({
            'apiKey': Config.EXCHANGE_API_KEY,
            'secret': Config.EXCHANGE_API_SECRET,
            'enableRateLimit': True,
        })
    
    async def get_market_data(self, symbol: str) -> MarketData:
        """Get real market data"""
        ticker = await self.exchange.fetch_ticker(symbol)
        
        return MarketData(
            symbol=symbol,
            price=ticker['last'],
            bid=ticker.get('bid'),
            ask=ticker.get('ask'),
            volume_24h=ticker.get('quoteVolume'),
            high_24h=ticker.get('high'),
            low_24h=ticker.get('low'),
            price_change_24h=ticker.get('change'),
            price_change_percent_24h=ticker.get('percentage'),
        )
    
    async def get_multiple_market_data(self, symbols: List[str]) -> Dict[str, MarketData]:
        """Get market data for multiple symbols"""
        result = {}
        for symbol in symbols:
            try:
                result[symbol] = await self.get_market_data(symbol)
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
        return result
    
    async def execute_trade(self, trade: Trade) -> Trade:
        """Execute real trade on exchange"""
        try:
            order_type = 'market'
            side = 'buy' if trade.trade_type == TradeType.BUY else 'sell'
            
            order = await self.exchange.create_order(
                symbol=trade.symbol,
                type=order_type,
                side=side,
                amount=trade.quantity,
            )
            
            trade.status = TradeStatus.EXECUTED
            trade.execution_time = order.get('timestamp')
            trade.is_mock = False
            
        except Exception as e:
            print(f"Trade execution failed: {e}")
            trade.status = TradeStatus.FAILED
        
        return trade
    
    async def get_balance(self, currency: str = "USDT") -> float:
        """Get real account balance"""
        balance = await self.exchange.fetch_balance()
        return balance.get(currency, {}).get('free', 0)
    
    async def cancel_trade(self, trade_id: str) -> bool:
        """Cancel a pending trade"""
        try:
            await self.exchange.cancel_order(trade_id)
            return True
        except Exception as e:
            print(f"Cancel failed: {e}")
            return False
    
    def is_mock(self) -> bool:
        """Check if this is a mock exchange"""
        return False
