#!/usr/bin/env python3
"""Streamlit web application for portfolio rebalancing.

This is a local demo web application that provides a graphical interface
for the portfolio rebalancing tool. It runs entirely locally with no database
or external services.

To run:
    streamlit run app.py

Requirements:
    - streamlit>=1.28.0
    - pandas>=1.5.0
    - portfolio_rebalancer (this package)
"""

import streamlit as st
import pandas as pd
from typing import Optional

# Import core rebalancing logic
from portfolio_rebalancer.models import Portfolio
from portfolio_rebalancer.engine import RebalancingEngine
from portfolio_rebalancer.policies.rounding import RoundingPolicy

# Import UI helpers
from webapp.ui_helpers import (
    create_default_assets,
    assets_to_dataframe,
    dataframe_to_assets,
    validate_assets_data,
    format_currency,
    format_percentage,
    create_current_state_dataframe,
    create_operations_dataframe,
    create_post_rebalancing_dataframe,
)


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Portfolio Rebalancer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if "assets_data" not in st.session_state:
    st.session_state.assets_data = create_default_assets()

if "rebalancing_result" not in st.session_state:
    st.session_state.rebalancing_result = None

if "portfolio_name_input" not in st.session_state:
    st.session_state.portfolio_name_input = "My Portfolio"

if "cash_available_input" not in st.session_state:
    st.session_state.cash_available_input = 0.0

if "apply_rounding_checkbox" not in st.session_state:
    st.session_state.apply_rounding_checkbox = False

if "rounding_policy_radio" not in st.session_state:
    st.session_state.rounding_policy_radio = "ROUND"

if "editing_asset_index" not in st.session_state:
    st.session_state.editing_asset_index = None


# ============================================================================
# HELPER FUNCTIONS FOR ASSET MANAGEMENT
# ============================================================================

def validate_asset_input(symbol: str, quantity: float, price: float, avg_cost: float,
                        tax_rate: float, target_weight: float) -> tuple[bool, str]:
    """Validate asset input fields.
    
    Args:
        symbol: Asset symbol
        quantity: Number of shares
        price: Current price
        avg_cost: Average cost basis
        tax_rate: Capital gains tax rate (%)
        target_weight: Target portfolio weight (%)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate symbol
    if not symbol or symbol.strip() == "":
        return False, "Asset name/symbol cannot be empty"
    
    # Validate quantity
    if quantity < 0:
        return False, "Quantity must be ≥ 0"
    
    # Validate price
    if price <= 0:
        return False, "Price must be > 0"
    
    # Validate avg_cost
    if avg_cost < 0:
        return False, "Average cost must be ≥ 0"
    
    # Validate tax_rate
    if tax_rate < 0 or tax_rate > 100:
        return False, "Tax rate must be between 0% and 100%"
    
    # Validate target_weight
    if target_weight < 0 or target_weight > 100:
        return False, "Target weight must be between 0% and 100%"
    
    return True, ""


def validate_commission_fields(buy_fixed: float, buy_pct: float, buy_min: float, buy_max: float,
                              sell_fixed: float, sell_pct: float, sell_min: float, sell_max: float) -> tuple[bool, str]:
    """Validate commission input fields.
    
    Args:
        All commission parameters
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    fields = [
        (buy_fixed, "Buy fixed fee"),
        (buy_pct, "Buy % fee"),
        (buy_min, "Buy min fee"),
        (buy_max, "Buy max fee"),
        (sell_fixed, "Sell fixed fee"),
        (sell_pct, "Sell % fee"),
        (sell_min, "Sell min fee"),
        (sell_max, "Sell max fee"),
    ]
    
    for value, name in fields:
        if value < 0:
            return False, f"{name} must be ≥ 0"
        if "% fee" in name and value > 100:
            return False, f"{name} must be ≤ 100%"
    
    return True, ""


def add_asset_to_portfolio(asset_data: dict) -> None:
    """Add a new asset to the portfolio.
    
    Args:
        asset_data: Dictionary containing asset data
    """
    st.session_state.assets_data.append(asset_data)


