# AI Trading Arena

An AI agent trading competition platform inspired by [nof1.ai's Alpha Arena](https://nof1.ai/), where multiple AI models compete in crypto trading with identical starting capital and market conditions.

## 🎯 Overview

Just like Alpha Arena, this platform allows different AI models to compete against each other in real market conditions. Each agent:
- Starts with $10,000 in capital
- Makes autonomous trading decisions
- Competes to maximize risk-adjusted returns
- Has all trades publicly visible and tracked

## 🤖 How AI Integration Works

The system **automatically detects** which AI APIs you've configured:

```bash
# .env configuration determines agent behavior:

# No API keys → Simulated agents (FREE)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=

# With API keys → Real AI agents (PAID)
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
GOOGLE_API_KEY=your-google-key-here
```

**What you'll see when running:**

Without API keys:
```
⚠️  No Anthropic API key - using simulated agent
⚠️  No OpenAI API key - using simulated agent
⚠️  No Google API key - using simulated agent
✅ Added agent: Claude-3.5-Sonnet-Simulated
✅ Added agent: GPT-4-Simulated
✅ Added agent: Gemini-Pro-Simulated
```

With API keys:
```
✅ Added Anthropic Claude agent (using API)
✅ Added OpenAI GPT agent (using API)
✅ Added Google Gemini agent (using API)
```

**Key point:** Same code, different intelligence level based on your configuration!

## ✨ Features

### Trading Modes
- 🔄 **Mock trading mode** (default) - Paper trading with no risk
- ⚠️ **Real trading mode** - Live trading with actual money (via flag switch)

### AI Agent Capabilities
- 🤖 **Simulated agents** - Rule-based momentum strategy (FREE, no API keys)
- 🧠 **AI-powered agents** - Real AI models (OpenAI GPT, Anthropic Claude, Google Gemini)
- 🔌 **Automatic detection** - Uses AI if API keys present, otherwise uses simulated agents
- � **Reasoning display** - See why each agent made its decision

### Competition Features
- � **Equal starting capital**: $10,000 per agent
- 📊 **Real-time leaderboard** with live rankings
- 📈 **Live market data** for BTC, ETH, SOL, BNB
- 📝 **Complete transparency** - all trades publicly visible
- 🎯 **Performance metrics** - returns, win rates, P&L tracking
- 📱 **Web dashboard** for visualization

### Safety & Management
- �️ **Risk management** - Position sizing, leverage limits, drawdown monitoring
- 🔐 **Secure configuration** - API keys via environment variables
- ✅ **Validation** - Trade and balance verification before execution

## 🚀 Quick Start

### Option 1: Quick Demo (Recommended First)

```bash
# Run a quick 10-cycle demo
python3 demo.py
```

### Option 2: Full Setup

```bash
# Use the automated setup script
./run_arena.sh

# Or manually:
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env to set MOCK_TRADING=true (already default)

# 4. Run the arena
python main.py

# 5. (Optional) Run dashboard in another terminal
python dashboard.py
# Then open http://127.0.0.1:8050 in your browser
```

## 📁 Project Structure

```
ai_trading2/
├── main.py              # Main entry point - runs the competition
├── demo.py              # Quick demo script
├── arena.py             # Core arena orchestrator
├── config.py            # Configuration management
├── dashboard.py         # Web dashboard for visualization
├── agents/              # AI agent implementations
│   ├── base_agent.py    # Abstract base class for agents
│   └── simple_agent.py  # Example momentum-based agent
├── exchange/            # Exchange integration layer
│   ├── base_exchange.py      # Exchange interface
│   ├── mock_exchange.py      # Paper trading implementation
│   ├── real_exchange.py      # Real exchange (CCXT)
│   └── exchange_factory.py   # Factory to switch modes
├── models/              # Data models
│   ├── trade.py         # Trade model
│   ├── position.py      # Position tracking
│   ├── agent_state.py   # Agent portfolio state
│   └── market_data.py   # Market data model
├── .env                 # Environment configuration (MOCK_TRADING flag)
└── requirements.txt     # Python dependencies
```

## 🎮 Trading Mode: Mock vs Real

The system has a **built-in flag** to switch between mock (paper) trading and real trading. This is controlled in the `.env` file:

### Mock Trading (Default - Safe)

```bash
# In .env file
MOCK_TRADING=true
```

**Mock trading features:**
- ✅ No real money at risk
- ✅ Simulated market prices with realistic movements
- ✅ Perfect for testing strategies
- ✅ Instant trade execution
- ✅ No API keys required
- ✅ **This is the default mode**

### Real Trading (Use with Extreme Caution)

```bash
# In .env file
MOCK_TRADING=false

# Also set your exchange API keys:
EXCHANGE_API_KEY=your_actual_api_key
EXCHANGE_API_SECRET=your_actual_api_secret
EXCHANGE_NAME=binance  # or other CCXT-supported exchange
```

**⚠️ CRITICAL WARNING:**
- ❗ Real trading uses **REAL MONEY**
- ❗ You can **LOSE REAL MONEY**
- ❗ Test thoroughly in mock mode first
- ❗ Start with small amounts
- ❗ Understand all risks before switching

### How It Works

The system uses an **Exchange Factory Pattern**:

```python
# In exchange/exchange_factory.py
if Config.MOCK_TRADING:
    return MockExchange()  # Paper trading
else:
    return RealExchange()  # Real trading
```

All trading logic remains the same - only the execution layer changes. This ensures:
- No code changes needed to switch modes
- Identical behavior in both modes
- Easy testing before going live

## 🏆 Competition Rules

Following the Alpha Arena model:

- 💰 **Starting Capital**: $10,000 per agent
- 📈 **Market**: Cryptocurrency spot trading (BTC, ETH, SOL, BNB)
- 🎯 **Objective**: Maximize risk-adjusted returns
- 👁️ **Transparency**: All trades, reasoning, and positions are public
- 🤖 **Autonomy**: AI agents make all decisions (entry, exit, sizing, timing)
- ⚖️ **Equal Opportunity**: All agents receive identical market data
- 🔄 **Real-time**: Continuous trading with regular decision cycles

## 🎨 Customization

### Adding Your Own AI Agent

Create a new agent by inheriting from `BaseAgent`:

```python
from agents import BaseAgent
from models import Trade, TradeType

class MyCustomAgent(BaseAgent):
    async def make_decision(self, market_data, current_portfolio_value, cash_balance):
        # Your trading logic here
        # Return Trade object or None
        pass
    
    def get_reasoning(self):
        return "Your agent's reasoning"
```

Then add it to the arena in `main.py`:

```python
from agents.my_custom_agent import MyCustomAgent

arena.add_agent(MyCustomAgent("agent_6", "My-Custom-Agent"))
```

### Using Real AI Models (OpenAI, Anthropic, Google)

By default, agents use simple simulated strategies. To use real AI models for trading decisions:

1. **Get API keys** from AI providers (see [API_SETUP.md](API_SETUP.md))
2. **Add to .env file:**

```bash
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
GOOGLE_API_KEY=your-google-key
```

3. **Run the arena** - it will automatically use AI agents if keys are present

**What changes:**
- ❌ Without API keys: Agents use simple rule-based strategy
- ✅ With API keys: Agents use real AI models (GPT-4, Claude, Gemini) to analyze markets and make decisions

**Cost:** ~$0.50-1.00 per 50-cycle session with all three AI models. Google Gemini has a free tier.

See [API_SETUP.md](API_SETUP.md) for detailed setup instructions.

### Configuring Trading Parameters

Edit `.env` to customize:

```bash
STARTING_CAPITAL=10000          # Starting capital per agent
MAX_POSITION_SIZE=0.1           # Max 10% of portfolio per trade
MAX_LEVERAGE=2                  # Maximum leverage allowed
MARKET_DATA_UPDATE_INTERVAL=60  # Seconds between updates
```

## 📊 Dashboard Features

The web dashboard (`dashboard.py`) provides:
- 🏆 Live leaderboard with rankings
- 📈 Performance charts over time
- 💹 Real-time market prices
- 📋 Trade history for each agent
- 🎯 Win rate and PnL tracking

Access at `http://127.0.0.1:8050` after running `python dashboard.py`

## 🔒 Security & Risk Management

**Built-in protections:**
- Maximum position sizing limits
- Drawdown monitoring
- Trade validation before execution
- Separate mock/real environments
- API key security via environment variables

**Best practices:**
1. ✅ Always test in mock mode first
2. ✅ Start with small capital in real mode
3. ✅ Monitor agents actively during real trading
4. ✅ Set stop-loss limits
5. ✅ Never share API keys
6. ✅ Use exchange sub-accounts with limited permissions

## 🛠️ Technology Stack

- **Python 3.8+**: Core language
- **asyncio**: Async trading operations
- **CCXT**: Exchange connectivity (real trading)
- **Pydantic**: Data validation
- **Dash/Plotly**: Interactive dashboard
- **FastAPI**: REST API (future enhancement)

## 📚 Inspired By

This project is inspired by [nof1.ai's Alpha Arena](https://nof1.ai/), which pioneered the concept of AI model competition in real financial markets. Their approach of testing AI capabilities through actual trading provides a dynamic, real-world benchmark that goes beyond static evaluations.

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- Additional AI agent implementations
- More sophisticated trading strategies
- Enhanced risk management
- Database persistence
- REST API for external agents
- Real-time WebSocket updates
- Advanced portfolio analytics

## ⚠️ Disclaimer

This software is for educational purposes only. Trading cryptocurrencies involves substantial risk of loss. The authors are not responsible for any financial losses incurred through the use of this software. Always trade responsibly and never invest more than you can afford to lose.

## 📄 License

MIT License - See LICENSE file for details

---

**Made with ❤️ for the AI trading community**

---

## 🎯 Quick Summary

**Two independent flags control everything:**

1. **MOCK_TRADING** (true/false) → Safe testing vs Real money
2. **API Keys** (empty/set) → Simple strategy vs AI intelligence

**Getting started is easy:**
```bash
python3 demo.py  # Works immediately, no setup!
```

**Want AI-powered agents?**
- See [API_SETUP.md](API_SETUP.md) for detailed instructions
- Add API keys to `.env` file
- Run `python3 main.py` - agents automatically use AI!

**Want real trading?**
- ⚠️ Test thoroughly in mock mode first!
- See [USAGE_GUIDE.md](USAGE_GUIDE.md) for safety guidelines
- Change `MOCK_TRADING=false` in `.env`

For more help: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
