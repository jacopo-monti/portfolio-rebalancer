# Web Application Guide

This guide provides detailed information about the Streamlit web application for portfolio rebalancing.

---

## Quick Start

### Installation and Launch

```bash
# Install the package with dependencies
pip install portfolio-rebalancer

# Launch the web application
streamlit run app.py
```

The app will automatically open in your default browser at `http://localhost:8501`.

---

## Application Architecture

### File Structure

```
portfolio-rebalancer/
├── app.py                     # Main Streamlit application (entry point)
└── webapp/
    ├── __init__.py            # Package initialization
    └── ui_helpers.py          # UI utility functions
```

### Design Principles

1. **UI as Wrapper**: The web app is a thin layer over the core rebalancing logic
2. **No Refactoring**: Core logic remains untouched; UI only converts between representations
3. **In-Memory Only**: No database, no persistence, no files saved
4. **Local First**: Runs entirely on your computer, no cloud services
5. **Single Source of Truth**: The `RebalancingEngine` in `src/portfolio_rebalancer/engine/` is the only calculation logic

---

## Application Components

### 1. Main Application (`app.py`)

The entry point for the Streamlit app with three main tabs:

#### Tab 1: Target & Portfolio
- **Purpose**: Input and configure portfolio data
- **Features**:
  - Interactive data table (Excel-like editing)
  - Add/remove assets dynamically
  - Portfolio metadata (name, available cash)
  - Real-time validation
  - Summary metrics

#### Tab 2: Analysis
- **Purpose**: Run rebalancing and display results
- **Features**:
  - One-click rebalancing calculation
  - Current portfolio state display
  - Required operations table
  - Cash flow summary
  - Post-rebalancing portfolio view
  - Accuracy metrics

#### Tab 3: Settings
- **Purpose**: Configure algorithm parameters
- **Features**:
  - Rounding policy selection
  - Algorithm information
  - Assumptions and limitations documentation

### 2. UI Helpers (`webapp/ui_helpers.py`)

Utility functions that bridge the UI and core logic:

#### Data Conversion Functions

**`create_default_assets()`**
- Creates a default 3-asset example portfolio
- Used for initialization and reset functionality

**`assets_to_dataframe(assets_data)`**
- Converts list of asset dictionaries to pandas DataFrame
- Enables display and editing in Streamlit

**`dataframe_to_assets(df)`**
- **Critical function**: Maps UI representation to domain models
- Converts percentages (0-100) to decimals (0-1)
- Creates `Asset` model objects from DataFrame rows
- Example:
  ```python
  # UI: Target Weight = 60.0 (user enters "60")
  # Core: target_weight = 0.60 (decimal for calculations)
  ```

**`validate_assets_data(df)`**
- Validates portfolio data before processing
- Checks:
  - At least one asset present
  - Required columns exist
  - No duplicate symbols
  - Target weights sum to 100%
  - Positive prices
  - Non-negative quantities
  - Valid tax rates (0-100%)
  - Valid target weights (0-100%)

#### Display Functions

**`create_current_state_dataframe(portfolio)`**
- Displays current portfolio before rebalancing
- Shows: Symbol, Quantity, Price, Value, Current Weight, Target Weight, Deviation

**`create_operations_dataframe(result)`**
- Displays required rebalancing operations
- Shows: Symbol, Action (BUY/SELL/HOLD), Quantity, Value, Tax

**`create_post_rebalancing_dataframe(result)`**
- Displays portfolio after rebalancing
- Shows: Symbol, New Quantity, New Value, New Weight, Target Weight, Deviation

#### Formatting Functions

**`format_currency(value)`**
- Formats numbers as euros: `€1,234.56`

**`format_percentage(value, decimal_places=2)`**
- Converts decimals to percentages: `0.26 → "26.00%"`

---

## Session State Management

Streamlit uses session state to persist data between reruns. The app stores:

### Core Data
- **`assets_data`**: List of asset dictionaries (the portfolio)
- **`rebalancing_result`**: Last rebalancing calculation result
- **`portfolio_name`**: User-defined portfolio name
- **`cash_available`**: Available cash to deploy

### Settings
- **`apply_rounding`**: Whether to round shares to integers
- **`rounding_policy`**: Rounding method (FLOOR/ROUND/CEIL)

### Access Pattern
```python
# Initialize (only runs once)
if "assets_data" not in st.session_state:
    st.session_state.assets_data = create_default_assets()

# Read
data = st.session_state.assets_data

# Write
st.session_state.assets_data = new_data
```

---

## Data Flow

### Input Flow (Tab 1 → Core Logic)

