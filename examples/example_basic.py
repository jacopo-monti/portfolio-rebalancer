#!/usr/bin/env python3
"""Basic example of portfolio rebalancing."""

from portfolio_rebalancer.models import Asset, Portfolio
from portfolio_rebalancer.engine import RebalancingEngine
from portfolio_rebalancer.policies import RoundingPolicy


def main():
    """Run basic rebalancing example."""
    
    # Create portfolio with 3 ETFs
    portfolio = Portfolio(
        name="My Portfolio",
        assets=[
            Asset(
                symbol="VWCE",
                quantity=50.0,
                price=100.0,
                avg_cost=95.0,
                tax_rate=0.26,
                target_weight=0.60,
            ),
            Asset(
                symbol="AGGH",
                quantity=30.0,
                price=110.0,
                avg_cost=108.0,
                tax_rate=0.26,
                target_weight=0.25,
            ),
            Asset(
                symbol="EIMI",
                quantity=20.0,
                price=135.0,
                avg_cost=130.0,
                tax_rate=0.26,
                target_weight=0.15,
            ),
        ],
    )
    
    print("Portfolio before rebalancing:")
    print("=" * 60)
    total_value = sum(a.quantity * a.price for a in portfolio.assets)
    for asset in portfolio.assets:
        value = asset.quantity * asset.price
        weight = value / total_value
        print(
            f"{asset.symbol:8} {asset.quantity:6.2f} shares × "
            f"€{asset.price:6.2f} = €{value:9,.2f} ({weight*100:5.2f}%)"
        )
    print(f"{'TOTAL':8} {'':13} €{total_value:9,.2f} (100.00%)")
    print()
    
    # Run rebalancing without rounding
    print("Rebalancing (continuous quantities)...")
    engine = RebalancingEngine()
    result = engine.rebalance(portfolio)
    
    print("\nOperations needed:")
    print("=" * 60)
    for asset in result.assets:
        if abs(asset.delta_quantity) > 1e-6:
            action = "BUY " if asset.delta_quantity > 0 else "SELL"
            qty = abs(asset.delta_quantity)
            value = qty * asset.price
            print(f"{asset.symbol:8} {action} {qty:8.4f} shares (€{value:,.2f})")
    
    print(f"\nCash flow: €{result.cash_flow:,.2f}")
    print(f"Total tax paid: €{result.total_tax_paid:,.2f}")
    
    # Run rebalancing with integer shares
    print("\n" + "=" * 60)
    print("Rebalancing (integer shares)...")
    engine_rounded = RebalancingEngine(rounding_policy=RoundingPolicy.ROUND)
    result_rounded = engine_rounded.rebalance(portfolio)
    
    print("\nOperations needed (rounded):")
    print("=" * 60)
    for asset in result_rounded.assets:
        if abs(asset.delta_quantity) > 1e-6:
            action = "BUY " if asset.delta_quantity > 0 else "SELL"
            qty = int(abs(asset.delta_quantity))
            value = qty * asset.price
            print(f"{asset.symbol:8} {action} {qty:4} shares (€{value:,.2f})")
    
    print(f"\nCash flow: €{result_rounded.cash_flow:,.2f}")
    print(f"Max deviation from target: {result_rounded.max_deviation*100:.2f}%")
    
    print("\nPortfolio after rebalancing:")
    print("=" * 60)
    total_value_after = 0
    for asset in result_rounded.assets:
        new_qty = asset.quantity + asset.delta_quantity
        new_value = new_qty * asset.price
        total_value_after += new_value
    
    for asset in result_rounded.assets:
        new_qty = asset.quantity + asset.delta_quantity
        new_value = new_qty * asset.price
        new_weight = new_value / total_value_after
        print(
            f"{asset.symbol:8} {new_qty:6.2f} shares × "
            f"€{asset.price:6.2f} = €{new_value:9,.2f} ({new_weight*100:5.2f}% / "
            f"target: {asset.target_weight*100:.2f}%)"
        )
    print(f"{'TOTAL':8} {'':13} €{total_value_after:9,.2f}")


if __name__ == "__main__":
    main()
