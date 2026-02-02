"""Example script to create a formatted Excel template for portfolio input.

This generates a professionally formatted Excel file that you can fill in with
your portfolio data and use with the Excel workflow.
"""

from portfolio_rebalancer.models import Portfolio, Asset
from portfolio_rebalancer.io import ExcelIO


def create_template():
    """Create a formatted Excel template with example data."""
    
    # Create example portfolio with sample data
    portfolio = Portfolio(
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
        cash_available=1000.0,  # €1,000 available to invest
    )
    
    # Write to Excel file
    io = ExcelIO()
    io.write_portfolio(portfolio, "my_portfolio_template.xlsx")
    
    print("✅ Excel template created: my_portfolio_template.xlsx")
    print("\nThe template includes:")
    print("  • Cash Available field (currently set to €1,000)")
    print("  • Sample portfolio with 3 ETFs")
    print("  • Professional formatting with colored headers")
    print("  • All required columns properly formatted")
    print("\nYou can now:")
    print("  1. Open the file in Excel")
    print("  2. Update the Cash Available amount")
    print("  3. Modify or add your assets")
    print("  4. Update prices to current market values")
    print("  5. Adjust target weights to your preferences")
    print("  6. Use it with the Excel workflow!")


if __name__ == "__main__":
    create_template()
