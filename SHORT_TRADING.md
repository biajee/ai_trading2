# Short Selling Guide

The AI Trading Arena now supports **short selling** - a trading strategy where you profit from declining prices.

## Overview

### Four Trade Types

1. **BUY** - Open long position (buy and own asset)
2. **SELL** - Close long position (sell owned asset)
3. **SHORT** - Open short position (borrow and sell asset)
4. **COVER** - Close short position (buy back borrowed asset)

## How Short Selling Works

### Opening a Short Position (SHORT)

When you SHORT an asset:
1. **Borrow** the asset from the broker
2. **Sell** it immediately at current market price
3. **Receive cash** from the sale (increases cash balance)
4. **Create negative position** (quantity is negative)
5. **Use bid price** (selling to the market)

```python
# Example: Short 0.1 BTC at $50,000
trade = Trade(
    trade_type=TradeType.SHORT,
    quantity=0.1,
    price=50000.0,  # Bid price
    total_value=5000.0
)
# Result: +$5,000 cash, -0.1 BTC position
```

### Closing a Short Position (COVER)

When you COVER (buy back):
1. **Buy back** the asset at current market price
2. **Return** it to the broker
3. **Pay cash** for the purchase (decreases cash balance)
4. **Reduce/close negative position**
5. **Use ask price** (buying from the market)

```python
# Example: Cover 0.1 BTC at $49,000 (profit!)
trade = Trade(
    trade_type=TradeType.COVER,
    quantity=0.1,
    price=49000.0,  # Ask price
    total_value=4900.0
)
# Result: -$4,900 cash, closes -0.1 BTC position
# P&L: $5,000 - $4,900 = +$100 profit
```

## Profit & Loss

### Short Position P&L Formula

```python
# Unrealized P&L for open short
pnl = (entry_price - current_price) * abs(quantity)

# Realized P&L when covering
pnl = proceeds_from_short - cost_to_cover
```

### Examples

#### Profitable Short Trade
```
1. SHORT 0.1 BTC at $50,000 → Receive $5,000
2. Price drops to $49,000
3. COVER 0.1 BTC at $49,000 → Pay $4,900
4. Profit: $5,000 - $4,900 = $100 ✅
```

#### Losing Short Trade
```
1. SHORT 0.1 BTC at $50,000 → Receive $5,000
2. Price rises to $51,000
3. COVER 0.1 BTC at $51,000 → Pay $5,100
4. Loss: $5,000 - $5,100 = -$100 ❌
```

## Position Representation

Positions use **signed quantities**:
- **Positive quantity**: Long position (you own the asset)
- **Negative quantity**: Short position (you owe the asset)

```python
# Long position
position = Position(
    quantity=0.1,  # Own 0.1 BTC
    average_entry_price=50000.0,
    current_price=51000.0
)
position.is_long  # True
position.current_value  # +5100.0
position.unrealized_pnl  # +100.0 (profit)

# Short position
position = Position(
    quantity=-0.1,  # Owe 0.1 BTC
    average_entry_price=50000.0,
    current_price=49000.0
)
position.is_short  # True
position.current_value  # -4900.0 (liability)
position.unrealized_pnl  # +100.0 (profit - price dropped)
```

## Agent Strategy

The SimpleAgent now includes short selling logic:

### When to SHORT
- Detects **strong negative momentum** (>2% drop)
- 40% chance to short instead of buying the dip
- Uses **bid price** to sell borrowed asset
- Risks 2-4% of portfolio value

### When to COVER
- **Take profit**: When short position has >5% gain
- **Stop loss**: When short position has >3% loss
- Uses **ask price** to buy back asset
- Covers 50-100% of position

```python
# Example agent short decision
if price_change_percent_24h < -2:
    if random.random() > 0.6:  # 40% chance
        # Open short position
        return Trade(
            trade_type=TradeType.SHORT,
            quantity=calculated_quantity,
            price=selected.bid,  # Sell at bid
            reasoning="Strong negative momentum detected"
        )
```

## Risk Management

### Short Selling Risks

1. **Unlimited Loss Potential**
   - Long positions: max loss = investment
   - Short positions: max loss = infinite (price can rise indefinitely)

2. **Price Increases Hurt**
   - Lose money when price goes UP
   - Must buy back at higher price

3. **Requires Margin**
   - Need sufficient cash to cover potential losses

### Agent Safeguards

✅ **Stop losses**: Auto-cover when loss exceeds 3%
✅ **Position sizing**: Only risk 2-4% per trade
✅ **Profit taking**: Lock in gains at 5%+
✅ **Cash requirements**: Validate sufficient funds

## Exchange Behavior

The mock exchange handles all four trade types:

```python
# SHORT trade
- Increases cash balance (receive proceeds)
- Creates negative holdings
- No upfront cash required

# COVER trade
- Decreases cash balance (pay to buy back)
- Reduces negative holdings
- Requires sufficient cash
- Validates short position exists
```

## Dashboard Display

Short positions are displayed with:
- **Negative quantity** indicating short
- **P&L calculation** showing profit/loss
- **Recent trades** marked with 📉 SHORT or 📈 COVER

## Testing

Comprehensive test coverage (9 tests):
- Position type detection
- Short P&L calculations
- SHORT trade execution
- COVER trade execution
- Profit and loss scenarios
- Edge cases and validation

Run tests:
```bash
python3 -m unittest tests.test_short_positions -v
```

## Example Trading Sequence

```python
# 1. Agent detects bearish signal
price_change = -3.5%  # Strong decline

# 2. Agent decides to SHORT
trade = SHORT 0.1 BTC @ $50,000 (bid)
cash: $10,000 → $15,000
position: 0 → -0.1 BTC

# 3. Price continues to fall
current_price: $48,000
unrealized_pnl: +$200

# 4. Agent takes profit by COVERING
trade = COVER 0.1 BTC @ $48,000 (ask)
cash: $15,000 → $10,200
position: -0.1 BTC → 0
realized_pnl: +$200 ✅
```

## Key Takeaways

✅ **SHORT** = Sell borrowed asset (receive cash, create negative position)
✅ **COVER** = Buy back borrowed asset (pay cash, close negative position)
✅ **Profit** when price **decreases**
✅ **Loss** when price **increases**
✅ Use **bid price** for SHORT, **ask price** for COVER
✅ Negative quantities represent short positions
✅ P&L calculation works for both long and short

---

**Warning**: Short selling is a high-risk strategy. In the real market, losses can be unlimited if the price rises significantly. Always use proper risk management!
