# Portfolio Rebalancer

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

A deterministic portfolio rebalancing tool with tax-aware calculations, broker commission support, and an intuitive web interface.

---

## ⚠️ IMPORTANT DISCLAIMERS

### No Financial Advice

**THIS SOFTWARE DOES NOT PROVIDE FINANCIAL, INVESTMENT, TAX, OR LEGAL ADVICE.**

This is a mathematical calculation tool only. It:

- ✅ **Computes mathematical operations** to bring a portfolio to predefined target percentages
- ✅ **Accounts for constraints** like taxation, broker commissions, cash flow, and integer share requirements
- ❌ **Does NOT optimize** returns, risk, or portfolio performance
- ❌ **Does NOT make predictions** about markets, asset prices, or future performance
- ❌ **Does NOT recommend** which assets to buy, sell, or hold
- ❌ **Does NOT provide advice** on investment strategy, asset allocation, or financial planning

**All investment decisions are entirely your own responsibility. Consult qualified professionals for personalized advice.**

### No Warranty

This software is provided "AS IS" without warranty of any kind. The authors make no guarantees about accuracy, reliability, or suitability, and are not liable for any damages or losses from using this software.

---

## 📖 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
  - [Mode 1: Web App (Recommended)](#mode-1-web-app-recommended)
  - [Mode 2: Excel Mode](#mode-2-excel-mode)
  - [Mode 3: Autocode Mode](#mode-3-autocode-mode)
- [Algorithm](#-algorithm)
- [For Developers](#-for-developers)
  - [Running Tests](#running-tests)
  - [Code Quality](#code-quality)
- [Documentation](#-documentation)
- [License](#-license)

---

## 🚀 Quick Start

The fastest way to use the portfolio rebalancer:

```bash
# 1. Clone the repository
git clone https://github.com/jacopo-monti/portfolio-rebalancer.git
cd portfolio-rebalancer

# 2. Create and activate environment
# Using conda:
conda create -n portfolio-rebalancer python=3.10
conda activate portfolio-rebalancer

# Or using venv:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the web app
streamlit run app.py
```

Your browser will open at `http://localhost:7860` with the interactive interface.

---

## 💻 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step 1: Clone Repository

```bash
git clone https://github.com/jacopo-monti/portfolio-rebalancer.git
cd portfolio-rebalancer
```

### Step 2: Create Environment

Using **conda** (recommended):

```bash
conda create -n portfolio-rebalancer python=3.10
conda activate portfolio-rebalancer
```

Using **venv**:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `streamlit` - Web application framework
- `pandas` - Data processing
- `openpyxl` - Excel file support
- `portfolio-rebalancer` package (local source)

---

## 📊 Usage

Choose one of three modes based on your preference:

### Mode 1: Web App (Recommended)

**Best for**: Visual interface, interactive editing, no coding required

#### Step 1: Activate Environment

```bash
# If using conda:
conda activate portfolio-rebalancer

# If using venv:
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Step 2: Navigate to Repository

```bash
cd /path/to/portfolio-rebalancer
```

#### Step 3: Run Streamlit App

```bash
streamlit run app.py
```

The app will automatically open at `http://localhost:7860` (or `http://localhost:8501` depending on your Streamlit version).

#### Web App Features

**🎯 Target & Portfolio Tab**
- Add assets in an Excel-like editable table
- Set quantities, prices, average costs, and target weights
- Configure broker commissions (optional)
- Define available cash to deploy
- Real-time validation

**📈 Analysis Tab**
- Run rebalancing calculation with one click
- View current portfolio state with deviations
- See required buy/sell operations
- Review cash flow summary and tax breakdown
- Check post-rebalancing portfolio

**⚙️ Settings Tab**
- Configure rounding policy (FLOOR, ROUND, CEIL)
- Select language (English / Italian)
- View algorithm information

**Benefits**:
- ✅ No coding required
- ✅ Interactive, visual interface
- ✅ Instant feedback
- ✅ Multi-language support
- ✅ Runs entirely locally (no data uploaded)
- ✅ In-memory only (no database)

---

### Mode 2: Excel Mode

**Best for**: Spreadsheet users, batch processing, persistent data

#### Step 1: Create Excel Template

Run the template generator:

```bash
python examples/create_excel_template.py
```

This creates `portfolio_template.xlsx` with the correct column structure.

#### Step 2: Modify Template

Open `portfolio_template.xlsx` and enter your portfolio data:

| Symbol | Quantity | Price | Avg Cost | Tax Rate | Target Weight | ... |
|--------|----------|-------|----------|----------|---------------|-----|
| VWCE   | 50       | 100   | 95       | 0.26     | 0.60          | ... |
| AGGH   | 30       | 110   | 108      | 0.26     | 0.25          | ... |
| EIMI   | 20       | 135   | 130      | 0.26     | 0.15          | ... |

**Note**: Target weights must sum to 1.0 (100%).

#### Step 3: Run Analysis

Execute the Excel rebalancing script:

```bash
python examples/my_rebalance_excel.py
```

Results are saved to `rebalancing_result.xlsx`.

---

### Mode 3: Autocode Mode

**Best for**: Developers, scripting, automation, version control

#### Step 1: Create Python Script

Copy and modify `examples/my_rebalance.py`:

```python
from portfolio_rebalancer.models import Portfolio, Asset
from portfolio_rebalancer.engine import RebalancingEngine

# Define your portfolio
portfolio = Portfolio(
    assets=[
        Asset(
            symbol="VWCE",
            quantity=50.0,
            price=100.0,
            avg_cost=95.0,
            tax_rate=0.26,
            target_weight=0.60
        ),
        Asset(
            symbol="AGGH",
            quantity=30.0,
            price=110.0,
            avg_cost=108.0,
            tax_rate=0.26,
            target_weight=0.25
        ),
        # Add more assets...
    ]
)

# Create engine and rebalance
engine = RebalancingEngine()
result = engine.rebalance(portfolio)

# Print results
print(f"Total Value: €{result.total_value_before:,.2f}")
print(f"Cash Flow: €{result.cash_flow:,.2f}")
print(f"Max Deviation: {result.max_deviation*100:.2f}%")

for asset in result.assets:
    action = "BUY" if asset.delta_quantity > 0 else "SELL"
    print(f"{asset.symbol}: {action} {abs(asset.delta_quantity):.2f} shares")
```

#### Step 2: Populate Asset Data

Edit the script with your actual portfolio data:
- Update `symbol`, `quantity`, `price`, `avg_cost`, `tax_rate`, `target_weight`
- Add or remove assets as needed
- Ensure target weights sum to 1.0

#### Step 3: Execute Script

```bash
python examples/my_rebalance.py
```

Results are printed to the console.

**Benefits**:
- ✅ Full programmatic control
- ✅ Easy to version control
- ✅ Scriptable and automatable
- ✅ Integrates with other Python code

---

## 📐 Algorithm

The tool implements a deterministic 8-step algorithm that:

1. **Computes current portfolio state** - Calculate current values and weights
2. **Calculates deviations** - Measure distance from target allocation
3. **Determines target value changes** - Compute required adjustments in currency
4. **Converts to share quantities** - Translate value changes to shares
5. **Calculates cash flow** - Account for taxes and commissions
6. **Closes cash flow** - Apply proportional scaling for cash neutrality
7. **Simulates post-rebalancing state** - Project final portfolio
8. **Applies rounding** - Optional integer share adjustment

**Key characteristics**:
- ✅ **Deterministic**: Same input always produces same output
- ✅ **Transparent**: Every step is mathematically explicit
- ✅ **Tax-aware**: Considers capital gains tax
- ✅ **Commission-aware**: Handles broker transaction fees
- ✅ **No optimization**: Simple proportional scaling, no solvers

**For detailed mathematical formulas and proofs, see**: [docs/ALGORITHM.md](docs/ALGORITHM.md)

---

## 👨‍💻 For Developers

### Project Structure

```
portfolio-rebalancer/
├── app.py                    # Streamlit web application entry point
├── webapp/                   # Web app modules
│   ├── ui_helpers.py         # Table generation and formatting
│   └── translations.py       # Multi-language support
├── src/portfolio_rebalancer/ # Core package
│   ├── models/               # Data models (Asset, Portfolio, Result)
│   ├── engine/               # Rebalancing algorithm
│   ├── policies/             # Rounding policies
│   └── io/                   # Excel I/O (future)
├── examples/                 # Usage examples
│   ├── create_excel_template.py
│   ├── my_rebalance.py
│   ├── my_rebalance_excel.py
│   └── example_*.py
├── tests/                    # Test suite
├── docs/                     # Documentation
│   ├── ALGORITHM.md
│   ├── DESIGN.md
│   ├── BROKER_COMMISSIONS.md
│   └── VARIABLES.md
└── requirements.txt          # Dependencies
```

### Running Tests

Run the full test suite:

```bash
pytest
```

Run with coverage report:

```bash
pytest --cov=portfolio_rebalancer --cov-report=html
```

Run specific test file:

```bash
pytest tests/test_engine.py
```

Run specific test:

```bash
pytest tests/test_engine.py::TestRebalancingEngine::test_cash_flow_approximates_zero
```

View HTML coverage report:

```bash
open htmlcov/index.html  # On macOS
# Or navigate to htmlcov/index.html in your browser
```

### Code Quality

Format code with Black:

```bash
black src/ tests/ webapp/
```

Check style with Flake8:

```bash
flake8 src/ tests/ webapp/
```

Type check with mypy:

```bash
mypy src/
```

Run all quality checks:

```bash
black src/ tests/ webapp/ && flake8 src/ tests/ webapp/ && mypy src/ && pytest
```

---

## 📚 Documentation

- **[ALGORITHM.md](docs/ALGORITHM.md)** - Detailed algorithm with mathematical formulas
- **[BROKER_COMMISSIONS.md](docs/BROKER_COMMISSIONS.md)** - Commission structures and examples
- **[DESIGN.md](docs/DESIGN.md)** - Design decisions and architecture
- **[VARIABLES.md](docs/VARIABLES.md)** - Variable nomenclature and definitions
- **[HUGGINGFACE_DEPLOYMENT.md](HUGGINGFACE_DEPLOYMENT.md)** - Hugging Face Spaces deployment guide

---

## 📧 Contact

**Author**: Jacopo Monti

**Repository**: [github.com/jacopo-monti/portfolio-rebalancer](https://github.com/jacopo-monti/portfolio-rebalancer)

**Issues**: [Open an issue](https://github.com/jacopo-monti/portfolio-rebalancer/issues) for bug reports or feature requests

---

## 📄 License

**Copyright © 2026 Jacopo Monti. All Rights Reserved.**

This software is proprietary and confidential. See [LICENSE](LICENSE) for details.

Unauthorized copying, distribution, or modification is strictly prohibited.

For licensing inquiries, contact the author.
