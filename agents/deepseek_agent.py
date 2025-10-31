"""DeepSeek-powered trading agent"""
import json
from typing import List, Optional
from datetime import datetime
from models import Trade, MarketData, TradeType
from .base_agent import BaseAgent
from config import Config


class DeepSeekAgent(BaseAgent):
    """Trading agent powered by DeepSeek's models"""
    
    def __init__(self, agent_id: str, agent_name: str, model: str = "deepseek-chat"):
        super().__init__(agent_id, agent_name)
        self.model = model
        self.last_reasoning = ""
        self.trade_counter = 0
        self.client = None
        
        # Initialize DeepSeek client if API key is available
        # DeepSeek API is OpenAI-compatible
        if Config.get_api_key("deepseek"):
            try:
                import openai
                self.client = openai.OpenAI(
                    api_key=Config.get_api_key("deepseek"),
                    base_url="https://api.deepseek.com"
                )
            except ImportError:
                print(f"⚠️  OpenAI library not installed. Install with: pip install openai")
            except Exception as e:
                print(f"⚠️  Failed to initialize DeepSeek client: {e}")
    
    async def make_decision(
        self,
        market_data: List[MarketData],
        current_portfolio_value: float,
        cash_balance: float,
        positions: dict = None
    ) -> Optional[Trade]:
        """Make trading decision using DeepSeek"""
        
        if not self.client:
            self.last_reasoning = "DeepSeek API not configured - skipping decision"
            return None
        
        # Prepare market context
        if positions is None:
            positions = {}
        market_summary = self._prepare_market_summary(market_data, current_portfolio_value, cash_balance, positions)
        
        try:
            # Call DeepSeek API for trading decision
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert cryptocurrency trader. Analyze the market data and make a trading decision.
                        
                        Respond ONLY with valid JSON in this exact format:
                        {
                            "action": "buy" or "sell" or "hold",
                            "symbol": "BTC/USDT" or "ETH/USDT" or "SOL/USDT" or "BNB/USDT",
                            "percentage": 0.02 to 0.5 (percentage of portfolio to risk),
                            "reasoning": "Brief explanation of your decision"
                        }
                        
                        Use technical analysis, momentum, and risk management principles.
                        You can SELL positions you currently hold to take profits or cut losses."""
                    },
                    {
                        "role": "user",
                        "content": market_summary
                    }
                ],
                temperature=0.7,
                max_tokens=300
            )
            print("DeepSeek market data:", market_summary)
            print("DeepSeek response:", response)

            # Parse response
            decision_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON if wrapped in markdown
            if "```json" in decision_text:
                decision_text = decision_text.split("```json")[1].split("```")[0].strip()
            elif "```" in decision_text:
                decision_text = decision_text.split("```")[1].split("```")[0].strip()
            
            decision = json.loads(decision_text)
            
            # Process decision
            return self._process_decision(decision, market_data, current_portfolio_value, cash_balance, positions)
            
        except Exception as e:
            self.last_reasoning = f"Error calling DeepSeek API: {str(e)}"
            print(f"❌ {self.agent_name} error: {e}")
            return None
    
    def _prepare_market_summary(self, market_data: List[MarketData], portfolio_value: float, cash: float, positions: dict) -> str:
        """Prepare market data summary for the AI"""
        summary = f"Current Portfolio Value: ${portfolio_value:.2f}\n"
        summary += f"Available Cash: ${cash:.2f}\n\n"

        if positions:
            summary += "Current Positions:\n"
            for symbol, pos in positions.items():
                pnl = pos.unrealized_pnl
                pnl_pct = (pnl / (pos.average_entry_price * pos.quantity)) * 100 if pos.quantity > 0 else 0
                summary += f"  {symbol}: {pos.quantity:.6f} @ ${pos.average_entry_price:.2f} (P&L: ${pnl:+.2f} / {pnl_pct:+.2f}%)\n"
            summary += "\n"

        summary += "Market Data:\n"

        for data in market_data:
            summary += f"\n{data.symbol}:\n"
            summary += f"  Price: ${data.price:.2f}\n"
            summary += f"  24h Change: {data.price_change_percent_24h:.2f}%\n"
            summary += f"  24h High: ${data.high_24h:.2f}\n"
            summary += f"  24h Low: ${data.low_24h:.2f}\n"

        return summary
    
    def _process_decision(
        self,
        decision: dict,
        market_data: List[MarketData],
        portfolio_value: float,
        cash_balance: float,
        positions: dict
    ) -> Optional[Trade]:
        """Process the AI's decision into a Trade object"""
        
        action = decision.get("action", "hold").lower()
        self.last_reasoning = decision.get("reasoning", "No reasoning provided")
        
        if action == "hold":
            return None
        
        symbol = decision.get("symbol")
        percentage = float(decision.get("percentage", 0.03))
        
        # Find market data for selected symbol
        selected_data = next((d for d in market_data if d.symbol == symbol), None)
        if not selected_data:
            self.last_reasoning = f"Symbol {symbol} not found in market data"
            return None
        
        # Calculate trade size
        trade_value = portfolio_value * percentage

        if action == "buy":
            if trade_value > cash_balance:
                self.last_reasoning = "Insufficient cash for buy order"
                return None

            # Use ask price (market price for buying)
            execution_price = selected_data.ask
            quantity = trade_value / execution_price
            trade_type = TradeType.BUY

        elif action == "sell":
            # Check if we have a position to sell
            if selected_data.symbol not in positions or positions[selected_data.symbol].quantity == 0:
                self.last_reasoning = f"No position in {selected_data.symbol} to sell"
                return None

            # Use bid price (market price for selling)
            execution_price = selected_data.bid
            # Sell up to the percentage of the position
            position_quantity = positions[selected_data.symbol].quantity
            quantity = min(position_quantity, position_quantity * percentage)
            trade_type = TradeType.SELL
        else:
            return None

        self.trade_counter += 1

        return Trade(
            id=f"{self.agent_id}_{self.trade_counter}_{int(datetime.now().timestamp())}",
            agent_id=self.agent_id,
            symbol=selected_data.symbol,
            trade_type=trade_type,
            quantity=quantity,
            price=execution_price,
            total_value=quantity * execution_price,
            reasoning=self.last_reasoning,
        )
    
    def get_reasoning(self) -> str:
        """Get the reasoning behind the last decision"""
        return self.last_reasoning
