# Configuration Guide

## Overview

The AI Trading Arena uses a `config.json` file for all configuration. This makes it easy to enable/disable agents, change parameters, and manage API keys without editing code.

## Structure

### Trading Settings

```json
{
  "trading": {
    "mock_trading": true,           // true = paper trading, false = real money
    "starting_capital": 10000,      // Starting capital per agent
    "trading_pairs": [              // Crypto pairs to track
      "BTC/USDT", 
      "ETH/USDT", 
      "SOL/USDT", 
      "BNB/USDT"
    ]
  }
}
```

### Agent Configuration

Each agent has:
- `enabled`: true/false to enable/disable the agent
- `name`: Display name for the agent
- `model`: Model identifier (e.g., "gpt-4", "claude-3-5-sonnet")
- `api_key_name`: Name of the API key in the `ai_api_keys` section
- `agent_class`: Python class name for the agent

```json
{
  "agents": {
    "deepseek": {
      "enabled": true,                    // Enable this agent
      "name": "DeepSeek-V3",              // Display name
      "model": "deepseek-chat",           // Model to use
      "api_key_name": "deepseek",         // Key name in ai_api_keys
      "agent_class": "DeepSeekAgent"      // Python class
    },
    "openai": {
      "enabled": false,                   // Disabled
      "name": "GPT-4",
      "model": "gpt-4",
      "api_key_name": "openai",
      "agent_class": "OpenAIAgent"
    }
  }
}
```

### API Keys

Store API keys in the `ai_api_keys` section:

```json
{
  "ai_api_keys": {
    "openai": "sk-your-openai-key-here",
    "anthropic": "sk-ant-your-anthropic-key-here",
    "google": "your-google-key-here",
    "deepseek": "your-deepseek-key-here"
  }
}
```

**Note**: You can also store keys in `.env` file for security (recommended for production).

### Risk Management

```json
{
  "risk_management": {
    "max_position_size": 0.1,      // Max 10% of portfolio per trade
    "max_leverage": 2,             // Maximum 2x leverage
    "max_drawdown": 0.2            // Maximum 20% drawdown
  }
}
```

### Competition Settings

```json
{
  "competition": {
    "duration_days": 7,            // Competition duration (informational)
    "cycles": 50,                  // Number of trading cycles
    "cycle_interval": 5            // Seconds between cycles
  }
}
```

## Quick Examples

### Enable Only DeepSeek Agent

```json
{
  "agents": {
    "deepseek": {
      "enabled": true,
      "name": "DeepSeek-V3",
      "model": "deepseek-chat",
      "api_key_name": "deepseek",
      "agent_class": "DeepSeekAgent"
    },
    "openai": { "enabled": false, ... },
    "anthropic": { "enabled": false, ... },
    "google": { "enabled": false, ... },
    "simple_agents": {
      "enabled": true,
      "count": 2,
      "names": ["Simple-Momentum-1", "Simple-Momentum-2"]
    }
  }
}
```

### Enable All AI Agents

```json
{
  "agents": {
    "deepseek": { "enabled": true, ... },
    "openai": { "enabled": true, ... },
    "anthropic": { "enabled": true, ... },
    "google": { "enabled": true, ... },
    "simple_agents": { "enabled": false }
  }
}
```

### Only Simple Agents (No API Costs)

```json
{
  "agents": {
    "deepseek": { "enabled": false },
    "openai": { "enabled": false },
    "anthropic": { "enabled": false },
    "google": { "enabled": false },
    "simple_agents": {
      "enabled": true,
      "count": 5,
      "names": [
        "Momentum-Agent-1",
        "Momentum-Agent-2",
        "Momentum-Agent-3",
        "Momentum-Agent-4",
        "Momentum-Agent-5"
      ]
    }
  }
}
```

### Real Trading Mode

```json
{
  "trading": {
    "mock_trading": false,        // ⚠️ REAL MONEY!
    "starting_capital": 100       // Start small!
  },
  "exchange": {
    "name": "binance",
    "api_key": "your-exchange-key",
    "api_secret": "your-exchange-secret"
  }
}
```

## Adding a New Agent

To add a completely new agent type:

1. **Create the agent class** (e.g., `agents/my_agent.py`):
```python
class MyCustomAgent(BaseAgent):
    # Implement your agent
    pass
```

2. **Add to config.json**:
```json
{
  "agents": {
    "my_custom": {
      "enabled": true,
      "name": "My Custom Agent",
      "model": "custom-model-v1",
      "api_key_name": "my_custom",
      "agent_class": "MyCustomAgent"
    }
  },
  "ai_api_keys": {
    "my_custom": "your-api-key-here"
  }
}
```

3. **Import in main.py**:
```python
from agents import MyCustomAgent
```

That's it! The agent will be loaded automatically.

## Configuration Priority

1. **config.json** - Primary source
2. **.env file** - Fallback for API keys (for security)
3. **Environment variables** - System level

Example: If `DEEPSEEK_API_KEY` is in .env but not in config.json, it will still be used.

## Best Practices

### Development
```json
{
  "trading": { "mock_trading": true },
  "agents": {
    "deepseek": { "enabled": true },
    "simple_agents": { "enabled": true }
  },
  "competition": { "cycles": 10, "cycle_interval": 2 }
}
```

### Testing AI Models
```json
{
  "trading": { "mock_trading": true },
  "agents": {
    "deepseek": { "enabled": true },
    "openai": { "enabled": true },
    "anthropic": { "enabled": true },
    "google": { "enabled": true }
  }
}
```

### Production
```json
{
  "trading": { "mock_trading": false },
  "agents": {
    "deepseek": { "enabled": true }
  },
  "ai_api_keys": {},  // Keep empty, use .env for security
  "competition": { "cycles": 1000, "cycle_interval": 60 }
}
```

## Validation

The configuration is automatically validated on startup. If there are errors, you'll see:

```
ValueError: Starting capital must be positive!
ValueError: Exchange API credentials required for real trading!
```

## Reloading Configuration

To reload without restarting:

```python
from config import Config
Config.reload()
```

## Security Notes

1. **Never commit API keys** to version control
2. Use `.env` file for sensitive keys in production
3. Keep `config.json` in `.gitignore` if it contains keys
4. Use `config.json.example` as a template

## Troubleshooting

**"No agents enabled in config.json!"**
- Check that at least one agent has `"enabled": true`

**"Agent class XYZ not found"**
- Make sure the agent class is imported in `main.py`
- Verify the `agent_class` name matches the actual class name

**"API not configured - skipping decision"**
- The agent is enabled but no API key is provided
- Add the key to `ai_api_keys` or `.env`

## Summary

✅ All configuration in one JSON file  
✅ Easy to enable/disable agents  
✅ No code changes needed  
✅ API keys separate from logic  
✅ Extensible for new agents  

Edit `config.json` to customize your trading arena!
