"""Market data model"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class MarketData(BaseModel):
    """Market data snapshot"""
    symbol: str
    timestamp: datetime = Field(default_factory=datetime.now)
    price: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    volume_24h: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    price_change_24h: Optional[float] = None
    price_change_percent_24h: Optional[float] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
