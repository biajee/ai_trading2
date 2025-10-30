"""Unit tests for data models"""
import unittest
from datetime import datetime
from models import Trade, TradeType, TradeStatus, Position, AgentState, MarketData


class TestTrade(unittest.TestCase):
    """Test Trade model"""

    def test_trade_creation(self):
        """Test creating a trade"""
        trade = Trade(
            id="test_1",
            agent_id="agent_1",
            symbol="BTC/USDT",
            trade_type=TradeType.BUY,
            quantity=0.1,
            price=50000.0,
            total_value=5000.0,
            reasoning="Test trade"
        )

        self.assertEqual(trade.id, "test_1")
        self.assertEqual(trade.agent_id, "agent_1")
        self.assertEqual(trade.symbol, "BTC/USDT")
        self.assertEqual(trade.trade_type, TradeType.BUY)
        self.assertEqual(trade.quantity, 0.1)
        self.assertEqual(trade.price, 50000.0)
        self.assertEqual(trade.total_value, 5000.0)
        self.assertEqual(trade.status, TradeStatus.PENDING)
        self.assertTrue(trade.is_mock)

    def test_sell_trade(self):
        """Test creating a sell trade"""
        trade = Trade(
            id="test_2",
            agent_id="agent_1",
            symbol="BTC/USDT",
            trade_type=TradeType.SELL,
            quantity=0.05,
            price=51000.0,
            total_value=2550.0,
            reasoning="Take profit"
        )

        self.assertEqual(trade.trade_type, TradeType.SELL)


class TestPosition(unittest.TestCase):
    """Test Position model"""

    def test_position_creation(self):
        """Test creating a position"""
        pos = Position(
            agent_id="agent_1",
            symbol="BTC/USDT",
            quantity=0.1,
            average_entry_price=50000.0,
            current_price=50000.0
        )

        self.assertEqual(pos.agent_id, "agent_1")
        self.assertEqual(pos.symbol, "BTC/USDT")
        self.assertEqual(pos.quantity, 0.1)
        self.assertEqual(pos.average_entry_price, 50000.0)
        self.assertEqual(pos.current_price, 50000.0)

    def test_position_value(self):
        """Test position value calculation"""
        pos = Position(
            agent_id="agent_1",
            symbol="BTC/USDT",
            quantity=0.1,
            average_entry_price=50000.0,
            current_price=51000.0
        )

        expected_value = 0.1 * 51000.0
        self.assertEqual(pos.current_value, expected_value)

    def test_position_pnl(self):
        """Test position P&L calculation"""
        pos = Position(
            agent_id="agent_1",
            symbol="BTC/USDT",
            quantity=0.1,
            average_entry_price=50000.0,
            current_price=51000.0
        )

        # Update price to calculate P&L
        pos.update_price(51000.0)

        # Unrealized P&L = (51000 - 50000) * 0.1 = 100
        self.assertEqual(pos.unrealized_pnl, 100.0)

    def test_position_negative_pnl(self):
        """Test position with negative P&L"""
        pos = Position(
            agent_id="agent_1",
            symbol="BTC/USDT",
            quantity=0.1,
            average_entry_price=50000.0,
            current_price=49000.0
        )

        # Update price to calculate P&L
        pos.update_price(49000.0)

        # Unrealized P&L = (49000 - 50000) * 0.1 = -100
        self.assertEqual(pos.unrealized_pnl, -100.0)

    def test_update_price(self):
        """Test updating position price"""
        pos = Position(
            agent_id="agent_1",
            symbol="BTC/USDT",
            quantity=0.1,
            average_entry_price=50000.0,
            current_price=50000.0
        )

        pos.update_price(52000.0)
        self.assertEqual(pos.current_price, 52000.0)
        self.assertEqual(pos.unrealized_pnl, 200.0)


class TestAgentState(unittest.TestCase):
    """Test AgentState model"""

    def test_agent_state_creation(self):
        """Test creating agent state"""
        state = AgentState(
            agent_id="agent_1",
            agent_name="Test Agent",
            starting_capital=10000.0,
            cash_balance=10000.0
        )

        self.assertEqual(state.agent_id, "agent_1")
        self.assertEqual(state.agent_name, "Test Agent")
        self.assertEqual(state.starting_capital, 10000.0)
        self.assertEqual(state.cash_balance, 10000.0)
        self.assertEqual(state.total_trades, 0)

    def test_portfolio_value_cash_only(self):
        """Test portfolio value with only cash"""
        state = AgentState(
            agent_id="agent_1",
            agent_name="Test Agent",
            starting_capital=10000.0,
            cash_balance=10000.0
        )

        self.assertEqual(state.total_portfolio_value, 10000.0)

    def test_portfolio_value_with_positions(self):
        """Test portfolio value with positions"""
        state = AgentState(
            agent_id="agent_1",
            agent_name="Test Agent",
            starting_capital=10000.0,
            cash_balance=5000.0
        )

        # Add position worth 5000
        state.positions["BTC/USDT"] = Position(
            agent_id="agent_1",
            symbol="BTC/USDT",
            quantity=0.1,
            average_entry_price=50000.0,
            current_price=50000.0
        )

        self.assertEqual(state.total_portfolio_value, 10000.0)

    def test_total_return(self):
        """Test total return calculation"""
        state = AgentState(
            agent_id="agent_1",
            agent_name="Test Agent",
            starting_capital=10000.0,
            cash_balance=11000.0
        )

        # 10% return
        self.assertEqual(state.total_return, 10.0)

    def test_win_rate(self):
        """Test win rate calculation"""
        state = AgentState(
            agent_id="agent_1",
            agent_name="Test Agent",
            starting_capital=10000.0,
            cash_balance=10000.0
        )

        state.total_trades = 10
        state.winning_trades = 6
        state.losing_trades = 4

        self.assertEqual(state.win_rate, 60.0)

    def test_win_rate_zero_trades(self):
        """Test win rate with zero trades"""
        state = AgentState(
            agent_id="agent_1",
            agent_name="Test Agent",
            starting_capital=10000.0,
            cash_balance=10000.0
        )

        self.assertEqual(state.win_rate, 0.0)


class TestMarketData(unittest.TestCase):
    """Test MarketData model"""

    def test_market_data_creation(self):
        """Test creating market data"""
        data = MarketData(
            symbol="BTC/USDT",
            price=50000.0,
            bid=49950.0,
            ask=50050.0,
            volume_24h=1000000.0,
            high_24h=51000.0,
            low_24h=49000.0,
            price_change_24h=500.0,
            price_change_percent_24h=1.0
        )

        self.assertEqual(data.symbol, "BTC/USDT")
        self.assertEqual(data.price, 50000.0)
        self.assertEqual(data.bid, 49950.0)
        self.assertEqual(data.ask, 50050.0)
        self.assertEqual(data.volume_24h, 1000000.0)


if __name__ == '__main__':
    unittest.main()
