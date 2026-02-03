# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Broker commission support**: Assets can now specify transaction fees for buy and sell operations
  - `commission_buy_fixed`: Fixed fee per buy transaction
  - `commission_buy_percent`: Percentage fee on buy transactions (e.g., 0.001 = 0.1%)
  - `commission_buy_min`: Minimum commission for percentage-based buy fees
  - `commission_buy_max`: Maximum commission for percentage-based buy fees
  - `commission_sell_fixed`: Fixed fee per sell transaction
  - `commission_sell_percent`: Percentage fee on sell transactions
  - `commission_sell_min`: Minimum commission for percentage-based sell fees
  - `commission_sell_max`: Maximum commission for percentage-based sell fees
- Excel I/O support for commission fields (8 new columns)
- Comprehensive test suite for commission functionality (`tests/test_commissions.py`)
- Detailed documentation in `docs/BROKER_COMMISSIONS.md`

### Changed
- `Asset` model extended with 8 commission fields (all default to 0.0)
- `Asset.compute_cash_in()` now accounts for sell commissions
- `Asset.compute_cash_out()` now accounts for buy commissions
- Excel I/O updated to support 14-column format (was 6 columns)
- Commissions are treated as additional costs in cash flow calculation, like taxes

### Technical Details

#### Commission Calculation
Commissions are calculated using a flexible formula:
```python
# 1. Calculate percentage commission
percentage_commission = operation_value × percent_rate

# 2. Apply min/max bounds (if specified)
if min > 0: percentage_commission = max(percentage_commission, min)
if max > 0: percentage_commission = min(percentage_commission, max)

# 3. Add fixed commission
total_commission = bounded_percentage_commission + fixed_commission
```

#### Cash Flow Impact
Cash flow formula now includes commissions:
```
Cash Flow = (sale_proceeds - taxes - sell_commissions) 
          - (purchase_costs + buy_commissions)
```

#### Backward Compatibility
- All commission fields default to 0.0
- Existing code without commission fields works unchanged
- Old Excel files (6 columns) are still supported
- Zero commissions produce identical results to previous versions

### Notes
- Commission functionality is fully tested with 20+ test cases
- Supports common broker fee structures (fixed, percentage, tiered with min/max)
- See `docs/BROKER_COMMISSIONS.md` for detailed usage examples

### Planned
- Web interface (planned for v0.2.0)
- Multi-currency support (planned for v0.3.0)

## [0.1.1] - 2026-02-02

### Fixed
- **Critical**: Fixed incorrect tax calculation formula in `Asset.compute_cash_in()` that was causing negative cash values for profitable sales
- **Critical**: Fixed cash flow closing tolerance to use relative tolerance instead of absolute, preventing cash flow imbalances
- Fixed Python 3.8 compatibility by using `Tuple` from `typing` instead of built-in `tuple` in type hints
- Updated test expectations to match corrected tax calculation formula

### Changed
- Improved documentation: comprehensive English README with separate sections for end users and developers
- Added detailed contributing guidelines in `docs/CONTRIBUTING.md`
- Updated CHANGELOG to English

### Technical Details

#### Tax Calculation Fix
Previous formula (incorrect):
```python
tax_factor = 1 - self.tax_rate * taxable_gain  # Could produce negative values!
```

Corrected formula:
```python
tax_per_share = self.tax_rate * taxable_gain_per_share
net_price = self.price - tax_per_share
cash_in = quantity_sold * net_price
```

#### Cash Flow Tolerance Fix
Previous (absolute tolerance):
```python
if abs(cash_flow) < 0.01:  # Too strict
    return
```

Corrected (relative tolerance):
```python
if abs(cash_flow / total_cash_out) < 1e-10:  # Scales with portfolio size
    return
```

### Impact
- All 17 tests now pass on Python 3.8, 3.9, 3.10, and 3.11
- Cash flow is correctly balanced (close to zero)
- Post-rebalancing weights are accurate (within 1% of targets)
- Tax calculations are mathematically correct

## [0.1.0] - 2026-02-02

### Added
- Core deterministic rebalancing engine (8-step algorithm)
- Data models: `Asset`, `Portfolio`, `RebalancingResult`
- Rounding policies: `RoundingPolicy` (FLOOR, ROUND, CEIL)
- Capital gains tax calculation
- Automatic cash flow closure with proportional scaling
- Unit tests for core engine and models
- Basic usage examples
- Comprehensive documentation:
  - `README.md` - Overview and quick start
  - `docs/ALGORITHM.md` - Detailed algorithm
  - `docs/DESIGN.md` - Design decisions
- CI/CD configuration with GitHub Actions
- MIT License

### Features
- ✅ Deterministic: same input → same output
- ✅ Transparent: every calculation is inspectable
- ✅ Tax-aware: capital gains tax handling
- ✅ Cash-flow neutral: minimizes external contributions/withdrawals
- ✅ No complex numerical optimization
- ✅ Complete type hints
- ✅ Comprehensive documentation

### Notes
- This is the first alpha release
- Core engine is stable and tested
- API may change in future versions

[Unreleased]: https://github.com/jacopo-monti/portfolio-rebalancer/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/jacopo-monti/portfolio-rebalancer/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/jacopo-monti/portfolio-rebalancer/releases/tag/v0.1.0
