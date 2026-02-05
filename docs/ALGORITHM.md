# Portfolio Rebalancing Algorithm

This document provides a detailed description of the algorithm implemented in the system.

## Overview

The rebalancing algorithm is a deterministic 8-step process that transforms a portfolio from its current state to the target state while respecting practical constraints.

**Key characteristics**:
- ✅ Deterministic (same input → same output)
- ✅ No complex numerical optimization
- ✅ Transparent and explainable
- ✅ Tax-aware (capital gains tax handling)
- ✅ Commission-aware (broker fees included)
- ✅ Cash-flow neutral or cash-deployment capable

---

## Step 1: Current State Computation

### Objective
Quantify the current value and weights of each instrument in the portfolio.

### Formulas

For each instrument *i*:

```
Vᵢ = Qᵢ × Pᵢ
```

Where:
- `Vᵢ` = current value of instrument *i* (€)
- `Qᵢ` = quantity of shares owned
- `Pᵢ` = current price per share (€)

Total portfolio value:

```
V_tot = Σᵢ₌₁ᴺ Vᵢ
```

Current percentage weight:

```
ŵᵢ = Vᵢ / V_tot
```

### Example

| Asset | Qᵢ | Pᵢ | Vᵢ | ŵᵢ |
|-------|-----|-----|-----|--------|
| VWCE | 50 | 100 | 5,000 | 45.45% |
| AGGH | 30 | 110 | 3,300 | 30.00% |
| EIMI | 20 | 135 | 2,700 | 24.55% |
| **TOTAL** | | | **11,000** | **100%** |

### Python Code

```python
def compute_current_state(portfolio):
    for asset in portfolio.assets:
        asset.current_value = asset.quantity * asset.price
    
    total_value = sum(a.current_value for a in portfolio.assets)
    
    for asset in portfolio.assets:
        asset.current_weight = asset.current_value / total_value
    
    return total_value
```

---

## Step 2: Deviation Computation

### Objective
Identify which assets are overweight (to be sold) and which are underweight (to be bought).

### Formula

```
Δwᵢ = ŵᵢ − wᵢ
```

### Interpretation

- **Δwᵢ > 0**: Overweight instrument → sell
- **Δwᵢ < 0**: Underweight instrument → buy
- **Δwᵢ = 0**: Instrument at target → no action

### Example

| Asset | ŵᵢ | wᵢ (target) | Δwᵢ | Action |
|-------|-----|-------------|--------|--------|
| VWCE | 45.45% | 60% | −14.55% | Buy |
| AGGH | 30.00% | 25% | +5.00% | Sell |
| EIMI | 24.55% | 15% | +9.55% | Sell |

### Python Code

```python
def compute_deviations(portfolio):
    deviations = {}
    for asset in portfolio.assets:
        deviation = asset.current_weight - asset.target_weight
        deviations[asset.symbol] = deviation
        asset.deviation = deviation
    return deviations
```

---

## Step 3: Target Value Computation

### Objective
Transform percentage deviations into value changes in euros.

### Formula

```
ΔVᵢ = (wᵢ × V_target) − Vᵢ
```

Where:
```
V_target = V_tot + C_available
```

- `V_target` = target total portfolio value
- `C_available` = available cash to deploy (if any)

Alternatively:

```
ΔVᵢ = (wᵢ × V_target) − (ŵᵢ × V_tot)
```

### Example

Assuming no additional cash available (`C_available = 0`):

| Asset | wᵢ | V_tot | Vᵢ | ΔVᵢ |
|-------|-----|-------|-----|---------|
| VWCE | 60% | 11,000 | 5,000 | +1,600 |
| AGGH | 25% | 11,000 | 3,300 | −550 |
| EIMI | 15% | 11,000 | 2,700 | −1,050 |

**Verification**: Σᵢ ΔVᵢ = 1,600 − 550 − 1,050 = 0 ✅

### Python Code

```python
def compute_target_values(portfolio, target_total_value):
    for asset in portfolio.assets:
        target_value = asset.target_weight * target_total_value
        asset.delta_value = target_value - asset.current_value
```

---

## Step 4: Quantity Conversion

### Objective
Transform value changes into quantities of shares to buy/sell.

### Formula

```
ΔQᵢ = ΔVᵢ / Pᵢ
```

### Example

| Asset | ΔVᵢ | Pᵢ | ΔQᵢ |
|-------|-----|-----|---------|
| VWCE | +1,600 | 100 | +16.00 |
| AGGH | −550 | 110 | −5.00 |
| EIMI | −1,050 | 135 | −7.78 |

