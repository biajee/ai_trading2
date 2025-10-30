"""Unit tests for trading arena"""
import unittest
import asyncio
import json
import os
from arena import TradingArena
from agents import SimpleAgent
from models import Trade, TradeType, TradeStatus, Position
from config import Config


class TestTradingArena(unittest.TestCase):
    """Test TradingArena functionality"""

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

    def test_arena_creation(self):
        """Test creating arena"""
        self.assertIsNotNone(self.arena.exchange)
        self.assertEqual(len(self.arena.agents), 0)
        self.assertEqual(len(self.arena.agent_states), 0)
        self.assertFalse(self.arena.is_running)

    def test_add_agent(self):
        """Test adding agent to arena"""
        self.arena.add_agent(self.test_agent)

        self.assertEqual(len(self.arena.agents), 1)
        self.assertIn("test_agent_1", self.arena.agents)
        self.assertIn("test_agent_1", self.arena.agent_states)

        state = self.arena.agent_states["test_agent_1"]
        self.assertEqual(state.agent_id, "test_agent_1")
        self.assertEqual(state.agent_name, "Test Agent 1")
        self.assertEqual(state.starting_capital, Config.STARTING_CAPITAL)
        self.assertEqual(state.cash_balance, Config.STARTING_CAPITAL)

    def test_add_multiple_agents(self):
        """Test adding multiple agents"""
        agent1 = SimpleAgent("agent_1", "Agent 1")
        agent2 = SimpleAgent("agent_2", "Agent 2")

        self.arena.add_agent(agent1)
        self.arena.add_agent(agent2)

        self.assertEqual(len(self.arena.agents), 2)
        self.assertEqual(len(self.arena.agent_states), 2)

    def test_update_market_data(self):
        """Test updating market data"""
        async def test():
            self.arena.add_agent(self.test_agent)
            market_data = await self.arena.update_market_data()

            self.assertIsNotNone(market_data)
            self.assertGreater(len(market_data), 0)

            # Should create state file
            self.assertTrue(os.path.exists("arena_state.json"))

        asyncio.run(test())

    def test_execute_buy_trade(self):
        """Test executing a buy trade updates agent state correctly"""
        async def test():
            self.arena.add_agent(self.test_agent)
            state = self.arena.agent_states["test_agent_1"]

            # Create market data
            market_data = await self.arena.update_market_data()

            # Create a buy trade
            trade = Trade(
                id="test_trade_1",
                agent_id="test_agent_1",
                symbol="BTC/USDT",
                trade_type=TradeType.BUY,
                quantity=0.1,
                price=50000.0,
                total_value=5000.0,
                reasoning="Test buy"
            )

            # Execute trade
            executed = await self.arena.exchange.execute_trade(trade)

            # Manually update state like arena does
            if executed.status == TradeStatus.EXECUTED:
                state.trade_history.append(executed)
                state.total_trades += 1
                state.cash_balance -= executed.total_value

                # Add position
                state.positions[executed.symbol] = Position(
                    agent_id="test_agent_1",
                    symbol=executed.symbol,
                    quantity=executed.quantity,
                    average_entry_price=executed.price,
                    current_price=executed.price
                )

            # Verify state
            self.assertEqual(state.total_trades, 1)
            self.assertEqual(state.cash_balance, Config.STARTING_CAPITAL - 5000.0)
            self.assertIn("BTC/USDT", state.positions)
            self.assertEqual(state.positions["BTC/USDT"].quantity, 0.1)

        asyncio.run(test())

    def test_execute_sell_trade(self):
        """Test executing a sell trade updates agent state correctly"""
        async def test():
            self.arena.add_agent(self.test_agent)
            state = self.arena.agent_states["test_agent_1"]

            # Set up initial position
            state.cash_balance = 5000.0
            state.positions["BTC/USDT"] = Position(
                agent_id="test_agent_1",
                symbol="BTC/USDT",
                quantity=0.1,
                average_entry_price=50000.0,
                current_price=51000.0
            )

            # Set up mock exchange holdings to match
            self.arena.exchange.holdings["BTC"] = 0.1
            self.arena.exchange.balances["USDT"] = 5000.0

            # Create a sell trade at profit
            trade = Trade(
                id="test_trade_2",
                agent_id="test_agent_1",
                symbol="BTC/USDT",
                trade_type=TradeType.SELL,
                quantity=0.05,
                price=51000.0,
                total_value=2550.0,
                reasoning="Take profit"
            )

            # Execute trade
            executed = await self.arena.exchange.execute_trade(trade)

            # Manually update state like arena does
            if executed.status == TradeStatus.EXECUTED:
                state.trade_history.append(executed)
                state.total_trades += 1

                pos = state.positions[executed.symbol]

                # Calculate P&L
                cost_basis = pos.average_entry_price * executed.quantity
                sale_proceeds = executed.total_value
                realized_pnl = sale_proceeds - cost_basis

                if realized_pnl > 0:
                    state.winning_trades += 1
                elif realized_pnl < 0:
                    state.losing_trades += 1

                state.cash_balance += executed.total_value
                pos.quantity -= executed.quantity

            # Verify state
            self.assertEqual(state.total_trades, 1)
            self.assertEqual(state.winning_trades, 1)
            self.assertEqual(state.cash_balance, 5000.0 + 2550.0)
            self.assertAlmostEqual(state.positions["BTC/USDT"].quantity, 0.05, places=6)

        asyncio.run(test())

    def test_execute_sell_removes_position_when_empty(self):
        """Test that selling entire position removes it"""
        async def test():
            self.arena.add_agent(self.test_agent)
            state = self.arena.agent_states["test_agent_1"]

            # Set up initial position
            state.cash_balance = 5000.0
            state.positions["BTC/USDT"] = Position(
                agent_id="test_agent_1",
                symbol="BTC/USDT",
                quantity=0.1,
                average_entry_price=50000.0,
                current_price=51000.0
            )

            # Set up mock exchange holdings to match
            self.arena.exchange.holdings["BTC"] = 0.1
            self.arena.exchange.balances["USDT"] = 5000.0

            # Sell entire position
            trade = Trade(
                id="test_trade_3",
                agent_id="test_agent_1",
                symbol="BTC/USDT",
                trade_type=TradeType.SELL,
                quantity=0.1,
                price=51000.0,
                total_value=5100.0,
                reasoning="Close position"
            )

            executed = await self.arena.exchange.execute_trade(trade)

            # Manually update state
            if executed.status == TradeStatus.EXECUTED:
                pos = state.positions[executed.symbol]
                state.cash_balance += executed.total_value
                pos.quantity -= executed.quantity

                # Remove position if quantity is zero
                if pos.quantity < 0.000001:
                    del state.positions[executed.symbol]

            # Verify position was removed
            self.assertNotIn("BTC/USDT", state.positions)
            self.assertEqual(state.cash_balance, 10100.0)

        asyncio.run(test())

    def test_save_state(self):
        """Test saving arena state to file"""
        self.arena.add_agent(self.test_agent)
        state = self.arena.agent_states["test_agent_1"]

        # Add some data
        state.cash_balance = 9500.0
        state.total_trades = 5
        state.winning_trades = 3
        state.losing_trades = 2

        # Save state
        self.arena.save_state()

        # Verify file exists
        self.assertTrue(os.path.exists("arena_state.json"))

        # Read and verify content
        with open("arena_state.json", 'r') as f:
            data = json.load(f)

        self.assertIn("timestamp", data)
        self.assertIn("agents", data)
        self.assertEqual(len(data["agents"]), 1)

        agent_data = data["agents"][0]
        self.assertEqual(agent_data["agent_id"], "test_agent_1")
        self.assertEqual(agent_data["agent_name"], "Test Agent 1")
        self.assertEqual(agent_data["cash_balance"], 9500.0)
        self.assertEqual(agent_data["total_trades"], 5)

    def test_portfolio_value_calculation(self):
        """Test portfolio value calculation with positions"""
        self.arena.add_agent(self.test_agent)
        state = self.arena.agent_states["test_agent_1"]

        # Set up state with cash and position
        state.cash_balance = 5000.0
        state.positions["BTC/USDT"] = Position(
            agent_id="test_agent_1",
            symbol="BTC/USDT",
            quantity=0.1,
            average_entry_price=50000.0,
            current_price=52000.0
        )

        # Portfolio value = cash + position value
        # = 5000 + (0.1 * 52000) = 10200
        self.assertEqual(state.total_portfolio_value, 10200.0)

    def test_total_return_calculation(self):
        """Test total return percentage calculation"""
        self.arena.add_agent(self.test_agent)
        state = self.arena.agent_states["test_agent_1"]

        # Portfolio grew from 10000 to 11000
        state.cash_balance = 11000.0

        # Should be 10% return
        self.assertEqual(state.total_return, 10.0)

    def test_win_rate_calculation(self):
        """Test win rate calculation"""
        self.arena.add_agent(self.test_agent)
        state = self.arena.agent_states["test_agent_1"]

        state.total_trades = 10
        state.winning_trades = 7
        state.losing_trades = 3

        # Should be 70% win rate
        self.assertEqual(state.win_rate, 70.0)

    def test_stop_arena(self):
        """Test stopping arena"""
        self.arena.is_running = True
        self.arena.stop()
        self.assertFalse(self.arena.is_running)


if __name__ == '__main__':
    unittest.main()
