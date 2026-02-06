---
title: Portfolio Rebalancer
emoji: 📊
colorFrom: green
colorTo: blue
sdk: streamlit
sdk_version: 1.28.0
app_file: app.py
pinned: false
license: other
short_description: Deterministic, tax-aware portfolio rebalancing calculator
tags:
  - finance
  - portfolio
  - investment
  - rebalancing
  - tax-aware
---

# Portfolio Rebalancing Tool 📊

A deterministic, tax-aware portfolio rebalancing calculator with an intuitive web interface. Calculate optimal buy/sell operations to reach your target allocation while accounting for taxes and commissions.

## 🎯 Features

✅ **Deterministic Algorithm** - Same input always produces the same output  
✅ **Tax-Aware Calculations** - Accounts for capital gains tax on profitable sales  
✅ **Commission Handling** - Includes broker transaction fees in all calculations  
✅ **Cash Flow Management** - Supports both cash-neutral and cash-deployment rebalancing  
✅ **Multi-Language Support** - Available in English and Italian  
✅ **Interactive Interface** - Real-time calculations with color-coded visual feedback

## 🚀 How to Use

### 1️⃣ Target & Portfolio Tab
- Add your assets with:
  - Current quantity and price
  - Average cost basis (for tax calculation)
  - Target allocation percentage
  - Optional: broker commission structure
- Define available cash to deploy (or set to 0 for cash-neutral rebalancing)

### 2️⃣ Analysis Tab
- Click "Run Rebalancing Analysis"
- Review three detailed tables:
  - **Current Portfolio State**: Shows current weights and deviations
  - **Required Operations**: Lists exact buy/sell transactions needed
  - **Post-Rebalancing Portfolio**: Displays final state after operations
- Examine cash flow summary and cost breakdown

### 3️⃣ Settings Tab
- Configure optional share rounding (for assets that don't support fractional shares)
- Choose rounding method: FLOOR (conservative), ROUND (balanced), or CEIL (aggressive)

## 💡 Key Capabilities

- **Optimal Operations**: Calculates exact quantities to buy/sell
- **Tax Calculation**: Computes capital gains tax on profitable sales
- **Commission Modeling**: Handles fixed, percentage, min/max broker fees
- **Cash Flow Neutrality**: Balances proceeds from sales with purchase costs
- **Deviation Tracking**: Color-coded indicators (green/yellow/red) for portfolio balance
- **Detailed Reports**: Complete breakdown of costs, taxes, and operations

## 🧠 Algorithm Overview

The tool uses an **8-step deterministic algorithm**:

1. **Compute Current State**: Calculate portfolio value, weights, and deviations
2. **Calculate Deviations**: Measure distance from target allocation
3. **Compute Target Changes**: Determine required value adjustments
4. **Convert to Quantities**: Translate value changes to share quantities
5. **Calculate Cash Flow**: Account for tax and commissions on each transaction
6. **Close Cash Flow**: Apply proportional scaling to achieve cash neutrality
7. **Simulate Final State**: Project post-rebalancing portfolio
8. **Apply Rounding**: Optional integer share adjustment

### Algorithm Characteristics

✅ **Deterministic**: Reproducible results for identical inputs  
✅ **Transparent**: Simple mathematics, no black-box optimization  
✅ **Tax-Efficient**: Minimizes tax impact through careful calculation  
✅ **Commission-Aware**: Factors in real-world transaction costs  
✅ **Cash-Flexible**: Works with or without additional cash deployment

## 📈 Example Use Case

**Scenario**: You have a portfolio with:
- 50 shares of VWCE @ €100 (target: 60%)
- 30 shares of AGGH @ €110 (target: 25%)
- 20 shares of EIMI @ €135 (target: 15%)

**Current allocation**: 56.8% / 27.6% / 15.6%  
**Available cash**: €0 (cash-neutral)

**The tool calculates**:
- Sell 4.32 shares of AGGH → Tax: €22.46  
- Buy 4.23 shares of VWCE → Commission: €0  
- Net cash flow: €0.12 (nearly balanced)

**Result**: Portfolio rebalanced to within 0.5% of targets

## ⚠️ Important Notes

**This tool is for calculation purposes only, not financial advice.**

- All data is processed locally and never stored externally
- Results are deterministic and reproducible
- No market predictions or forecasts included
- No asset selection or recommendations provided
- Always verify calculations independently
- Consult a qualified financial advisor before making investment decisions

## 🔧 Technical Details

**Built with**:
- **Streamlit**: Interactive web framework
- **Pandas**: Data processing and analysis
- **Python 3.8+**: Core language

**Architecture**:
- Modular design with clean separation of concerns
- Core engine independent of UI
- Extensible policy system for rounding strategies
- Type-safe models with validation

**Performance**:
- Instant calculations for portfolios up to 100 assets
- Optimized for low latency and memory efficiency
- No external API calls or network dependencies

## 📚 Documentation

For complete documentation, algorithm details, and source code:

**GitHub Repository**: [jacopo-monti/portfolio-rebalancer](https://github.com/jacopo-monti/portfolio-rebalancer)

Includes:
- Detailed algorithm documentation
- API reference
- CLI usage examples
- Excel export functionality
- Development setup guide
- Test suite

## 🌐 Languages

- 🇬🇧 English
- 🇮🇹 Italiano

Switch languages using the selector in the top-right corner.

## 👨‍💻 Author

**Jacopo Monti**
- GitHub: [@jacopo-monti](https://github.com/jacopo-monti)
- Email: jacopo.monti.jm@gmail.com

## 📝 License

Proprietary - See repository for details

## 🤝 Contributing

Contributions welcome! Please see the GitHub repository for guidelines.

## 🐛 Known Limitations

- Single currency only (no multi-currency support)
- Linear capital gains tax model
- No tax loss harvesting optimization
- No lot-specific tracking (uses average cost basis)
- Assumes infinite liquidity (can buy/sell any quantity)
- Assumes simultaneous execution of all operations
- Prices assumed constant during execution

## 🔄 Version

**Current**: v0.1.1  
**Last Updated**: February 2026  
**Status**: Active Development

---

**Enjoy using the Portfolio Rebalancer!** 🚀

If you find this tool useful, please ⭐ star the repository on GitHub.
