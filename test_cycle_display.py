#!/usr/bin/env python3
"""Test script to demonstrate cycle tracking in the dashboard"""
import asyncio
import time
from arena import TradingArena
from agents import SimpleAgent
from config import Config


async def test_cycles():
    """Run a few cycles to test cycle tracking"""
    print("="*60)
    print("Testing Cycle Display Feature")
    print("="*60)

    # Create arena
    arena = TradingArena()

    # Add test agents
    agents = [
        SimpleAgent("agent_1", "Alice"),
        SimpleAgent("agent_2", "Bob"),
        SimpleAgent("agent_3", "Charlie")
    ]

    for agent in agents:
        arena.add_agent(agent)

    print(f"\n✅ Added {len(agents)} agents")
    print(f"📊 Starting Capital: ${Config.STARTING_CAPITAL:,.2f} each")

    # Run 5 cycles
    num_cycles = 5
    print(f"\n🔄 Running {num_cycles} trading cycles...")
    print("Watch the dashboard update in real-time!\n")

    for cycle_num in range(1, num_cycles + 1):
        print(f"\n{'='*60}")
        print(f"Cycle {cycle_num}/{num_cycles}")
        print(f"{'='*60}")

        await arena.run_trading_cycle()

        if cycle_num < num_cycles:
            print(f"\n⏳ Waiting 3 seconds before next cycle...")
            await asyncio.sleep(3)

    print(f"\n{'='*60}")
    print("✅ Test Complete!")
    print(f"{'='*60}")

    # Show cycle history summary
    print("\n📊 Cycle History Summary:")
    print("-" * 60)

    for agent_id, history in arena.cycle_history.items():
        agent_name = arena.agent_states[agent_id].agent_name
        print(f"\n{agent_name}:")

        for snapshot in history:
            print(
                f"  Cycle {snapshot['cycle']}: "
                f"${snapshot['portfolio_value']:,.2f} "
                f"({snapshot['total_return']:+.2f}%) "
                f"- {snapshot['total_trades']} trades"
            )

    print("\n" + "="*60)
    print("Dashboard Instructions:")
    print("="*60)
    print("1. Keep this script running")
    print("2. Open another terminal and run: python3 dashboard.py")
    print("3. Open http://localhost:8050 in your browser")
    print("4. Watch the chart show real cycle-by-cycle progression!")
    print("5. Hover over points to see detailed cycle info")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_cycles())
