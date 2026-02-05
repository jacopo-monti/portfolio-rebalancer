# Design Decisions

This document explains the rationale behind the architectural and algorithmic choices of the project.

## Project Philosophy

### Why NOT an Optimizer?

Many portfolio management tools use numerical optimizers (solvers, quadratic programming, etc.). We chose **not** to do this for several reasons:

#### 1. Transparency and Explainability

A numerical optimizer is a "black box":
- Users don't understand *why* a certain operation is suggested
- It's difficult to debug when something goes wrong
- The decision-making process cannot be traced

**Our choice**: Elementary mathematics, every step is understandable.

#### 2. Determinism

Many numerical solvers are stochastic or depend on initial conditions:
- Different executions → slightly different results
- Difficult to test
- Not reproducible

**Our choice**: Same input → **always** the same output.

#### 3. Simplicity

Optimization adds heavy dependencies:
- Libraries like SciPy, CVXPY, or commercial solvers
- Greater code complexity
- Harder to maintain

**Our choice**: Only pandas and elementary operations.

#### 4. The Problem Doesn't Require It

Rebalancing to target percentages is a **mathematically simple** problem:
- No complex objective functions needed
- No non-linear constraints
- The "obvious" solution (proportional) works well

**Our choice**: Keep it simple.

---

## Software Architecture

### Core / I/O Separation

```
┌─────────────────┐
│   Core Engine   │  ← Pure mathematics, NO external dependencies
│  (engine/)      │
└────────┬────────┘
         │
         │  uses
         ▼
┌─────────────────┐
│     Models      │  ← Pure data structures
│   (models/)     │
└────────┬────────┘
         │
         │  used by
         ▼
┌─────────────────┐
│   I/O Layer     │  ← Excel, CSV, JSON, ...  (may depend on external libraries)
│    (io/)        │
└─────────────────┘
         ▲
         │
         │  configured by
┌─────────────────┐
│    Policies     │  ← Behavioral configuration
│  (policies/)    │
└─────────────────┘
```

#### Advantages

1. **Testability**: The core engine can be tested without creating Excel files
2. **Extensibility**: New I/O formats without touching the core
3. **Portability**: The core can be used in different contexts (CLI, web app, Jupyter, etc.)

### Models: Pure Data Classes

Classes in `models/` are **simple data containers**:
- No business logic
- No external dependencies
- Easily serializable

```python
@dataclass
class Asset:
    symbol: str
    quantity: float
    price: float
    avg_cost: float
    tax_rate: float
    target_weight: float
    # Commission parameters
    commission_buy_fixed: float = 0.0
    commission_buy_percent: float = 0.0
    # ... (and sell commissions)
```

### Engine: Pure Functions

The core engine consists of pure (or nearly pure) functions:
- Input → processing → output
- No side effects
- No global state

```python
def rebalance(portfolio: Portfolio) -> RebalancingResult:
    # Steps 1-8 of the algorithm
    ...
    return result
```

### Policies: Configurability

Policies allow behavior configuration without modifying the core:
- `RoundingPolicy`: How to round shares
- Future extensions: `TolerancePolicy`, `TaxPolicy`, etc.

---

## Algorithmic Choices

### Cash Flow Closure: Proportional Scaling

#### The Problem

After calculating ΔQᵢ, the cash flow might not be at target:
```
CF = Σ cash_inᵢ − Σ cash_outᵢ ≠ CF_target
```

Where `CF_target = -cash_available` (negative because we want to spend it).

#### Approach 1: Optimization (REJECTED)

We could formulate an optimization problem:

```
minimize:  Σᵢ (ŵᵢ,new − wᵢ)²
subject to: CF = CF_target
```

Problems:
- Requires a solver
- Non-deterministic
- Complex
- Overkill for the problem

#### Approach 2: Proportional Scaling (CHOSEN)

Scale only purchases proportionally:

