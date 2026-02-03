"""Example: Portfolio rebalancing with broker commissions.

This example demonstrates:
1. How to specify broker commissions for each asset
2. How commissions affect cash flow calculations
3. Comparison of results with and without commissions
"""

from portfolio_rebalancer.models import Portfolio, Asset
from portfolio_rebalancer.engine import RebalancingEngine


def example_basic_commissions():
    """Basic example with fixed commissions."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Portfolio with Fixed Commissions")
    print("="*70)
    
    # Portfolio: 100% in VWCE, want to rebalance to 60/25/15 split
    portfolio = Portfolio(
        assets=[
            Asset(
                symbol="VWCE",
                quantity=100.0,
                price=100.0,
                avg_cost=95.0,
                tax_rate=0.26,
                target_weight=0.60,
                # Degiro-like fees: €1 per transaction
                commission_buy_fixed=1.00,
                commission_sell_fixed=1.00,
            ),
            Asset(
                symbol="AGGH",
                quantity=0.0,
                price=110.0,
                avg_cost=0.0,
                tax_rate=0.26,
                target_weight=0.25,
                commission_buy_fixed=1.00,
                commission_sell_fixed=1.00,
            ),
            Asset(
                symbol="EIMI",
                quantity=0.0,
                price=135.0,
                avg_cost=0.0,
                tax_rate=0.26,
                target_weight=0.15,
                commission_buy_fixed=1.00,
                commission_sell_fixed=1.00,
            ),
        ],
        cash_available=0.0,
    )
    
    engine = RebalancingEngine()
    result = engine.rebalance(portfolio)
    
    print(f"\nTotal Portfolio Value: €{result.total_value_before:,.2f}")
    print(f"\nOperations Needed:")
    print("-" * 70)
    for asset in result.assets:
        if asset.delta_quantity != 0:
            action = "BUY" if asset.delta_quantity > 0 else "SELL"
            print(f"  {asset.symbol:6s} {action:4s} {abs(asset.delta_quantity):8.2f} shares "
                  f"(€{abs(asset.delta_value):,.2f})")
    
    print(f"\nCash Flow Summary:")
    print("-" * 70)
    print(f"  Cash from sales:     €{result.total_cash_in:,.2f}")
    print(f"  Cash for purchases: -€{result.total_cash_out:,.2f}")
    print(f"  Net cash needed:    -€{abs(result.cash_flow):,.2f}")
    
    # Extract tax and commission costs from the calculation
    # For sell operations: cash_in includes both tax and commission deductions
    # For buy operations: cash_out includes commission additions
    sell_operations = sum(1 for a in result.assets if a.delta_quantity < 0)
    buy_operations = sum(1 for a in result.assets if a.delta_quantity > 0)
    
    estimated_commissions = (sell_operations + buy_operations) * 1.00
    print(f"\n  Estimated commissions: €{estimated_commissions:.2f}")
    print(f"  (1 sell + 2 buys = 3 operations × €1.00)")


def example_percentage_commissions():
    """Example with percentage-based commissions."""
    print("\n\n" + "="*70)
    print("EXAMPLE 2: Portfolio with Percentage Commissions (+ min/max)")
    print("="*70)
    
    # Directa-like fees: 0.19% with min €1.50 and max €19
    portfolio = Portfolio(
        assets=[
            Asset(
                symbol="VWCE",
                quantity=100.0,
                price=100.0,
                avg_cost=95.0,
                tax_rate=0.26,
                target_weight=0.60,
                commission_buy_percent=0.0019,   # 0.19%
                commission_buy_min=1.50,
                commission_buy_max=19.00,
                commission_sell_percent=0.0019,
                commission_sell_min=1.50,
                commission_sell_max=19.00,
            ),
            Asset(
                symbol="AGGH",
                quantity=0.0,
                price=110.0,
                avg_cost=0.0,
                tax_rate=0.26,
                target_weight=0.25,
                commission_buy_percent=0.0019,
                commission_buy_min=1.50,
                commission_buy_max=19.00,
                commission_sell_percent=0.0019,
                commission_sell_min=1.50,
                commission_sell_max=19.00,
            ),
            Asset(
                symbol="EIMI",
                quantity=0.0,
                price=135.0,
                avg_cost=0.0,
                tax_rate=0.26,
                target_weight=0.15,
                commission_buy_percent=0.0019,
                commission_buy_min=1.50,
                commission_buy_max=19.00,
                commission_sell_percent=0.0019,
                commission_sell_min=1.50,
                commission_sell_max=19.00,
            ),
        ],
        cash_available=0.0,
    )
    
    engine = RebalancingEngine()
    result = engine.rebalance(portfolio)
    
    print(f"\nTotal Portfolio Value: €{result.total_value_before:,.2f}")
    print(f"\nOperations Needed:")
    print("-" * 70)
    for asset in result.assets:
        if asset.delta_quantity != 0:
            action = "BUY" if asset.delta_quantity > 0 else "SELL"
            operation_value = abs(asset.delta_quantity * asset.price)
            # Calculate commission for display
            comm_pct = operation_value * 0.0019
            comm_actual = max(1.50, min(comm_pct, 19.00))
            print(f"  {asset.symbol:6s} {action:4s} {abs(asset.delta_quantity):8.2f} shares "
                  f"(€{operation_value:,.2f}) - commission: €{comm_actual:.2f}")
    
    print(f"\nCash Flow Summary:")
    print("-" * 70)
    print(f"  Cash from sales:     €{result.total_cash_in:,.2f}")
    print(f"  Cash for purchases: -€{result.total_cash_out:,.2f}")
    print(f"  Net cash needed:    -€{abs(result.cash_flow):,.2f}")


def example_comparison_with_without():
    """Compare results with and without commissions."""
    print("\n\n" + "="*70)
    print("EXAMPLE 3: Impact of Commissions on Cash Flow")
    print("="*70)
    
    # Same portfolio, tested with and without commissions
    assets_no_comm = [
        Asset(
            symbol="VWCE",
            quantity=100.0,
            price=100.0,
            avg_cost=95.0,
            tax_rate=0.26,
            target_weight=0.60,
            # No commissions
        ),
        Asset(
            symbol="AGGH",
            quantity=0.0,
            price=110.0,
            avg_cost=0.0,
            tax_rate=0.26,
            target_weight=0.40,
        ),
    ]
    
    assets_with_comm = [
        Asset(
            symbol="VWCE",
            quantity=100.0,
            price=100.0,
            avg_cost=95.0,
            tax_rate=0.26,
            target_weight=0.60,
            commission_buy_fixed=2.50,
            commission_sell_fixed=2.50,
        ),
        Asset(
            symbol="AGGH",
            quantity=0.0,
            price=110.0,
            avg_cost=0.0,
            tax_rate=0.26,
            target_weight=0.40,
            commission_buy_fixed=2.50,
            commission_sell_fixed=2.50,
        ),
    ]
    
    engine = RebalancingEngine()
    
    # Without commissions
    portfolio_no_comm = Portfolio(assets=assets_no_comm, cash_available=0.0)
    result_no_comm = engine.rebalance(portfolio_no_comm)
    
    # With commissions
    portfolio_with_comm = Portfolio(assets=assets_with_comm, cash_available=0.0)
    result_with_comm = engine.rebalance(portfolio_with_comm)
    
    print("\nWithout Commissions:")
    print("-" * 70)
    print(f"  Cash from sales:     €{result_no_comm.total_cash_in:,.2f}")
    print(f"  Cash for purchases: -€{result_no_comm.total_cash_out:,.2f}")
    print(f"  Net cash needed:    -€{abs(result_no_comm.cash_flow):,.2f}")
    
    print("\nWith Commissions (€2.50 per operation):")
    print("-" * 70)
    print(f"  Cash from sales:     €{result_with_comm.total_cash_in:,.2f}")
    print(f"  Cash for purchases: -€{result_with_comm.total_cash_out:,.2f}")
    print(f"  Net cash needed:    -€{abs(result_with_comm.cash_flow):,.2f}")
    
    # Calculate difference
    diff = abs(result_with_comm.cash_flow) - abs(result_no_comm.cash_flow)
    print("\nImpact:")
    print("-" * 70)
    print(f"  Additional cash needed due to commissions: €{diff:.2f}")
    print(f"  (1 sell + 1 buy = 2 operations × €2.50 = €5.00)")


if __name__ == "__main__":
    print("\n" + "#"*70)
    print("#" + " "*68 + "#")
    print("#" + "  Portfolio Rebalancing with Broker Commissions".center(68) + "#")
    print("#" + " "*68 + "#")
    print("#"*70)
    
    example_basic_commissions()
    example_percentage_commissions()
    example_comparison_with_without()
    
    print("\n" + "#"*70)
    print("#" + " "*68 + "#")
    print("#" + "  See docs/BROKER_COMMISSIONS.md for more examples".center(68) + "#")
    print("#" + " "*68 + "#")
    print("#"*70 + "\n")