### Python Code

```python
def compute_quantity_changes(portfolio):
    for asset in portfolio.assets:
        asset.delta_quantity = asset.delta_value / asset.price
```

---

## Step 5: Cash Flow Computation with Taxation and Commissions

### Objective
Determine the cash generated from sales (net of taxes and commissions) and the cash required for purchases (including commissions).

### Formulas

#### For sales (ΔQᵢ < 0)

```
cash_inᵢ = |ΔQᵢ| × Pᵢ − |ΔQᵢ| × Tᵢ × max(0, Pᵢ − PMCᵢ) − Cₛₑₗₗ,ᵢ
```

Or in factored form:
```
cash_inᵢ = |ΔQᵢ| × (Pᵢ − Tᵢ × max(0, Pᵢ − PMCᵢ)) − Cₛₑₗₗ,ᵢ
```

**Detailed explanation**:

1. `|ΔQᵢ| × Pᵢ` = gross proceeds from sale
2. `Pᵢ − PMCᵢ` = capital gain per share (can be negative)
3. `max(0, Pᵢ − PMCᵢ)` = taxable capital gain per share (only if positive)
4. `Tᵢ × max(0, Pᵢ − PMCᵢ)` = tax per share
5. `|ΔQᵢ| × Tᵢ × max(0, Pᵢ − PMCᵢ)` = total capital gains tax
6. `Cₛₑₗₗ,ᵢ` = broker commission for selling

**Special cases**:
- If `Pᵢ ≤ PMCᵢ` (selling at a loss): `cash_inᵢ = |ΔQᵢ| × Pᵢ − Cₛₑₗₗ,ᵢ` (no tax)
- If `Pᵢ > PMCᵢ` (selling at a profit): capital gains tax applies

#### Broker commission calculation

Commissions are calculated as:
```
C = Cₓᵢₓₑ𝒹 + bounded(V_operation × Pₚₑᵣcₑₙₜ, Cₘᵢₙ, Cₘₐₓ)
```

Where:
- `Cₓᵢₓₑ𝒹` = fixed commission component
- `Pₚₑᵣcₑₙₜ` = percentage commission rate
- `Cₘᵢₙ`, `Cₘₐₓ` = min/max bounds for percentage component
- `V_operation` = operation value (quantity × price)

#### For purchases (ΔQᵢ > 0)

```
cash_outᵢ = ΔQᵢ × Pᵢ + Cᵦᵤᵧ,ᵢ
```

Where `Cᵦᵤᵧ,ᵢ` = broker commission for buying (calculated as above)

#### Total cash flow

```
CF = Σᵢ cash_inᵢ − Σᵢ cash_outᵢ
```

### Example

**Assumptions**: 
- Average cost: AGGH = 108, EIMI = 130
- Tax rate: T = 26%
- No broker commissions (for simplicity)

| Asset | ΔQᵢ | Type | Calculation | Cash |
|-------|-----|------|-------------|-----------|
| VWCE | +16.00 | Purchase | 16 × 100 | −1,600.00 |
| AGGH | −5.00 | Sale | 5 × (110 − 0.26×2) | +547.40 |
| EIMI | −7.78 | Sale | 7.78 × (135 − 0.26×5) | +1,040.77 |
| **CF** | | | | **−11.83** |

**Result**: CF = −11.83€ (small deficit)

### Python Code

```python
def compute_cash_flow(portfolio):
    cash_in = 0
    cash_out = 0
    
    for asset in portfolio.assets:
        if asset.delta_quantity < 0:  # Sale
            qty_sold = abs(asset.delta_quantity)
            cash_in += asset.compute_cash_in(qty_sold)
        
        elif asset.delta_quantity > 0:  # Purchase
            cash_out += asset.compute_cash_out(asset.delta_quantity)
    
    return cash_in - cash_out
```

---

## Step 6: Cash Flow Closure

### Objective
Balance the cash flow to either achieve neutrality (CF ≈ 0) or deploy available cash (CF = −C_available).

### Problem

If CF ≠ CF_target:
- CF < CF_target: need more money for purchases than sales generate
- CF > CF_target: sales generate more cash than needed

Where:
```
CF_target = −C_available
```

- If `C_available = 0`: target is CF = 0 (cash-neutral rebalancing)
- If `C_available > 0`: target is CF = −C_available (deploy available cash)

### Solution: Proportional Scaling

**Concept**: Scale purchases proportionally to balance the cash flow.

**Formula**:

