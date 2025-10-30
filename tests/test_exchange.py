"""Unit tests for exchange functionality"""
import unittest
import asyncio
from datetime import datetime
from exchange import MockExchange
from models import Trade, TradeType, TradeStatus


class TestMockExchange(unittest.TestCase):
    """Test MockExchange functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.exchange = MockExchange()
        self.exchange.set_balance("USDT", 10000.0)

    def test_is_mock(self):
        """Test is_mock returns True"""
        self.assertTrue(self.exchange.is_mock())

    def test_get_balance(self):
        """Test getting balance"""
        async def test():
            balance = await self.exchange.get_balance("USDT")
            self.assertEqual(balance, 10000.0)

        asyncio.run(test())

    def test_get_market_data(self):
        """Test getting market data"""
        async def test():
            data = await self.exchange.get_market_data("BTC/USDT")
            self.assertIsNotNone(data)
            self.assertEqual(data.symbol, "BTC/USDT")
            self.assertGreater(data.price, 0)
            self.assertGreater(data.bid, 0)
            self.assertGreater(data.ask, 0)

        asyncio.run(test())

    def test_execute_buy_trade_success(self):
        """Test executing a successful buy trade"""
        async def test():
            trade = Trade(
                id="test_1",
                agent_id="agent_1",
                symbol="BTC/USDT",
                trade_type=TradeType.BUY,
                quantity=0.1,
                price=50000.0,
                total_value=5000.0,
                reasoning="Test buy"
            )

            executed = await self.exchange.execute_trade(trade)

            self.assertEqual(executed.status, TradeStatus.EXECUTED)
            self.assertIsNotNone(executed.execution_time)
            self.assertTrue(executed.is_mock)

            # Check balance was deducted
            balance = await self.exchange.get_balance("USDT")
            self.assertEqual(balance, 5000.0)

            # Check holdings were updated
            self.assertEqual(self.exchange.holdings.get("BTC", 0), 0.1)

        asyncio.run(test())

    def test_execute_buy_insufficient_funds(self):
        """Test executing buy with insufficient funds"""
        async def test():
            trade = Trade(
                id="test_2",
                agent_id="agent_1",
                symbol="BTC/USDT",
                trade_type=TradeType.BUY,
                quantity=1.0,
                price=50000.0,
                total_value=50000.0,  # More than available balance
                reasoning="Test buy fail"
            )

            executed = await self.exchange.execute_trade(trade)

            self.assertEqual(executed.status, TradeStatus.FAILED)

        asyncio.run(test())

    def test_execute_sell_trade_success(self):
        """Test executing a successful sell trade"""
        async def test():
            # First buy some BTC
            self.exchange.holdings["BTC"] = 0.1
            self.exchange.balances["USDT"] = 5000.0

            # Now sell it
            trade = Trade(
                id="test_3",
                agent_id="agent_1",
                symbol="BTC/USDT",
                trade_type=TradeType.SELL,
                quantity=0.05,
                price=51000.0,
                total_value=2550.0,
                reasoning="Test sell"
            )

            executed = await self.exchange.execute_trade(trade)

            self.assertEqual(executed.status, TradeStatus.EXECUTED)

            # Check balance was increased
            balance = await self.exchange.get_balance("USDT")
            self.assertEqual(balance, 7550.0)

            # Check holdings were decreased
            self.assertAlmostEqual(self.exchange.holdings.get("BTC", 0), 0.05, places=6)

        asyncio.run(test())

    def test_execute_sell_insufficient_holdings(self):
        """Test executing sell with insufficient holdings"""
        async def test():
            trade = Trade(
                id="test_4",
                agent_id="agent_1",
                symbol="BTC/USDT",
                trade_type=TradeType.SELL,
                quantity=0.1,
                price=50000.0,
                total_value=5000.0,
                reasoning="Test sell fail"
            )

            executed = await self.exchange.execute_trade(trade)

            self.assertEqual(executed.status, TradeStatus.FAILED)

        asyncio.run(test())

    def test_get_multiple_market_data(self):
        """Test getting multiple market data"""
        async def test():
            symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
            data = await self.exchange.get_multiple_market_data(symbols)

            self.assertEqual(len(data), 3)
            self.assertIn("BTC/USDT", data)
            self.assertIn("ETH/USDT", data)
            self.assertIn("SOL/USDT", data)

        asyncio.run(test())

    def test_cancel_trade(self):
        """Test canceling a trade"""
        async def test():
            result = await self.exchange.cancel_trade("test_trade_id")
            self.assertTrue(result)

        asyncio.run(test())


if __name__ == '__main__':
    unittest.main()
