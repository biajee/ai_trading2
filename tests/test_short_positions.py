"""Unit tests for short position functionality"""
import unittest
import asyncio
from arena import TradingArena
from agents import SimpleAgent
from models import Trade, TradeType, TradeStatus, Position
from config import Config
import os


class TestShortPositions(unittest.TestCase):
    """Test short position functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.arena = TradingArena()
        self.test_agent = SimpleAgent("test_agent_1", "Test Agent 1")

        # Clean up any existing state file
        if os.path.exists("arena_state.json"):
            os.remove("arena_state.json")

    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists("arena_state.json"):
            os.remove("arena_state.json")

    def test_position_is_long(self):
        """Test Position.is_long property"""
        pos = Position(
            agent_id="agent_1",
            symbol="BTC/USDT",
            quantity=0.1,  # Positive
            average_entry_price=50000.0,
            current_price=50000.0
        )
        self.assertTrue(pos.is_long)
        self.assertFalse(pos.is_short)

    def test_position_is_short(self):
        """Test Position.is_short property"""
        pos = Position(
            agent_id="agent_1",
            symbol="BTC/USDT",
            quantity=-0.1,  # Negative
            average_entry_price=50000.0,
            current_price=50000.0
        )
        self.assertFalse(pos.is_long)
        self.assertTrue(pos.is_short)

    def test_short_position_value(self):
        """Test short position value calculation"""
        pos = Position(
            agent_id="agent_1",
            symbol="BTC/USDT",
            quantity=-0.1,
            average_entry_price=50000.0,
            current_price=50000.0
        )
        # Short position value is negative
        self.assertEqual(pos.current_value, -5000.0)

    def test_short_position_pnl_profit(self):
        """Test short position P&L when profitable (price decreased)"""
        pos = Position(
            agent_id="agent_1",
            symbol="BTC/USDT",
            quantity=-0.1,
            average_entry_price=50000.0,
            current_price=49000.0  # Price went down
        )
        pos.update_price(49000.0)

        # Short profits when price goes down
        # P&L = (49000 - 50000) * (-0.1) = -1000 * -0.1 = 100
        self.assertEqual(pos.unrealized_pnl, 100.0)

    def test_short_position_pnl_loss(self):
        """Test short position P&L when losing (price increased)"""
        pos = Position(
            agent_id="agent_1",
            symbol="BTC/USDT",
            quantity=-0.1,
            average_entry_price=50000.0,
            current_price=51000.0  # Price went up
        )
        pos.update_price(51000.0)

        # Short loses when price goes up
        # P&L = (51000 - 50000) * (-0.1) = 1000 * -0.1 = -100
        self.assertEqual(pos.unrealized_pnl, -100.0)

    def test_execute_short_trade(self):
        """Test executing a short trade"""
        async def test():
            self.arena.add_agent(self.test_agent)
            state = self.arena.agent_states["test_agent_1"]

            # Create a short trade
            trade = Trade(
                id="test_short_1",
                agent_id="test_agent_1",
                symbol="BTC/USDT",
                trade_type=TradeType.SHORT,
                quantity=0.1,
                price=50000.0,
                total_value=5000.0,
                reasoning="Test short"
            )

            # Execute trade
            executed = await self.arena.exchange.execute_trade(trade)

            # Manually update state like arena does
            if executed.status == TradeStatus.EXECUTED:
                state.trade_history.append(executed)
                state.total_trades += 1
                state.cash_balance += executed.total_value

                # Create short position (negative quantity)
                from models import Position
                state.positions[executed.symbol] = Position(
                    agent_id="test_agent_1",
                    symbol=executed.symbol,
                    quantity=-executed.quantity,  # Negative for short
                    average_entry_price=executed.price,
                    current_price=executed.price
                )

            # Verify state
            self.assertEqual(state.total_trades, 1)
            self.assertEqual(state.cash_balance, Config.STARTING_CAPITAL + 5000.0)
            self.assertIn("BTC/USDT", state.positions)
            self.assertEqual(state.positions["BTC/USDT"].quantity, -0.1)
            self.assertTrue(state.positions["BTC/USDT"].is_short)

        asyncio.run(test())

    def test_execute_cover_trade_profit(self):
        """Test covering short position at profit"""
        async def test():
            self.arena.add_agent(self.test_agent)
            state = self.arena.agent_states["test_agent_1"]

            # Set up short position
            state.cash_balance = 15000.0  # Started with 10000, shorted at 50000 for 0.1 BTC = +5000
            state.positions["BTC/USDT"] = Position(
                agent_id="test_agent_1",
                symbol="BTC/USDT",
                quantity=-0.1,  # Short 0.1 BTC
                average_entry_price=50000.0,
                current_price=49000.0  # Price went down
            )

            # Set up mock exchange
            self.arena.exchange.holdings["BTC"] = -0.1  # Short position
            self.arena.exchange.balances["USDT"] = 15000.0

            # Cover at profit (price dropped)
            trade = Trade(
                id="test_cover_1",
                agent_id="test_agent_1",
                symbol="BTC/USDT",
                trade_type=TradeType.COVER,
                quantity=0.1,
                price=49000.0,  # Covering at lower price
                total_value=4900.0,
                reasoning="Take profit on short"
            )

            executed = await self.arena.exchange.execute_trade(trade)

            # Manually update state
            if executed.status == TradeStatus.EXECUTED:
                pos = state.positions[executed.symbol]

                # Calculate P&L
                cost_to_cover = executed.total_value
                proceeds_from_short = pos.average_entry_price * executed.quantity
                realized_pnl = proceeds_from_short - cost_to_cover

                if realized_pnl > 0:
                    state.winning_trades += 1

                state.cash_balance -= executed.total_value
                pos.quantity += executed.quantity

                if abs(pos.quantity) < 0.000001:
                    del state.positions[executed.symbol]

            # Verify results
            # Shorted at 50000 for 0.1 BTC = received 5000
            # Covered at 49000 for 0.1 BTC = paid 4900
            # Profit = 5000 - 4900 = 100
            self.assertEqual(state.winning_trades, 1)
            self.assertAlmostEqual(state.cash_balance, 15000.0 - 4900.0, places=2)
            self.assertNotIn("BTC/USDT", state.positions)

        asyncio.run(test())

    def test_execute_cover_trade_loss(self):
        """Test covering short position at loss"""
        async def test():
            self.arena.add_agent(self.test_agent)
            state = self.arena.agent_states["test_agent_1"]

            # Set up short position
            state.cash_balance = 15000.0
            state.positions["BTC/USDT"] = Position(
                agent_id="test_agent_1",
                symbol="BTC/USDT",
                quantity=-0.1,
                average_entry_price=50000.0,
                current_price=51000.0  # Price went up
            )

            # Set up mock exchange
            self.arena.exchange.holdings["BTC"] = -0.1
            self.arena.exchange.balances["USDT"] = 15000.0

            # Cover at loss (price increased)
            trade = Trade(
                id="test_cover_2",
                agent_id="test_agent_1",
                symbol="BTC/USDT",
                trade_type=TradeType.COVER,
                quantity=0.1,
                price=51000.0,
                total_value=5100.0,
                reasoning="Cut losses on short"
            )

            executed = await self.arena.exchange.execute_trade(trade)

            # Manually update state
            if executed.status == TradeStatus.EXECUTED:
                pos = state.positions[executed.symbol]

                cost_to_cover = executed.total_value
                proceeds_from_short = pos.average_entry_price * executed.quantity
                realized_pnl = proceeds_from_short - cost_to_cover

                if realized_pnl < 0:
                    state.losing_trades += 1

                state.cash_balance -= executed.total_value
                pos.quantity += executed.quantity

                if abs(pos.quantity) < 0.000001:
                    del state.positions[executed.symbol]

            # Verify results
            # Shorted at 50000 for 0.1 BTC = received 5000
            # Covered at 51000 for 0.1 BTC = paid 5100
            # Loss = 5000 - 5100 = -100
            self.assertEqual(state.losing_trades, 1)
            self.assertAlmostEqual(state.cash_balance, 15000.0 - 5100.0, places=2)
            self.assertNotIn("BTC/USDT", state.positions)

        asyncio.run(test())

    def test_trade_type_enum(self):
        """Test TradeType enum includes SHORT and COVER"""
        self.assertEqual(TradeType.SHORT.value, "short")
        self.assertEqual(TradeType.COVER.value, "cover")


if __name__ == '__main__':
    unittest.main()