1. **User edits data in table** → Streamlit `data_editor` widget
2. **DataFrame updated** → `st.session_state.assets_data`
3. **Validation** → `validate_assets_data(df)`
4. **Conversion to domain models** → `dataframe_to_assets(df)` creates `Asset` objects
5. **Portfolio creation** → `Portfolio(assets=assets, cash_available=...)`
6. **Ready for rebalancing** → Core logic receives pure domain models

### Processing Flow (Tab 2)

1. **User clicks "Run Analysis"** → Button click triggers calculation
2. **Retrieve portfolio data** → From session state
3. **Validation check** → Ensure data is valid
4. **Create domain models** → Convert UI → `Asset` → `Portfolio`
5. **Create engine** → `RebalancingEngine(rounding_policy=...)`
6. **Execute rebalancing** → `engine.rebalance(portfolio)`
7. **Store result** → `st.session_state.rebalancing_result = result`
8. **Display results** → Convert `RebalancingResult` to DataFrames for display

### Output Flow (Core Logic → Display)

1. **RebalancingResult object** → Returned by engine
2. **Extract data** → Access `result.assets`, `result.cash_flow`, etc.
3. **Format for display** → `create_operations_dataframe(result)`
4. **Render in UI** → `st.dataframe(...)`, `st.metric(...)`, etc.

---

## Key Design Decisions

### Why Percentages in UI?

Users think in percentages ("60% in stocks"), but the core logic uses decimals (0.60).

**Conversion happens in `dataframe_to_assets()`:**
```python
target_weight=float(row["Target Weight (%)"]) / 100.0  # 60.0 → 0.60
tax_rate=float(row["Tax Rate (%)"]) / 100.0           # 26.0 → 0.26
commission_buy_percent=float(row["Buy % Fee"]) / 100.0 # 0.1 → 0.001
```

### Why In-Memory Only?

This is a **demo application** to showcase the rebalancing logic. Features intentionally excluded:
- No database (PostgreSQL, SQLite, etc.)
- No file persistence
- No user authentication
- No cloud deployment
- No API endpoints

**Benefits:**
- Simple to run locally
- No setup complexity
- Privacy (data never leaves your computer)
- Focus on core calculation logic

### Why Three Tabs?

Mirrors the workflow of the Excel files:
1. **Excel Input File** → Tab 1 (Target & Portfolio)
2. **Run Calculation** → Tab 2 (Analysis)
3. **Excel Output File** → Tab 2 (Results display)
4. **Configuration** → Tab 3 (Settings)

---

## Extending the Web App

### Adding a New Input Field

**Example: Add a "Notes" field for each asset**

1. **Update default data** in `ui_helpers.py`:
   ```python
   def create_default_assets():
       return [
           {
               "Symbol": "VWCE",
               "Quantity": 50.0,
               # ... other fields ...
               "Notes": "Core holding",  # New field
           },
       ]
   ```

2. **Update data editor** in `app.py` (Tab 1):
   ```python
   column_config={
       # ... existing config ...
       "Notes": st.column_config.TextColumn("Notes", max_chars=100),
   }
   ```

3. **Handle in conversion** (if needed for core logic):
   ```python
   # In dataframe_to_assets() if the core Asset model needs it
   # Otherwise, just ignore it (for display-only fields)
   ```

### Adding a New Display Section

**Example: Add a "Tax Summary" section**

1. **Create helper function** in `ui_helpers.py`:
   ```python
   def create_tax_summary_dataframe(result):
       data = []
       for asset in result.assets:
           if asset.delta_quantity < 0:  # Only sales
               # Calculate tax details
               data.append({...})
       return pd.DataFrame(data)
   ```

2. **Add to Analysis tab** in `app.py`:
   ```python
   st.subheader("💰 Tax Summary")
   tax_df = create_tax_summary_dataframe(result)
   st.dataframe(tax_df, use_container_width=True)
   ```

### Adding a New Algorithm Parameter

**Example: Add a "minimum transaction value" threshold**

1. **Add to session state** in `app.py`:
   ```python
   if "min_transaction_value" not in st.session_state:
       st.session_state.min_transaction_value = 100.0
   ```

2. **Add input in Settings tab**:
   ```python
   st.session_state.min_transaction_value = st.number_input(
       "Minimum Transaction Value (€)",
       min_value=0.0,
       value=st.session_state.min_transaction_value,
       help="Skip buy/sell operations below this value"
   )
   ```

3. **Pass to core logic** (if implemented in engine):
   ```python
   engine = RebalancingEngine(
       rounding_policy=rounding_policy,
       min_transaction_value=st.session_state.min_transaction_value
   )
   ```

---

## Troubleshooting

### Common Issues

**Issue**: Data disappears when I refresh the page
- **Cause**: Session state is reset on page refresh (by design)
- **Solution**: Use Python scripts or Excel files for persistent workflows

