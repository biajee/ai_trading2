# Usage Guide: Mock vs Real Trading

## Overview

The AI Trading Arena has a simple flag-based system to switch between mock (paper) trading and real trading. This guide explains how to use both modes.

## 🎮 Mock Trading Mode (Recommended for Starting)

### What is Mock Trading?

Mock trading simulates real trading without using actual money. It's perfect for:
- Testing new strategies
- Training AI agents
- Learning the platform
- Debugging code
- Running competitions without risk

### How to Enable Mock Trading

**Step 1:** Check your `.env` file:

```bash
MOCK_TRADING=true
```

**Step 2:** That's it! This is the default mode.

### What Happens in Mock Mode?

```
User → Arena → MockExchange → Simulated Trade
                    ↓
              No Real Money
                    ↓
              Fake Balances
                    ↓
          Simulated Price Feeds
```

The mock exchange:
- ✅ Simulates realistic price movements
- ✅ Tracks virtual balances
- ✅ Executes trades instantly
- ✅ Records complete history
- ✅ Provides realistic slippage/fees

### Running in Mock Mode

```bash
# Quick demo (10 cycles)
python3 demo.py

# Full arena (50 cycles)
python3 main.py

# With dashboard
python3 dashboard.py  # In one terminal
python3 main.py       # In another terminal
```

### Example Output in Mock Mode

```
╔═══════════════════════════════════════════════════════════╗
║                   AI TRADING ARENA                        ║
╚═══════════════════════════════════════════════════════════╝

🎮 Using MOCK EXCHANGE (Paper Trading)
✅ Added agent: Claude-4.5-Sonnet (ID: agent_1)
✅ Added agent: GPT-5 (ID: agent_2)
✅ Added agent: Gemini-2.5-Pro (ID: agent_3)

Mode: MOCK TRADING
Starting Capital: $10,000.00 per agent
Trading Pairs: BTC/USDT, ETH/USDT, SOL/USDT, BNB/USDT

🔄 Trading Cycle - 2025-10-30 14:30:00
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Claude-4.5-Sonnet: BUY 0.001234 BTC/USDT @ $67,145.23
   Reasoning: Positive momentum detected: 2.3% gain

📊 GPT-5: BUY 0.089456 ETH/USDT @ $3,521.45
   Reasoning: Dip detected: -2.1% drop. Buying the dip

🏆 LEADERBOARD - MOCK TRADING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Rank   Agent                Portfolio       Return      Trades   Win Rate
───────────────────────────────────────────────────────────────────────────
1      Claude-4.5-Sonnet    $10,342.15     +3.42%      8        75.0%
2      GPT-5                $10,156.89     +1.57%      6        66.7%
3      Gemini-2.5-Pro       $9,987.23      -0.13%      5        60.0%
```

## ⚠️ Real Trading Mode

### What is Real Trading?

Real trading mode connects to an actual cryptocurrency exchange and executes trades with real money.

### Prerequisites for Real Trading

1. **Exchange Account**: Create account on supported exchange (Binance, Coinbase, etc.)
2. **API Keys**: Generate API keys with trading permissions
3. **Funding**: Deposit actual funds (start small!)
4. **Testing**: Thoroughly test in mock mode first
5. **Understanding**: Know the risks involved

### How to Enable Real Trading

**Step 1:** Get API keys from your exchange

**Step 2:** Edit `.env` file:

```bash
# Switch to real trading mode
MOCK_TRADING=false

# Add your exchange credentials
EXCHANGE_API_KEY=your_actual_api_key_here
EXCHANGE_API_SECRET=your_actual_secret_here
EXCHANGE_NAME=binance

# Optional: Start with lower capital
STARTING_CAPITAL=100
```

**Step 3:** Double-check everything:

```bash
# Verify your settings
cat .env | grep MOCK_TRADING
# Should show: MOCK_TRADING=false

# Verify API keys are set
cat .env | grep EXCHANGE_API_KEY
# Should show your key (not empty)
```

**Step 4:** Run with extreme caution:

```bash
python3 main.py
```

### What Happens in Real Mode?

```
User → Arena → RealExchange → CCXT Library → Exchange API
                    ↓
              REAL MONEY! ⚠️
                    ↓
              Real Balances
                    ↓
          Live Market Prices
                    ↓
          Actual Trade Execution
```

### Safety Checklist for Real Trading

Before switching to real mode:

