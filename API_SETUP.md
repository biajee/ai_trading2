# API Setup Guide

This guide explains how to configure AI model API keys so your agents can use real AI models (OpenAI GPT, Anthropic Claude, Google Gemini) for trading decisions.

## Overview

The AI Trading Arena can work in two modes for agents:

1. **Simulated Agents** (default) - Uses simple momentum-based strategy
2. **AI-Powered Agents** - Uses real AI models via APIs to make intelligent decisions

## Why Use AI-Powered Agents?

Real AI models analyze market data using:
- Advanced pattern recognition
- Natural language reasoning
- Multi-factor analysis
- Risk assessment
- Market sentiment understanding

This provides more sophisticated and potentially better trading decisions than simple algorithmic strategies.

## Setting Up API Keys

### 1. OpenAI (GPT-4, GPT-3.5)

**Get API Key:**
1. Visit https://platform.openai.com/
2. Sign up or log in
3. Go to API Keys section
4. Create new secret key
5. Copy the key (starts with `sk-...`)

**Add to .env:**
```bash
OPENAI_API_KEY=sk-your-actual-key-here
```

**Cost:** Pay-per-use, approximately $0.01-0.03 per trading decision

**Models available:**
- `gpt-4` - Most capable, higher cost
- `gpt-3.5-turbo` - Faster, lower cost

### 2. Anthropic (Claude)

**Get API Key:**
1. Visit https://console.anthropic.com/
2. Sign up or log in
3. Go to API Keys
4. Create new key
5. Copy the key (starts with `sk-ant-...`)

**Add to .env:**
```bash
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

**Cost:** Pay-per-use, competitive pricing with OpenAI

**Models available:**
- `claude-3-5-sonnet-20241022` - Latest and most capable
- `claude-3-opus-20240229` - Most powerful
- `claude-3-sonnet-20240229` - Balanced
- `claude-3-haiku-20240307` - Fastest, lowest cost

### 3. Google (Gemini)

**Get API Key:**
1. Visit https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Create API key
4. Copy the key

**Add to .env:**
```bash
GOOGLE_API_KEY=your-google-api-key-here
```

**Cost:** Free tier available, then pay-per-use

**Models available:**
- `gemini-pro` - Text generation
- `gemini-pro-vision` - Multimodal (if needed for charts)

### 4. DeepSeek

**Get API Key:**
1. Visit https://platform.deepseek.com/
2. Sign up or log in
3. Go to API Keys section
4. Create new key
5. Copy the key (starts with `sk-...`)

**Add to .env:**
```bash
DEEPSEEK_API_KEY=your-deepseek-key-here
```

**Cost:** Very competitive pricing, often cheaper than OpenAI/Anthropic

**Models available:**
- `deepseek-chat` - Latest conversational model
- `deepseek-coder` - Specialized for code analysis

## Complete .env File Example

```bash
# Trading Mode Configuration
MOCK_TRADING=true

# Starting Capital
STARTING_CAPITAL=10000

# Exchange API Keys (only needed for real trading)
EXCHANGE_API_KEY=
EXCHANGE_API_SECRET=

# AI Model API Keys - ADD YOURS HERE!
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
GOOGLE_API_KEY=your-google-api-key-here
DEEPSEEK_API_KEY=your-deepseek-key-here

# Market Data
MARKET_DATA_UPDATE_INTERVAL=60

# Risk Management
MAX_POSITION_SIZE=0.1
MAX_LEVERAGE=2
```

## How It Works

### Without API Keys (Simulated Agents)

```
Market Data → SimpleAgent (rule-based) → Trading Decision
```

The agent uses basic momentum strategy:
- If price up >2%: Consider buying
- If price down >2%: Consider buying dip or avoiding
- Random selection and sizing

### With API Keys (AI-Powered Agents)

```
Market Data → AI Model API → Intelligent Analysis → Trading Decision
                                     ↓
                          • Technical Analysis
                          • Pattern Recognition
                          • Risk Assessment
                          • Multi-factor Decision