def update_asset_in_portfolio(index: int, asset_data: dict) -> None:
    """Update an existing asset in the portfolio.
    
    Args:
        index: Index of asset to update
        asset_data: Dictionary containing updated asset data
    """
    st.session_state.assets_data[index] = asset_data


def delete_asset_from_portfolio(index: int) -> None:
    """Delete an asset from the portfolio.
    
    Args:
        index: Index of asset to delete
    """
    st.session_state.assets_data.pop(index)


def check_duplicate_symbol(symbol: str, exclude_index: Optional[int] = None) -> bool:
    """Check if symbol already exists in portfolio.
    
    Args:
        symbol: Symbol to check
        exclude_index: Optional index to exclude (for edit mode)
        
    Returns:
        True if duplicate exists
    """
    for i, asset in enumerate(st.session_state.assets_data):
        if i != exclude_index and asset["Symbol"].upper() == symbol.upper():
            return True
    return False


# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.image("https://via.placeholder.com/150x50/4CAF50/FFFFFF?text=Portfolio+Tool", width=150)
    st.title("Portfolio Rebalancer")
    st.markdown("---")
    
    st.markdown("""
    ### About
    This is a **deterministic** portfolio rebalancing tool that:
    - Calculates optimal buy/sell operations
    - Considers capital gains tax
    - Handles broker commissions
    - Maintains cash flow neutrality
    
    ### How to Use
    1. **Target & Portfolio**: Add assets and define targets
    2. **Analysis**: Run rebalancing and view results
    3. **Settings**: Configure algorithm parameters
    
    ### Note
    This tool is for **calculation purposes only**, not financial advice.
    All data is stored in-memory and lost when you close the browser.
    """)


# ============================================================================
# MAIN APPLICATION
# ============================================================================

st.title("📊 Portfolio Rebalancing Tool")
st.markdown("A deterministic, tax-aware portfolio rebalancing calculator")
st.markdown("---")

# Create tabs for the three main sections
tab1, tab2, tab3 = st.tabs(["🎯 Target & Portfolio", "📈 Analysis", "⚙️ Settings"])


# ============================================================================
# TAB 1: TARGET & PORTFOLIO
# ============================================================================

