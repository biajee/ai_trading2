"""Unit tests for dashboard functionality"""
import unittest
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config


class TestDashboard(unittest.TestCase):
    """Test Dashboard functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Clean up any existing state file
        if os.path.exists("arena_state.json"):
            os.remove("arena_state.json")

    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists("arena_state.json"):
            os.remove("arena_state.json")

    def test_load_agent_data_no_file(self):
        """Test loading agent data when file doesn't exist"""
        # Import here to avoid circular imports
        from dashboard import load_agent_data

        agents = load_agent_data()

        # Should return placeholder data
        self.assertEqual(len(agents), 1)
        self.assertEqual(agents[0]["name"], "No Active Arena")
        self.assertEqual(agents[0]["value"], Config.STARTING_CAPITAL)
        self.assertEqual(agents[0]["return"], 0.0)
        self.assertEqual(agents[0]["trades"], 0)

    def test_load_agent_data_with_file(self):
        """Test loading agent data from file"""
        # Create a test state file
        test_data = {
            "timestamp": "2025-01-01T00:00:00",
            "agents": [
                {
                    "agent_id": "agent_1",
                    "agent_name": "Test Agent 1",
                    "portfolio_value": 11000.0,
                    "cash_balance": 6000.0,
                    "total_return": 10.0,
                    "total_trades": 5,
                    "win_rate": 60.0,
                    "positions": {
                        "BTC/USDT": {
                            "quantity": 0.1,
                            "avg_price": 50000.0,
                            "current_price": 50000.0,
                            "value": 5000.0,
                            "pnl": 0.0
                        }
                    },
                    "recent_trades": [
                        {
                            "symbol": "BTC/USDT",
                            "type": "buy",
                            "quantity": 0.1,
                            "price": 50000.0,
                            "timestamp": "2025-01-01T00:00:00",
                            "reasoning": "Test trade"
                        }
                    ]
                },
                {
                    "agent_id": "agent_2",
                    "agent_name": "Test Agent 2",
                    "portfolio_value": 9500.0,
                    "cash_balance": 9500.0,
                    "total_return": -5.0,
                    "total_trades": 3,
                    "win_rate": 33.3,
                    "positions": {},
                    "recent_trades": []
                }
            ]
        }

        with open("arena_state.json", 'w') as f:
            json.dump(test_data, f)

        # Import and load data
        from dashboard import load_agent_data
        agents = load_agent_data()

        # Verify data loaded correctly
        self.assertEqual(len(agents), 2)

        # Check first agent
        self.assertEqual(agents[0]["name"], "Test Agent 1")
        self.assertEqual(agents[0]["value"], 11000.0)
        self.assertEqual(agents[0]["return"], 10.0)
        self.assertEqual(agents[0]["trades"], 5)
        self.assertEqual(agents[0]["win_rate"], 60.0)
        self.assertIn("BTC/USDT", agents[0]["positions"])

        # Check second agent
        self.assertEqual(agents[1]["name"], "Test Agent 2")
        self.assertEqual(agents[1]["value"], 9500.0)
        self.assertEqual(agents[1]["return"], -5.0)

    def test_load_agent_data_empty_agents(self):
        """Test loading when file has empty agents list"""
        test_data = {
            "timestamp": "2025-01-01T00:00:00",
            "agents": []
        }

        with open("arena_state.json", 'w') as f:
            json.dump(test_data, f)

        from dashboard import load_agent_data
        agents = load_agent_data()

        # Should return placeholder
        self.assertEqual(len(agents), 1)
        self.assertEqual(agents[0]["name"], "No Active Agents")

    def test_load_agent_data_malformed_json(self):
        """Test loading with malformed JSON"""
        with open("arena_state.json", 'w') as f:
            f.write("invalid json {{{")

        from dashboard import load_agent_data
        agents = load_agent_data()

        # Should return error data
        self.assertEqual(len(agents), 1)
        self.assertEqual(agents[0]["name"], "Error Loading Data")


if __name__ == '__main__':
    unittest.main()
