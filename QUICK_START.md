# Quick Start Guide

## 🚀 Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Your Arena

Edit `config.json` to customize:

#### Enable/Disable Agents
```json
{
  "agents": {
    "deepseek": {
      "enabled": true,    // ← Change to false to disable
      "name": "DeepSeek-V3",
      "model": "deepseek-chat",
      "api_key_name": "deepseek",
      "agent_class": "DeepSeekAgent"
    }
  }
}
```

#### Add API Keys
```json
{
  "ai_api_keys": {
    "deepseek": "your-deepseek-key-here",
    "openai": "your-openai-key-here"
  }
}
```

Or use `.env` file:
```bash
DEEPSEEK_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
```

#### Select Trading Pairs
```json
{
  "trading": {
    "trading_pairs": [
      "BTC/USDT",
      "ETH/USDT",
      "SOL/USDT"
    ]
  }
}
```

### 3. Run the Arena

```bash
# Start the competition
python3 main.py

# Open dashboard (in another terminal)
python3 dashboard.py
```

Visit: http://127.0.0.1:8050

## 🎯 Common Tasks

### Add a New Agent

1. **Create agent class**:
```python
# agents/my_agent.py
from agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def decide_action(self, market_data):
        # Your logic here
        pass
```

2. **Update config.json**:
```json
{
  "agents": {
    "my_agent": {
      "enabled": true,
      "name": "My Custom Agent",
      "model": "custom-v1",
      "api_key_name": "my_agent",
      "agent_class": "MyAgent"
    }
  },
  "ai_api_keys": {
    "my_agent": "your-api-key"
  }
}
```

3. **Import in main.py**:
```python
from agents import MyAgent
```

Done! ✅

### Change Trading Pairs

Edit `config.json`:
```json
{
  "trading": {
    "trading_pairs": [
      "BTC/USDT",
      "ETH/USDT",
      "MATIC/USDT",  // Added
      "AVAX/USDT"    // Added
    ]
  }
}
```

Restart dashboard - it will automatically track new pairs! ✅

### Enable Multiple Agents

```json
{
  "agents": {
    "deepseek": { "enabled": true },
    "openai": { "enabled": true },
    "anthropic": { "enabled": true },
    "simple_agents": {
      "enabled": true,
      "count": 3
    }
  }
}
```

### Switch to Real Trading ⚠️

```json
{
  "trading": {
    "mock_trading": false,  // REAL MONEY!
    "starting_capital": 100  // Start small
  },
  "exchange": {
    "name": "binance",
    "api_key": "your-exchange-key",
    "api_secret": "your-exchange-secret"
  }
}
```

## 📊 Dashboard

The dashboard automatically shows:
- All **enabled agents** from config
- All **trading pairs** from config
- Live prices from Binance API
- Competition leaderboard

Update interval can be configured:
```json
{
  "dashboard": {
    "update_interval": 5  // seconds
  }
}
```

## 🔧 Configuration Reference

### Minimal Config
```json
{
  "trading": {
    "mock_trading": true,
    "trading_pairs": ["BTC/USDT"]
  },
  "agents": {
    "simple_agents": {
      "enabled": true,
      "count": 2
    }
  }
}
```

### Full AI Setup
```json
{
  "trading": {
    "mock_trading": true,
    "starting_capital": 10000,
    "trading_pairs": ["BTC/USDT", "ETH/USDT"]
  },
  "agents": {
    "deepseek": {
      "enabled": true,
      "name": "DeepSeek-V3",
      "model": "deepseek-chat",
      "api_key_name": "deepseek",
      "agent_class": "DeepSeekAgent"
    }
  },
  "ai_api_keys": {
    "deepseek": "your-key-here"
  },
  "competition": {
    "cycles": 50,
    "cycle_interval": 5
  }
}
```

## 🐛 Troubleshooting

### "No agents enabled in config.json!"
**Solution**: Set at least one agent to `"enabled": true`

### "API not configured - skipping decision"
**Solution**: Add API key to `ai_api_keys` section or `.env` file

### "Agent class XYZ not found"
**Solution**: Import the agent class in `main.py`

### Dashboard shows simulated data
**Solution**: This is normal if Binance API is unavailable. Uses config `trading_pairs` for fallback.

## 📚 More Documentation

- **CONFIG_GUIDE.md** - Detailed configuration guide
- **CONFIGURATION_SUMMARY.md** - Technical architecture
- **CHANGELOG.md** - Recent changes
- **API_SETUP.md** - API key setup instructions
- **FEATURES.md** - Full feature list

## 💡 Tips

1. **Start with mock trading** to test strategies
2. **Use simple agents first** to understand the system
3. **Add one AI agent at a time** to compare performance
4. **Monitor the dashboard** to track competition in real-time
5. **Check logs** for detailed agent decisions

## 🎯 Quick Commands

```bash
# Run arena
python3 main.py

# Start dashboard
python3 dashboard.py

# Test configuration
python3 -c "from config import Config; print(Config.get_all_agent_types())"

# Check enabled agents
python3 -c "from config import Config; print([a for a in Config.get_all_agent_types() if Config.is_agent_enabled(a)])"
```

## 🏁 Ready to Go!

Everything is configured through `config.json` - no code changes needed!

Just edit the config, add your API keys, and run:
```bash
python3 main.py
```

Happy Trading! 🚀📈