**Issue**: Validation errors even though data looks correct
- **Cause**: Target weights might not sum to exactly 100% due to rounding
- **Solution**: Check the sum displayed below the table, adjust weights slightly

**Issue**: "Module not found" error when running
- **Cause**: Package not installed or not in editable mode
- **Solution**: Run `pip install -e .` from the project root

**Issue**: Changes in code don't reflect in the app
- **Cause**: Streamlit caches code and data
- **Solution**: Press `C` in the terminal running Streamlit to clear cache, or click "Rerun" in the browser

### Debugging Tips

**1. Enable debug mode:**
```python
# Add this at the top of app.py after imports
if st.checkbox("Show Debug Info"):
    st.write("Session State:", st.session_state)
```

**2. Inspect data at each step:**
```python
# In Tab 2, before calling engine.rebalance()
st.write("Portfolio Assets:", portfolio.assets)
st.write("Total Value:", portfolio.total_value)
```

**3. Check validation results:**
```python
# After validate_assets_data()
is_valid, error_msg = validate_assets_data(df)
st.write(f"Valid: {is_valid}, Error: {error_msg}")
```

---

## Performance Considerations

### Current Performance

- **Typical portfolios (3-10 assets)**: Instant (<100ms)
- **Large portfolios (50+ assets)**: Still fast (<500ms)
- **Bottleneck**: Not the calculation, but the UI rendering

### Optimization Tips

If you extend the app and notice slowness:

1. **Use `@st.cache_data` for expensive computations:**
   ```python
   @st.cache_data
   def expensive_calculation(data):
       # ... complex processing ...
       return result
   ```

2. **Avoid recomputing in every rerun:**
   ```python
   # Bad: Recalculates every time
   result = engine.rebalance(portfolio)
   
   # Good: Only recalculates when button clicked
   if st.button("Run Analysis"):
       result = engine.rebalance(portfolio)
       st.session_state.result = result
   ```

3. **Use `use_container_width=True` for tables:**
   ```python
   st.dataframe(df, use_container_width=True)  # Better rendering
   ```

---

## Security Considerations

### What's Safe

✅ **Running locally**: All processing happens on your computer
✅ **No network requests**: App doesn't connect to external services
✅ **No data persistence**: Data is lost when you close the browser
✅ **Open source**: Code is visible and auditable

### What to Avoid

❌ **Don't deploy to public internet** without:
  - Adding authentication
  - Implementing rate limiting
  - Securing data transmission
  - Adding input sanitization

❌ **Don't store sensitive data** in the app:
  - Account numbers
  - Personal financial details
  - API keys or credentials

### Best Practices

1. **Run on localhost only** (default behavior)
2. **Use HTTPS if deploying** (even locally with self-signed cert)
3. **Don't commit sensitive data** to version control
4. **Review code changes** before running updates

---

## Deployment (Optional)

While the app is designed for local use, you can deploy it if needed:

### Local Network Deployment

```bash
# Make app accessible on your local network
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

### Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t portfolio-rebalancer .
docker run -p 8501:8501 portfolio-rebalancer
```

**Note**: Deployment is not required for the demo use case.

---

## Future Enhancements (Not Implemented)

Potential features for future versions:

- 📊 **Visualization**: Charts showing weight deviations, cash flow breakdown
- 💾 **Save/Load**: Export portfolios to JSON, import from CSV
- 📝 **History**: Track rebalancing operations over time
- 🔔 **Alerts**: Notify when portfolio drifts beyond threshold
- 🌍 **Multi-currency**: Support for non-euro portfolios
- 📱 **Mobile UI**: Responsive design for phones/tablets
- 🔐 **Authentication**: User accounts for multi-user deployments
- ☁️ **Cloud Storage**: Optional save to cloud services

**But for the demo**: Keep it simple, local, and focused on the core calculation logic.

---

## Summary

### What the Web App Does

✅ Provides a visual, Excel-like interface for portfolio rebalancing
✅ Wraps the existing Python logic without modifying it
✅ Runs entirely locally with no external dependencies
✅ Stores data in-memory only (no persistence)
✅ Validates inputs and displays results clearly

### What the Web App Doesn't Do

❌ Doesn't store data permanently
❌ Doesn't connect to brokers or market data APIs
❌ Doesn't execute trades automatically
❌ Doesn't replace the core rebalancing engine
❌ Doesn't require a database or cloud services

### Key Takeaway

**The web app is a thin UI layer over the core rebalancing logic.**

The `RebalancingEngine` in `src/portfolio_rebalancer/engine/rebalancer.py` is the single source of truth. The web app just makes it easier to use without writing Python code.

---

## Questions?

For issues or suggestions about the web app, open an issue on GitHub:
https://github.com/jacopo-monti/portfolio-rebalancer/issues