```

The AI agent:
1. Receives current market data
2. Sends it to the AI model (OpenAI/Anthropic/Google)
3. AI analyzes using advanced reasoning
4. Returns structured trading decision with reasoning
5. Agent executes the decision

## Testing Your Setup

### Step 1: Check if API keys are loaded

```bash
cd /home/turtle/Documents/code/ai_trading2
python3 -c "from config import Config; print('OpenAI:', 'SET' if Config.OPENAI_API_KEY else 'NOT SET'); print('Anthropic:', 'SET' if Config.ANTHROPIC_API_KEY else 'NOT SET'); print('Google:', 'SET' if Config.GOOGLE_API_KEY else 'NOT SET')"
```

### Step 2: Run with AI agents

```bash
source venv/bin/activate
python3 main.py
```

You should see:
```
✅ Added Anthropic Claude agent (using API)
✅ Added OpenAI GPT agent (using API)
✅ Added Google Gemini agent (using API)
✅ Added DeepSeek agent (using API)
```

Instead of:
```
⚠️  No Anthropic API key - using simulated agent
⚠️  No OpenAI API key - using simulated agent
⚠️  No Google API key - using simulated agent
⚠️  No DeepSeek API key - using simulated agent
```

## Cost Management

### Estimated Costs per Trading Session

**Assumptions:**
- 50 trading cycles
- Each agent makes ~15 decisions
- ~300 tokens per decision

**Per AI Agent:**
- OpenAI GPT-4: ~$0.30-0.45
- OpenAI GPT-3.5: ~$0.03-0.05
- Anthropic Claude: ~$0.25-0.40
- Google Gemini: ~$0.10-0.20 (or free on free tier)
- DeepSeek: ~$0.02-0.05 (very competitive pricing)

**Total for 4 AI agents:** ~$0.60-1.20 per session

### Reducing Costs

1. **Use simulated agents for testing**
   ```python
   # Keep API keys empty for cost-free testing
   ```

2. **Mix AI and simulated agents**
   ```python
   # Set only one API key, others will be simulated
   OPENAI_API_KEY=sk-...
   ANTHROPIC_API_KEY=
   GOOGLE_API_KEY=
   ```

3. **Use cheaper models**
   ```python
   # In openai_agent.py, change to:
   OpenAIAgent("agent_gpt", "GPT-3.5", "gpt-3.5-turbo")
   ```

4. **Reduce trading frequency**
   ```bash
   # In .env
   MARKET_DATA_UPDATE_INTERVAL=300  # 5 minutes instead of 1
   ```

## Troubleshooting

### "OpenAI library not installed"

```bash
pip install openai
```

### "Anthropic library not installed"

```bash
pip install anthropic
```

### "Google Generative AI library not installed"

```bash
pip install google-generativeai
```

### "Error calling [Model] API"

Check:
1. API key is correct in .env
2. API key has credits/quota available
3. Network connection is working
4. API service is not down

### "API not configured - skipping decision"

This means the API key is not set in .env. The agent will skip decisions but not crash. This is normal if you want to run without that specific AI model.

## Security Best Practices

1. **Never commit .env file to git** (already in .gitignore)
2. **Use environment-specific keys** (dev vs production)
3. **Set spending limits** on API dashboards
4. **Rotate keys regularly**
5. **Use read-only keys** where possible
6. **Monitor API usage** on provider dashboards

## Free Tier Information

### OpenAI
- New accounts get free credits
- After credits expire, need to add payment

### Anthropic
- Trial credits available
- Need payment method for continued use

### Google Gemini
- Generous free tier
- 60 requests per minute free
- Best option for cost-free testing

### DeepSeek
- Very competitive pricing
- Often cheaper than OpenAI/Anthropic
- Good performance-to-cost ratio

## Recommendation for Starting

**For Learning/Testing:**
```bash
# No API keys - use simulated agents (FREE)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
```

**For Evaluation:**
```bash
# Use only Google Gemini (FREE tier)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=your-google-key-here
```

**For Competition:**
```bash
# Use all four for fair comparison (PAID)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
DEEPSEEK_API_KEY=...
```

---

## Summary

| What You Want | What To Do |
|---------------|------------|
| Free testing | Don't set any API keys |
| Try one AI model | Set Google API key (free tier) |
| Compare AI models | Set all three API keys |
| Production use | Set API keys + monitor costs |

**Remember:** Start with simulated agents, then add AI models one at a time!
