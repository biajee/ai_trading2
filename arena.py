"""Main trading arena orchestrator"""
import asyncio
import json
from typing import Dict, List
from datetime import datetime
from models import AgentState, Trade, TradeStatus
from agents import BaseAgent, SimpleAgent
from exchange import ExchangeFactory, BaseExchange
from config import Config


class TradingArena:
    """Main trading arena orchestrator"""
    
    def __init__(self):
        self.exchange: BaseExchange = ExchangeFactory.create_exchange()
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_states: Dict[str, AgentState] = {}
        self.is_running = False
        self.state_file = "arena_state.json"
        self.current_cycle = 0
        self.cycle_history: Dict[str, List[dict]] = {}  # agent_id -> list of cycle snapshots
        
    def add_agent(self, agent: BaseAgent):
        """Add an agent to the arena"""
        self.agents[agent.agent_id] = agent

        # Initialize agent state
        self.agent_states[agent.agent_id] = AgentState(
            agent_id=agent.agent_id,
            agent_name=agent.agent_name,
            starting_capital=Config.STARTING_CAPITAL,
            cash_balance=Config.STARTING_CAPITAL,
        )

        # Initialize cycle history for this agent
        self.cycle_history[agent.agent_id] = []
        
        # Set initial balance for mock exchange
        if self.exchange.is_mock():
            self.exchange.set_balance("USDT", Config.STARTING_CAPITAL)
        
        print(f"✅ Added agent: {agent.agent_name} (ID: {agent.agent_id})")
    
    async def update_market_data(self):
        """Update market data for all trading pairs"""
        market_data = await self.exchange.get_multiple_market_data(Config.TRADING_PAIRS)
        
        # Update prices in agent states
        market_prices = {symbol: data.price for symbol, data in market_data.items()}
        for state in self.agent_states.values():
            state.update_portfolio_value(market_prices)

        # Save state to file for dashboard
        self.save_state()

        return list(market_data.values())
    
    async def execute_agent_decision(self, agent: BaseAgent, market_data: List):
        """Execute trading decision for a single agent"""
        state = self.agent_states[agent.agent_id]
        
        try:
            # Agent makes decision
            trade = await agent.make_decision(
                market_data=market_data,
                current_portfolio_value=state.total_portfolio_value,
                cash_balance=state.cash_balance,
                positions=state.positions
            )
            
            if trade:
                # Execute trade
                executed_trade = await self.exchange.execute_trade(trade)
                
                if executed_trade.status == TradeStatus.EXECUTED:
                    # Update agent state
                    state.trade_history.append(executed_trade)
                    state.total_trades += 1
                    
                    # Update positions and cash
                    if executed_trade.trade_type.value == "buy":
                        state.cash_balance -= executed_trade.total_value

                        # Update or create position
                        if executed_trade.symbol in state.positions:
                            pos = state.positions[executed_trade.symbol]
                            new_quantity = pos.quantity + executed_trade.quantity
                            new_avg_price = (
                                (pos.average_entry_price * pos.quantity +
                                 executed_trade.price * executed_trade.quantity) / new_quantity
                            )
                            pos.quantity = new_quantity
                            pos.average_entry_price = new_avg_price
                        else:
                            from models import Position
                            state.positions[executed_trade.symbol] = Position(
                                agent_id=agent.agent_id,
                                symbol=executed_trade.symbol,
                                quantity=executed_trade.quantity,
                                average_entry_price=executed_trade.price,
                                current_price=executed_trade.price,
                            )

                    elif executed_trade.trade_type.value == "sell":
                        # Check if position exists
                        if executed_trade.symbol in state.positions:
                            pos = state.positions[executed_trade.symbol]

                            # Verify sufficient quantity
                            if pos.quantity >= executed_trade.quantity:
                                # Calculate realized P&L
                                cost_basis = pos.average_entry_price * executed_trade.quantity
                                sale_proceeds = executed_trade.total_value
                                realized_pnl = sale_proceeds - cost_basis

                                # Track win/loss
                                if realized_pnl > 0:
                                    state.winning_trades += 1
                                elif realized_pnl < 0:
                                    state.losing_trades += 1

                                # Add cash from sale
                                state.cash_balance += executed_trade.total_value

                                # Update position
                                pos.quantity -= executed_trade.quantity

                                # Remove position if quantity is zero or very small
                                if pos.quantity < 0.000001:
                                    del state.positions[executed_trade.symbol]
                                    print(f"   💰 Position closed. Realized P&L: ${realized_pnl:+,.2f}")
                                else:
                                    print(f"   💰 Partial sell. Realized P&L: ${realized_pnl:+,.2f}, Remaining: {pos.quantity:.6f}")
                            else:
                                print(f"   ⚠️  Insufficient quantity to sell. Have: {pos.quantity:.6f}, Wanted: {executed_trade.quantity:.6f}")
                        else:
                            print(f"   ⚠️  No position in {executed_trade.symbol} to sell")

                    elif executed_trade.trade_type.value == "short":
                        # Open short position: borrow and sell asset
                        # Receive cash from selling (use bid price)
                        state.cash_balance += executed_trade.total_value

                        # Create or update short position (negative quantity)
                        if executed_trade.symbol in state.positions:
                            pos = state.positions[executed_trade.symbol]
                            new_quantity = pos.quantity - executed_trade.quantity  # Subtract to make more negative

                            # Calculate new average entry price for short
                            if pos.is_short:
                                # Adding to existing short position
                                total_proceeds = abs(pos.average_entry_price * pos.quantity) + executed_trade.total_value
                                new_qty_abs = abs(new_quantity)
                                new_avg_price = total_proceeds / new_qty_abs if new_qty_abs > 0 else executed_trade.price
                            else:
                                # This shouldn't happen (shorting while having long), but handle it
                                new_avg_price = executed_trade.price

                            pos.quantity = new_quantity
                            pos.average_entry_price = new_avg_price
                        else:
                            from models import Position
                            state.positions[executed_trade.symbol] = Position(
                                agent_id=agent.agent_id,
                                symbol=executed_trade.symbol,
                                quantity=-executed_trade.quantity,  # Negative for short
                                average_entry_price=executed_trade.price,
                                current_price=executed_trade.price,
                            )

                        print(f"   📉 Short opened. Received: ${executed_trade.total_value:,.2f}")

                    elif executed_trade.trade_type.value == "cover":
                        # Close short position: buy back to return borrowed asset
                        # Check if we have a short position to cover
                        if executed_trade.symbol in state.positions:
                            pos = state.positions[executed_trade.symbol]

                            # Verify we have a short position
                            if pos.is_short and abs(pos.quantity) >= executed_trade.quantity:
                                # Calculate realized P&L for covering short
                                # P&L = (entry_price - exit_price) * quantity
                                # For short: profit when exit_price < entry_price
                                cost_to_cover = executed_trade.total_value  # Cost to buy back
                                proceeds_from_short = pos.average_entry_price * executed_trade.quantity  # What we got when we shorted
                                realized_pnl = proceeds_from_short - cost_to_cover

                                # Track win/loss
                                if realized_pnl > 0:
                                    state.winning_trades += 1
                                elif realized_pnl < 0:
                                    state.losing_trades += 1

                                # Pay cash to buy back
                                state.cash_balance -= executed_trade.total_value

                                # Reduce short position (add positive quantity to negative)
                                pos.quantity += executed_trade.quantity

                                # Remove position if fully covered
                                if abs(pos.quantity) < 0.000001:
                                    del state.positions[executed_trade.symbol]
                                    print(f"   💰 Short position closed. Realized P&L: ${realized_pnl:+,.2f}")
                                else:
                                    print(f"   💰 Partial cover. Realized P&L: ${realized_pnl:+,.2f}, Remaining short: {abs(pos.quantity):.6f}")
                            else:
                                if not pos.is_short:
                                    print(f"   ⚠️  Cannot cover: position is LONG, not SHORT")
                                else:
                                    print(f"   ⚠️  Insufficient short position to cover. Have: {abs(pos.quantity):.6f}, Wanted: {executed_trade.quantity:.6f}")
                        else:
                            print(f"   ⚠️  No short position in {executed_trade.symbol} to cover")

                    print(f"📊 {agent.agent_name}: {executed_trade.trade_type.value.upper()} "
                          f"{executed_trade.quantity:.6f} {executed_trade.symbol} @ ${executed_trade.price:.2f}")
                    print(f"   Reasoning: {executed_trade.reasoning}")
                    
        except Exception as e:
            print(f"❌ Error executing decision for {agent.agent_name}: {e}")
    
    async def run_trading_cycle(self):
        """Run one trading cycle"""
        self.current_cycle += 1

        print(f"\n{'='*60}")
        print(f"🔄 Trading Cycle #{self.current_cycle} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        # Update market data
        market_data = await self.update_market_data()

        # Each agent makes decision
        tasks = [
            self.execute_agent_decision(agent, market_data)
            for agent in self.agents.values()
        ]
        await asyncio.gather(*tasks)

        # Save cycle snapshot for each agent
        self.save_cycle_snapshot()

        # Print leaderboard
        self.print_leaderboard()
    
    def print_leaderboard(self):
        """Print current leaderboard"""
        print(f"\n{'='*60}")
        print(f"🏆 LEADERBOARD - {Config.get_trading_mode_str()}")
        print(f"{'='*60}")
        
        # Sort by portfolio value
        sorted_states = sorted(
            self.agent_states.values(),
            key=lambda s: s.total_portfolio_value,
            reverse=True
        )
        
        print(f"{'Rank':<6} {'Agent':<20} {'Portfolio':<15} {'Return':<12} {'Trades':<8} {'Win Rate'}")
        print("-" * 80)
        
        for rank, state in enumerate(sorted_states, 1):
            print(
                f"{rank:<6} "
                f"{state.agent_name:<20} "
                f"${state.total_portfolio_value:>12,.2f}  "
                f"{state.total_return:>+8.2f}%  "
                f"{state.total_trades:>6}   "
                f"{state.win_rate:>6.1f}%"
            )
        print("=" * 80)
    
    async def start(self, cycles: int = 100, cycle_interval: int = 10):
        """
        Start the trading arena
        
        Args:
            cycles: Number of trading cycles to run
            cycle_interval: Seconds between cycles
        """
        print(f"\n{'='*60}")
        print(f"🚀 Starting AI Trading Arena")
        print(f"{'='*60}")
        print(f"Mode: {Config.get_trading_mode_str()}")
        print(f"Starting Capital: ${Config.STARTING_CAPITAL:,.2f} per agent")
        print(f"Trading Pairs: {', '.join(Config.TRADING_PAIRS)}")
        print(f"Agents: {len(self.agents)}")
        print(f"Cycles: {cycles}")
        print(f"Cycle Interval: {cycle_interval}s")
        print(f"{'='*60}\n")
        
        self.is_running = True
        
        for cycle in range(1, cycles + 1):
            if not self.is_running:
                break
            
            print(f"\n📈 Cycle {cycle}/{cycles}")
            await self.run_trading_cycle()
            
            if cycle < cycles:
                await asyncio.sleep(cycle_interval)
        
        print(f"\n{'='*60}")
        print(f"🏁 Trading Arena Completed")
        print(f"{'='*60}")
        self.print_leaderboard()
    
    def save_cycle_snapshot(self):
        """Save snapshot of current cycle for all agents"""
        for agent_id, state in self.agent_states.items():
            snapshot = {
                "cycle": self.current_cycle,
                "timestamp": datetime.now().isoformat(),
                "portfolio_value": state.total_portfolio_value,
                "cash_balance": state.cash_balance,
                "total_return": state.total_return,
                "total_trades": state.total_trades,
                "win_rate": state.win_rate,
                "num_positions": len(state.positions)
            }
            self.cycle_history[agent_id].append(snapshot)

    def save_state(self):
        """Save arena state to file for dashboard"""
        try:
            state_data = {
                "timestamp": datetime.now().isoformat(),
                "current_cycle": self.current_cycle,
                "agents": []
            }

            for agent_id, state in self.agent_states.items():
                agent_data = {
                    "agent_id": state.agent_id,
                    "agent_name": state.agent_name,
                    "portfolio_value": state.total_portfolio_value,
                    "cash_balance": state.cash_balance,
                    "total_return": state.total_return,
                    "total_trades": state.total_trades,
                    "win_rate": state.win_rate,
                    "positions": {
                        symbol: {
                            "quantity": pos.quantity,
                            "avg_price": pos.average_entry_price,
                            "current_price": pos.current_price,
                            "value": pos.current_value,
                            "pnl": pos.unrealized_pnl
                        } for symbol, pos in state.positions.items()
                    },
                    "recent_trades": [
                        {
                            "symbol": trade.symbol,
                            "type": trade.trade_type.value,
                            "quantity": trade.quantity,
                            "price": trade.price,
                            "timestamp": trade.timestamp.isoformat(),
                            "reasoning": trade.reasoning
                        } for trade in state.trade_history[-5:]  # Last 5 trades
                    ],
                    "cycle_history": self.cycle_history.get(agent_id, [])
                }
                state_data["agents"].append(agent_data)

            # Sort by portfolio value
            state_data["agents"].sort(key=lambda x: x["portfolio_value"], reverse=True)

            with open(self.state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving state: {e}")

    def stop(self):
        """Stop the trading arena"""
        self.is_running = False
        print("\n⏹️  Stopping arena...")