with tab1:
    st.header("Portfolio Configuration")
    st.markdown("""
    Build your portfolio by adding assets one at a time. Define each asset's current holdings 
    and target allocation.
    """)
    
    # Portfolio metadata
    col1, col2 = st.columns(2)
    with col1:
        st.text_input(
            "Portfolio Name",
            key="portfolio_name_input",
            help="Give your portfolio a name for identification"
        )
    
    with col2:
        st.number_input(
            "Available Cash to Deploy (€)",
            min_value=0.0,
            step=100.0,
            key="cash_available_input",
            help="Additional cash you want to invest. Set to 0 for cash-neutral rebalancing."
        )
    
    st.markdown("---")
    
    # Asset creation/editing form
    st.subheader("Add Asset" if st.session_state.editing_asset_index is None else "Edit Asset")
    
    # If editing, pre-populate form with existing asset data
    editing_asset = None
    if st.session_state.editing_asset_index is not None:
        editing_asset = st.session_state.assets_data[st.session_state.editing_asset_index]
    
    with st.form(key="asset_form", clear_on_submit=True):
        st.markdown("**Basic Information**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            form_symbol = st.text_input(
                "Asset Symbol/Name *",
                value=editing_asset["Symbol"] if editing_asset else "",
                help="e.g., VWCE, AAPL, BTC",
                max_chars=20
            )
        
        with col2:
            form_quantity = st.number_input(
                "Quantity (shares) *",
                min_value=0.0,
                value=float(editing_asset["Quantity"]) if editing_asset else 0.0,
                step=0.1,
                format="%.4f",
                help="Number of shares you currently own"
            )
        
        with col3:
            form_price = st.number_input(
                "Current Price (€) *",
                min_value=0.01,
                value=float(editing_asset["Price"]) if editing_asset else 100.0,
                step=0.01,
                format="%.2f",
                help="Current market price per share"
            )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            form_avg_cost = st.number_input(
                "Average Cost (€) *",
                min_value=0.0,
                value=float(editing_asset["Avg Cost"]) if editing_asset else 100.0,
                step=0.01,
                format="%.2f",
                help="Your average purchase price (for tax calculation)"
            )
        
        with col2:
            form_tax_rate = st.number_input(
                "Tax Rate (%) *",
                min_value=0.0,
                max_value=100.0,
                value=float(editing_asset["Tax Rate (%)"]) if editing_asset else 26.0,
                step=0.1,
                format="%.2f",
                help="Capital gains tax rate"
            )
        
        with col3:
            form_target_weight = st.number_input(
                "Target Weight (%) *",
                min_value=0.0,
                max_value=100.0,
                value=float(editing_asset["Target Weight (%)"]) if editing_asset else 0.0,
                step=0.1,
                format="%.2f",
                help="Desired portfolio allocation"
            )
        
        # Commission fields in expander
        with st.expander("📋 Commission Settings (Optional)", expanded=False):
            st.markdown("**Buy Commissions**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                form_buy_fixed = st.number_input(
                    "Fixed Fee (€)",
                    min_value=0.0,
                    value=float(editing_asset["Buy Fixed Fee"]) if editing_asset else 0.0,
                    step=0.01,
                    format="%.2f",
                    key="buy_fixed"
                )
            
            with col2:
                form_buy_pct = st.number_input(
                    "% Fee",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(editing_asset["Buy % Fee"]) if editing_asset else 0.0,
                    step=0.001,
                    format="%.3f",
                    key="buy_pct"
                )
            
            with col3:
                form_buy_min = st.number_input(
                    "Min Fee (€)",
                    min_value=0.0,
                    value=float(editing_asset["Buy Min Fee"]) if editing_asset else 0.0,
                    step=0.01,
                    format="%.2f",
                    key="buy_min"
                )
            
            with col4:
                form_buy_max = st.number_input(
                    "Max Fee (€)",
                    min_value=0.0,
                    value=float(editing_asset["Buy Max Fee"]) if editing_asset else 0.0,
                    step=0.01,
                    format="%.2f",
                    key="buy_max"
                )
            
            st.markdown("**Sell Commissions**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                form_sell_fixed = st.number_input(
                    "Fixed Fee (€)",
                    min_value=0.0,
                    value=float(editing_asset["Sell Fixed Fee"]) if editing_asset else 0.0,
                    step=0.01,
                    format="%.2f",
                    key="sell_fixed"
                )
            
            with col2:
                form_sell_pct = st.number_input(
                    "% Fee",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(editing_asset["Sell % Fee"]) if editing_asset else 0.0,
                    step=0.001,
                    format="%.3f",
                    key="sell_pct"
                )
            
            with col3:
                form_sell_min = st.number_input(
                    "Min Fee (€)",
                    min_value=0.0,
                    value=float(editing_asset["Sell Min Fee"]) if editing_asset else 0.0,
                    step=0.01,
                    format="%.2f",
                    key="sell_min"
                )
            
            with col4:
                form_sell_max = st.number_input(
                    "Max Fee (€)",
                    min_value=0.0,
                    value=float(editing_asset["Sell Max Fee"]) if editing_asset else 0.0,
                    step=0.01,
                    format="%.2f",
                    key="sell_max"
                )
        
        # Form submit buttons
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if st.session_state.editing_asset_index is not None:
                submit_button = st.form_submit_button("✅ Update Asset", type="primary", use_container_width=True)
            else:
                submit_button = st.form_submit_button("➕ Add Asset to Portfolio", type="primary", use_container_width=True)
        
        with col2:
            if st.session_state.editing_asset_index is not None:
                cancel_button = st.form_submit_button("❌ Cancel", use_container_width=True)
            else:
                cancel_button = False
        
        # Process form submission
        if submit_button:
            # Validate basic fields
            is_valid, error_msg = validate_asset_input(
                form_symbol, form_quantity, form_price, form_avg_cost,
                form_tax_rate, form_target_weight
            )
            
            if not is_valid:
                st.error(f"❌ {error_msg}")
            else:
                # Validate commission fields
                is_valid_comm, error_msg_comm = validate_commission_fields(
                    form_buy_fixed, form_buy_pct, form_buy_min, form_buy_max,
                    form_sell_fixed, form_sell_pct, form_sell_min, form_sell_max
                )
                
                if not is_valid_comm:
                    st.error(f"❌ {error_msg_comm}")
                else:
                    # Check for duplicate symbol
                    if check_duplicate_symbol(form_symbol, st.session_state.editing_asset_index):
                        st.error(f"❌ Asset '{form_symbol}' already exists in portfolio")
                    else:
                        # Create asset data dictionary
                        asset_data = {
                            "Symbol": form_symbol.strip(),
                            "Quantity": form_quantity,
                            "Price": form_price,
                            "Avg Cost": form_avg_cost,
                            "Tax Rate (%)": form_tax_rate,
                            "Target Weight (%)": form_target_weight,
                            "Buy Fixed Fee": form_buy_fixed,
                            "Buy % Fee": form_buy_pct,
                            "Buy Min Fee": form_buy_min,
                            "Buy Max Fee": form_buy_max,
                            "Sell Fixed Fee": form_sell_fixed,
                            "Sell % Fee": form_sell_pct,
                            "Sell Min Fee": form_sell_min,
                            "Sell Max Fee": form_sell_max,
                        }
                        
                        # Add or update asset
                        if st.session_state.editing_asset_index is not None:
                            update_asset_in_portfolio(st.session_state.editing_asset_index, asset_data)
                            st.success(f"✅ Asset '{form_symbol}' updated successfully!")
                            st.session_state.editing_asset_index = None
                        else:
                            add_asset_to_portfolio(asset_data)
                            st.success(f"✅ Asset '{form_symbol}' added to portfolio!")
                        
                        st.rerun()
        
        if cancel_button:
            st.session_state.editing_asset_index = None
            st.rerun()
    
    st.markdown("---")
    
    # Display current assets
    st.subheader("Current Portfolio Assets")
    
    if len(st.session_state.assets_data) == 0:
        st.info("📝 No assets in portfolio. Add your first asset using the form above.")
    else:
        # Display each asset as a card
        for i, asset in enumerate(st.session_state.assets_data):
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    # Asset header
                    current_value = asset["Quantity"] * asset["Price"]
                    st.markdown(f"### {asset['Symbol']}")
                    st.markdown(f"**Value:** {format_currency(current_value)} | "
                              f"**Target:** {asset['Target Weight (%)']}% | "
                              f"**Quantity:** {asset['Quantity']:.4f} @ {format_currency(asset['Price'])}")
                    
                    # Additional details in expander
                    with st.expander("📊 Details", expanded=False):
                        detail_col1, detail_col2, detail_col3 = st.columns(3)
                        
                        with detail_col1:
                            st.markdown("**Holdings**")
                            st.markdown(f"- Quantity: {asset['Quantity']:.4f}")
                            st.markdown(f"- Current Price: {format_currency(asset['Price'])}")
                            st.markdown(f"- Current Value: {format_currency(current_value)}")
                        
                        with detail_col2:
                            st.markdown("**Tax & Target**")
                            st.markdown(f"- Avg Cost: {format_currency(asset['Avg Cost'])}")
                            st.markdown(f"- Tax Rate: {asset['Tax Rate (%)']}%")
                            st.markdown(f"- Target Weight: {asset['Target Weight (%)']}%")
                        
                        with detail_col3:
                            st.markdown("**Commissions**")
                            has_buy_comm = (asset['Buy Fixed Fee'] > 0 or asset['Buy % Fee'] > 0 or 
                                          asset['Buy Min Fee'] > 0 or asset['Buy Max Fee'] > 0)
                            has_sell_comm = (asset['Sell Fixed Fee'] > 0 or asset['Sell % Fee'] > 0 or 
                                           asset['Sell Min Fee'] > 0 or asset['Sell Max Fee'] > 0)
                            
                            if has_buy_comm:
                                st.markdown(f"- Buy: {format_currency(asset['Buy Fixed Fee'])} + {asset['Buy % Fee']}%")
                            else:
                                st.markdown("- Buy: None")
                            
                            if has_sell_comm:
                                st.markdown(f"- Sell: {format_currency(asset['Sell Fixed Fee'])} + {asset['Sell % Fee']}%")
                            else:
                                st.markdown("- Sell: None")
                
                with col2:
                    # Action buttons
                    st.markdown("<div style='padding-top: 8px;'></div>", unsafe_allow_html=True)
                    
                    if st.button("✏️ Edit", key=f"edit_{i}", use_container_width=True):
                        st.session_state.editing_asset_index = i
                        st.rerun()
                    
                    if st.button("🗑️ Delete", key=f"delete_{i}", use_container_width=True, type="secondary"):
                        delete_asset_from_portfolio(i)
                        st.rerun()
                
                st.markdown("---")
        
        # Portfolio summary
        st.subheader("Portfolio Summary")
        
        df = assets_to_dataframe(st.session_state.assets_data)
        is_valid, error_msg = validate_assets_data(df)
        
        if is_valid:
            st.success("✅ Portfolio is valid and ready for analysis")
            
            total_value = sum(row["Quantity"] * row["Price"] for row in st.session_state.assets_data)
            total_target = df["Target Weight (%)"].sum()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Portfolio Value", format_currency(total_value))
            with col2:
                st.metric("Number of Assets", len(df))
            with col3:
                st.metric("Target Weights Sum", f"{total_target:.2f}%")
        else:
            st.error(f"❌ Portfolio Validation Error: {error_msg}")
            st.warning("Fix the issue before running analysis.")
    
    # Quick actions
    st.markdown("---")
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Reset to Example", key="reset_button", help="Reset to default 3-asset example portfolio"):
            st.session_state.assets_data = create_default_assets()
            st.session_state.editing_asset_index = None
            st.rerun()


