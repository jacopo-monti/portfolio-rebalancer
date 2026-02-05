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
# Streamlit's session state allows us to persist data between reruns
# This is our "in-memory database" for the demo
#
# CRITICAL: Each state variable is initialized ONCE using a guard condition.
# This prevents re-initialization on every rerun, which was the root cause
# of the state rollback bug.

if "assets_data" not in st.session_state:
    # Initialize with default example portfolio
    st.session_state.assets_data = create_default_assets()

if "rebalancing_result" not in st.session_state:
    # Store the result of the last rebalancing calculation
    st.session_state.rebalancing_result = None

if "portfolio_name" not in st.session_state:
    st.session_state.portfolio_name = "My Portfolio"

if "cash_available" not in st.session_state:
    st.session_state.cash_available = 0.0

if "apply_rounding" not in st.session_state:
    st.session_state.apply_rounding = False

if "rounding_policy" not in st.session_state:
    st.session_state.rounding_policy = "ROUND"


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
    1. **Target & Portfolio**: Enter your assets and targets
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
# This tab replicates the Excel input file structure

with tab1:
    st.header("Portfolio Configuration")
    st.markdown("""
    Define your portfolio composition, current holdings, and target allocation.
    This mirrors the structure of the Excel input file.
    """)
    
    # Portfolio metadata
    col1, col2 = st.columns(2)
    with col1:
        # FIX: Widget with unique key stores its value directly in session_state['portfolio_name_input']
        # We no longer read from and write to the same session_state variable, breaking the circular dependency
        st.text_input(
            "Portfolio Name",
            value=st.session_state.portfolio_name,
            key="portfolio_name_input",
            help="Give your portfolio a name for identification"
        )
        # Update the canonical session_state variable from the widget's state
        # This happens AFTER the widget renders, so user input is preserved
        st.session_state.portfolio_name = st.session_state.portfolio_name_input
    
    with col2:
        # FIX: Increment/decrement buttons were causing double-click behavior because:
        # 1. Widget reads from session_state.cash_available
        # 2. Widget updates its internal state
        # 3. We immediately overwrote session_state.cash_available with the OLD value
        # 4. Next rerun used the OLD value, causing rollback
        #
        # SOLUTION: Let Streamlit manage the widget state through the key parameter.
        # The widget automatically stores its value in session_state['cash_available_input'].
        # We sync this to our canonical variable AFTER rendering.
        st.number_input(
            "Available Cash to Deploy (€)",
            min_value=0.0,
            value=st.session_state.cash_available,
            step=100.0,
            key="cash_available_input",
            help="Additional cash you want to invest. Set to 0 for cash-neutral rebalancing."
        )
        # Sync from widget state to canonical state AFTER rendering
        st.session_state.cash_available = st.session_state.cash_available_input
    
    st.markdown("---")
    
    # Asset table section
    st.subheader("Asset Table")
    st.markdown("""
    Enter your assets below. You can edit cells directly in the table.
    - **Symbol**: Asset ticker/identifier
    - **Quantity**: Current shares owned
    - **Price**: Current market price per share
    - **Avg Cost**: Your average purchase price (for tax calculation)
    - **Tax Rate (%)**: Capital gains tax rate
    - **Target Weight (%)**: Desired portfolio allocation (must sum to 100%)
    - **Commission fields**: Broker fees for buying/selling
    """)
    
    # FIX: The data_editor bug was caused by this sequence:
    # 1. Read st.session_state.assets_data and create DataFrame
    # 2. Pass DataFrame to data_editor
    # 3. User edits cell
    # 4. Streamlit reruns
    # 5. We read st.session_state.assets_data AGAIN (still has old value)
    # 6. Initialize data_editor with old value
    # 7. User edit is lost
    #
    # SOLUTION: The data_editor return value contains the user's edits.
    # We must save this IMMEDIATELY to session_state, and on the next rerun,
    # the data_editor will be initialized with the UPDATED data.
    
    # Convert current session state to DataFrame for editing
    df = assets_to_dataframe(st.session_state.assets_data)
    
    # Render the data editor with a stable key
    # The key ensures this specific widget instance is tracked across reruns
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",  # Allow adding/removing rows
        use_container_width=True,
        key="assets_table_editor",
        column_config={
            "Symbol": st.column_config.TextColumn("Symbol", required=True, max_chars=10),
            "Quantity": st.column_config.NumberColumn("Quantity", min_value=0.0, format="%.4f"),
            "Price": st.column_config.NumberColumn("Price (€)", min_value=0.01, format="%.2f"),
            "Avg Cost": st.column_config.NumberColumn("Avg Cost (€)", min_value=0.0, format="%.2f"),
            "Tax Rate (%)": st.column_config.NumberColumn("Tax Rate (%)", min_value=0.0, max_value=100.0, format="%.2f"),
            "Target Weight (%)": st.column_config.NumberColumn("Target Weight (%)", min_value=0.0, max_value=100.0, format="%.2f"),
            "Buy Fixed Fee": st.column_config.NumberColumn("Buy Fixed Fee (€)", min_value=0.0, format="%.2f"),
            "Buy % Fee": st.column_config.NumberColumn("Buy % Fee", min_value=0.0, max_value=100.0, format="%.3f"),
            "Buy Min Fee": st.column_config.NumberColumn("Buy Min Fee (€)", min_value=0.0, format="%.2f"),
            "Buy Max Fee": st.column_config.NumberColumn("Buy Max Fee (€)", min_value=0.0, format="%.2f"),
            "Sell Fixed Fee": st.column_config.NumberColumn("Sell Fixed Fee (€)", min_value=0.0, format="%.2f"),
            "Sell % Fee": st.column_config.NumberColumn("Sell % Fee", min_value=0.0, max_value=100.0, format="%.3f"),
            "Sell Min Fee": st.column_config.NumberColumn("Sell Min Fee (€)", min_value=0.0, format="%.2f"),
            "Sell Max Fee": st.column_config.NumberColumn("Sell Max Fee (€)", min_value=0.0, format="%.2f"),
        },
        hide_index=True,
    )
    
    # CRITICAL FIX: Save the edited dataframe to session state IMMEDIATELY
    # This ensures that on the next rerun (triggered by the edit), the data_editor
    # will be initialized with the UPDATED data, not the stale data.
    # This is the single source of truth for asset data.
    st.session_state.assets_data = edited_df.to_dict('records')
    
    # Validation feedback
    st.markdown("---")
    is_valid, error_msg = validate_assets_data(edited_df)
    
    if is_valid:
        # Calculate and display portfolio summary
        st.success("✅ Portfolio data is valid")
        
        total_value = sum(row["Quantity"] * row["Price"] for row in st.session_state.assets_data)
        total_target = edited_df["Target Weight (%)"].sum()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Portfolio Value", format_currency(total_value))
        with col2:
            st.metric("Number of Assets", len(edited_df))
        with col3:
            st.metric("Target Weights Sum", f"{total_target:.2f}%")
    else:
        st.error(f"❌ Validation Error: {error_msg}")
        st.warning("Please fix the errors above before running analysis.")
    
    # Quick actions
    st.markdown("---")
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Reset to Example", key="reset_button", help="Reset to default 3-asset example portfolio"):
            st.session_state.assets_data = create_default_assets()
            # Explicit rerun is necessary here because we're resetting data
            # that needs to be reflected in the data_editor on the next render
            st.rerun()


