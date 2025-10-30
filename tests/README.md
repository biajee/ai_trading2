# AI Trading Arena - Test Suite

Comprehensive unit tests for the AI Trading Arena project.

## Test Coverage

### 1. **Model Tests** (`test_models.py`)
Tests for data models including:
- Trade creation and status
- Position tracking and P&L calculations
- Agent state management
- Portfolio value calculations
- Win rate and return calculations
- Market data structures

**14 tests total**

### 2. **Exchange Tests** (`test_exchange.py`)
Tests for mock exchange functionality:
- Market data retrieval
- Trade execution (buy/sell)
- Balance management
- Insufficient funds/holdings handling
- Multiple market data queries

**9 tests total**

### 3. **Agent Tests** (`test_agents.py`)
Tests for agent decision making:
- Agent creation and initialization
- Buy decisions using ask price
- Sell decisions with profit targets
- Stop-loss functionality
- Trade reasoning

**6 tests total**

### 4. **Arena Tests** (`test_arena.py`)
Tests for arena orchestration:
- Agent addition and management
- Buy trade execution and state updates
- Sell trade execution and P&L tracking
- Position removal when fully sold
- Portfolio value calculations
- State persistence to file
- Leaderboard calculations

**12 tests total**

### 5. **Dashboard Tests** (`test_dashboard.py`)
Tests for dashboard data loading:
- Loading from state file
- Handling missing files
- Handling empty data
- Handling malformed JSON
- Data structure validation

**4 tests total**

### 6. **Short Position Tests** (`test_short_positions.py`)
Tests for short selling functionality:
- Position type detection (long vs short)
- Short position value calculations
- Short position P&L (profit when price drops)
- SHORT trade execution
- COVER trade execution
- Profit/loss tracking for shorts
- TradeType enum validation

**9 tests total**

## Running Tests

### Run All Tests
```bash
# Using unittest
python3 -m unittest discover tests -v

# Using the test runner script
python3 run_tests.py
```

### Run Specific Test Module
```bash
# Test models only
python3 -m unittest tests.test_models -v

# Test exchange only
python3 -m unittest tests.test_exchange -v

# Test agents only
python3 -m unittest tests.test_agents -v

# Test arena only
python3 -m unittest tests.test_arena -v

# Test dashboard only
python3 -m unittest tests.test_dashboard -v

# Or using the runner
python3 run_tests.py test_models
```

### Run Specific Test Class
```bash
python3 -m unittest tests.test_models.TestPosition -v
```

### Run Specific Test Method
```bash
python3 -m unittest tests.test_models.TestPosition.test_position_pnl -v
```

## Test Results

**Total: 54 tests**

All tests passing ✅

## Key Test Scenarios

### Buy Trading (Long)
- ✅ Agents use **ask price** for buying
- ✅ Cash balance is deducted correctly
- ✅ Positions are created/updated
- ✅ Insufficient funds are handled

### Sell Trading (Close Long)
- ✅ Agents use **bid price** for selling
- ✅ P&L is calculated correctly
- ✅ Win/loss tracking works
- ✅ Positions are reduced/removed
- ✅ Cash balance is increased
- ✅ Insufficient holdings are handled

### Short Trading
- ✅ Agents use **bid price** for shorting (selling borrowed asset)
- ✅ Cash balance is increased (receive proceeds)
- ✅ Negative positions are created
- ✅ P&L profits when price decreases
- ✅ Short positions tracked correctly

### Cover Trading (Close Short)
- ✅ Agents use **ask price** for covering (buying back)
- ✅ Cash balance is decreased (pay to buy back)
- ✅ Short positions are reduced/removed
- ✅ P&L is calculated correctly
- ✅ Insufficient cash/position handled

### Position Management
- ✅ Position values calculated correctly
- ✅ Unrealized P&L tracked
- ✅ Average entry price maintained
- ✅ Positions removed when empty

### State Persistence
- ✅ Arena state saved to JSON
- ✅ Dashboard loads state correctly
- ✅ Handles missing/corrupt files gracefully

## Test Coverage by Component

| Component | Tests | Coverage |
|-----------|-------|----------|
| Models | 14 | Complete data model validation |
| Exchange | 9 | Full buy/sell/short/cover execution |
| Agents | 6 | Decision making and pricing |
| Arena | 12 | Full trading lifecycle |
| Dashboard | 4 | Data loading and display |
| Short Positions | 9 | Complete short selling functionality |

## Notes

- Tests use the mock exchange for fast, deterministic execution
- Tests clean up `arena_state.json` after running
- Async tests properly handled with `asyncio.run()`
- Position P&L calculations verified with precision
- Random agent behavior tested over multiple iterations
