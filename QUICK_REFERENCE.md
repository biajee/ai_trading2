# Quick Reference Guide

## 🚀 Getting Started (30 seconds)

```bash
# 1. Run the demo (uses simulated agents - FREE)
python3 demo.py

# That's it! No API keys needed for basic functionality.
```

## 🎛️ Two Key Flags

### Flag 1: Trading Mode (Mock vs Real)

```bash
# In .env file:
MOCK_TRADING=true   # 👈 Safe paper trading (DEFAULT)
MOCK_TRADING=false  # ⚠️  Real money trading
```

### Flag 2: Agent Intelligence (Simulated vs AI)

```bash
# In .env file:
OPENAI_API_KEY=           # Empty = Simulated agent (FREE)
OPENAI_API_KEY=sk-xxx     # Set = AI-powered agent (PAID)
```

## 📊 Four Operating Modes

| Mode | Mock Trading | API Keys | Cost | Use Case |
|------|--------------|----------|------|----------|
| **1. Safe Demo** | ✅ true | ❌ None | FREE | Learning, testing |
| **2. AI Evaluation** | ✅ true | ✅ Set | ~$1/session | Compare AI models |
| **3. Real (Simple)** | ❌ false | ❌ None | Exchange fees | Production simple |
| **4. Real (AI)** | ❌ false | ✅ Set | API + fees | Full production |

**Recommendation:** Start with Mode 1, progress to Mode 2, be very careful with Modes 3-4.

## 🔑 API Key Quick Setup

### Option 1: No Keys (Free)
```bash
# Leave .env as-is, run immediately
python3 demo.py
```

### Option 2: Google Only (Free Tier)
```bash
# In .env:
GOOGLE_API_KEY=your-google-key-here
# Get key: https://makersuite.google.com/app/apikey
```

### Option 3: All Three (Full Competition)
```bash
# In .env:
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

## 📝 Common Commands

```bash
# Test configuration
python3 test_config.py

# Run quick demo (10 cycles, 3 agents)
python3 demo.py

# Run full arena (50 cycles, 5 agents)
python3 main.py

# Start dashboard
python3 dashboard.py
# Then open http://127.0.0.1:8050

# Install dependencies
pip install -r requirements-minimal.txt  # Basic
pip install -r requirements-ai.txt       # + AI libraries
pip install -r requirements.txt          # Everything
```

## 🎯 Decision Tree

```
Want to try it?
│
├─ Just testing/learning?
│  └─ Use: python3 demo.py (no setup needed!)
│
├─ Want AI agents to compete?
│  ├─ Free option?
│  │  └─ Add Google API key → python3 main.py
│  └─ Full comparison?
│     └─ Add all 3 API keys → python3 main.py
│
└─ Ready for real money?
   ├─ Are you SURE?
   │  └─ Test in mock mode first!
   └─ Really ready?
      └─ Set MOCK_TRADING=false + Exchange keys
```

## 💡 Pro Tips

### 1. Start Free
```bash
# No API keys = Free forever
python3 demo.py
```

### 2. Test Configuration
```bash
python3 test_config.py
# See what's configured before running
```

### 3. Mix Agents
```bash
# Set only 1 API key to compare AI vs simulated
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
```

### 4. Monitor Costs
- Check API dashboards
- Set spending limits
- Use free tiers first

### 5. Safe Progression
```
Demo → Test Config → Add 1 API Key → Full AI → Real Trading
(Free)   (Check)      (Cheap)          (Cost)    (⚠️ Risk)
```

## 🆘 Troubleshooting

### "No module named 'openai'"
```bash
pip install openai
# or
pip install -r requirements-ai.txt
```

### "API not configured - skipping decision"
- This is NORMAL if you don't have API keys
- Agents will use simulated strategy instead
- Not an error, just informational

### "Exchange API credentials required"
- You set MOCK_TRADING=false without exchange keys
- Either add exchange keys OR set MOCK_TRADING=true

### Want to see AI agents?
```bash
# Check if detected:
python3 test_config.py

# Should show:
# ✅ OpenAI: SET
# ✅ Anthropic: SET
# ✅ Google: SET
```

## 📂 Important Files

```
.env                    # YOUR CONFIGURATION (API keys, flags)
README.md              # Main documentation
API_SETUP.md          # Detailed API key instructions
USAGE_GUIDE.md        # Mock vs Real trading guide
FEATURES.md           # Complete feature list
test_config.py        # Test your setup
demo.py               # Quick 10-cycle demo
main.py               # Full arena
```

## 🎓 Learning Path

### Day 1: Basics
```bash
python3 demo.py
# Watch simulated agents trade
```

### Day 2: Configuration
```bash
python3 test_config.py
# Understand the settings
```

### Day 3: Add AI
```bash
# Add Google API key (free tier)
python3 main.py
# See real AI decisions
```

### Week 2: Compare
```bash
# Add all 3 API keys
python3 main.py
# Watch AI models compete
```

### Month 2+: Production
```bash
# Only after thorough testing!
# Set MOCK_TRADING=false
# Start with small capital
```

## 🔄 Quick Mode Switching

### From: Free Testing
```bash
MOCK_TRADING=true
OPENAI_API_KEY=
```

### To: AI Evaluation  
```bash
MOCK_TRADING=true
OPENAI_API_KEY=sk-...  # Add this
```

### To: Real Trading (CAREFUL!)
```bash
MOCK_TRADING=false  # Change this
EXCHANGE_API_KEY=...  # Add this
EXCHANGE_API_SECRET=...  # Add this
```

## 📊 What Each File Does

| File | Purpose | Need API Keys? |
|------|---------|----------------|
| demo.py | Quick demo | ❌ No |
| main.py | Full arena | ⚠️ Optional (better with) |
| dashboard.py | Web UI | ❌ No |
| test_config.py | Check setup | ❌ No |

## ✅ Pre-flight Checklist

Before real trading:
- [ ] Tested extensively in mock mode
- [ ] Understand the strategy
- [ ] Set conservative capital
- [ ] Exchange API has IP restrictions
- [ ] Using sub-account with limited funds
- [ ] Monitoring system is ready
- [ ] Can afford to lose the capital
- [ ] Have stop-loss strategy

## 🎉 Success Indicators

You're ready when:
- ✅ `python3 test_config.py` shows green checks
- ✅ `python3 demo.py` runs without errors
- ✅ You understand mock vs real trading
- ✅ You know how API keys work
- ✅ Dashboard displays correctly

---

**Remember:** 
- 🆓 **Free mode works great** - no pressure to add API keys
- 🧪 **Test first** - mock trading is your friend
- 💡 **Learn gradually** - no rush to real trading
- 🤝 **Ask questions** - check docs or community

**Start here:** `python3 demo.py` 🚀
