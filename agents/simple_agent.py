"""Simple trading agent with basic strategy"""
import random
from typing import List, Optional, Dict
from datetime import datetime
from models import Trade, MarketData, TradeType, Position
from .base_agent import BaseAgent


class SimpleAgent(BaseAgent):
    """Simple agent with momentum-based strategy"""

    def __init__(self, agent_id: str, agent_name: str):
        super().__init__(agent_id, agent_name)
        self.last_reasoning = ""
        self.trade_counter = 0

    async def make_decision(
        self,
        market_data: List[MarketData],
        current_portfolio_value: float,
        cash_balance: float,
        positions: Dict[str, Position] = None
    ) -> Optional[Trade]:
        """
        Make trading decision based on simple momentum strategy
        """
        if positions is None:
            positions = {}

        # Don't trade every time
        if random.random() > 0.3:  # 30% chance to trade
            self.last_reasoning = "No strong signal detected, holding position"
            return None

        # Select random market data
        if not market_data:
            return None

        selected = random.choice(market_data)

        # Check if we have a position in this asset
        has_position = selected.symbol in positions

        # Handle existing positions (long or short)
        if has_position and random.random() > 0.5:  # 50% chance to consider closing when we have position
            pos = positions[selected.symbol]

            # Handle LONG positions
            if pos.is_long:
                current_price = selected.bid  # Use bid price for selling
                pnl_percent = ((current_price - pos.average_entry_price) / pos.average_entry_price) * 100

                # Sell if profit > 5% or loss > -3%
                if pnl_percent > 5:
                    # Take profit
                    execution_price = selected.bid
                    quantity = pos.quantity * random.uniform(0.5, 1.0)  # Sell 50-100% of position

                    self.last_reasoning = (
                        f"Taking profit: {pnl_percent:.2f}% gain. "
                        f"Selling {quantity:.6f} {selected.symbol} at ${execution_price:.2f} (bid)"
                    )

                    self.trade_counter += 1
                    return Trade(
                        id=f"{self.agent_id}_{self.trade_counter}_{int(datetime.now().timestamp())}",
                        agent_id=self.agent_id,
                        symbol=selected.symbol,
                        trade_type=TradeType.SELL,
                        quantity=quantity,
                        price=execution_price,
                        total_value=quantity * execution_price,
                        reasoning=self.last_reasoning,
                    )

                elif pnl_percent < -3:
                    # Cut losses
                    execution_price = selected.bid
                    quantity = pos.quantity  # Sell entire position

                    self.last_reasoning = (
                        f"Cutting losses: {pnl_percent:.2f}% loss. "
                        f"Selling {quantity:.6f} {selected.symbol} at ${execution_price:.2f} (bid)"
                    )

                    self.trade_counter += 1
                    return Trade(
                        id=f"{self.agent_id}_{self.trade_counter}_{int(datetime.now().timestamp())}",
                        agent_id=self.agent_id,
                        symbol=selected.symbol,
                        trade_type=TradeType.SELL,
                        quantity=quantity,
                        price=execution_price,
                        total_value=quantity * execution_price,
                        reasoning=self.last_reasoning,
                    )

            # Handle SHORT positions
            elif pos.is_short:
                current_price = selected.ask  # Use ask price for covering (buying back)
                # For shorts, profit when price goes down
                pnl_percent = ((pos.average_entry_price - current_price) / pos.average_entry_price) * 100

                # Cover if profit > 5% or loss > -3%
                if pnl_percent > 5:
                    # Take profit on short
                    execution_price = selected.ask
                    quantity = abs(pos.quantity) * random.uniform(0.5, 1.0)  # Cover 50-100%

                    self.last_reasoning = (
                        f"Taking profit on short: {pnl_percent:.2f}% gain. "
                        f"Covering {quantity:.6f} {selected.symbol} at ${execution_price:.2f} (ask)"
                    )

                    self.trade_counter += 1
                    return Trade(
                        id=f"{self.agent_id}_{self.trade_counter}_{int(datetime.now().timestamp())}",
                        agent_id=self.agent_id,
                        symbol=selected.symbol,
                        trade_type=TradeType.COVER,
                        quantity=quantity,
                        price=execution_price,
                        total_value=quantity * execution_price,
                        reasoning=self.last_reasoning,
                    )

                elif pnl_percent < -3:
                    # Cut losses on short (price went up)
                    execution_price = selected.ask
                    quantity = abs(pos.quantity)  # Cover entire short position

                    self.last_reasoning = (
                        f"Cutting losses on short: {pnl_percent:.2f}% loss. "
                        f"Covering {quantity:.6f} {selected.symbol} at ${execution_price:.2f} (ask)"
                    )

                    self.trade_counter += 1
                    return Trade(
                        id=f"{self.agent_id}_{self.trade_counter}_{int(datetime.now().timestamp())}",
                        agent_id=self.agent_id,
                        symbol=selected.symbol,
                        trade_type=TradeType.COVER,
                        quantity=quantity,
                        price=execution_price,
                        total_value=quantity * execution_price,
                        reasoning=self.last_reasoning,
                    )

        # Simple momentum strategy for buying
        if selected.price_change_percent_24h and selected.price_change_percent_24h > 2:
            # Positive momentum - BUY
            trade_type = TradeType.BUY
            # Use ask price (market price for buying)
            execution_price = selected.ask
            # Risk 2-5% of portfolio
            trade_value = current_portfolio_value * random.uniform(0.02, 0.05)
            quantity = trade_value / execution_price

            if trade_value > cash_balance:
                self.last_reasoning = "Insufficient cash for buy order"
                return None

            self.last_reasoning = (
                f"Positive momentum detected: {selected.price_change_percent_24h:.2f}% gain. "
                f"Buying {quantity:.6f} {selected.symbol} at ${execution_price:.2f} (ask)"
            )
            
        elif selected.price_change_percent_24h and selected.price_change_percent_24h < -2:
            # Negative momentum - Could short or buy the dip
            if random.random() > 0.6:  # 40% chance to short on negative momentum
                # SHORT - expect further decline
                trade_type = TradeType.SHORT
                # Use bid price (selling borrowed asset)
                execution_price = selected.bid
                trade_value = current_portfolio_value * random.uniform(0.02, 0.04)
                quantity = trade_value / execution_price

                self.last_reasoning = (
                    f"Strong negative momentum: {selected.price_change_percent_24h:.2f}% drop. "
                    f"Shorting {quantity:.6f} {selected.symbol} at ${execution_price:.2f} (bid)"
                )

            elif random.random() > 0.5:
                # Buy the dip
                trade_type = TradeType.BUY
                execution_price = selected.ask
                trade_value = current_portfolio_value * random.uniform(0.01, 0.03)
                quantity = trade_value / execution_price

                if trade_value > cash_balance:
                    self.last_reasoning = "Insufficient cash for buy order"
                    return None

                self.last_reasoning = (
                    f"Dip detected: {selected.price_change_percent_24h:.2f}% drop. "
                    f"Buying the dip - {quantity:.6f} {selected.symbol} at ${execution_price:.2f} (ask)"
                )
            else:
                self.last_reasoning = "Negative momentum, avoiding this asset"
                return None
        else:
            self.last_reasoning = "No strong momentum signal"
            return None

        self.trade_counter += 1

        return Trade(
            id=f"{self.agent_id}_{self.trade_counter}_{int(datetime.now().timestamp())}",
            agent_id=self.agent_id,
            symbol=selected.symbol,
            trade_type=trade_type,
            quantity=quantity,
            price=execution_price,
            total_value=quantity * execution_price,
            reasoning=self.last_reasoning,
        )
    
    def get_reasoning(self) -> str:
        """Get the reasoning behind the last decision"""
        return self.last_reasoning
