#!/usr/bin/env python3
"""Basic portfolio rebalancing example.

This example demonstrates how to use the portfolio rebalancer
for a simple 3-asset portfolio.
"""

from portfolio_rebalancer.models import Portfolio, Asset
from portfolio_rebalancer.engine import RebalancingEngine


def main():
    """Run basic rebalancing example."""
    
    print("="*70)
    print("PORTFOLIO REBALANCER - BASIC EXAMPLE")
    print("="*70)
    
    # Define your portfolio
    # Replace these values with your actual portfolio data
    portfolio = Portfolio(
        assets=[
            Asset(
                symbol="VWCE",           # Vanguard FTSE All-World UCITS ETF
                quantity=50.0,           # You own 50 shares
                price=100.0,             # Current price: €100
                avg_cost=95.0,           # You bought at average €95
                tax_rate=0.26,           # 26% capital gains tax
                target_weight=0.60       # Target: 60% of portfolio
            ),
            Asset(
                symbol="AGGH",           # iShares Core Global Aggregate Bond
                quantity=30.0,           # You own 30 shares
                price=110.0,             # Current price: €110
                avg_cost=108.0,          # You bought at average €108
                tax_rate=0.26,           # 26% capital gains tax
                target_weight=0.25       # Target: 25% of portfolio
            ),
            Asset(
                symbol="EIMI",           # iShares Core MSCI EM IMI UCITS ETF
                quantity=20.0,           # You own 20 shares
                price=135.0,             # Current price: €135
                avg_cost=130.0,          # You bought at average €130
                tax_rate=0.26,           # 26% capital gains tax
                target_weight=0.15       # Target: 15% of portfolio
            ),
        ],
        name="My Portfolio"
    )
    
    print("\n" + "-"*70)
    print("CURRENT PORTFOLIO STATE")
    print("-"*70)
    
    # Display current state
    total_value = portfolio.total_value
    print(f"\nTotal Portfolio Value: €{total_value:,.2f}\n")
    
    for asset in portfolio.assets:
        current_value = asset.quantity * asset.price
        current_weight = current_value / total_value
        deviation = current_weight - asset.target_weight
        
        print(f"{asset.symbol:6s}: {asset.quantity:7.2f} shares × €{asset.price:7.2f} = €{current_value:9,.2f}")
        print(f"         Weight: {current_weight*100:5.2f}% (target: {asset.target_weight*100:5.2f}%, "
              f"deviation: {deviation*100:+6.2f}%)")
        if asset.price > asset.avg_cost:
            gain = asset.price - asset.avg_cost
            print(f"         Capital gain: €{gain:.2f} per share ({gain/asset.avg_cost*100:.1f}%)")
        print()
    
    # Create rebalancing engine
    print("\n" + "-"*70)
    print("REBALANCING CALCULATION")
    print("-"*70)
    print("\nCalculating optimal operations...\n")
    
    engine = RebalancingEngine()
    result = engine.rebalance(portfolio)
    
    # Display operations needed
    print("-"*70)
    print("OPERATIONS NEEDED")
    print("-"*70)
    print()
    
    for asset in result.assets:
        if abs(asset.delta_quantity) < 0.01:
            action_text = "HOLD (no action needed)"
            print(f"{asset.symbol:6s}: {action_text}")
        else:
            action = "BUY" if asset.delta_quantity > 0 else "SELL"
            quantity = abs(asset.delta_quantity)
            value = abs(asset.delta_value)
            
            print(f"{asset.symbol:6s}: {action:4s} {quantity:8.4f} shares (€{value:,.2f})")
            
            if action == "SELL" and asset.price > asset.avg_cost:
                # Calculate tax on this sale
                capital_gain = (asset.price - asset.avg_cost) * quantity
                tax_amount = capital_gain * asset.tax_rate
                net_proceeds = quantity * asset.price - tax_amount
                print(f"         Capital gain: €{capital_gain:.2f}")
                print(f"         Tax ({asset.tax_rate*100:.0f}%): €{tax_amount:.2f}")
                print(f"         Net proceeds: €{net_proceeds:.2f}")
        print()
    
    # Display cash flow summary
    print("-"*70)
    print("CASH FLOW SUMMARY")
    print("-"*70)
    print()
    print(f"Total cash from sales:    €{result.total_cash_in:>10,.2f}")
    print(f"Total cash for purchases: €{result.total_cash_out:>10,.2f}")
    print(f"Net cash flow:            €{result.cash_flow:>10,.2f}")
    
    if abs(result.cash_flow) < 1.0:
        print("\n✓ Cash flow is balanced (no external funds needed)")
    elif result.cash_flow < 0:
        print(f"\n⚠️  You'll need to add €{abs(result.cash_flow):.2f} to complete purchases")
    else:
        print(f"\n✓ You'll have €{result.cash_flow:.2f} left over after rebalancing")
    
    # Display post-rebalancing state
    print("\n" + "-"*70)
    print("POST-REBALANCING PORTFOLIO")
    print("-"*70)
    print()
    print(f"Total Portfolio Value: €{result.total_value_after:,.2f}\n")
    
    for asset in result.assets:
        new_quantity = asset.quantity + asset.delta_quantity
        new_value = new_quantity * asset.price
        new_weight = new_value / result.total_value_after
        deviation = new_weight - asset.target_weight
        
        print(f"{asset.symbol:6s}: {new_quantity:7.4f} shares × €{asset.price:7.2f} = €{new_value:9,.2f}")
        print(f"         Weight: {new_weight*100:5.2f}% (target: {asset.target_weight*100:5.2f}%, "
              f"deviation: {deviation*100:+6.2f}%)")
        print()
    
    # Display accuracy metrics
    print("-"*70)
    print("ACCURACY METRICS")
    print("-"*70)
    print()
    print(f"Maximum weight deviation: {result.max_deviation*100:.2f}%")
    print(f"Cash flow imbalance:      €{abs(result.cash_flow):.2f}")
    
    if result.max_deviation < 0.01:
        print("\n✓ Excellent: All weights within 1% of target")
    elif result.max_deviation < 0.05:
        print("\n✓ Good: All weights within 5% of target")
    else:
        print("\n⚠️  Large deviations remain (consider adjusting parameters)")
    
    print("\n" + "="*70)
    print("END OF REBALANCING ANALYSIS")
    print("="*70)
    print("\nNOTE: This is a calculation tool, not financial advice.")
    print("Always verify calculations and consult a financial advisor if needed.")
    print()


if __name__ == "__main__":
    main()
