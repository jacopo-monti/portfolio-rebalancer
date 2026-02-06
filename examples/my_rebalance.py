from portfolio_rebalancer.models import Portfolio, Asset
from portfolio_rebalancer.engine import RebalancingEngine
from portfolio_rebalancer.policies import RoundingPolicy

# Define your portfolio
portfolio = Portfolio(
    assets=[
        Asset(
            symbol="VWCE",           # Asset name/ticker
            quantity=50.0,           # Shares you own
            price=100.0,             # Current market price
            avg_cost=95.0,           # Your average purchase price
            tax_rate=0.26,           # Tax rate (26% = 0.26)
            target_weight=0.60       # Target: 60% of portfolio
        ),
        Asset(
            symbol="AGGH",
            quantity=30.0,
            price=110.0,
            avg_cost=108.0,
            tax_rate=0.26,
            target_weight=0.25       # Target: 25% of portfolio
        ),
        Asset(
            symbol="EIMI",
            quantity=20.0,
            price=135.0,
            avg_cost=130.0,
            tax_rate=0.26,
            target_weight=0.15       # Target: 15% of portfolio
        ),
    ]
)

portfolio.cash_available = 1000

# Create rebalancing engine
engine = RebalancingEngine(rounding_policy=RoundingPolicy.ROUND)

# Calculate rebalancing operations
result = engine.rebalance(portfolio)

# Print detailed results
print("\n" + "="*60)
print("PORTFOLIO REBALANCING RESULTS")
print("="*60)

print(f"\nTotal Portfolio Value: €{result.total_value_before:,.2f}")
print(f"Cash Flow: €{result.cash_flow:,.2f}")
print(f"Max Deviation: {result.max_deviation*100:.2f}%")

print("\nOperations Needed:")
print("-" * 60)
for asset in result.assets:
    action = "BUY" if asset.delta_quantity > 0 else "SELL"
    print(f"{asset.symbol:6s} {action:4s} {abs(asset.delta_quantity):8.2f} shares "
          f"(€{abs(asset.delta_value):,.2f})")

print("\nPost-Rebalancing Portfolio:")
print("-" * 60)
for asset in result.assets:
    new_qty = asset.quantity + asset.delta_quantity
    new_value = new_qty * asset.price
    new_weight = new_value / result.total_value_after
    print(f"{asset.symbol:6s}: {new_qty:8.2f} shares @ €{asset.price:7.2f} = "
          f"€{new_value:10,.2f} ({new_weight*100:5.2f}% vs target {asset.target_weight*100:.2f}%)")