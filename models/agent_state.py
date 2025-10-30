"""Agent state model"""
from datetime import datetime
from typing import Dict, List
from pydantic import BaseModel, Field
from .position import Position
from .trade import Trade


class AgentState(BaseModel):
    """Agent state tracking"""
    agent_id: str
    agent_name: str
    starting_capital: float
    cash_balance: float
    positions: Dict[str, Position] = Field(default_factory=dict)
    trade_history: List[Trade] = Field(default_factory=list)
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    
    @property
    def total_portfolio_value(self) -> float:
        """Calculate total portfolio value (cash + positions)"""
        positions_value = sum(pos.current_value for pos in self.positions.values())
        return self.cash_balance + positions_value
    
    @property
    def total_return(self) -> float:
        """Calculate total return percentage"""
        if self.starting_capital == 0:
            return 0.0
        return ((self.total_portfolio_value - self.starting_capital) / self.starting_capital) * 100
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage"""
        if self.total_trades == 0:
            return 0.0
        return (self.winning_trades / self.total_trades) * 100
    
    @property
    def total_pnl(self) -> float:
        """Calculate total profit/loss"""
        return self.total_portfolio_value - self.starting_capital
    
    def update_portfolio_value(self, market_prices: Dict[str, float]):
        """Update all position prices"""
        for symbol, position in self.positions.items():
            if symbol in market_prices:
                position.update_price(market_prices[symbol])
        self.last_updated = datetime.now()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