```
ΔQᵢ,adjusted = ΔQᵢ × (1 + (CF − CF_target) / Σⱼ cash_outⱼ)    for ΔQᵢ > 0
ΔQᵢ,adjusted = ΔQᵢ                                            for ΔQᵢ ≤ 0
```

**Rationale**: Using `1 + (CF − CF_target)/total_cash_out` because:
- If CF > CF_target (surplus), the factor > 1 → increase purchases
- If CF < CF_target (deficit), the factor < 1 → decrease purchases

### Example

From our example: CF = −11.83€, cash_out_total = 1,600€, C_available = 0

Target: CF_target = 0

```
factor = 1 + (−11.83 − 0) / 1,600 = 1 − 0.0074 = 0.9926
```

Adjusted quantities:

| Asset | ΔQᵢ original | Type | ΔQᵢ,adjusted |
|-------|--------------|------|------------------|
| VWCE | +16.00 | Purchase | 16.00 × 0.9926 = 15.88 |
| AGGH | −5.00 | Sale | −5.00 (unchanged) |
| EIMI | −7.78 | Sale | −7.78 (unchanged) |

**New CF**: 547.40 + 1,040.77 − (15.88 × 100) ≈ 0 ✅

### Why Not Complex Optimization?

We could use numerical solvers to distribute the adjustment "optimally," but:
- Would add complexity
- Would no longer be deterministic
- Practical difference is minimal
- Would violate the project's simplicity philosophy

### Python Code

```python
def close_cash_flow(portfolio, cash_flow, total_cash_out, cash_available):
    if total_cash_out == 0:
        return  # No purchases to scale
    
    # Target cash flow: negative of available cash (we want to spend it)
    target_cash_flow = -cash_available
    
    # Check if already at target (with tolerance)
    cash_flow_diff = cash_flow - target_cash_flow
    relative_tolerance = 1e-10
    if abs(cash_flow_diff / total_cash_out) < relative_tolerance:
        return  # Already balanced
    
    # Scale factor for purchases
    scale_factor = 1 + cash_flow_diff / total_cash_out
    
    # Apply only to purchases
    for asset in portfolio.assets:
        if asset.delta_quantity > 0:
            asset.delta_quantity *= scale_factor
```

---

## Step 7: Post-Rebalancing Simulation

### Objective
Calculate the portfolio state after applying the operations.

### Formulas

```
Qᵢ,new = Qᵢ + ΔQᵢ,adjusted
Vᵢ,new = Qᵢ,new × Pᵢ
V_tot,new = Σᵢ Vᵢ,new
ŵᵢ,new = Vᵢ,new / V_tot,new
```

### Example

| Asset | Qᵢ | ΔQᵢ | Qᵢ,new | Vᵢ,new | ŵᵢ,new | wᵢ (target) |
|-------|-----|-----|--------|--------|--------|-------------|
| VWCE | 50 | +15.88 | 65.88 | 6,588 | 60.00% | 60% |
| AGGH | 30 | −5.00 | 25.00 | 2,750 | 25.04% | 25% |
| EIMI | 20 | −7.78 | 12.22 | 1,650 | 15.02% | 15% |
| **TOT** | | | | **10,988** | **100%** | **100%** |

**Observation**: Very close to target weights!

### Python Code

```python
def simulate_post_rebalancing(portfolio):
    results = []
    
    for asset in portfolio.assets:
        new_qty = asset.quantity + asset.delta_quantity
        new_value = new_qty * asset.price
        results.append({
            'symbol': asset.symbol,
            'new_quantity': new_qty,
            'new_value': new_value
        })
    
    total_new_value = sum(r['new_value'] for r in results)
    
    for r in results:
        r['new_weight'] = r['new_value'] / total_new_value
    
    return results
```

---

## Step 8: Rounding to Integer Shares

### Objective
Adapt continuous quantities to integer shares (when required).

### Problem

Up to this point, ΔQᵢ can be a decimal number (e.g., 15.88 shares). In reality, many instruments are traded in whole shares only.

### Solutions (Policy)

1. **Floor rounding**
   ```
   ΔQᵢ,rounded = ⌊ΔQᵢ⌋
   ```
   Example: 15.88 → 15

2. **Mathematical rounding**
   ```
   ΔQᵢ,rounded = round(ΔQᵢ)
   ```
   Example: 15.88 → 16

3. **Ceiling rounding**
   ```
   ΔQᵢ,rounded = ⌈ΔQᵢ⌉
   ```
   Example: 15.88 → 16

### Consequences

After rounding:
- Cash flow will no longer be exactly at target
- Weights will not be perfectly at target

**Action**: Recalculate CF and residual deviations and report them to the user.

### Default Policy

