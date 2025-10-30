"""Position model"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Position(BaseModel):
    """
    Position model representing holdings

    Quantity can be positive (long) or negative (short):
    - Positive quantity: Long position (owns the asset)
    - Negative quantity: Short position (borrowed and sold the asset)
    """
    agent_id: str
    symbol: str
    quantity: float  # Positive = long, Negative = short
    average_entry_price: float
    current_price: float
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    last_updated: datetime = Field(default_factory=datetime.now)

    @property
    def is_long(self) -> bool:
        """Check if this is a long position"""
        return self.quantity > 0

    @property
    def is_short(self) -> bool:
        """Check if this is a short position"""
        return self.quantity < 0

    @property
    def current_value(self) -> float:
        """
        Calculate current position value
        For longs: positive value (asset worth)
        For shorts: negative value (liability)
        """
        return self.quantity * self.current_price

    @property
    def cost_basis(self) -> float:
        """Calculate original cost/proceeds"""
        return self.quantity * self.average_entry_price

    def update_price(self, new_price: float):
        """
        Update current price and unrealized PnL

        P&L calculation works for both long and short:
        - Long (positive qty): profit when price goes up
        - Short (negative qty): profit when price goes down
        """
        self.current_price = new_price
        self.unrealized_pnl = (new_price - self.average_entry_price) * self.quantity
        self.last_updated = datetime.now()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
