# Portfolio Rebalancer

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](LICENSE)
[![Commercial License](https://img.shields.io/badge/License-Commercial-orange.svg)](LICENSE-COMMERCIAL.md)
[![GitHub Pages](https://img.shields.io/badge/Deploy-GitHub%20Pages-222?logo=github)](https://jacopo-monti.github.io/portfolio-rebalancer/)

A deterministic, tax-aware portfolio rebalancing calculator — runs entirely in your browser, no installation required.

🔗 **[Open the app](https://jacopo-monti.github.io/portfolio-rebalancer/)**

---

## ⚠️ Disclaimer

**THIS SOFTWARE DOES NOT PROVIDE FINANCIAL, INVESTMENT, TAX, OR LEGAL ADVICE.**

This is a mathematical calculation tool only. It:

- ✅ Computes buy/sell operations to bring a portfolio to predefined target percentages
- ✅ Accounts for capital gains taxation, broker commissions, and cash flow
- ❌ Does NOT optimize returns, risk, or portfolio performance
- ❌ Does NOT make predictions about markets or future performance
- ❌ Does NOT recommend which assets to buy, sell, or hold

**All investment decisions are entirely your own responsibility. Consult qualified professionals for personalized advice.**

---

## ✨ Features

- **No installation** — single HTML file, runs in any modern browser
- **No server, no data upload** — all calculations happen locally in JavaScript
- **Tax-aware** — accounts for capital gains tax on sales
- **Commission-aware** — supports fixed fee, percentage, min/max per broker
- **Share rounding** — FLOOR / ROUND / CEIL policies for integer shares
- **Multi-language** — English and Italian
- **Deterministic** — same input always produces same output

---

## 🚀 Usage

Just open [`index.html`](index.html) in a browser, or visit the hosted version at:

**[https://jacopo-monti.github.io/portfolio-rebalancer/](https://jacopo-monti.github.io/portfolio-rebalancer/)**

### How it works

**1 — Portfolio tab**
Add your assets (symbol, quantity, current price, average cost, tax rate, target weight). Optionally configure broker commissions. Set available cash to deploy.

**2 — Analysis tab**
Click "Run Rebalancing Analysis" to get:
- Current portfolio state with weight deviations
- Required buy/sell operations
- Cash flow summary
- Tax and commission cost breakdown
- Post-rebalancing projected portfolio

**3 — Settings tab**
Enable integer share rounding and choose the rounding policy (FLOOR, ROUND, CEIL).

---

## 📐 Algorithm

The rebalancer implements a deterministic 8-step algorithm:

1. Compute current portfolio state (values and weights)
2. Calculate deviations from target weights
3. Compute required value changes
4. Convert value changes to share quantities
5. Calculate cash flow (accounting for tax and commissions)
6. Close cash flow via proportional scaling
7. Simulate post-rebalancing state
8. Apply rounding (optional)

**Key properties**: deterministic, no solver, transparent math, cash-neutral or cash-deployment capable.

For the full mathematical derivation see [`docs/ALGORITHM.md`](docs/ALGORITHM.md).

---

## 🗂️ Repository Structure

```
portfolio-rebalancer/
├── index.html      # The entire application (HTML + CSS + JS)
├── README.md
├── LICENSE
├── LICENSE-COMMERCIAL.md
└── docs/
    ├── ALGORITHM.md
    ├── BROKER_COMMISSIONS.md
    ├── DESIGN.md
    └── VARIABLES.md
```

The app is a single self-contained HTML file. There are no dependencies, no build step, and no framework to install.

---

## 🌐 Self-hosting / GitHub Pages

To host your own instance:

1. Fork or clone this repository
2. Go to **Settings → Pages → Source → Deploy from branch → main**
3. The app will be live at `https://<your-username>.github.io/portfolio-rebalancer/`

Alternatively, just download `index.html` and open it locally — it works offline.

---

## ⚖️ Licensing

**Copyright © 2026 Jacopo Monti. All Rights Reserved.**

This software is available under a dual licensing model.

### 🆓 Open Source: GNU AGPL v3.0

For non-commercial use, licensed under AGPL-3.0. You may use, modify, and share the software provided that any modifications or derivative works are also released under AGPL-3.0, including when deployed as a web service.

See [LICENSE](LICENSE) for full terms.

### 💼 Commercial License

A commercial license is required if you use this software in a commercial product or service, want to keep modifications proprietary, or cannot comply with AGPL source disclosure requirements.

See [LICENSE-COMMERCIAL.md](LICENSE-COMMERCIAL.md) for details and tiers.

### 📞 Commercial inquiries

**Jacopo Monti**  
📧 jacopo.monti.jm@gmail.com  
🐙 [@jacopo-monti](https://github.com/jacopo-monti)

---

## 📧 Contact

**Issues & feature requests**: [open an issue](https://github.com/jacopo-monti/portfolio-rebalancer/issues)  
**Commercial licensing**: jacopo.monti.jm@gmail.com
