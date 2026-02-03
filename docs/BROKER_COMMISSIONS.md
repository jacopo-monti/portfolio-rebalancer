# Broker Commissions

This document explains how to use the broker commission feature in Portfolio Rebalancer.

## Overview

Broker commissions are transaction fees charged by your broker when buying or selling assets. The rebalancer now accounts for these costs when calculating cash flow requirements, ensuring you have enough cash to cover both:

1. **Purchase costs** (asset price + buy commissions)
2. **Sale proceeds** (asset price - taxes - sell commissions)

## Commission Structure

Each asset can have **separate commission structures** for buying and selling, with four components each:

### Buy Commissions

- **commission_buy_fixed**: Fixed fee per buy transaction (e.g., €2.50)
- **commission_buy_percent**: Percentage of transaction value (e.g., 0.001 = 0.1%)
- **commission_buy_min**: Minimum commission for percentage part (e.g., €1.00)
- **commission_buy_max**: Maximum commission for percentage part (e.g., €10.00)

### Sell Commissions

- **commission_sell_fixed**: Fixed fee per sell transaction (e.g., €2.50)
- **commission_sell_percent**: Percentage of transaction value (e.g., 0.001 = 0.1%)
- **commission_sell_min**: Minimum commission for percentage part (e.g., €1.00)
- **commission_sell_max**: Maximum commission for percentage part (e.g., €10.00)

## How Commissions Are Calculated

For any operation (buy or sell):

1. **Calculate percentage commission**:
   ```
   percentage_commission = operation_value × percent_rate
   ```

2. **Apply min/max bounds** (if specified):
   ```
   if min > 0: percentage_commission = max(percentage_commission, min)
   if max > 0: percentage_commission = min(percentage_commission, max)
   ```

3. **Add fixed commission**:
   ```
   total_commission = bounded_percentage_commission + fixed_commission
   ```

### Examples

#### Example 1: Fixed Commission Only
```
Fixed: €2.50
Percent: 0%

Buy 10 shares @ €100 each:
Operation value: €1,000
Commission: €2.50
Total cost: €1,002.50
```

#### Example 2: Percentage Commission Only
```
Fixed: €0
Percent: 0.1% (0.001)

Buy 10 shares @ €100 each:
Operation value: €1,000
Commission: €1,000 × 0.001 = €1.00
Total cost: €1,001.00
```

#### Example 3: Combined Fixed + Percentage
```
Fixed: €2.50
Percent: 0.1% (0.001)

Buy 10 shares @ €100 each:
Operation value: €1,000
Percentage commission: €1,000 × 0.001 = €1.00
Total commission: €1.00 + €2.50 = €3.50
Total cost: €1,003.50
```

#### Example 4: Percentage with Minimum
```
Fixed: €0
Percent: 0.1% (0.001)
Min: €5.00

Buy 2 shares @ €100 each:
Operation value: €200
Percentage commission: €200 × 0.001 = €0.20
Actual commission: max(€0.20, €5.00) = €5.00  ← minimum applied
Total cost: €205.00
```

#### Example 5: Percentage with Maximum
```
Fixed: €0
Percent: 1% (0.01)
Max: €10.00

Buy 200 shares @ €100 each:
Operation value: €20,000
Percentage commission: €20,000 × 0.01 = €200
Actual commission: min(€200, €10.00) = €10.00  ← maximum applied
Total cost: €20,010.00
```

## Using Commissions in Excel

### Excel File Format

Your Excel file should have these columns (in order):

| Col | Header | Description | Example |
|-----|--------|-------------|--------|
| A | Symbol | Asset ticker | VWCE |
| B | Quantity | Shares owned | 50 |
| C | Price | Current price | 100.00 |
| D | Avg Cost | Purchase price | 95.00 |
| E | Tax Rate | Capital gains tax | 0.26 |
| F | Target Weight | Target allocation | 0.60 |
| G | Comm Buy Fixed | Fixed buy fee (€) | 2.50 |
| H | Comm Buy % | Buy fee % (decimal) | 0.001 |
| I | Comm Buy Min | Min buy fee (€) | 1.00 |
| J | Comm Buy Max | Max buy fee (€) | 10.00 |
| K | Comm Sell Fixed | Fixed sell fee (€) | 2.50 |
| L | Comm Sell % | Sell fee % (decimal) | 0.001 |
| M | Comm Sell Min | Min sell fee (€) | 1.00 |
| N | Comm Sell Max | Max sell fee (€) | 10.00 |