# ============================================================================
# TAB 2: ANALYSIS
# ============================================================================

with tab2:
    st.header("Rebalancing Analysis")
    st.markdown("""
    Run the rebalancing algorithm to see what operations are needed.
    Results mirror the structure of the Excel output file.
    """)
    
    if st.button("▶️ Run Rebalancing Analysis", type="primary", use_container_width=True, key="run_analysis_button"):
        df = assets_to_dataframe(st.session_state.assets_data)
        is_valid, error_msg = validate_assets_data(df)
        
        if not is_valid:
            st.error(f"Cannot run analysis: {error_msg}")
        else:
            try:
                assets = dataframe_to_assets(df)
                portfolio = Portfolio(
                    assets=assets,
                    cash_available=st.session_state.cash_available_input,
                    name=st.session_state.portfolio_name_input,
                )
                
                rounding_policy = None
                if st.session_state.apply_rounding_checkbox:
                    policy_map = {
                        "FLOOR": RoundingPolicy.FLOOR,
                        "ROUND": RoundingPolicy.ROUND,
                        "CEIL": RoundingPolicy.CEIL,
                    }
                    rounding_policy = policy_map[st.session_state.rounding_policy_radio]
                
                engine = RebalancingEngine(rounding_policy=rounding_policy)
                
                with st.spinner("Calculating optimal rebalancing operations..."):
                    result = engine.rebalance(portfolio)
                
                st.session_state.rebalancing_result = result
                st.success("✅ Rebalancing calculation complete!")
                
            except Exception as e:
                st.error(f"Error during rebalancing: {str(e)}")
                st.session_state.rebalancing_result = None
    
    if st.session_state.rebalancing_result is not None:
        result = st.session_state.rebalancing_result
        
        st.markdown("---")
        st.subheader("📊 Current Portfolio State")
        st.markdown("Your portfolio before rebalancing:")
        
        df = assets_to_dataframe(st.session_state.assets_data)
        assets = dataframe_to_assets(df)
        portfolio = Portfolio(
            assets=assets,
            cash_available=st.session_state.cash_available_input,
            name=st.session_state.portfolio_name_input,
        )
        
        engine = RebalancingEngine()
        engine._compute_current_state(portfolio)
        
        current_df = create_current_state_dataframe(portfolio)
        st.dataframe(current_df, use_container_width=True, hide_index=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Value (Before)", format_currency(result.total_value_before))
        with col2:
            if st.session_state.cash_available_input > 0:
                st.metric("Available Cash", format_currency(st.session_state.cash_available_input))
        
        st.markdown("---")
        st.subheader("🔄 Required Operations")
        st.markdown("Buy and sell operations needed to reach target allocation:")
        
        operations_df = create_operations_dataframe(result)
        st.dataframe(operations_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("💰 Cash Flow Summary")
        st.markdown("Financial impact of the rebalancing operations:")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Cash from Sales",
                format_currency(result.total_cash_in),
                help="Total cash generated from selling assets (after tax and commissions)"
            )
        with col2:
            st.metric(
                "Cash for Purchases",
                format_currency(result.total_cash_out),
                help="Total cash needed for buying assets (including commissions)"
            )
        with col3:
            cash_flow = result.cash_flow
            st.metric(
                "Net Cash Flow",
                format_currency(cash_flow),
                delta=None,
                help="Positive = surplus, Negative = you need to add cash, ~0 = balanced"
            )
        
        if abs(cash_flow) < 1.0:
            st.success("✅ Cash flow is balanced (no external funds needed)")
        elif cash_flow < -1.0:
            st.warning(f"⚠️ You'll need to add {format_currency(abs(cash_flow))} to complete purchases")
        else:
            st.info(f"ℹ️ You'll have {format_currency(cash_flow)} left over after rebalancing")
        
        st.markdown("---")
        st.subheader("💳 Rebalancing Cost Breakdown")
        st.markdown("Total cost to execute the rebalancing operations:")
        
        total_tax = result.total_tax_paid
        commission_buy = result.total_commission_buy
        commission_sell = result.total_commission_sell
        total_commission = result.total_commission
        total_cost = total_tax + total_commission
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.metric(
                "💸 Total Cost to Rebalance",
                format_currency(total_cost),
                help="Sum of all taxes and transaction fees"
            )
        
        st.markdown("**Cost Components:**")
        
        breakdown_col1, breakdown_col2 = st.columns(2)
        
        with breakdown_col1:
            st.markdown("**Transaction Fees (Commissions)**")
            st.metric("Buy Commissions", format_currency(commission_buy))
            st.metric("Sell Commissions", format_currency(commission_sell))
            st.metric("Total Commissions", format_currency(total_commission))
        
        with breakdown_col2:
            st.markdown("**Capital Gains Tax**")
            st.metric("Total Tax Paid", format_currency(total_tax))
            
            if total_tax > 0.01:
                st.markdown("*Tax applies only to profitable sales*")
            else:
                st.markdown("*No capital gains tax (no profitable sales)*")
        
        st.info("""
        **Note on costs:**
        - **Commissions** are charged by your broker on each transaction
        - **Capital gains tax** applies only when selling assets at a profit
        - These costs are already reflected in the cash flow calculations above
        - The total cost reduces the effective return of your rebalancing
        """)
        
        st.markdown("---")
        st.subheader("🎯 Post-Rebalancing Portfolio")
        st.markdown("Your portfolio after executing the operations:")
        
        post_df = create_post_rebalancing_dataframe(result)
        st.dataframe(post_df, use_container_width=True, hide_index=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Value (After)", format_currency(result.total_value_after))
        with col2:
            st.metric("Max Weight Deviation", format_percentage(result.max_deviation))
        
        if result.max_deviation < 0.01:
            st.success("✅ Excellent: All weights within 1% of target")
        elif result.max_deviation < 0.05:
            st.info("ℹ️ Good: All weights within 5% of target")
        else:
            st.warning("⚠️ Large deviations remain (consider adjusting parameters)")
        
        st.markdown("---")
        st.info("""
        **Note:** This is a calculation tool, not financial advice. Always verify calculations 
        and consult a financial advisor if needed.
        """)
    
    else:
        st.info("👆 Click 'Run Rebalancing Analysis' above to calculate operations.")


# ============================================================================
# TAB 3: SETTINGS
# ============================================================================

with tab3:
    st.header("Algorithm Settings")
    st.markdown("""
    Configure how the rebalancing algorithm behaves.
    These settings affect the calculation in the Analysis tab.
    """)
    
    st.markdown("---")
    
    st.subheader("Share Rounding")
    st.markdown("""
    Some assets require whole shares. Enable rounding to convert fractional 
    share calculations to integers.
    """)
    
    st.checkbox(
        "Apply rounding to share quantities",
        key="apply_rounding_checkbox",
        help="Round calculated share quantities to whole numbers"
    )
    
    if st.session_state.apply_rounding_checkbox:
        st.radio(
            "Rounding method:",
            options=["FLOOR", "ROUND", "CEIL"],
            key="rounding_policy_radio",
            help="FLOOR: Round down, ROUND: Round to nearest, CEIL: Round up",
            horizontal=True,
        )
        
        if st.session_state.rounding_policy_radio == "FLOOR":
            st.info("🔽 **FLOOR**: Always rounds down. Conservative, may leave cash unallocated.")
        elif st.session_state.rounding_policy_radio == "ROUND":
            st.info("🎯 **ROUND**: Rounds to nearest integer. Balanced approach (recommended).")
        else:
            st.info("🔼 **CEIL**: Always rounds up. May require slightly more cash.")
        
        st.warning("""
        **Note:** Rounding will cause the final weights to deviate slightly from targets 
        and the cash flow may not be exactly zero. These deviations are reported in the Analysis.
        """)
    
    st.markdown("---")
    
    st.subheader("Algorithm Information")
    st.markdown("""
    This tool uses a **deterministic 8-step algorithm**:
    1. Compute current portfolio state
    2. Calculate deviations from target weights
    3. Compute target value changes
    4. Convert to share quantities
    5. Calculate cash flow (with tax and commissions)
    6. Close cash flow (proportional scaling)
    7. Simulate post-rebalancing state
    8. Apply rounding (optional)
    
    **Key Features:**
    - ✅ Deterministic (same input → same output)
    - ✅ No complex optimization (simple, transparent math)
    - ✅ Tax-aware (capital gains tax included)
    - ✅ Commission-aware (broker fees included)
    - ✅ Cash-neutral or cash-deployment capable
    
    For more details, see the documentation in the `docs/` folder.
    """)
    
    st.markdown("---")
    
    with st.expander("📋 Assumptions & Limitations"):
        st.markdown("""
        **Assumptions:**
        - Prices remain constant during execution
        - Infinite liquidity (can buy/sell any quantity)
        - All operations execute simultaneously
        - Average cost basis is known
        
        **Limitations:**
        - Single currency only
        - Linear capital gains tax
        - No tax loss harvesting
        - No lot size constraints (unless rounding is enabled)
        
        **Not Included:**
        - Market predictions or forecasts
        - Risk/return optimization
        - Asset selection or recommendations
        - Automatic order execution
        """)


# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <small>
    Portfolio Rebalancer v0.1.1 | 
    <a href='https://github.com/jacopo-monti/portfolio-rebalancer' target='_blank'>GitHub</a> | 
    Local demo - no data is stored or transmitted
    </small>
</div>
""", unsafe_allow_html=True)
