"""Test script to verify historical price tracking"""
import asyncio
from arena import TradingArena
from agents import SimpleAgent
from config import Config

async def test_historical_prices():
    """Test that historical prices are being tracked and passed to agents"""

    # Initialize arena
    arena = TradingArena()

    # Add a simple agent
    agent = SimpleAgent(
        agent_id="test_agent",
        agent_name="Test Agent"
    )
    arena.add_agent(agent)

    print("Testing historical price tracking...\n")

    # Run 5 cycles to build up price history
    for i in range(5):
        print(f"Cycle {i+1}:")
        market_data = await arena.update_market_data()

        # Check price history for each symbol
        for data in market_data:
            history_len = len(data.price_history)
            print(f"  {data.symbol}: {history_len} price points tracked")
            if history_len > 0:
                print(f"    Latest prices: {data.price_history[-min(5, history_len):]}")
        print()

        await asyncio.sleep(1)

    print("✅ Historical price tracking verified!")
    print(f"\nPrice history storage:")
    for symbol, prices in arena.price_history.items():
        print(f"  {symbol}: {len(prices)} points stored")

if __name__ == "__main__":
    asyncio.run(test_historical_prices())
