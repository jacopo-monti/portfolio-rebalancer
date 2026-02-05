# Formal Variable Definitions

This document provides rigorous definitions of all variables used in the system.

## Conventions

- **Index**: `i` represents the index of the financial instrument (i = 1, 2, ..., N)
- **Units of measure**: Monetary values are expressed in euros (€), unless otherwise indicated
- **Percentages**: Expressed as decimal values (e.g., 0.26 for 26%, 0.6 for 60%)

## Input Variables

These are the variables that must be provided by the user.

### N
**Type**: Integer  
**Description**: Total number of instruments in the portfolio  
**Constraints**: N ≥ 1  
**Example**: N = 5 (the portfolio contains 5 ETFs)

### Qᵢ
**Type**: Decimal number (can be integer for whole shares)  
**Description**: Current quantity of shares owned of instrument i  
**Constraints**: Qᵢ ≥ 0  
**Unit**: shares  
**Example**: Q₁ = 50 (I own 50 shares of the first ETF)

### Pᵢ
**Type**: Positive decimal number  
**Description**: Current price of one share of instrument i  
**Constraints**: Pᵢ > 0  
**Unit**: €/share  
**Example**: P₁ = 100.50 €

### PMCᵢ
**Type**: Positive decimal number  
**Description**: Average cost basis of instrument i  
**Constraints**: PMCᵢ > 0 (or PMCᵢ = 0 if Qᵢ = 0 for new assets)  
**Unit**: €/share  
**Usage**: Capital gain calculation for taxation  
**Example**: PMC₁ = 95.00 € (I bought at an average of 95€/share)

### Tᵢ
**Type**: Decimal number  
**Description**: Tax rate applicable to capital gains of instrument i  
**Constraints**: 0 ≤ Tᵢ ≤ 1  
**Format**: Decimal value (e.g., 0.26 for 26%)  
**Special notes**:
- If Pᵢ ≤ PMCᵢ (selling at a loss), effective taxation is zero
- Tᵢ can vary by instrument (e.g., favorable taxation for some bonds)

**Example**: T₁ = 0.26 (26% capital gains tax in Italy)

### wᵢ
**Type**: Decimal number  
**Description**: Target (desired) percentage weight for instrument i in the portfolio  
**Constraints**: 
- 0 ≤ wᵢ ≤ 1 for each i
- Σᵢ wᵢ = 1 (the sum must be exactly 100%)

**Example**: w₁ = 0.60 (I want 60% of the portfolio in this instrument)

### C_available
**Type**: Non-negative decimal number  
**Description**: Additional cash available to deploy into the portfolio  
**Constraints**: C_available ≥ 0  
**Unit**: €  
**Usage**: When positive, the algorithm will deploy this cash into the portfolio while rebalancing to target weights  
**Default**: 0.0 (cash-neutral rebalancing)  
**Example**: C_available = 1,000 € (I have 1,000€ to invest)

---

## Commission Variables

These variables configure broker commission structures for each asset.

### Commission Parameters (Buy)

#### C_buy_fixed,i
**Type**: Non-negative decimal number  
**Description**: Fixed commission component for buying instrument i  
**Constraints**: C_buy_fixed,i ≥ 0  
**Unit**: €  
**Default**: 0.0  
**Example**: C_buy_fixed,1 = 2.50 € (flat fee per buy transaction)

#### C_buy_percent,i
**Type**: Non-negative decimal number  
**Description**: Percentage commission rate for buying instrument i  
**Constraints**: C_buy_percent,i ≥ 0  
**Format**: Decimal (e.g., 0.001 for 0.1%)  
**Default**: 0.0  
**Example**: C_buy_percent,1 = 0.001 (0.1% of transaction value)

#### C_buy_min,i and C_buy_max,i
**Type**: Non-negative decimal number  
**Description**: Minimum and maximum bounds for percentage-based buy commission  
**Constraints**: C_buy_min,i ≥ 0, C_buy_max,i ≥ 0  
**Unit**: €  
**Default**: 0.0 (no bounds)  
**Usage**: Caps the percentage commission within a range  
**Example**: C_buy_min,1 = 1.00 €, C_buy_max,1 = 10.00 €

### Commission Parameters (Sell)

#### C_sell_fixed,i, C_sell_percent,i, C_sell_min,i, C_sell_max,i
**Description**: Same structure as buy commissions, but applied to sell transactions  
**Note**: Buy and sell commissions are configured independently

