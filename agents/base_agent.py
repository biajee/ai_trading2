"""Base agent interface"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from models import Trade, MarketData, Position


class BaseAgent(ABC):
    """Base agent interface for trading agents"""

    def __init__(self, agent_id: str, agent_name: str):
        self.agent_id = agent_id
        self.agent_name = agent_name

    @abstractmethod
    async def make_decision(
        self,
        market_data: List[MarketData],
        current_portfolio_value: float,
        cash_balance: float,
        positions: Dict[str, Position] = None
    ) -> Optional[Trade]:
        """
        Make a trading decision based on market data

        Args:
            market_data: Current market data for all tracked symbols
            current_portfolio_value: Total portfolio value
            cash_balance: Available cash
            positions: Current open positions (symbol -> Position)

        Returns:
            Trade object if decision is made, None otherwise
        """
        pass
    
    @abstractmethod
    def get_reasoning(self) -> str:
        """Get the reasoning behind the last decision"""
        pass
