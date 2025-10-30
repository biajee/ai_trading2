"""Main entry point for AI Trading Arena"""
import asyncio
from arena import TradingArena
from agents import SimpleAgent, OpenAIAgent, AnthropicAgent, GoogleAgent, DeepSeekAgent
from config import Config


async def main():
    """Main function to run the trading arena"""
    # Create arena
    arena = TradingArena()
    
    # Add competing agents based on config.json
    agents = []
    agent_id_counter = 1
    
    print("\n🤖 Loading agents from config.json...")
    print("=" * 60)
    
    # Load AI agents dynamically from config
    ai_agent_types = ["deepseek", "openai", "anthropic", "google"]
    
    for agent_type in ai_agent_types:
        if Config.is_agent_enabled(agent_type):
            agent_config = Config.get_agent_config(agent_type)
            api_key = Config.get_api_key(agent_type)
            agent_name = agent_config.get("name", agent_type.capitalize())
            agent_class_name = agent_config.get("agent_class")
            
            if api_key and agent_class_name:
                # Get the agent class dynamically
                agent_class = globals().get(agent_class_name)
                if agent_class:
                    agents.append(agent_class(
                        f"agent_{agent_id_counter}",
                        agent_name,
                        agent_config.get("model", "")
                    ))
                    print(f"✅ Added {agent_name} agent (using API)")
                    agent_id_counter += 1
                else:
                    print(f"⚠️  Agent class {agent_class_name} not found")
            else:
                # No API key or class - use simulated agent
                agents.append(SimpleAgent(
                    f"agent_{agent_id_counter}",
                    f"{agent_name}-Simulated"
                ))
                if not api_key:
                    print(f"⚠️  {agent_name} enabled but no API key - using simulated agent")
                agent_id_counter += 1
    
    # Simple agents
    if Config.is_agent_enabled("simple_agents"):
        simple_config = Config.get_agent_config("simple_agents")
        count = simple_config.get("count", 2)
        names = simple_config.get("names", [f"Simple-Agent-{i+1}" for i in range(count)])
        
        for i, name in enumerate(names[:count]):
            agents.append(SimpleAgent(f"agent_{agent_id_counter}", name))
            print(f"✅ Added simple agent: {name}")
            agent_id_counter += 1
    
    if not agents:
        print("❌ No agents enabled in config.json!")
        print("💡 Edit config.json to enable agents")
        return
    
    print("=" * 60)
    print(f"\n📊 Total agents: {len(agents)}\n")
    
    for agent in agents:
        arena.add_agent(agent)
    
    # Start the arena with settings from config
    cycles = Config.COMPETITION_CYCLES
    interval = Config.COMPETITION_CYCLE_INTERVAL
    
    try:
        await arena.start(cycles=cycles, cycle_interval=interval)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        arena.stop()


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║           🤖 AI TRADING ARENA 🤖                         ║
    ║                                                           ║
    ║   Where AI Models Compete in Crypto Trading              ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(main())