### Commission Calculation

**Formula**:
```
C_operation,i = C_fixed,i + bounded(V_operation × C_percent,i, C_min,i, C_max,i)
```

Where `bounded(x, min, max)` applies min/max constraints to the percentage component.

**Example**:  
Buying 10 shares at 100€ with C_fixed = 2.50€, C_percent = 0.001, C_min = 1€, C_max = 10€:  
```
Percentage component = max(1, min(10, 1000 × 0.001)) = max(1, min(10, 1)) = 1€
Total commission = 2.50 + 1 = 3.50€
```

---

## Derived Variables

These variables are automatically calculated by the system.

### Vᵢ
**Type**: Decimal number  
**Description**: Current value of instrument i in the portfolio  
**Formula**: `Vᵢ = Qᵢ × Pᵢ`  
**Unit**: €  
**Example**: V₁ = 50 × 100.50 = 5,025.00 €

### V_tot
**Type**: Decimal number  
**Description**: Total current portfolio value  
**Formula**: `V_tot = Σᵢ Vᵢ`  
**Unit**: €  
**Example**: V_tot = 11,000.00 €

### V_target
**Type**: Decimal number  
**Description**: Target total portfolio value (including available cash to deploy)  
**Formula**: `V_target = V_tot + C_available`  
**Unit**: €  
**Usage**: Used in Step 3 to calculate target values for each asset  
**Example**: V_target = 11,000 + 1,000 = 12,000.00 €

### ŵᵢ
**Type**: Decimal number  
**Description**: Current percentage weight of instrument i  
**Formula**: `ŵᵢ = Vᵢ / V_tot`  
**Constraints**: 
- 0 ≤ ŵᵢ ≤ 1
- Σᵢ ŵᵢ = 1

**Interpretation**: Indicates how much of the portfolio is currently allocated to this instrument  
**Example**: ŵ₁ = 5,025 / 11,000 = 0.4568 (45.68%)

### Δwᵢ
**Type**: Decimal number (can be positive or negative)  
**Description**: Percentage deviation of current weight from target  
**Formula**: `Δwᵢ = ŵᵢ − wᵢ`  
**Interpretation**:
- Δwᵢ > 0 → overweight instrument (sell)
- Δwᵢ < 0 → underweight instrument (buy)
- Δwᵢ = 0 → instrument already at target

**Example**: Δw₁ = 0.4568 − 0.60 = −0.1432 (underweight by 14.32%)

---

## Decision Variables

These variables represent the actions to be taken.

### ΔVᵢ
**Type**: Decimal number (can be positive or negative)  
**Description**: Required value change for instrument i (in euros)  
**Formula**: `ΔVᵢ = (wᵢ × V_target) − Vᵢ`  
**Unit**: €  
**Interpretation**:
- ΔVᵢ > 0 → increase position (buy)
- ΔVᵢ < 0 → decrease position (sell)
- ΔVᵢ = 0 → do nothing

**Example**: ΔV₁ = (0.60 × 12,000) − 5,025 = 2,175 € (need to increase by 2,175€)

### ΔQᵢ
**Type**: Decimal number (can be positive or negative)  
**Description**: Required quantity change for instrument i  
**Formula**: `ΔQᵢ = ΔVᵢ / Pᵢ`  
**Unit**: shares  
**Interpretation**:
- ΔQᵢ > 0 → buy ΔQᵢ shares
- ΔQᵢ < 0 → sell |ΔQᵢ| shares
- ΔQᵢ = 0 → do nothing

**Example**: ΔQ₁ = 2,175 / 100.50 = 21.64 shares to purchase

---

## Cash Flow Variables

### cash_inᵢ
**Type**: Non-negative decimal number  
**Description**: Cash generated from selling instrument i (net of taxes and commissions)  
**Formula**: 
```
cash_inᵢ = |ΔQᵢ| × Pᵢ − |ΔQᵢ| × Tᵢ × max(0, Pᵢ − PMCᵢ) − C_sell,i   if ΔQᵢ < 0
cash_inᵢ = 0                                                           otherwise
```

Or in factored form:
```
cash_inᵢ = |ΔQᵢ| × (Pᵢ − Tᵢ × max(0, Pᵢ − PMCᵢ)) − C_sell,i   if ΔQᵢ < 0
```

**Unit**: €  
**Note**: The formula accounts for taxation only on capital gains and subtracts the sell commission

