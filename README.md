# Portfolio Rebalancer

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](LICENSE)
[![Commercial License](https://img.shields.io/badge/License-Commercial-orange.svg)](LICENSE-COMMERCIAL.md)

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
- [Licensing](#-licensing)
- [Contact](#-contact)

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

Using **conda**:

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

## ⚖️ Licensing

**Copyright © 2026 Jacopo Monti. All Rights Reserved.**

This software is available under a **dual licensing model**. You can choose the license that best fits your needs:

### 🆓 Open Source License: GNU AGPL v3.0

**For non-commercial use**, this software is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**, the strongest copyleft license available.

#### What AGPL-3.0 Means:

**✅ You CAN**:
- Use the software for personal, non-commercial purposes
- Modify the software for your own use
- Study how the software works
- Share the software with others
- Use it in educational and research contexts

**📋 You MUST**:
- **Release ALL source code** of any modifications you make
- **Release ALL source code** of any software that includes this code
- **Provide source code to users** even if they only access it over a network (e.g., web app)
- License your entire work under AGPL-3.0 or compatible license
- Preserve copyright and license notices
- State changes you made to the code

**❌ You CANNOT**:
- Use for commercial purposes without a commercial license
- Keep modifications proprietary
- Incorporate into closed-source software
- Distribute without providing complete source code

#### Why AGPL-3.0?

AGPL-3.0 is specifically designed for network applications like the Streamlit web app included in this repository. Unlike regular GPL, AGPL requires source code disclosure even when the software is used as a web service, ensuring that all improvements benefit the community.

**📄 Full License**: See [LICENSE](LICENSE) for complete AGPL-3.0 terms.

---

### 💼 Commercial License

**For commercial use**, you must obtain a separate commercial license.

#### When You Need a Commercial License:

A commercial license is **required** if you:

- 🏢 Use the software in a **commercial product or service**
- 💰 Offer portfolio rebalancing as a **paid service**
- 🔒 Want to keep your **modifications proprietary**
- 📦 Integrate into **commercial financial software**
- 🌐 Run a **modified version as a web service** without releasing source code
- 🏦 Use in **financial advisory platforms** or robo-advisors
- 🏭 Deploy in **enterprise environments** for business purposes

#### Commercial License Benefits:

✅ **Freedom from AGPL obligations**:
- No requirement to publish your source code
- No requirement to release modifications
- No requirement to license your software under AGPL
- Keep your proprietary code private

✅ **Commercial rights**:
- Use in commercial products and services
- Modify without disclosure requirements
- Distribute as part of proprietary software
- Sublicense rights (depending on tier)

✅ **Additional benefits**:
- Priority support (depending on tier)
- Commercial documentation
- Custom feature development (negotiable)
- Legal protection and indemnification (Enterprise tier)

#### Commercial License Tiers:

1. **Startup License**: For companies < 10 employees or < $1M revenue
2. **Business License**: For companies < 100 employees or < $10M revenue
3. **Enterprise License**: For larger organizations with custom terms
4. **OEM/Redistribution License**: For software vendors redistributing the software

**📄 Full Details**: See [LICENSE-COMMERCIAL.md](LICENSE-COMMERCIAL.md) for complete commercial licensing information and pricing.

---

### 🤔 Which License Do I Need?

#### Use **AGPL-3.0** (Free) if:
- ✅ Personal, non-commercial use
- ✅ Open source project (compliant with AGPL)
- ✅ Educational or research purposes
- ✅ You're willing to release ALL modifications as open source
- ✅ You can provide source code to all users

#### Get **Commercial License** (Paid) if:
- ✅ Commercial product or service
- ✅ Want to keep modifications proprietary
- ✅ Cannot comply with AGPL source disclosure requirements
- ✅ Need proprietary distribution rights
- ✅ Require priority support or custom features

**💡 Not sure?** Contact us and we'll help you determine which license applies to your use case.

**🚀 Can I start with AGPL and switch later?** Yes! You can evaluate under AGPL-3.0 and purchase a commercial license before commercial deployment.

---

### 📞 Commercial License Inquiries

To obtain a commercial license:

**Jacopo Monti**  
📧 Email: jacopo.monti.jm@gmail.com  
🐙 GitHub: [@jacopo-monti](https://github.com/jacopo-monti)  
🔗 Repository: [github.com/jacopo-monti/portfolio-rebalancer](https://github.com/jacopo-monti/portfolio-rebalancer)

Please include:
1. Company information (name, size, revenue)
2. Use case details (how you plan to use the software)
3. Desired license tier
4. Any special requirements

**Response time**: We aim to respond within 2-3 business days.

---

### ⚠️ Important License Notes

**No Warranty**: Under both licenses, the software is provided "AS IS" without warranty. See license files for details.

**No Financial Advice**: This is a calculation tool only. It does NOT provide financial, investment, tax, or legal advice. Consult qualified professionals.

**Compliance**: Ensure you comply with the terms of whichever license you choose. Unauthorized commercial use violates copyright law.

---

## 📧 Contact

**Author**: Jacopo Monti

**Repository**: [github.com/jacopo-monti/portfolio-rebalancer](https://github.com/jacopo-monti/portfolio-rebalancer)

**Issues**: [Open an issue](https://github.com/jacopo-monti/portfolio-rebalancer/issues) for bug reports or feature requests

**Commercial Licensing**: jacopo.monti.jm@gmail.com

---

## 🙏 Contributing

We welcome contributions! Since this project is licensed under AGPL-3.0, any contributions must also be licensed under AGPL-3.0.

By contributing, you agree that your contributions will be licensed under AGPL-3.0.

For contribution guidelines, see issues or contact the maintainer.
