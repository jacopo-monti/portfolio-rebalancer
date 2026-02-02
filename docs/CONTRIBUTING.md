# Contributing to Portfolio Rebalancer

Thank you for your interest in contributing to Portfolio Rebalancer! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Project Philosophy](#project-philosophy)

## Code of Conduct

### Our Standards

- **Be respectful**: Treat everyone with respect and consideration
- **Be constructive**: Provide constructive feedback
- **Be collaborative**: Work together towards common goals
- **Be professional**: Keep discussions focused and professional

### Unacceptable Behavior

- Harassment or discriminatory language
- Personal attacks
- Trolling or insulting comments
- Publishing others' private information

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- GitHub account
- Familiarity with:
  - Python programming
  - Git version control
  - pytest testing framework
  - Basic financial concepts (portfolios, rebalancing)

### Setting Up Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/portfolio-rebalancer.git
   cd portfolio-rebalancer
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/jacopo-monti/portfolio-rebalancer.git
   ```

4. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Install in development mode**:
   ```bash
   pip install -e ".[dev]"
   ```

6. **Verify installation**:
   ```bash
   pytest
   ```

## Development Workflow

### 1. Create a Branch

Always work on a feature branch, not on `main`:

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create and switch to feature branch
git checkout -b feature/my-feature-name
```

Branch naming conventions:
- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/improvements

Examples:
- `feature/add-custom-rounding`
- `bugfix/fix-cash-flow-calculation`
- `docs/improve-algorithm-explanation`

### 2. Make Changes

Follow these guidelines:

#### Code Changes

- Write clean, readable code
- Follow existing code style
- Add docstrings to all public functions/classes
- Keep functions small and focused
- Avoid complex nested structures

#### Test Changes

- Add tests for new features
- Update tests for modified features
- Ensure all tests pass
- Aim for high test coverage (>80%)

#### Documentation Changes

- Update relevant documentation
- Add docstrings for new code
- Update README.md if needed
- Keep language clear and concise

### 3. Commit Changes

Write clear, descriptive commit messages:

```bash
git add <files>
git commit -m "Type: Brief description

Detailed explanation of what changed and why.
Reference any related issues.

Fixes #123"
```

Commit message format:
```
Type: Brief description (50 chars or less)

Detailed explanation wrapped at 72 characters. Explain:
- What changed
- Why it changed
- Any breaking changes
- Related issues

Example types:
- Feature: Add new feature
- Bugfix: Fix bug in X
- Docs: Update documentation
- Refactor: Refactor code structure
- Test: Add/update tests
- Style: Format code (no functional changes)
```

Example:
```
Feature: Add custom rounding policy

Implement a new rounding policy that allows users to specify
custom rounding logic. This adds flexibility for edge cases
where standard floor/round/ceil is insufficient.

- Add CUSTOM enum to RoundingPolicy
- Implement _apply_custom_rounding method
- Add comprehensive tests
- Update documentation

Resolves #42
```

### 4. Stay Updated

Regularly sync with upstream:

```bash
git fetch upstream
git rebase upstream/main
```

If there are conflicts:
1. Resolve them manually
2. `git add <resolved-files>`
3. `git rebase --continue`

### 5. Push Changes

```bash
git push origin feature/my-feature-name
```

## Code Standards

### Python Style

We follow [PEP 8](https://pep8.org/) with these additions:

#### Code Formatting

- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings
- **Imports**: Grouped and sorted
  ```python
  # Standard library
  import math
  from typing import Optional, Tuple
  
  # Third party
  import pytest
  
  # Local
  from portfolio_rebalancer.models import Asset
  ```

#### Naming Conventions

- **Classes**: `PascalCase` (e.g., `RebalancingEngine`)
- **Functions/Methods**: `snake_case` (e.g., `compute_cash_flow`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_ITERATIONS`)
- **Private methods**: Prefix with `_` (e.g., `_compute_current_state`)

#### Docstrings

Use Google-style docstrings:

```python
def compute_cash_in(self, quantity_sold: float) -> float:
    """Compute net cash from selling quantity, accounting for taxes.
    
    Formula: 
        Capital gain per share: G = P − PMC
        Tax per share: T_share = T × max(0, G)
        Cash in: cash_in = qty × (P − T_share)
    
    Args:
        quantity_sold: Number of shares to sell (positive value)
        
    Returns:
        Net cash received after capital gains tax
        
    Raises:
        ValueError: If quantity_sold is negative
        
    Example:
        >>> asset = Asset("VWCE", 100, 110.0, 100.0, 0.26, 0.60)
        >>> asset.compute_cash_in(10.0)
        1074.0
    """
```

### Type Hints

Use type hints for all function signatures:

```python
from typing import Optional, Tuple, List

def rebalance(self, portfolio: Portfolio) -> RebalancingResult:
    """Execute rebalancing algorithm."""
    pass

def _compute_cash_flow(self, portfolio: Portfolio) -> Tuple[float, float, float]:
    """Compute cash flow with taxation."""
    pass
```

**Important**: For Python 3.8 compatibility, use `Tuple` from `typing`, not built-in `tuple`.

### Code Quality Tools

#### Black (Code Formatter)

```bash
# Format all code
black src/ tests/

# Check without modifying
black --check src/ tests/
```

#### Flake8 (Linter)

```bash
# Check code style
flake8 src/ tests/
```

Configuration in `pyproject.toml`:
```toml
[tool.flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,venv
```

#### MyPy (Type Checker)

```bash
# Type check
mypy src/
```

## Testing Guidelines

### Test Structure

Tests are organized by module:

```
tests/
├── test_engine.py      # RebalancingEngine tests
├── test_models.py      # Asset, Portfolio, Result tests
└── test_policies.py    # Policy tests
```

### Writing Tests

#### Test Class Structure

```python
import pytest
from portfolio_rebalancer.models import Asset, Portfolio
from portfolio_rebalancer.engine import RebalancingEngine


class TestRebalancingEngine:
    """Tests for RebalancingEngine."""
    
    @pytest.fixture
    def simple_portfolio(self):
        """Create a simple test portfolio."""
        return Portfolio(
            assets=[
                Asset("A", 50.0, 100.0, 95.0, 0.26, 0.60),
                Asset("B", 30.0, 110.0, 108.0, 0.26, 0.40),
            ]
        )
    
    def test_engine_initialization(self):
        """Test engine can be initialized."""
        engine = RebalancingEngine()
        assert engine is not None
        assert engine.rounding_policy is None
    
    def test_rebalance_returns_result(self, simple_portfolio):
        """Test that rebalancing returns a RebalancingResult."""
        engine = RebalancingEngine()
        result = engine.rebalance(simple_portfolio)
        
        assert result is not None
        assert result.total_value_before > 0
```

#### Test Naming

- Test files: `test_<module>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<what_it_tests>`

Examples:
- `test_cash_flow_approximates_zero`
- `test_weights_close_to_target`
- `test_invalid_tax_rate_raises_error`

#### Assertions

Use descriptive assertions:

```python
# Good
assert result.cash_flow < 1.0, f"Cash flow {result.cash_flow} exceeds tolerance"

# Better with pytest.approx for floats
assert result.total_value == pytest.approx(expected, rel=1e-6)
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=portfolio_rebalancer --cov-report=html

# Run specific test file
pytest tests/test_engine.py

# Run specific test
pytest tests/test_engine.py::TestRebalancingEngine::test_cash_flow_approximates_zero

# Run with verbose output
pytest -v

# Run and stop at first failure
pytest -x
```

### Coverage Requirements

- Aim for **>80% coverage** overall
- **100% coverage** for core engine logic
- New features must include tests
- Bug fixes must include regression tests

## Documentation

### When to Update Documentation

Update documentation when you:
- Add new features
- Change existing behavior
- Fix bugs with user-visible impact
- Add/remove dependencies
- Change API

### Documentation Files

- **README.md**: User-facing documentation
- **docs/ALGORITHM.md**: Detailed algorithm explanation
- **docs/DESIGN.md**: Design decisions and rationale
- **docs/CONTRIBUTING.md**: This file
- **Docstrings**: In-code documentation

### Docstring Style

Follow Google style:

```python
def function_name(param1: type1, param2: type2) -> return_type:
    """Brief description (one line).
    
    Detailed description if needed. Can span multiple paragraphs.
    Explain what the function does, not how it does it.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ErrorType: When this error occurs
        
    Example:
        >>> function_name(value1, value2)
        expected_result
    """
```

## Submitting Changes

### Before Submitting

Ensure your changes meet these criteria:

- [ ] All tests pass
- [ ] Code is formatted with Black
- [ ] No linting errors (Flake8)
- [ ] Type checking passes (MyPy)
- [ ] Coverage maintained or improved
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] No merge conflicts with main

### Creating a Pull Request

1. **Push your branch**:
   ```bash
   git push origin feature/my-feature
   ```

2. **Open Pull Request** on GitHub:
   - Go to your fork on GitHub
   - Click "Pull Request"
   - Select your branch
   - Fill in the PR template

3. **PR Description Template**:
   ```markdown
   ## Description
   Brief description of changes
   
   ## Motivation
   Why are these changes needed?
   
   ## Changes Made
   - Change 1
   - Change 2
   - Change 3
   
   ## Testing
   How were these changes tested?
   
   ## Related Issues
   Closes #123
   
   ## Checklist
   - [ ] Tests pass
   - [ ] Code formatted
   - [ ] Documentation updated
   - [ ] No breaking changes
   ```

4. **Respond to feedback**:
   - Be open to suggestions
   - Make requested changes promptly
   - Discuss disagreements respectfully

### Review Process

1. **Automated checks** run (tests, linting)
2. **Maintainer reviews** code
3. **Feedback provided** if changes needed
4. **Approval** when ready
5. **Merge** by maintainer

## Project Philosophy

### Core Principles

When contributing, respect these principles:

1. **Determinism First**
   - Same input must always produce same output
   - No random number generation
   - No stochastic optimization
   
2. **Simplicity Over Optimization**
   - Use elementary math when possible
   - Avoid complex numerical solvers
   - No black-box optimization
   
3. **Transparency**
   - Every calculation must be traceable
   - Algorithm must be explainable
   - No hidden assumptions
   
4. **No Financial Advice**
   - Tool computes, doesn't advise
   - No market predictions
   - No asset recommendations

### Acceptable Contributions

✅ **Yes**:
- Bug fixes
- Performance improvements (that maintain determinism)
- Documentation improvements
- Test additions
- Code quality improvements
- New I/O formats (Excel, JSON, etc.)
- New rounding policies
- Better error messages
- Usability improvements

❌ **No**:
- Machine learning features
- Stochastic optimization
- Market prediction
- Asset recommendation
- Non-deterministic features
- Features that violate core principles

### When in Doubt

If you're unsure whether a contribution fits the project:
1. Open an issue first to discuss
2. Explain your idea and rationale
3. Wait for feedback from maintainers
4. Only then start coding

## Questions?

If you have questions:
- Check existing documentation
- Search closed issues
- Open a new issue with the `question` label

## Thank You!

Your contributions make this project better. We appreciate your time and effort! 🙏
