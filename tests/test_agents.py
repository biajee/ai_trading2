"""Unit tests for agent functionality"""
import unittest
import asyncio
from agents import SimpleAgent
from models import MarketData, Position, TradeType


class TestSimpleAgent(unittest.TestCase):
    """Test SimpleAgent functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.agent = SimpleAgent("test_agent", "Test Agent")
        self.market_data = [
            MarketData(
                symbol="BTC/USDT",
                price=50000.0,
                bid=49950.0,
                ask=50050.0,
                volume_24h=1000000.0,
                high_24h=51000.0,
                low_24h=49000.0,
                price_change_24h=500.0,
                price_change_percent_24h=1.0
            ),
            MarketData(
                symbol="ETH/USDT",
                price=3500.0,
                bid=3495.0,
                ask=3505.0,
                volume_24h=500000.0,
                high_24h=3600.0,
                low_24h=3400.0,
                price_change_24h=100.0,
                price_change_percent_24h=3.0  # Strong positive momentum
            )
        ]

    def test_agent_creation(self):
        """Test creating an agent"""
        self.assertEqual(self.agent.agent_id, "test_agent")
        self.assertEqual(self.agent.agent_name, "Test Agent")
        self.assertEqual(self.agent.trade_counter, 0)

    def test_make_decision_returns_trade_or_none(self):
        """Test that make_decision returns Trade or None"""
        async def test():
            # Run multiple times since agent has randomness
            for _ in range(10):
                decision = await self.agent.make_decision(
                    market_data=self.market_data,
                    current_portfolio_value=10000.0,
                    cash_balance=10000.0,
                    positions={}
                )
                # Should return Trade or None
                self.assertTrue(decision is None or hasattr(decision, 'trade_type'))

        asyncio.run(test())

    def test_buy_decision_uses_ask_price(self):
        """Test that buy decisions use ask price"""
        async def test():
            # Create market data with strong positive momentum
            market = [MarketData(
                symbol="BTC/USDT",
                price=50000.0,
                bid=49950.0,
                ask=50050.0,
                volume_24h=1000000.0,
                high_24h=51000.0,
                low_24h=49000.0,
                price_change_24h=1500.0,
                price_change_percent_24h=5.0  # Strong momentum
            )]

            # Try multiple times to get a buy decision
            for _ in range(50):
                decision = await self.agent.make_decision(
                    market_data=market,
                    current_portfolio_value=10000.0,
                    cash_balance=10000.0,
                    positions={}
                )
                if decision and decision.trade_type == TradeType.BUY:
                    # Should use ask price
                    self.assertEqual(decision.price, 50050.0)
                    break

        asyncio.run(test())

    def test_sell_decision_with_profit(self):
        """Test sell decision with profitable position"""
        async def test():
            # Create a profitable position
            positions = {
                "BTC/USDT": Position(
                    agent_id="test_agent",
                    symbol="BTC/USDT",
                    quantity=0.1,
                    average_entry_price=50000.0,
                    current_price=53000.0  # 6% profit
                )
            }

            market = [MarketData(
                symbol="BTC/USDT",
                price=53000.0,
                bid=52950.0,
                ask=53050.0,
                volume_24h=1000000.0,
                high_24h=54000.0,
                low_24h=52000.0,
                price_change_24h=3000.0,
                price_change_percent_24h=6.0
            )]

            # Try multiple times to get a sell decision
            for _ in range(100):
                decision = await self.agent.make_decision(
                    market_data=market,
                    current_portfolio_value=10000.0,
                    cash_balance=7000.0,
                    positions=positions
                )
                if decision and decision.trade_type == TradeType.SELL:
                    # Should use bid price
                    self.assertEqual(decision.price, 52950.0)
                    self.assertLessEqual(decision.quantity, 0.1)
                    break

        asyncio.run(test())

    def test_sell_decision_with_loss(self):
        """Test sell decision with losing position"""
        async def test():
            # Create a losing position
            positions = {
                "BTC/USDT": Position(
                    agent_id="test_agent",
                    symbol="BTC/USDT",
                    quantity=0.1,
                    average_entry_price=50000.0,
                    current_price=48000.0  # -4% loss
                )
            }

            market = [MarketData(
                symbol="BTC/USDT",
                price=48000.0,
                bid=47950.0,
                ask=48050.0,
                volume_24h=1000000.0,
                high_24h=49000.0,
                low_24h=47000.0,
                price_change_24h=-2000.0,
                price_change_percent_24h=-4.0
            )]

            # Try multiple times to get a sell decision (stop loss)
            for _ in range(100):
                decision = await self.agent.make_decision(
                    market_data=market,
                    current_portfolio_value=10000.0,
                    cash_balance=5000.0,
                    positions=positions
                )
                if decision and decision.trade_type == TradeType.SELL:
                    # Should sell entire position to cut losses
                    self.assertEqual(decision.quantity, 0.1)
                    self.assertEqual(decision.price, 47950.0)
                    break

        asyncio.run(test())

    def test_get_reasoning(self):
        """Test getting reasoning"""
        reasoning = self.agent.get_reasoning()
        self.assertIsInstance(reasoning, str)


if __name__ == '__main__':
    unittest.main()
