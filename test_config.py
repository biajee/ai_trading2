#!/usr/bin/env python3
"""Test configuration and API key setup"""
from config import Config

print("=" * 60)
print("AI Trading Arena - Configuration Test")
print("=" * 60)

print(f"\n📊 Trading Mode: {Config.get_trading_mode_str()}")
print(f"💰 Starting Capital: ${Config.STARTING_CAPITAL:,.2f}")

print("\n🔑 API Keys Status:")
print(f"  OpenAI:    {'✅ SET' if Config.OPENAI_API_KEY else '❌ NOT SET'}")
print(f"  Anthropic: {'✅ SET' if Config.ANTHROPIC_API_KEY else '❌ NOT SET'}")
print(f"  Google:    {'✅ SET' if Config.GOOGLE_API_KEY else '❌ NOT SET'}")
print(f"  DeepSeek:  {'✅ SET' if Config.DEEPSEEK_API_KEY else '❌ NOT SET'}")

print("\n📈 Trading Pairs:")
for pair in Config.TRADING_PAIRS:
    print(f"  • {pair}")

print("\n⚙️  Risk Management:")
print(f"  Max Position Size: {Config.MAX_POSITION_SIZE * 100:.1f}%")
print(f"  Max Leverage: {Config.MAX_LEVERAGE}x")
print(f"  Max Drawdown: {Config.MAX_DRAWDOWN * 100:.1f}%")

print("\n🤖 Agent Configuration:")
if not Config.OPENAI_API_KEY and not Config.ANTHROPIC_API_KEY and not Config.GOOGLE_API_KEY and not Config.DEEPSEEK_API_KEY:
    print("  ⚠️  No AI API keys configured")
    print("  ➜  Agents will use simulated strategy")
    print("  ➜  Add API keys to .env to enable AI-powered agents")
    print("  ➜  See API_SETUP.md for instructions")
else:
    print("  ✅ AI API keys detected")
    if Config.OPENAI_API_KEY:
        print("  ➜  OpenAI GPT agents: ENABLED")
    if Config.ANTHROPIC_API_KEY:
        print("  ➜  Anthropic Claude agents: ENABLED")
    if Config.GOOGLE_API_KEY:
        print("  ➜  Google Gemini agents: ENABLED")
    if Config.DEEPSEEK_API_KEY:
        print("  ➜  DeepSeek agents: ENABLED")

print("\n" + "=" * 60)

# Test importing agents
print("\n🧪 Testing Agent Imports:")
try:
    from agents import SimpleAgent, OpenAIAgent, AnthropicAgent, GoogleAgent, DeepSeekAgent
    print("  ✅ All agent classes imported successfully")
except Exception as e:
    print(f"  ❌ Error importing agents: {e}")

# Test AI libraries
print("\n📦 AI Library Status:")
try:
    import openai
    print("  ✅ openai library installed")
except ImportError:
    print("  ❌ openai library not installed (pip install openai)")

try:
    import anthropic
    print("  ✅ anthropic library installed")
except ImportError:
    print("  ❌ anthropic library not installed (pip install anthropic)")

try:
    import google.generativeai
    print("  ✅ google-generativeai library installed")
except ImportError:
    print("  ❌ google-generativeai library not installed (pip install google-generativeai)")

print("\n" + "=" * 60)
print("✅ Configuration test complete!")
print("=" * 60)

if not Config.OPENAI_API_KEY and not Config.ANTHROPIC_API_KEY and not Config.GOOGLE_API_KEY:
    print("\n💡 Tip: To enable AI-powered agents:")
    print("   1. Get API keys from AI providers")
    print("   2. Add them to .env file")
    print("   3. See API_SETUP.md for detailed instructions")