# ============================================================================
# TAB 2: ANALYSIS
# ============================================================================
# This tab replicates the Excel output file structure

with tab2:
    st.header("Rebalancing Analysis")
    st.markdown("""
    Run the rebalancing algorithm to see what operations are needed.
    Results mirror the structure of the Excel output file.
    """)
    
    # Button to trigger calculation
    if st.button("▶️ Run Rebalancing Analysis", type="primary", use_container_width=True, key="run_analysis_button"):
        # Validate data before running
        df = assets_to_dataframe(st.session_state.assets_data)
        is_valid, error_msg = validate_assets_data(df)
        
        if not is_valid:
            st.error(f"Cannot run analysis: {error_msg}")
        else:
            try:
                # Convert UI data to domain models
                # This is where we map from the UI representation (DataFrame)
                # to the core domain models (Asset, Portfolio)
                assets = dataframe_to_assets(df)
                portfolio = Portfolio(
                    assets=assets,
                    cash_available=st.session_state.cash_available,
                    name=st.session_state.portfolio_name,
                )
                
                # Create the rebalancing engine with optional rounding policy
                rounding_policy = None
                if st.session_state.apply_rounding:
                    policy_map = {
                        "FLOOR": RoundingPolicy.FLOOR,
                        "ROUND": RoundingPolicy.ROUND,
                        "CEIL": RoundingPolicy.CEIL,
                    }
                    rounding_policy = policy_map[st.session_state.rounding_policy]
                
                engine = RebalancingEngine(rounding_policy=rounding_policy)
                
                # Execute the core rebalancing logic
                # This is the single source of truth - the UI is just a wrapper
                with st.spinner("Calculating optimal rebalancing operations..."):
                    result = engine.rebalance(portfolio)
                
                # Store result in session state
                st.session_state.rebalancing_result = result
                st.success("✅ Rebalancing calculation complete!")
                
            except Exception as e:
                st.error(f"Error during rebalancing: {str(e)}")
                st.session_state.rebalancing_result = None
    
    # Display results if available
    if st.session_state.rebalancing_result is not None:
        result = st.session_state.rebalancing_result
        
        st.markdown("---")
        
        # Section 1: Current Portfolio State
        st.subheader("📊 Current Portfolio State")
        st.markdown("Your portfolio before rebalancing:")
        
        # Reconstruct portfolio for display
        df = assets_to_dataframe(st.session_state.assets_data)
        assets = dataframe_to_assets(df)
        portfolio = Portfolio(
            assets=assets,
            cash_available=st.session_state.cash_available,
            name=st.session_state.portfolio_name,
        )
        
        # Compute current state (mimics Step 1 of the algorithm)
        engine = RebalancingEngine()
        engine._compute_current_state(portfolio)
        
        current_df = create_current_state_dataframe(portfolio)
        st.dataframe(current_df, use_container_width=True, hide_index=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Value (Before)", format_currency(result.total_value_before))
        with col2:
            if st.session_state.cash_available > 0:
                st.metric("Available Cash", format_currency(st.session_state.cash_available))
        
        st.markdown("---")
        
        # Section 2: Required Operations
        st.subheader("🔄 Required Operations")
        st.markdown("Buy and sell operations needed to reach target allocation:")
        
        operations_df = create_operations_dataframe(result)
        st.dataframe(operations_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Section 3: Cash Flow Summary
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
            delta_color = "normal" if abs(cash_flow) < 1.0 else ("inverse" if cash_flow < 0 else "off")
            st.metric(
                "Net Cash Flow",
                format_currency(cash_flow),
                delta=None,
                help="Positive = surplus, Negative = you need to add cash, ~0 = balanced"
            )
        
        # Cash flow interpretation
        if abs(cash_flow) < 1.0:
            st.success("✅ Cash flow is balanced (no external funds needed)")
        elif cash_flow < -1.0:
            st.warning(f"⚠️ You'll need to add {format_currency(abs(cash_flow))} to complete purchases")
        else:
            st.info(f"ℹ️ You'll have {format_currency(cash_flow)} left over after rebalancing")
        
        st.markdown("---")
        
        # NEW SECTION: Rebalancing Cost Breakdown
        st.subheader("💳 Rebalancing Cost Breakdown")
        st.markdown("Total cost to execute the rebalancing operations:")
        
        # Calculate total cost components
        # These calculations reuse existing logic from RebalancingResult properties
        # Total tax paid on capital gains (only on profitable sales)
        total_tax = result.total_tax_paid
        
        # Total commissions split by operation type
        # Uses the commission calculation logic already present in RebalancingResult
        commission_buy = result.total_commission_buy
        commission_sell = result.total_commission_sell
        total_commission = result.total_commission
        
        # Total rebalancing cost is the sum of taxes and commissions
        # This represents the actual cost to execute the rebalancing
        total_cost = total_tax + total_commission
        
        # Display as prominent metric
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.metric(
                "💸 Total Cost to Rebalance",
                format_currency(total_cost),
                help="Sum of all taxes and transaction fees"
            )
        
        # Display detailed breakdown
        st.markdown("**Cost Components:**")
        
        breakdown_col1, breakdown_col2 = st.columns(2)
        
        with breakdown_col1:
            st.markdown("**Transaction Fees (Commissions)**")
            st.metric(
                "Buy Commissions",
                format_currency(commission_buy),
                help="Broker fees on purchase operations"
            )
            st.metric(
                "Sell Commissions",
                format_currency(commission_sell),
                help="Broker fees on sell operations"
            )
            st.metric(
                "Total Commissions",
                format_currency(total_commission),
                help="Sum of buy and sell commissions"
            )
        
        with breakdown_col2:
            st.markdown("**Capital Gains Tax**")
            st.metric(
                "Total Tax Paid",
                format_currency(total_tax),
                help="Tax on realized capital gains from selling at profit"
            )
            
            # Show tax breakdown by asset if any taxes are paid
            if total_tax > 0.01:
                st.markdown("*Tax applies only to profitable sales*")
            else:
                st.markdown("*No capital gains tax (no profitable sales)*")
        
        # Add explanatory note
        st.info("""
        **Note on costs:**
        - **Commissions** are charged by your broker on each transaction
        - **Capital gains tax** applies only when selling assets at a profit
        - These costs are already reflected in the cash flow calculations above
        - The total cost reduces the effective return of your rebalancing
        """)
        
        st.markdown("---")
        
        # Section 4: Post-Rebalancing Portfolio
        st.subheader("🎯 Post-Rebalancing Portfolio")
        st.markdown("Your portfolio after executing the operations:")
        
        post_df = create_post_rebalancing_dataframe(result)
        st.dataframe(post_df, use_container_width=True, hide_index=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Value (After)", format_currency(result.total_value_after))
        with col2:
            st.metric("Max Weight Deviation", format_percentage(result.max_deviation))
        
        # Accuracy assessment
        if result.max_deviation < 0.01:
            st.success("✅ Excellent: All weights within 1% of target")
        elif result.max_deviation < 0.05:
            st.info("ℹ️ Good: All weights within 5% of target")
        else:
            st.warning("⚠️ Large deviations remain (consider adjusting parameters)")
        
        st.markdown("---")
        
        # Disclaimer
        st.info("""
        **Note:** This is a calculation tool, not financial advice. Always verify calculations 
        and consult a financial advisor if needed.
        """)
    
    else:
        st.info("👆 Click 'Run Rebalancing Analysis' above to calculate operations.")


# ============================================================================
# TAB 3: SETTINGS
# ============================================================================
# Configuration for algorithm behavior

with tab3:
    st.header("Algorithm Settings")
    st.markdown("""
    Configure how the rebalancing algorithm behaves.
    These settings affect the calculation in the Analysis tab.
    """)
    
    st.markdown("---")
    
    # Rounding policy section
    st.subheader("Share Rounding")
    st.markdown("""
    Some assets require whole shares. Enable rounding to convert fractional 
    share calculations to integers.
    """)
    
    # FIX: Widget with unique key manages its own state
    # We read from the widget's state after rendering
    st.checkbox(
        "Apply rounding to share quantities",
        value=st.session_state.apply_rounding,
        key="apply_rounding_checkbox",
        help="Round calculated share quantities to whole numbers"
    )
    st.session_state.apply_rounding = st.session_state.apply_rounding_checkbox
    
    if st.session_state.apply_rounding:
        st.radio(
            "Rounding method:",
            options=["FLOOR", "ROUND", "CEIL"],
            index=["FLOOR", "ROUND", "CEIL"].index(st.session_state.rounding_policy),
            key="rounding_policy_radio",
            help="FLOOR: Round down, ROUND: Round to nearest, CEIL: Round up",
            horizontal=True,
        )
        st.session_state.rounding_policy = st.session_state.rounding_policy_radio
        
        # Explain the implications
        if st.session_state.rounding_policy == "FLOOR":
            st.info("🔽 **FLOOR**: Always rounds down. Conservative, may leave cash unallocated.")
        elif st.session_state.rounding_policy == "ROUND":
            st.info("🎯 **ROUND**: Rounds to nearest integer. Balanced approach (recommended).")
        else:
            st.info("🔼 **CEIL**: Always rounds up. May require slightly more cash.")
        
        st.warning("""
        **Note:** Rounding will cause the final weights to deviate slightly from targets 
        and the cash flow may not be exactly zero. These deviations are reported in the Analysis.
        """)
    
    st.markdown("---")
    
    # Algorithm information
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
    
    # Limitations and assumptions
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
