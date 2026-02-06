# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Multi-currency support (planned for v0.4.0)
- Historical rebalancing analysis
- Portfolio optimization features
- API documentation

## [0.3.1] - 2026-02-06

### Changed - Dual Licensing Implementation

**🎉 Major Update: Dual Licensing Model**

The project has transitioned from proprietary licensing to a **dual licensing model**, providing both open source and commercial licensing options.

#### Open Source License: GNU AGPL v3.0

**Adopted the GNU Affero General Public License v3.0 (AGPL-3.0)** for non-commercial use:

- **Strongest copyleft license available** - ensures all modifications remain open source
- **Network copyleft provision** - requires source disclosure even for web services
- **Perfect fit for Streamlit app** - covers network-based usage
- **Community-friendly** - enables open source ecosystem growth

**What AGPL-3.0 requires**:
- ✅ Release ALL source code of modifications
- ✅ Release ALL source code of derivative works
- ✅ Provide source to network service users
- ✅ License entire work under AGPL-3.0
- ✅ Preserve copyright notices
- ✅ Document changes made

**What AGPL-3.0 allows**:
- ✅ Personal, non-commercial use
- ✅ Modification and redistribution
- ✅ Study and inspection
- ✅ Educational and research use
- ✅ Open source project integration

#### Commercial License

**New commercial licensing option** for business use:

**When required**:
- Commercial products or services
- Proprietary modifications
- Closed-source distribution
- SaaS offerings without source disclosure
- Enterprise deployments
- Financial advisory platforms

**Benefits**:
- 🔓 Freedom from AGPL obligations
- 💼 No requirement to publish source code
- 🔒 Keep modifications proprietary
- 📦 Commercial distribution rights
- 🛡️ Priority support (tier-dependent)
- 📝 Custom feature development (negotiable)

**License Tiers**:
1. **Startup License** - Companies < 10 employees or < $1M revenue
2. **Business License** - Companies < 100 employees or < $10M revenue
3. **Enterprise License** - Larger organizations with custom terms
4. **OEM/Redistribution License** - For software vendors

#### Files Added

- **LICENSE**: Full GNU AGPL v3.0 license text (replaces proprietary license)
- **LICENSE-COMMERCIAL.md**: Comprehensive commercial licensing documentation
  - License tier descriptions
  - Pricing guidelines
  - Benefits and restrictions
  - FAQ section
  - Contact information

#### Documentation Updates

**README.md**:
- New comprehensive **Licensing** section
- Dual license badge display
- Clear explanation of when each license applies
- "Which license do I need?" decision guide
- Commercial inquiry contact information

**pyproject.toml**:
- Updated `license` field to reflect dual licensing
- Changed from "Proprietary" to dual declaration
- Updated license classifiers

#### Why Dual Licensing?

This model provides the best of both worlds:

1. **Open Source Community**:
   - Free for personal, educational, and open source use
   - Strong copyleft ensures improvements benefit everyone
   - Transparent, auditable code
   - Community contributions welcome

2. **Commercial Sustainability**:
   - Revenue from commercial licenses funds development
   - Businesses get flexibility for proprietary use
   - Professional support options available
   - Custom feature development possible

3. **Legal Clarity**:
   - Clear separation between free and paid use
   - No ambiguity about commercial requirements
   - Protection for both users and copyright holder

#### Compliance Notes

**For Open Source Users**:
- Must comply with AGPL-3.0 obligations
- Must release source code of modifications
- Must provide source to network service users
- Cannot use for commercial purposes without commercial license

**For Commercial Users**:
- Must obtain commercial license before commercial deployment
- Contact copyright holder for licensing inquiries
- Evaluation under AGPL-3.0 permitted before purchase

**Transition Period**:
- Existing users should review which license applies
- Commercial users must obtain license by [TBD]
- Open source use remains free under AGPL-3.0

### Technical Details

#### License Implementation

**AGPL-3.0 Features**:
- Section 13: Network interaction clause (key for web apps)
- Requires source provision for remote network users
- Derivative works must be AGPL-3.0 licensed
- Compatible with GPL v3

**Commercial License Structure**:
- Non-exclusive, non-transferable rights
- Freedom from AGPL copyleft obligations
- Tiered pricing based on company size and use case
- Optional support and custom development

#### Choosing a License

**Decision Tree**:

```
Are you using for commercial purposes?
├─ YES → Need Commercial License
│   ├─ Startup tier (< $1M revenue)
│   ├─ Business tier (< $10M revenue)
│   └─ Enterprise tier (larger)
└─ NO → Can use AGPL-3.0
    ├─ Personal use ✅
    ├─ Educational use ✅
    ├─ Open source project ✅
    └─ Must share modifications ❗
```

### Impact

✅ **Enables open source ecosystem** - Community can fork, modify, improve  
✅ **Protects open source nature** - AGPL ensures modifications stay open  
✅ **Provides commercial option** - Businesses can use without AGPL restrictions  
✅ **Funds ongoing development** - Commercial revenue sustains project  
✅ **Legal clarity** - Clear terms for all use cases  
✅ **Backward compatible** - Existing open source use unaffected