**Example**:  
Selling 10 shares at 110€ (PMC = 108€, T = 0.26, C_sell = 2.50€):  
```
Gross proceeds = 10 × 110 = 1,100.00€
Capital gain tax = 10 × 0.26 × (110 − 108) = 10 × 0.26 × 2 = 5.20€
Sell commission = 2.50€
cash_in = 1,100.00 − 5.20 − 2.50 = 1,092.30€
```

### cash_outᵢ
**Type**: Non-negative decimal number  
**Description**: Cash required to purchase instrument i (including commissions)  
**Formula**: 
```
cash_outᵢ = ΔQᵢ × Pᵢ + C_buy,i   if ΔQᵢ > 0
cash_outᵢ = 0                     otherwise
```
**Unit**: €  

**Example**:  
Buying 21.64 shares at 100.50€ with C_buy = 3.50€:  
```
Purchase cost = 21.64 × 100.50 = 2,174.82€
Buy commission = 3.50€
cash_out = 2,174.82 + 3.50 = 2,178.32€
```

### CF
**Type**: Decimal number (can be positive or negative)  
**Description**: Total rebalancing cash flow  
**Formula**: `CF = Σᵢ cash_inᵢ − Σᵢ cash_outᵢ`  
**Unit**: €  
**Interpretation**:
- CF > 0 → sales generate more cash than needed for purchases (surplus)
- CF < 0 → more money needed for purchases than sales generate (deficit)
- CF = 0 → perfect balance (ideal target when C_available = 0)

**Target**: When C_available > 0, the target is `CF = −C_available` (we want to spend the available cash)

**Operational constraint**: The system adjusts purchases to achieve `CF ≈ CF_target`

---

## Post-Rebalancing Variables

These variables describe the portfolio state after rebalancing.

### Qᵢ,new
**Type**: Decimal number  
**Description**: New quantity of shares of instrument i after rebalancing  
**Formula**: `Qᵢ,new = Qᵢ + ΔQᵢ`  
**Unit**: shares  

### Vᵢ,new
**Type**: Decimal number  
**Description**: New value of instrument i after rebalancing  
**Formula**: `Vᵢ,new = Qᵢ,new × Pᵢ`  
**Unit**: €  

### V_tot,new
**Type**: Decimal number  
**Description**: New total portfolio value after rebalancing  
**Formula**: `V_tot,new = Σᵢ Vᵢ,new`  
**Unit**: €  
**Note**: Should be approximately equal to V_target (differences due to rounding or commission impacts)

### ŵᵢ,new
**Type**: Decimal number  
**Description**: New percentage weight of instrument i after rebalancing  
**Formula**: `ŵᵢ,new = Vᵢ,new / V_tot,new`  
**Constraints**: 0 ≤ ŵᵢ,new ≤ 1, Σᵢ ŵᵢ,new = 1  

**Goal**: Ideally ŵᵢ,new ≈ wᵢ (the closer to target, the better)

---

## Symbol Glossary

| Symbol | Name | Meaning |
|---------|------|-------------|
| i | Index | Identifies a specific instrument |
| N | Number of instruments | Total assets in the portfolio |
| Q | Quantity | Number of shares |
| P | Price | Current price |
| PMC | Prezzo Medio di Carico | Average cost basis |
| T | Tax rate | Tax rate |
| w | Weight | Percentage weight |
| ŵ | Current weight | Current percentage weight (with hat) |
| Δ | Delta | Change, difference |
| V | Value | Value in euros |
| CF | Cash Flow | Cash flow |
| C | Commission | Broker commission/fee |
| Σ | Sigma | Sum over all instruments |
| max(a,b) | Maximum | Maximum between a and b |
| | | min(a,b) | Minimum | Minimum between a and b |

---

## Implementation Notes

### Numerical Precision

All calculations should be performed with decimal precision (not float) to avoid rounding errors in financial calculations.

**Python**: Use `Decimal` from the `decimal` module for critical calculations, or be mindful of floating-point precision

### Input Validation

Before executing calculations, verify:
1. Σᵢ wᵢ = 1 (with tolerance of 1e-6)
2. All positive values respect constraints
3. No NaN or infinite values
4. C_available ≥ 0
5. Commission parameters are non-negative

### Rounding

Rounding quantities to integer shares occurs **after** calculating continuous ΔQᵢ, using configurable policies defined in `policies/`.

### Commission Impact

Commissions affect cash flow and can cause the final weights to deviate slightly from targets. This is expected and reported to the user.