- [ ] Tested thoroughly in mock mode
- [ ] Understand the trading strategy
- [ ] Set appropriate `STARTING_CAPITAL` (start small!)
- [ ] Configure `MAX_POSITION_SIZE` conservatively
- [ ] API keys are from a sub-account with limited funds
- [ ] Exchange API keys have IP restrictions
- [ ] Monitoring the system actively
- [ ] Have a stop-loss strategy
- [ ] Understand you can lose money

### Recommended First Real Trade Setup

```bash
# Conservative settings for first real run
MOCK_TRADING=false
STARTING_CAPITAL=50          # Start with just $50
MAX_POSITION_SIZE=0.05       # Max 5% per trade
MAX_LEVERAGE=1               # No leverage
```

### Switching Back to Mock Mode

At any time, switch back to mock mode:

```bash
# In .env file
MOCK_TRADING=true
```

Then restart the application.

## 🔧 Technical Details

### Exchange Factory Pattern

The system uses a factory pattern to create the appropriate exchange:

```python
# In exchange/exchange_factory.py
def create_exchange() -> BaseExchange:
    if Config.MOCK_TRADING:
        return MockExchange()
    else:
        return RealExchange()
```

### Interface Consistency

Both exchanges implement the same interface:

```python
class BaseExchange(ABC):
    async def get_market_data(symbol: str) -> MarketData
    async def execute_trade(trade: Trade) -> Trade
    async def get_balance(currency: str) -> float
    async def cancel_trade(trade_id: str) -> bool
```

This means:
- ✅ Same code works in both modes
- ✅ Easy testing before real trading
- ✅ No code changes needed to switch
- ✅ Agents don't know if it's mock or real

## 📊 Comparison: Mock vs Real

| Feature | Mock Trading | Real Trading |
|---------|--------------|--------------|
| Risk | ❌ None | ⚠️ HIGH - Real money |
| Cost | Free | Exchange fees + spreads |
| Speed | Instant | Network latency |
| Market Data | Simulated | Live, real-time |
| Slippage | Simulated | Actual |
| API Keys | Not needed | Required |
| Learning | ✅ Perfect | ✅ Real experience |
| Testing | ✅ Ideal | ❌ Expensive |

## 🎯 Best Practices

### Development Workflow

1. **Develop**: Write agents in mock mode
2. **Test**: Run extensive mock trading
3. **Validate**: Verify strategy performance
4. **Deploy**: Switch to real with small capital
5. **Monitor**: Watch closely during real trading
6. **Scale**: Gradually increase if successful

### When to Use Mock Mode

- ✅ Developing new strategies
- ✅ Testing code changes
- ✅ Training/learning
- ✅ Demonstrations
- ✅ Competitions (no risk)
- ✅ Backtesting concepts

### When to Use Real Mode

- ✅ After thorough mock testing
- ✅ With expendable capital only
- ✅ When you understand all risks
- ✅ For actual performance validation
- ✅ With proper monitoring

## 🚨 Emergency Procedures

### If Something Goes Wrong in Real Mode

1. **Stop the arena immediately**: Press Ctrl+C
2. **Check your exchange account**: Verify positions
3. **Close positions manually**: Use exchange interface if needed
4. **Switch back to mock**: Set `MOCK_TRADING=true`
5. **Investigate**: Review logs and trade history
6. **Fix issues**: Correct before re-enabling real trading

### Monitoring Real Trading

```bash
# Monitor logs
tail -f trading_arena.log

# Watch for errors
grep ERROR trading_arena.log

# Check specific agent
grep "agent_1" trading_arena.log
```

## 💡 Tips

1. **Start Small**: Begin with minimum viable capital
2. **Test Everything**: Mock trade for days/weeks first
3. **Monitor Actively**: Don't leave real trading unattended
4. **Use Limits**: Set max position sizes and stop losses
5. **Keep Records**: Log everything for analysis
6. **Learn Gradually**: Master mock before real
7. **Stay Informed**: Understand market conditions

## 🤝 Getting Help

If you encounter issues:

1. Check `.env` configuration
2. Verify API keys (for real mode)
3. Review logs in `trading_arena.log`
4. Test in mock mode first
5. Check exchange API status
6. Review documentation

Remember: **When in doubt, use mock mode!** There's no rush to trade with real money.

---

**Happy Trading! 🚀 (Safely, in mock mode first! 😊)**