### Example Excel Data

```
Cash Available: €1,000

Symbol | Qty | Price | Avg Cost | Tax  | Target | BuyFix | Buy%  | BuyMin | BuyMax | SellFix | Sell% | SellMin | SellMax
VWCE   | 50  | 100   | 95       | 0.26 | 0.60   | 2.50   | 0.001 | 1.00   | 10.00  | 2.50    | 0.001 | 1.00    | 10.00
AGGH   | 30  | 110   | 108      | 0.26 | 0.25   | 2.50   | 0.001 | 1.00   | 10.00  | 2.50    | 0.001 | 1.00    | 10.00
EIMI   | 20  | 135   | 130      | 0.26 | 0.15   | 2.50   | 0.001 | 1.00   | 10.00  | 2.50    | 0.001 | 1.00    | 10.00
```

### Loading and Using Excel File

```python
from portfolio_rebalancer.io import ExcelIO
from portfolio_rebalancer.engine import RebalancingEngine

# Load portfolio from Excel (with commissions)
io = ExcelIO()
portfolio = io.read_portfolio("my_portfolio.xlsx")

# Rebalance
engine = RebalancingEngine()
result = engine.rebalance(portfolio)

# Save results
io.write_result(result, "rebalancing_result.xlsx")
```

**Note**: Commission columns are optional. If missing or empty, they default to 0.0 (no commission).

## Using Commissions in Python

### Simple Example

```python
from portfolio_rebalancer.models import Portfolio, Asset
from portfolio_rebalancer.engine import RebalancingEngine

# Create assets with commissions
portfolio = Portfolio(
    assets=[
        Asset(
            symbol="VWCE",
            quantity=50.0,
            price=100.0,
            avg_cost=95.0,
            tax_rate=0.26,
            target_weight=0.60,
            # Buy commissions: €2.50 fixed + 0.1% (min €1, max €10)
            commission_buy_fixed=2.50,
            commission_buy_percent=0.001,
            commission_buy_min=1.00,
            commission_buy_max=10.00,
            # Sell commissions: same structure
            commission_sell_fixed=2.50,
            commission_sell_percent=0.001,
            commission_sell_min=1.00,
            commission_sell_max=10.00,
        ),
        Asset(
            symbol="AGGH",
            quantity=30.0,
            price=110.0,
            avg_cost=108.0,
            tax_rate=0.26,
            target_weight=0.40,
            # No commissions for this asset (all default to 0.0)
        ),
    ],
    cash_available=1000.0,
)

# Rebalance
engine = RebalancingEngine()
result = engine.rebalance(portfolio)

# Check impact of commissions
print(f"Total cash needed: €{abs(result.cash_flow):,.2f}")
print(f"Total cash in: €{result.total_cash_in:,.2f}")
print(f"Total cash out: €{result.total_cash_out:,.2f}")
```

### Different Commissions for Buy/Sell

You can specify different commission structures for buying and selling:

```python
Asset(
    symbol="STOCK",
    quantity=100.0,
    price=50.0,
    avg_cost=45.0,
    tax_rate=0.26,
    target_weight=0.50,
    # Cheap to buy (flat €1 fee)
    commission_buy_fixed=1.00,
    # Expensive to sell (€5 + 0.5%)
    commission_sell_fixed=5.00,
    commission_sell_percent=0.005,
)
```

## Impact on Cash Flow

Commissions directly affect the cash flow calculation:

### Without Commissions

```
Cash Flow = Cash In (from sales) - Cash Out (for purchases)
          = (sale_proceeds - taxes) - purchase_costs
```

### With Commissions

```
Cash Flow = Cash In (from sales) - Cash Out (for purchases)
          = (sale_proceeds - taxes - sell_commissions) - (purchase_costs + buy_commissions)
```

### Example Impact

**Scenario**: Sell €1,000 of Asset A, buy €1,000 of Asset B

**Without commissions**:
- Sell A: €1,000 (gross) - €26 (tax) = €974 cash in
- Buy B: €1,000 cash out
- Cash flow: €974 - €1,000 = **-€26** (need to add €26)

**With €2.50 commission on each side**:
- Sell A: €1,000 - €26 (tax) - €2.50 (commission) = €971.50 cash in
- Buy B: €1,000 + €2.50 (commission) = €1,002.50 cash out
- Cash flow: €971.50 - €1,002.50 = **-€31** (need to add €31)