```
ΔQᵢ,adjusted = ΔQᵢ × (1 + (CF − CF_target) / Σⱼ cash_outⱼ)    for ΔQᵢ > 0
```

Advantages:
- Simple (one line of code)
- Deterministic
- Intuitive: "reduce all purchases by the same percentage"
- No external dependencies

Disadvantages:
- Not "optimal" in mathematical sense
- May slightly unbalance weights

**Verdict**: The advantages far outweigh the disadvantages. The practical difference is negligible.

### Taxation: Simplified Approach

The cash_in formula includes taxation:

```
cash_inᵢ = |ΔQᵢ| × (Pᵢ − Tᵢ × max(0, Pᵢ − PMCᵢ)) − C_sell,i
```

Or expanded:
```
cash_inᵢ = |ΔQᵢ| × Pᵢ − |ΔQᵢ| × Tᵢ × max(0, Pᵢ − PMCᵢ) − C_sell,i
```

#### Assumptions

1. **Linear capital gains tax**: Constant rate Tᵢ
2. **No loss harvesting**: If selling at a loss, tax is 0, but we don't recover prior losses
3. **No FIFO/LIFO**: Use average cost (PMC) for simplicity

#### Future Extensions

- **Tax loss harvesting**: Sell assets at a loss to offset gains
- **FIFO/LIFO**: Choose which lots to sell
- **Progressive tax rates**: Handle tax brackets

**Current choice**: Keep it simple. 90% of cases are covered.

### Broker Commissions: Implemented and Configurable

The system includes comprehensive broker commission handling:

```python
# For each asset, commissions can be configured separately for buy/sell
commission = fixed_fee + bounded(value × percent, min, max)
```

#### Features

1. **Fixed component**: Flat fee per transaction
2. **Percentage component**: Proportional to transaction value
3. **Min/max bounds**: For percentage-based commissions
4. **Separate buy/sell**: Different commission structures for purchases and sales

#### Impact on Cash Flow

- **Sales**: `cash_in = gross_proceeds − tax − sell_commission`
- **Purchases**: `cash_out = purchase_cost + buy_commission`

This affects the cash flow closure calculation, making it more realistic for real-world trading.

### Rounding: Outside the Core

Rounding to integer shares is **optional** and happens **after** calculation:

1. The core calculates ΔQᵢ as a decimal number
2. An (optional) policy rounds it
3. CF and residual deviations are recalculated

#### Why?

- **Flexibility**: Some assets (funds, fractional shares) allow decimal quantities
- **Separation**: The core doesn't need to know about integer share restrictions
- **Transparency**: Users see both the "ideal" value and the rounded value

---

## Implementation Choices

### Python as Language

**Advantages**:
- Readable: code is almost pseudocode
- Rich ecosystem: pandas, pytest, black, mypy
- Portable: runs everywhere
- Popular in quantitative finance

**Disadvantages**:
- Performance: slower than C++/Rust
- Type safety: optional (mypy helps)

**Verdict**: For this type of application, Python is perfect. Performance is not critical (< 1s even for hundreds of assets).

### Pandas vs NumPy

**Choice**: We use pandas for I/O (Excel), but the core uses native structures.

**Why?**
- Pandas is convenient for reading/writing Excel
- But for the core, lists and dataclasses are simpler
- Fewer "heavy" dependencies in the core

### Type Hints and MyPy

The code uses complete type hints:

```python
def rebalance(portfolio: Portfolio) -> RebalancingResult:
    ...
```

**Advantages**:
- Inline documentation
- Static checking with mypy
- Better IDE support (autocomplete)
- Harder to make mistakes

### Testing Strategy

```
tests/
├── test_models.py        # Test data structures
├── test_engine.py        # Test core engine
├── test_policies.py      # Test policies
├── test_io_excel.py      # Test Excel I/O
└── test_integration.py   # End-to-end tests
```

**Goal**: 100% code coverage of the core engine.

---

## Choices NOT Made (and Why)

### Multi-Objective Optimization

