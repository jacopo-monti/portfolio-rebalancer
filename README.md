# Portfolio Rebalancer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/jacopo-monti/portfolio-rebalancer/workflows/Tests/badge.svg)](https://github.com/jacopo-monti/portfolio-rebalancer/actions)

A deterministic portfolio rebalancing tool with tax-aware calculations. No optimization, no financial advice, just math.

## ⚠️ Important Disclaimer

**This software does NOT provide financial advice.**

This tool is a mathematical calculator that:
- ✅ Computes operations needed to bring a portfolio back to predefined target percentages
- ✅ Accounts for practical constraints (taxation, cash flow, integer shares)
- ❌ Does NOT optimize returns or risk
- ❌ Does NOT make market predictions
- ❌ Does NOT suggest which assets to buy
- ❌ Does NOT provide investment recommendations

**Use this software entirely at your own risk.**

## 📖 Table of Contents

- [Quick Start](#-quick-start)
- [For End Users](#-for-end-users)
  - [Installation](#installation)
  - [Basic Usage](#basic-usage)
  - [Excel Workflow](#excel-workflow)
- [For Developers](#-for-developers)
  - [Development Setup](#development-setup)
  - [Project Structure](#project-structure)
  - [Running Tests](#running-tests)
  - [Contributing](#contributing)
- [Algorithm](#-algorithm)
- [Philosophy](#-philosophy)
- [Documentation](#-documentation)

## 🚀 Quick Start

### Install

```bash
pip install portfolio-rebalancer
```

### Basic Example

```python
from portfolio_rebalancer.models import Portfolio, Asset
from portfolio_rebalancer.engine import RebalancingEngine

# Define your portfolio
portfolio = Portfolio(
    assets=[
        Asset("VWCE", quantity=50, price=100.0, avg_cost=95.0, 
              tax_rate=0.26, target_weight=0.60),
        Asset("AGGH", quantity=30, price=110.0, avg_cost=108.0, 
              tax_rate=0.26, target_weight=0.25),
        Asset("EIMI", quantity=20, price=135.0, avg_cost=130.0, 
              tax_rate=0.26, target_weight=0.15),
    ]
)

# Rebalance
engine = RebalancingEngine()
result = engine.rebalance(portfolio)

# View results
print(result.summary())
```

---

## 👤 For End Users

### Installation

#### Requirements
- Python 3.8 or higher
- pip (Python package manager)

#### From PyPI (Recommended)

```bash
pip install portfolio-rebalancer
```

#### From Source

```bash
git clone https://github.com/jacopo-monti/portfolio-rebalancer.git
cd portfolio-rebalancer
pip install .
```

### Basic Usage

#### Step 1: Prepare Your Data

You need the following information for each asset in your portfolio:

- **Symbol**: Asset identifier (e.g., ticker symbol)
- **Quantity**: Number of shares you currently own
- **Price**: Current market price per share
- **Average Cost**: Your average purchase price (for tax calculation)
- **Tax Rate**: Capital gains tax rate as decimal (e.g., 0.26 for 26%)
- **Target Weight**: Desired percentage of total portfolio (e.g., 0.60 for 60%)

#### Step 2: Create a Python Script

Create a file called `my_rebalance.py`:

```python
from portfolio_rebalancer.models import Portfolio, Asset
from portfolio_rebalancer.engine import RebalancingEngine

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

# Create rebalancing engine
engine = RebalancingEngine()

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
```

#### Step 3: Run the Script

```bash
python my_rebalance.py
```

#### Understanding the Output

The output will show:
1. **Current state**: Your portfolio before rebalancing
2. **Operations needed**: Which assets to buy/sell and by how much
3. **Cash flow**: Net cash required (should be close to zero)
4. **Post-rebalancing state**: Expected portfolio after operations
5. **Deviations**: How close you'll be to your target weights

### Excel Workflow

For users who prefer working with spreadsheets:

#### Step 1: Create Excel Template

Create an Excel file with these columns:

| Symbol | Quantity | Price | Avg Cost | Tax Rate | Target Weight |
|--------|----------|-------|----------|----------|---------------|
| VWCE   | 50       | 100   | 95       | 0.26     | 0.60          |
| AGGH   | 30       | 110   | 108      | 0.26     | 0.25          |
| EIMI   | 20       | 135   | 130      | 0.26     | 0.15          |

**Note**: Target weights must sum to 1.0 (100%)

#### Step 2: Load and Process

```python
from portfolio_rebalancer.io import ExcelIO
from portfolio_rebalancer.engine import RebalancingEngine

# Load portfolio from Excel
io = ExcelIO()
portfolio = io.read_portfolio("my_portfolio.xlsx")

# Rebalance
engine = RebalancingEngine()
result = engine.rebalance(portfolio)

# Save results to Excel
io.write_result(result, "rebalancing_result.xlsx")

print("Results saved to rebalancing_result.xlsx")
```

### Advanced Options

#### Rounding Policy

If you want to buy/sell only whole shares (no fractional shares):

```python
from portfolio_rebalancer.policies import RoundingPolicy

# Round to nearest integer
engine = RebalancingEngine(rounding_policy=RoundingPolicy.ROUND)
result = engine.rebalance(portfolio)

# Other options:
# RoundingPolicy.FLOOR  - Always round down
# RoundingPolicy.CEIL   - Always round up
```

**Note**: Rounding will cause:
- Cash flow to deviate from zero
- Post-rebalancing weights to deviate slightly from targets

These deviations are reported in the results.

### Troubleshooting

**Problem**: "Target weights must sum to 1.0"
- **Solution**: Make sure all target weights add up to exactly 1.0 (100%)

**Problem**: "Quantity must be non-negative"
- **Solution**: Check that all quantities are positive numbers or zero

**Problem**: "Price must be positive"
- **Solution**: Ensure all prices are greater than zero

**Problem**: Large cash flow imbalance
- **Solution**: This can happen when:
  - Assets with large capital gains need to be sold (taxes reduce cash inflow)
  - Portfolio is heavily imbalanced
  - Check your input data for errors

---

## 👨‍💻 For Developers

### Development Setup

#### Prerequisites
- Python 3.8+
- Git
- pip

#### Clone and Install

```bash
# Clone repository
git clone https://github.com/jacopo-monti/portfolio-rebalancer.git
cd portfolio-rebalancer

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

#### Development Dependencies

The `dev` extra includes:
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `black` - Code formatter
- `flake8` - Linter
- `mypy` - Static type checker

### Project Structure

```
portfolio-rebalancer/
├── src/
│   └── portfolio_rebalancer/
│       ├── __init__.py           # Package initialization
│       ├── models/               # Data models
│       │   ├── __init__.py
│       │   ├── asset.py          # Asset class
│       │   ├── portfolio.py      # Portfolio class
│       │   └── result.py         # RebalancingResult class
│       ├── engine/               # Core rebalancing logic
│       │   ├── __init__.py
│       │   └── rebalancer.py     # RebalancingEngine (8-step algorithm)
│       ├── policies/             # Rounding and tolerance policies
│       │   ├── __init__.py
│       │   └── rounding.py       # RoundingPolicy enum
│       └── io/                   # Input/Output handlers
│           ├── __init__.py
│           └── excel.py          # Excel I/O (future)
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── test_engine.py            # Engine tests
│   ├── test_models.py            # Model tests
│   └── test_policies.py          # Policy tests (future)
├── examples/                     # Example scripts
│   ├── example_basic.py
│   └── example_rounding.py
├── docs/                         # Documentation
│   ├── ALGORITHM.md
│   ├── DESIGN.md
│   └── CONTRIBUTING.md
├── .github/
│   └── workflows/
│       └── tests.yml             # CI/CD configuration
├── README.md                     # This file
├── LICENSE                       # MIT License
├── pyproject.toml               # Project metadata and dependencies
└── .gitignore
```

### Architecture Principles

1. **Core/IO Separation**: The core engine (`engine/`) has zero I/O dependencies
2. **Determinism**: Same input always produces same output (no randomness, no optimization solvers)
3. **Testability**: Every component can be tested in isolation
4. **Extensibility**: New policies and I/O formats without modifying core logic

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=portfolio_rebalancer --cov-report=html

# Run specific test file
pytest tests/test_engine.py

# Run specific test
pytest tests/test_engine.py::TestRebalancingEngine::test_cash_flow_approximates_zero

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code with black
black src/ tests/

# Check code style with flake8
flake8 src/ tests/

# Type check with mypy
mypy src/
```

### Contributing

We welcome contributions! This project is open source to enable:

- Code and algorithm review
- Bug reports
- Documentation improvements
- New features (that respect the project's philosophy)

#### Contribution Workflow

1. **Fork** the repository
2. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/my-feature
   ```
3. **Make your changes** and ensure tests pass:
   ```bash
   pytest
   ```
4. **Commit** your changes:
   ```bash
   git commit -am 'Add new feature: description'
   ```
5. **Push** to your fork:
   ```bash
   git push origin feature/my-feature
   ```
6. **Open a Pull Request** on GitHub

#### Contribution Guidelines

- **Core engine must remain deterministic** - no stochastic optimization
- **No complex numerical optimization** - no solvers, no machine learning
- **Well-documented code** - docstrings for all public APIs
- **Tested code** - maintain or improve test coverage
- **Respect the philosophy** - transparency and explainability first

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for detailed guidelines.

### Adding New Features

#### Example: Adding a New Rounding Policy

1. **Update the enum** in `src/portfolio_rebalancer/policies/rounding.py`:
   ```python
   class RoundingPolicy(Enum):
       FLOOR = "floor"
       ROUND = "round"
       CEIL = "ceil"
       CUSTOM = "custom"  # New policy
   ```

2. **Implement logic** in `src/portfolio_rebalancer/engine/rebalancer.py`:
   ```python
   def _apply_rounding(self, portfolio: Portfolio, policy: RoundingPolicy) -> None:
       for asset in portfolio.assets:
           if policy == RoundingPolicy.CUSTOM:
               # Your custom logic here
               asset.delta_quantity = custom_round(asset.delta_quantity)
   ```

3. **Add tests** in `tests/test_policies.py`:
   ```python
   def test_custom_rounding_policy():
       # Test your new policy
       pass
   ```

4. **Update documentation** in relevant files

5. **Submit pull request**

---

## 📐 Algorithm

The tool implements a deterministic 8-step algorithm:

### Step 1: Current Portfolio State

For each asset *i*:
```
Vᵢ = Qᵢ × Pᵢ
ŵᵢ = Vᵢ / V_total
```

Where:
- `Qᵢ` = current quantity of shares
- `Pᵢ` = current market price
- `Vᵢ` = current value
- `ŵᵢ` = current portfolio weight

### Step 2: Deviation from Target

```
Δwᵢ = ŵᵢ − wᵢ
```

Where `wᵢ` is the target weight:
- `Δwᵢ > 0` → overweight (sell)
- `Δwᵢ < 0` → underweight (buy)

### Step 3: Target Value in Currency

```
ΔVᵢ = (wᵢ × V_total) − Vᵢ
```

### Step 4: Convert to Quantities

```
ΔQᵢ = ΔVᵢ / Pᵢ
```

### Step 5: Cash Flow with Taxation

For sales (`ΔQᵢ < 0`):
```
cash_in = |ΔQᵢ| × (Pᵢ − T × max(0, Pᵢ − PMCᵢ))
```

Where:
- `PMCᵢ` = average cost basis (purchase price)
- `T` = tax rate (e.g., 0.26 for 26%)
- Tax is applied only on capital gains: `(Pᵢ − PMCᵢ)`

For purchases (`ΔQᵢ > 0`):
```
cash_out = ΔQᵢ × Pᵢ
```

Total cash flow:
```
CF = Σ cash_in − Σ cash_out
```

### Step 6: Cash Flow Closure

If `CF ≠ 0`, purchases are scaled proportionally:
```
ΔQᵢ_adjusted = ΔQᵢ × (1 + CF / Σ cash_out)    for ΔQᵢ > 0
```

**Important**: We use simple proportional scaling, not numerical optimization solvers.

### Step 7: Post-Rebalancing Simulation

```
Qᵢ_new = Qᵢ + ΔQᵢ
Vᵢ_new = Qᵢ_new × Pᵢ
ŵᵢ_new = Vᵢ_new / V_total_new
```

### Step 8: Rounding (Optional)

If rounding policy is specified, round `ΔQᵢ` to integers and recompute cash flow and deviations.

For detailed algorithm documentation, see [docs/ALGORITHM.md](docs/ALGORITHM.md).

---

## 🎯 Philosophy

This project is built on clear principles:

### What We Believe In

1. **Transparency**: Every calculation is inspectable and reproducible
2. **Determinism**: Same input → same output (always)
3. **Separation of Concerns**: Mathematical core independent of I/O
4. **Simplicity**: No black-box optimization, just elementary math
5. **Explainability**: Every decision can be traced back to inputs

### What We DON'T Do

- ❌ Market predictions
- ❌ Risk/return optimization
- ❌ Asset selection recommendations
- ❌ Direct broker integration
- ❌ Automatic price fetching
- ❌ Machine learning or AI
- ❌ Multi-currency (advanced)

### Target Audience

- Power users interested in personal finance
- Investor communities wanting to automate rebalancing
- Finance professors and students
- Anyone who wants to understand exactly what happens in their portfolio

---

## 📚 Documentation

- [ALGORITHM.md](docs/ALGORITHM.md) - Detailed algorithm with all formulas
- [DESIGN.md](docs/DESIGN.md) - Design decisions and rationale
- [CONTRIBUTING.md](docs/CONTRIBUTING.md) - Contribution guidelines

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

This means you can:
- ✅ Use commercially
- ✅ Modify
- ✅ Distribute
- ✅ Use privately

But:
- ⚠️ No warranty provided
- ⚠️ No liability accepted

---

## 🙏 Acknowledgments

This project was created out of the need for a rebalancing tool that is:
- Completely transparent
- Mathematically simple
- Verifiable by anyone
- Free of algorithmic "magic"

---

## 📧 Contact

For questions, suggestions, or bug reports: [Open an issue](https://github.com/jacopo-monti/portfolio-rebalancer/issues)

---

**Remember**: This software is a calculation tool, not a financial advisor. Investment decisions are always yours alone.
