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
---

# Portfolio Rebalancing Tool 📊

A deterministic, tax-aware portfolio rebalancing calculator built with Streamlit.

## Features

✅ **Deterministic Algorithm** - Same input always produces same output  
✅ **Tax-Aware** - Considers capital gains tax on profitable sales  
✅ **Commission-Aware** - Handles broker transaction fees  
✅ **Cash Flow Management** - Supports cash-neutral or cash-deployment rebalancing  
✅ **Multi-Language** - Available in English and Italian  
✅ **Interactive UI** - Easy-to-use web interface with real-time calculations

## How to Use

1. **Target & Portfolio Tab**: Add your assets with current holdings and target allocations
2. **Analysis Tab**: Run the rebalancing algorithm to see required operations
3. **Settings Tab**: Configure optional share rounding preferences

## Key Capabilities

- Calculate optimal buy/sell operations to reach target allocation
- Account for capital gains tax on profitable sales
- Include broker commissions in cash flow calculations
- Maintain cash flow neutrality or deploy additional cash
- Display color-coded portfolio deviations
- Generate detailed rebalancing reports

## About

This tool uses an 8-step deterministic algorithm that:
1. Computes current portfolio state
2. Calculates deviations from target weights
3. Computes target value changes
4. Converts to share quantities
5. Calculates cash flow (with tax and commissions)
6. Closes cash flow through proportional scaling
7. Simulates post-rebalancing state
8. Applies optional share rounding

## Important Notes

⚠️ **This tool is for calculation purposes only, not financial advice.**

- All data is processed locally and never stored externally
- Results are deterministic and reproducible
- No market predictions or asset recommendations provided
- Always verify calculations and consult a financial advisor

## Repository

Full source code and documentation: [github.com/jacopo-monti/portfolio-rebalancer](https://github.com/jacopo-monti/portfolio-rebalancer)