**Not implemented**: Simultaneous optimization of multiple objectives (e.g., minimize taxes AND minimize number of operations).

**Why**: Adds enormous complexity. Users can choose different policies to achieve different results.

### Broker Integration

**Not implemented**: Automatic order execution with a broker.

**Why**: 
- Increases legal liability
- Every broker has different APIs
- Requires error handling, authentication, security
- Out of scope: "calculate operations", not "execute operations"

### Automatic Price Retrieval

**Not implemented**: Automatic download of prices from Yahoo Finance, Alpha Vantage, etc.

**Why**:
- External APIs can change or become paid
- Rate limiting
- Different providers for different instruments
- Users often already have prices from their broker

**Compromise**: We provide example scripts in the `examples/` folder for those who want it.

### Machine Learning

**Not implemented**: Predictions, asset clustering, etc.

**Why**: Completely out of scope. This tool does NOT make predictions. Only deterministic mathematics.

### Multi-Currency Management

**Not implemented**: Portfolios with assets in different currencies.

**Why**: 
- Adds complexity (exchange rates, hedging, etc.)
- 90% of users have single-currency portfolios
- Can be added in the future as an extension

**Current workaround**: Users manually convert all prices to a reference currency.

---

## Design Constraints

### Must Have

1. ✅ Determinism
2. ✅ Transparency
3. ✅ No complex numerical optimization
4. ✅ Tax-aware
5. ✅ Commission-aware
6. ✅ Cash-flow neutral or cash-deployment capable

### Should Have

1. ✅ Integer share handling
2. ✅ Excel input
3. ✅ Readable output
4. ✅ Complete documentation

### Nice to Have

1. ⏳ Web interface
2. ⏳ Automatic price retrieval (example)
3. ⏳ PDF report export
4. ⏳ Multi-currency

### Won't Have

1. ❌ Risk/return optimization
2. ❌ Asset selection
3. ❌ Market predictions
4. ❌ Automatic broker integration
5. ❌ Machine learning

---

## Performance

### Time Complexity

- **Steps 1-5**: O(N) where N = number of assets
- **Step 6**: O(N)
- **Step 7**: O(N)
- **Step 8**: O(N)

**Total**: O(N)

### Benchmarks

On a modern laptop (2020):
- Portfolio of 10 assets: < 1 ms
- Portfolio of 100 assets: < 10 ms
- Portfolio of 1000 assets: < 100 ms

Performance is **not** a problem.

---

## Lessons Learned

### Keep It Simple

The temptation to "optimize" was strong. Resisting and keeping the algorithm simple was the right choice.

### Documentation Before Code

Writing mathematical specifications first (ALGORITHM.md, VARIABLES.md) made coding much easier and less error-prone.

### Testing Is Fundamental

Comprehensive tests allow:
- Refactoring without fear
- Adding features with confidence
- Documenting expected behavior

### Separation of Concerns

Core engine separated from I/O was a winning choice. Enables reuse and testability.

---

## Future Evolution

The project is designed to be extensible:

### Version 1.x (Current)
- Mathematical core engine
- Excel I/O
- Basic policies
- CLI
- Broker commission support

### Version 2.x (Future)
- Web interface (Flask/FastAPI + React)
- Database for operation history
- More export formats (PDF, JSON, CSV)
- REST API

### Version 3.x (Vision)
- Multi-currency
- Tax loss harvesting
- Advanced constraints (lots, multiples)
- Integration with data providers (optional)

**Important**: The core engine will always remain **simple and deterministic**. Advanced features will be additional layers.

---

## Conclusions

This project demonstrates that:

1. **Simple ≠ Stupid**: An elementary algorithm can solve real problems
2. **Transparency > Optimality**: It's more important to understand what the software does than to have a "perfect" solution
3. **Determinism > Flexibility**: For financial tools, reproducibility is critical
4. **Documentation = Code**: A well-documented project is a usable project

The goal has been achieved: **a tool that anyone can understand, critique, and use with confidence**.