**Result**: Commissions increase cash needed by €5.

## Common Broker Commission Structures

### Degiro
```python
# ETFs on core selection: €1 per transaction
commission_buy_fixed=1.00
commission_sell_fixed=1.00
```

### Interactive Brokers
```python
# Tiered pricing: 0.05% (min €1.25, max 0.05% of trade value)
commission_buy_percent=0.0005
commission_buy_min=1.25
commission_sell_percent=0.0005
commission_sell_min=1.25
```

### Fineco
```python
# Italian broker: €2.95 for trades up to €5,000
# For simplicity, using flat rate:
commission_buy_fixed=2.95
commission_sell_fixed=2.95
```

### Directa
```python
# 0.19% (min €1.50, max €19)
commission_buy_percent=0.0019
commission_buy_min=1.50
commission_buy_max=19.00
commission_sell_percent=0.0019
commission_sell_min=1.50
commission_sell_max=19.00
```

## Best Practices

### 1. Always Specify All Four Components

Even if you don't need them, explicitly set unused fields to 0.0 for clarity:

```python
Asset(
    symbol="ETF",
    # ... other fields ...
    commission_buy_fixed=2.50,
    commission_buy_percent=0.0,   # No percentage
    commission_buy_min=0.0,       # No min
    commission_buy_max=0.0,       # No max
)
```

### 2. Verify Your Broker's Fee Structure

Check your broker's website or fee schedule to ensure accurate values:
- Some brokers have different fees for different exchanges
- Some have tiered pricing based on monthly volume
- Some charge custody fees (not transaction fees)

### 3. Test Before Using

Run a test rebalance with a small portfolio to verify commission calculations:

```python
# Create test portfolio
test_portfolio = Portfolio(
    assets=[
        Asset(
            symbol="TEST",
            quantity=10.0,
            price=100.0,
            avg_cost=100.0,
            tax_rate=0.0,  # No tax for simplicity
            target_weight=1.0,
            commission_buy_fixed=2.50,
        ),
    ],
    cash_available=0.0,
)

# Expected: no operations needed (already at target)
result = engine.rebalance(test_portfolio)
assert result.num_operations == 0
```

### 4. Commission-Aware Portfolio Sizing

When planning how much to invest, account for commissions:

```python
# If you have €1,000 to invest and commissions are €2.50 per asset:
total_cash = 1000.0
num_assets = 3
total_commissions = 2.50 * num_assets  # €7.50
available_for_assets = total_cash - total_commissions  # €992.50

portfolio = Portfolio(
    assets=[...],
    cash_available=total_cash,  # Use full amount
)
```

## Backward Compatibility

### Existing Code Works Without Changes

If you have existing code that doesn't specify commissions:

```python
# Old code (still works!)
Asset(
    symbol="ETF",
    quantity=50.0,
    price=100.0,
    avg_cost=95.0,
    tax_rate=0.26,
    target_weight=0.60,
    # Commission fields not specified → default to 0.0
)
```

Behavior is **identical** to previous versions (zero commissions).

### Old Excel Files Work

Excel files with only 6 columns (Symbol, Quantity, Price, Avg Cost, Tax Rate, Target Weight) are still supported:

```python
io = ExcelIO()
portfolio = io.read_portfolio("old_format.xlsx")  # Works!
# All commission fields automatically set to 0.0
```

## Troubleshooting

**Problem**: "commission_buy_fixed must be non-negative"
- **Solution**: Check that all commission values are ≥ 0 (negative commissions don't make sense)

**Problem**: Results don't match expectations
- **Solution**: 
  1. Verify commission values are in correct units (euros, not cents)
  2. Verify percentages are decimals (0.001 = 0.1%, not 0.1 = 0.1%)
  3. Check that min/max values make sense for your portfolio size

**Problem**: Cash flow increased significantly
- **Solution**: This is expected! Commissions reduce cash from sales and increase cash for purchases.
  - Review the `total_cash_in` and `total_cash_out` in results
  - Verify commission values match your broker's fee schedule

## See Also

- [Algorithm Documentation](ALGORITHM.md) - Mathematical formulas
- [README](../README.md) - General usage guide
- [Contributing](CONTRIBUTING.md) - Development guidelines