By default, **mathematical rounding** is used.

### Python Code

```python
from enum import Enum
import math

class RoundingPolicy(Enum):
    FLOOR = 'floor'
    ROUND = 'round'
    CEIL = 'ceil'

def apply_rounding(portfolio, policy=RoundingPolicy.ROUND):
    for asset in portfolio.assets:
        if policy == RoundingPolicy.FLOOR:
            asset.delta_quantity = math.floor(asset.delta_quantity)
        elif policy == RoundingPolicy.ROUND:
            asset.delta_quantity = round(asset.delta_quantity)
        elif policy == RoundingPolicy.CEIL:
            asset.delta_quantity = math.ceil(asset.delta_quantity)
```

---

## Flow Diagram

```
┌─────────────────────────────┐
│  Input: Portfolio           │
│  (Q, P, PMC, T, w, C_avail)│
└──────────┬──────────────────┘
           │
           ▼
  ┌────────────────────────┐
  │ Step 1: Current state  │
  │  V, ŵ, V_tot          │
  └──────────┬─────────────┘
             │
             ▼
  ┌────────────────────────┐
  │ Step 2: Deviations     │
  │  Δw = ŵ − w           │
  └──────────┬─────────────┘
             │
             ▼
  ┌────────────────────────┐
  │ Step 3: Target value   │
  │  ΔV = Δw × V_target   │
  └──────────┬─────────────┘
             │
             ▼
  ┌────────────────────────┐
  │ Step 4: Quantities     │
  │  ΔQ = ΔV / P          │
  └──────────┬─────────────┘
             │
             ▼
  ┌────────────────────────┐
  │ Step 5: Cash flow      │
  │  CF with tax & commiss.│
  └──────────┬─────────────┘
             │
             ▼
        ┌────────────┐
        │CF=CF_target?│
        └─────┬──────┘
              │ No
              ▼
  ┌────────────────────────┐
  │ Step 6: Close CF       │
  │  Scale purchases       │
  └──────────┬─────────────┘
             │
             ▼
  ┌────────────────────────┐
  │ Step 7: Simulation     │
  │  Q_new, ŵ_new         │
  └──────────┬─────────────┘
             │
             ▼
  ┌────────────────────────┐
  │ Step 8: Rounding       │
  │  (if required)         │
  └──────────┬─────────────┘
             │
             ▼
   ┌───────────────────────┐
   │ Output: Operations    │
   │  ΔQ for each asset    │
   └───────────────────────┘
```

---

## Invariants and Properties

### Mathematical Invariants

1. **Sum of weights = 100%**
   ```
   Σᵢ wᵢ = 1
   Σᵢ ŵᵢ = 1
   Σᵢ ŵᵢ,new = 1
   ```

2. **Sum of value changes = available cash** (before CF closure)
   ```
   Σᵢ ΔVᵢ = C_available
   ```

3. **Cash flow at target** (after step 6)
   ```
   Σᵢ cash_inᵢ − Σᵢ cash_outᵢ ≈ −C_available
   ```

### Desirable Properties

1. **Determinism**: Same input → same output
2. **Explainability**: Every step is reconstructable
3. **Efficiency**: O(N) time complexity
4. **Robustness**: Handles edge cases (empty portfolio, 100% target on one asset, etc.)

---

## Limitations and Assumptions

### Assumptions

1. **Constant prices**: Prices don't change during operation execution
2. **Infinite liquidity**: Can buy/sell any quantity
3. **Known average cost**: Average cost basis is available for all holdings
4. **Simultaneous execution**: All operations happen at once

### Limitations

1. **No optimization**: Proportional scaling, not numerical optimization
2. **Single currency**: All prices in the same currency
3. **Simplified taxation**: Linear capital gains tax, no loss harvesting
4. **No lot constraints**: Doesn't consider minimum lots or multiples

### Possible Future Extensions

- Lot constraint handling (e.g., multiples of 100)
- Tax loss harvesting
- Purchase prioritization based on criteria
- Multi-currency handling with exchange rates
- Non-linear commission structures

---

## Validation

### Unit Tests

Each step must be tested individually with:
- Normal cases
- Edge cases (1-asset portfolio, all targets at 0 except one, etc.)
- Error cases (target sum ≠ 100%, negative prices, etc.)

### Integration Tests

The complete algorithm must be tested end-to-end with:
- Real portfolios
- Verification that invariants are respected
- Check that final CF is close to target
- Validation that ŵᵢ,new ≈ wᵢ

### Property-Based Testing

Use frameworks like Hypothesis to automatically generate test cases and verify universal properties.