### Contact for Commercial Licensing

**Jacopo Monti**  
Email: jacopo.monti.jm@gmail.com  
GitHub: [@jacopo-monti](https://github.com/jacopo-monti)  
Repository: [github.com/jacopo-monti/portfolio-rebalancer](https://github.com/jacopo-monti/portfolio-rebalancer)

**Response time**: 2-3 business days for commercial inquiries

---

## [0.3.0] - 2026-02-06

### Added - Web Interface

**🎉 Major Feature: Interactive Web Application**

- **Streamlit-based web interface** (`app.py`) providing visual, no-code access to rebalancing functionality
- **Three main tabs**:
  - **Target & Portfolio**: Excel-like editable table for asset data entry
  - **Analysis**: One-click rebalancing with detailed results visualization
  - **Settings**: Rounding policy configuration and language selection

**Multi-Language Support** 🌍

- **English and Italian** language options
- **Complete UI translation** including:
  - Tab titles and section headers
  - Form labels and tooltips
  - Table column headers
  - Validation messages and warnings
  - Help text and descriptions
- **Translation module** (`webapp/translations.py`) with extensible architecture
- **Instant language switching** via top-right selector

**Interactive Features**

- **Real-time data validation** with immediate user feedback
- **Color-coded deviation indicators**:
  - 🟢 Green: < 1% deviation (good)
  - 🟡 Yellow: 1-3% deviation (acceptable)
  - 🔴 Red: > 3% deviation (needs rebalancing)
- **Formatted tables** with HTML rendering for better readability
- **Cash flow summary** with detailed breakdown
- **Post-rebalancing projection** showing expected final state

**UI Helper Modules**

- `webapp/ui_helpers.py`: Table generation, formatting, and data conversion
- `webapp/translations.py`: Centralized translation system
- Modular design for easy maintenance and extension

### Added - Hugging Face Spaces Support

**Zero-Configuration Deployment**

- `requirements.txt`: Python dependencies for Spaces deployment
- `packages.txt`: System-level dependencies (libxml2-dev, libxslt-dev)
- `.streamlit/config.toml`: Streamlit server configuration
- `.python-version`: Python 3.10 specification
- `README_HF.md`: Hugging Face Space metadata with YAML frontmatter
- `HUGGINGFACE_DEPLOYMENT.md`: Complete deployment guide

**Repository now deployable to Hugging Face Spaces** by simply connecting the GitHub repository - no manual configuration required.

### Changed

- **Entry point**: `app.py` now serves as both local and cloud deployment entry point
- **Project structure**: Added `webapp/` package for UI components
- **Documentation**: Reorganized README with three usage modes (Web, Excel, Autocode)
- **Streamlit config**: Optimized for both local development and container deployment

### Technical Details

#### Web App Architecture

- **Session state management**: Persistent data across interactions
- **Form-based input**: Clean separation of user input and processing
- **Error handling**: Graceful degradation with user-friendly messages
- **Performance**: Sub-second response times for typical portfolios

#### Translation System

- **Centralized dictionaries**: All strings in one location
- **Fallback mechanism**: Missing translations default to English
- **Parameterized strings**: Support for dynamic content (e.g., "Total: €X")
- **Extensible design**: Easy to add new languages

#### Deployment Configuration

- **Container-ready**: Works in Docker, Hugging Face Spaces, cloud platforms
- **Localhost-compatible**: Runs on `localhost:7860` for local development
- **Automatic binding**: Container environments override to `0.0.0.0` as needed

### Benefits

✅ **Accessibility**: No coding skills required to use the tool  
✅ **Visual clarity**: Tables, colors, and formatting improve comprehension  
✅ **Multi-language**: Accessible to Italian and English speakers  
✅ **Local privacy**: All data in-memory, nothing persisted or uploaded  
✅ **Cloud-ready**: Can be deployed to Hugging Face Spaces for web access  
✅ **Backward compatible**: CLI and Python API unchanged

### Notes

- Web app is **in-memory only** - data is lost when browser is closed (by design)
- For persistent workflows, use Excel Mode or Autocode Mode
- Web interface provides same calculation results as CLI/API
- Hugging Face Spaces deployment enables browser access from any device

## [0.2.0] - 2026-02-03

### Added - Broker Commission Support

- **Comprehensive commission modeling**: Assets can now specify transaction fees
- **8 new commission fields per asset**:
  - `commission_buy_fixed`: Fixed fee per buy transaction
  - `commission_buy_percent`: Percentage fee on buy (e.g., 0.001 = 0.1%)
  - `commission_buy_min`: Minimum commission for percentage-based buy fees
  - `commission_buy_max`: Maximum commission for percentage-based buy fees
  - `commission_sell_fixed`: Fixed fee per sell transaction
  - `commission_sell_percent`: Percentage fee on sell
  - `commission_sell_min`: Minimum commission for percentage-based sell fees
  - `commission_sell_max`: Maximum commission for percentage-based sell fees
- **Excel I/O support** for commission fields (14-column format)
- **Test suite**: 20+ test cases in `tests/test_commissions.py`
- **Documentation**: `docs/BROKER_COMMISSIONS.md` with examples

### Changed

- `Asset` model extended with commission fields (all default to 0.0)
- `Asset.compute_cash_in()` now accounts for sell commissions
- `Asset.compute_cash_out()` now accounts for buy commissions
- Excel output Summary section reorganized:
  1. Cash available to invest (input)
  2. Cash flow actually used (calculated)
  3. Total cash in from sales
  4. Total cash out for purchases
  5. Total tax paid
  6. Total commission on purchases
  7. Total commission on sales
  8. Total commissions
  9. **Total rebalancing cost** (NEW: tax + commissions)
  10. Total portfolio value before
  11. Total portfolio value after
  12. Max deviation from target
- Removed "Number of Operations" from Summary (still available via API)

### Technical Details

#### Commission Calculation Formula

```python
# 1. Calculate percentage commission
percentage_commission = operation_value × percent_rate

# 2. Apply min/max bounds (if specified)
if min > 0: percentage_commission = max(percentage_commission, min)
if max > 0: percentage_commission = min(percentage_commission, max)

# 3. Add fixed commission
total_commission = bounded_percentage_commission + fixed_commission
```

#### Cash Flow with Commissions

```
Cash Flow = (sale_proceeds - taxes - sell_commissions)
          - (purchase_costs + buy_commissions)
```

### Backward Compatibility

✅ All commission fields default to 0.0  
✅ Existing code without commissions works unchanged  
✅ Old Excel files (6 columns) still supported  
✅ Zero commissions produce identical results to v0.1.x

## [0.1.1] - 2026-02-02

### Fixed

- **Critical**: Fixed incorrect tax calculation in `Asset.compute_cash_in()` causing negative cash values
- **Critical**: Fixed cash flow closing tolerance to use relative instead of absolute tolerance
- Fixed Python 3.8 compatibility (`Tuple` from `typing` instead of built-in `tuple`)
- Updated test expectations to match corrected formulas

### Changed

- Improved documentation: comprehensive English README
- Added `docs/CONTRIBUTING.md` with contribution guidelines
- Updated CHANGELOG to English

### Technical Details

#### Tax Calculation Fix

**Previous (incorrect)**:
```python
tax_factor = 1 - self.tax_rate * taxable_gain  # Could be negative!
```

**Corrected**:
```python
tax_per_share = self.tax_rate * taxable_gain_per_share
net_price = self.price - tax_per_share
cash_in = quantity_sold * net_price
```

#### Cash Flow Tolerance Fix

**Previous (absolute)**:
```python
if abs(cash_flow) < 0.01:  # Too strict for large portfolios
    return
```

**Corrected (relative)**:
```python
if abs(cash_flow / total_cash_out) < 1e-10:  # Scales with portfolio size
    return
```

### Impact

- All tests pass on Python 3.8, 3.9, 3.10, 3.11
- Cash flow correctly balanced (close to zero)
- Post-rebalancing weights accurate (within 1% of targets)
- Tax calculations mathematically correct

## [0.1.0] - 2026-02-02

### Added - Initial Release

- **Core deterministic rebalancing engine** (8-step algorithm)
- **Data models**: `Asset`, `Portfolio`, `RebalancingResult`
- **Rounding policies**: `RoundingPolicy` (FLOOR, ROUND, CEIL)
- **Capital gains tax calculation**
- **Automatic cash flow closure** with proportional scaling
- **Unit tests** for core engine and models
- **Usage examples** in `examples/`
- **Comprehensive documentation**:
  - `README.md` - Overview and quick start
  - `docs/ALGORITHM.md` - Detailed algorithm
  - `docs/DESIGN.md` - Design decisions
- **CI/CD configuration** with GitHub Actions

### Features

✅ Deterministic: same input → same output  
✅ Transparent: every calculation is inspectable  
✅ Tax-aware: capital gains tax handling  
✅ Cash-flow neutral: minimizes external contributions/withdrawals  
✅ No complex numerical optimization  
✅ Complete type hints  
✅ Comprehensive documentation

### Notes

- First alpha release
- Core engine stable and tested
- API may change in future versions

---

[Unreleased]: https://github.com/jacopo-monti/portfolio-rebalancer/compare/v0.3.1...HEAD
[0.3.1]: https://github.com/jacopo-monti/portfolio-rebalancer/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/jacopo-monti/portfolio-rebalancer/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/jacopo-monti/portfolio-rebalancer/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/jacopo-monti/portfolio-rebalancer/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/jacopo-monti/portfolio-rebalancer/releases/tag/v0.1.0
