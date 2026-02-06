from portfolio_rebalancer.io import ExcelIO
from portfolio_rebalancer.engine import RebalancingEngine
from portfolio_rebalancer.policies import RoundingPolicy


# Load portfolio from Excel
io = ExcelIO()
portfolio = io.read_portfolio("my_portfolio.xlsx")

# Rebalance
engine = RebalancingEngine(rounding_policy=RoundingPolicy.ROUND)
result = engine.rebalance(portfolio)

# Save results to Excel
io.write_result(result, "rebalancing_result.xlsx")

print("Results saved to rebalancing_result.xlsx")