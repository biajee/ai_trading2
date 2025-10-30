"""Quick demo of the AI Trading Arena"""
import asyncio
from arena import TradingArena
from agents import SimpleAgent
from config import Config


async def demo():
    """Run a quick demo of the trading arena"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║           🤖 AI TRADING ARENA - QUICK DEMO 🤖            ║
    ║                                                           ║
    ║   This demo runs 10 quick trading cycles to show          ║
    ║   how different AI agents compete in the market.          ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Create arena
    arena = TradingArena()
    
    # Add 3 competing agents for quick demo (using simple agents for speed)
    print("Note: This demo uses simulated agents. To use real AI models,")
    print("add your API keys to the .env file and run main.py instead.\n")
    
    agents = [
        SimpleAgent("agent_1", "Claude-4.5-Sonnet-Simulated"),
        SimpleAgent("agent_2", "GPT-4-Simulated"),
        SimpleAgent("agent_3", "Gemini-Pro-Simulated"),
    ]
    
    for agent in agents:
        arena.add_agent(agent)
    
    print(f"\n⚡ Running quick demo with {len(agents)} agents...")
    print(f"💰 Each agent starts with ${Config.STARTING_CAPITAL:,.2f}")
    print(f"🎮 Mode: {Config.get_trading_mode_str()}\n")
    
    # Start the arena with shorter cycles for demo
    try:
        await arena.start(
            cycles=10,  # Just 10 cycles for demo
            cycle_interval=2  # 2 seconds between cycles
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        arena.stop()
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   ✅ Demo Complete!                                       ║
    ║                                                           ║
    ║   To run the full arena: python main.py                   ║
    ║   To view dashboard: python dashboard.py                  ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    asyncio.run(demo())
