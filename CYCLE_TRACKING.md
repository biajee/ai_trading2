# Cycle Tracking & Dashboard Display

The dashboard now displays **real-time cycle-by-cycle progression** showing how agents perform across all trading cycles.

## Features Added

### 1. **Cycle Tracking in Arena**

The arena now tracks every trading cycle:

```python
# New arena attributes
self.current_cycle = 0                     # Current cycle number
self.cycle_history: Dict[str, List[dict]] # Historical data per agent
```

After each cycle, the arena saves a snapshot containing:
- Cycle number
- Timestamp
- Portfolio value
- Cash balance
- Total return percentage
- Number of trades
- Win rate
- Number of open positions

### 2. **Historical Data Storage**

State file (`arena_state.json`) now includes:
```json
{
  "timestamp": "2025-01-01T12:00:00",
  "current_cycle": 15,
  "agents": [
    {
      "agent_name": "Alice",
      "portfolio_value": 11500.00,
      "cycle_history": [
        {
          "cycle": 1,
          "timestamp": "2025-01-01T11:00:00",
          "portfolio_value": 10000.00,
          "total_return": 0.0,
          "total_trades": 0,
          "win_rate": 0.0
        },
        {
          "cycle": 2,
          "timestamp": "2025-01-01T11:10:00",
          "portfolio_value": 10200.00,
          "total_return": 2.0,
          "total_trades": 3,
          "win_rate": 66.7
        },
        ...
      ]
    }
  ]
}
```

### 3. **Enhanced Dashboard Chart**

The performance chart now shows:

**Real Cycle Progression**
- X-axis: Actual cycle numbers
- Y-axis: Portfolio values
- Lines connect real data points (no interpolation)

**Rich Hover Information**
- Cycle number
- Portfolio value
- Return percentage
- Number of trades
- Win rate

**Visual Features**
- Solid lines for active agents with history
- Dashed lines for agents without history yet
- Different colors per agent
- Markers at each cycle point

### 4. **Arena Status Widget**

New widget showing:
- **Current Cycle Number** (large, bold display)
- **Active Agents** count
- **Last Update** timestamp

## How It Works

### Arena Side

1. **Cycle Initialization**
```python
async def run_trading_cycle(self):
    self.current_cycle += 1  # Increment cycle
    # ... run trading logic ...
    self.save_cycle_snapshot()  # Save after each cycle
```

2. **Snapshot Creation**
```python
def save_cycle_snapshot(self):
    for agent_id, state in self.agent_states.items():
        snapshot = {
            "cycle": self.current_cycle,
            "portfolio_value": state.total_portfolio_value,
            "total_return": state.total_return,
            # ... more metrics ...
        }
        self.cycle_history[agent_id].append(snapshot)
```

3. **State Persistence**
```python
def save_state(self):
    state_data = {
        "current_cycle": self.current_cycle,
        "agents": [
            {
                "agent_name": ...,
                "cycle_history": self.cycle_history[agent_id],
                # ... current state ...
            }
        ]
    }
```

### Dashboard Side

1. **Load Cycle History**
```python
agents = load_agent_data()
for agent in agents:
    cycle_history = agent.get('cycle_history', [])
```

2. **Plot Real Data**
```python
if cycle_history:
    cycles = [h['cycle'] for h in cycle_history]
    values = [h['portfolio_value'] for h in cycle_history]

    fig.add_trace(go.Scatter(
        x=cycles,
        y=values,
        mode='lines+markers',
        name=agent['name']
    ))
```

3. **Rich Hover Text**
```python
hover_text = [
    f"Cycle {h['cycle']}<br>"
    f"Value: ${h['portfolio_value']:,.2f}<br>"
    f"Return: {h['total_return']:+.2f}%<br>"
    # ... more info ...
    for h in cycle_history
]
```

## Usage

### Test the Feature

Run the test script to see cycles in action:

```bash
# Terminal 1: Run cycles
python3 test_cycle_display.py

# Terminal 2: Start dashboard
python3 dashboard.py

# Browser: Open http://localhost:8050
```

The test script runs 5 cycles with 3-second intervals, allowing you to watch the dashboard update in real-time.

### Production Use

When running the arena normally:

```bash
# Start arena (runs cycles automatically)
python3 main.py

# In another terminal, start dashboard
python3 dashboard.py

# Open http://localhost:8050
```

## What You'll See

### Performance Chart

Before (fake data):
```
📈 Portfolio Value Progression
[Simple linear interpolation between start and end]
```

After (real data):
```
📈 Portfolio Value Over Trading Cycles
[Actual cycle-by-cycle progression showing:
 - Real ups and downs
 - Trading decisions impact
 - Agent performance divergence]
```

### Arena Status Widget

```
🔄 Arena Status
━━━━━━━━━━━━━━━━
Cycle: #15
Active Agents: 3
Last Update: 14:32:45
```

### Hover Details

When you hover over any point:
```
Cycle 10
Value: $11,234.56
Return: +12.35%
Trades: 8
Win Rate: 75.0%
```

## Benefits

✅ **Real progression tracking** - See exactly how agents performed each cycle
✅ **Performance comparison** - Compare agent strategies over time
✅ **Trend identification** - Spot winning/losing streaks
✅ **Decision validation** - Correlate trades with performance changes
✅ **Historical analysis** - Full cycle-by-cycle history preserved

## Technical Details

### Memory Usage

Each cycle snapshot is ~200 bytes per agent:
- 100 cycles × 10 agents = ~200 KB (minimal)

### Update Frequency

- Arena: Saves after every cycle
- Dashboard: Auto-refreshes every N seconds (configurable)
- No lag between arena and dashboard

### Data Persistence

- Stored in `arena_state.json`
- Survives arena restarts
- Can be analyzed offline

## Example Output

Console output when running cycles:

```
============================================================
🔄 Trading Cycle #1 - 2025-01-01 14:30:00
============================================================
📊 Alice: BUY 0.1 BTC/USDT @ $50,000.00
   Reasoning: Positive momentum detected
📊 Bob: HOLD
   Reasoning: No strong signal
============================================================
🏆 LEADERBOARD - MOCK TRADING MODE
============================================================
Rank   Agent                Portfolio        Return    Trades   Win Rate
1      Alice                $10,150.00      +1.50%    1        0.0%
2      Bob                  $10,000.00      +0.00%    0        0.0%
============================================================
```

Dashboard shows this immediately in the chart!

## Troubleshooting

**Chart shows dashed line:**
- Arena hasn't completed any cycles yet
- Wait for at least one cycle to complete

**No cycle history:**
- Delete `arena_state.json` and restart
- Check arena is calling `save_cycle_snapshot()`

**Data not updating:**
- Check dashboard auto-refresh interval
- Verify `arena_state.json` is being written
- Restart dashboard to clear cache

## Future Enhancements

Potential additions:
- 📊 Per-cycle trade details
- 📈 Return distribution histogram
- 🎯 Cycle-by-cycle win rate chart
- 📉 Drawdown tracking
- 🔄 Compare specific cycle ranges

---

The cycle tracking feature provides complete visibility into agent performance over time, making the dashboard a powerful tool for analyzing trading strategies!
