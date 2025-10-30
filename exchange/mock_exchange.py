"""Mock exchange for paper trading"""
import asyncio
import random
from datetime import datetime
from typing import Dict, List, Optional
from models import Trade, MarketData, TradeStatus
from .base_exchange import BaseExchange


class MockExchange(BaseExchange):
    """Mock exchange implementation for paper trading"""
    
    def __init__(self):
        self.balances: Dict[str, float] = {"USDT": 0}
        self.holdings: Dict[str, float] = {}
        self.mock_prices: Dict[str, float] = {
            "BTC/USDT": 67000.0,
            "ETH/USDT": 3500.0,
            "SOL/USDT": 170.0,
            "BNB/USDT": 600.0,
        }
        self.trades_executed: List[Trade] = []
        self.use_real_prices = True  # Try to use real Binance prices
        self._real_price_cache = {}
        self._cache_timestamp = 0
    
    async def get_market_data(self, symbol: str) -> MarketData:
        """Get market data - uses real Binance prices if available"""
        import time
        
        # Try to get real prices from Binance
        if self.use_real_prices:
            try:
                current_time = time.time()
                # Cache for 10 seconds
                if current_time - self._cache_timestamp > 10:
                    from market_data_service import get_market_service
                    service = get_market_service()
                    self._real_price_cache = service.get_all_tickers()
                    self._cache_timestamp = current_time
                
                # Convert symbol format: BTC/USDT -> BTC
                symbol_key = symbol.split('/')[0]
                if symbol_key in self._real_price_cache:
                    real_data = self._real_price_cache[symbol_key]
                    # Update our base price
                    self.mock_prices[symbol] = real_data['price']
                    
                    return MarketData(
                        symbol=symbol,
                        price=real_data['price'],
                        bid=real_data['price'] * 0.9995,
                        ask=real_data['price'] * 1.0005,
                        volume_24h=real_data.get('volume', 0),
                        high_24h=real_data.get('high', real_data['price']),
                        low_24h=real_data.get('low', real_data['price']),
                        price_change_24h=real_data.get('change', 0),
                        price_change_percent_24h=real_data.get('change_percent', 0),
                    )
            except Exception as e:
                print(f"⚠️  Could not fetch real prices, using simulated: {e}")
        
        # Fallback to simulated prices
        base_price = self.mock_prices.get(symbol, 100.0)
        current_price = base_price * (1 + random.uniform(-0.02, 0.02))
        self.mock_prices[symbol] = current_price
        
        return MarketData(
            symbol=symbol,
            price=current_price,
            bid=current_price * 0.9995,
            ask=current_price * 1.0005,
            volume_24h=random.uniform(1000000, 5000000),
            high_24h=current_price * 1.05,
            low_24h=current_price * 0.95,
            price_change_24h=random.uniform(-1000, 1000),
            price_change_percent_24h=random.uniform(-5, 5),
        )
    
    async def get_multiple_market_data(self, symbols: List[str]) -> Dict[str, MarketData]:
        """Get market data for multiple symbols"""
        result = {}
        for symbol in symbols:
            result[symbol] = await self.get_market_data(symbol)
        return result
    
    async def execute_trade(self, trade: Trade) -> Trade:
        """
        Simulate trade execution

        Supports four trade types:
        - BUY: Purchase asset (decrease cash, increase holdings)
        - SELL: Sell owned asset (increase cash, decrease holdings)
        - SHORT: Borrow and sell asset (increase cash, create negative holdings)
        - COVER: Buy back to return borrowed asset (decrease cash, reduce negative holdings)
        """
        # Simulate network delay
        await asyncio.sleep(random.uniform(0.1, 0.5))

        # Update trade status
        trade.status = TradeStatus.EXECUTED
        trade.execution_time = datetime.now()
        trade.is_mock = True

        base_currency = trade.symbol.split("/")[0]

        # Update mock balances and holdings
        if trade.trade_type.value == "buy":
            cost = trade.total_value
            if self.balances.get("USDT", 0) >= cost:
                self.balances["USDT"] -= cost
                self.holdings[base_currency] = self.holdings.get(base_currency, 0) + trade.quantity
            else:
                trade.status = TradeStatus.FAILED

        elif trade.trade_type.value == "sell":
            # Need positive holdings to sell
            if self.holdings.get(base_currency, 0) >= trade.quantity:
                self.holdings[base_currency] -= trade.quantity
                self.balances["USDT"] = self.balances.get("USDT", 0) + trade.total_value
            else:
                trade.status = TradeStatus.FAILED

        elif trade.trade_type.value == "short":
            # Short: receive cash, create negative holdings (borrowed position)
            self.balances["USDT"] = self.balances.get("USDT", 0) + trade.total_value
            self.holdings[base_currency] = self.holdings.get(base_currency, 0) - trade.quantity

        elif trade.trade_type.value == "cover":
            # Cover: pay cash to buy back, reduce negative holdings
            cost = trade.total_value
            current_holdings = self.holdings.get(base_currency, 0)

            # Can only cover if we have a short position (negative holdings)
            if current_holdings < 0 and abs(current_holdings) >= trade.quantity:
                if self.balances.get("USDT", 0) >= cost:
                    self.balances["USDT"] -= cost
                    self.holdings[base_currency] += trade.quantity  # Add to negative (reduces short)
                else:
                    trade.status = TradeStatus.FAILED
            else:
                trade.status = TradeStatus.FAILED

        self.trades_executed.append(trade)
        return trade
    
    async def get_balance(self, currency: str = "USDT") -> float:
        """Get simulated balance"""
        return self.balances.get(currency, 0)
    
    async def cancel_trade(self, trade_id: str) -> bool:
        """Cancel a pending trade (always succeeds in mock)"""
        return True
    
    def is_mock(self) -> bool:
        """Check if this is a mock exchange"""
        return True
    
    def set_balance(self, currency: str, amount: float):
        """Set balance (for testing)"""
        self.balances[currency] = amount
