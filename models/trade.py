"""Trade model"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class TradeType(str, Enum):
    """Trade type enumeration"""
    BUY = "buy"
    SELL = "sell"
    SHORT = "short"  # Open short position (borrow and sell)
    COVER = "cover"  # Close short position (buy back)


class TradeStatus(str, Enum):
    """Trade status enumeration"""
    PENDING = "pending"
    EXECUTED = "executed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class Trade(BaseModel):
    """Trade model"""
    id: str
    agent_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    symbol: str
    trade_type: TradeType
    quantity: float
    price: float
    total_value: float
    status: TradeStatus = TradeStatus.PENDING
    reasoning: Optional[str] = None
    execution_time: Optional[datetime] = None
    is_mock: bool = True
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
