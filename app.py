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

# ============================================================================
# PYTHON PATH SETUP FOR HUGGING FACE SPACES
# ============================================================================
# Add src/ directory to Python path to enable imports of portfolio_rebalancer
# This is necessary for Hugging Face Spaces which doesn't support editable installs
import sys
from pathlib import Path

# Get the directory containing this script
app_dir = Path(__file__).parent
src_dir = app_dir / "src"

# Add src/ to Python path if it exists and is not already included
if src_dir.exists() and str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# ============================================================================
# IMPORTS
# ============================================================================
import streamlit as st
import pandas as pd
from typing import Optional, Tuple

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

# Import translation system
from webapp.translations import get_text, get_available_languages


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
# IMPORTANT: Initialize ALL session state variables at the top level
# BEFORE any widgets are created. This prevents settings from being reset
# during reruns triggered by portfolio modifications.

if "assets_data" not in st.session_state:
    st.session_state.assets_data = create_default_assets()

if "rebalancing_result" not in st.session_state:
    st.session_state.rebalancing_result = None

if "portfolio_name_input" not in st.session_state:
    st.session_state.portfolio_name_input = "My Portfolio"

if "cash_available_input" not in st.session_state:
    st.session_state.cash_available_input = 0.0

# Settings persistence: Initialize before any widget creation
if "apply_rounding_checkbox" not in st.session_state:
    st.session_state.apply_rounding_checkbox = False

if "rounding_policy_radio" not in st.session_state:
    st.session_state.rounding_policy_radio = "ROUND"

if "editing_asset_index" not in st.session_state:
    st.session_state.editing_asset_index = None

# Language preference: Initialize before any widget creation
if "language" not in st.session_state:
    st.session_state.language = "en"  # Default to English


# ============================================================================
# HELPER FUNCTIONS FOR ASSET MANAGEMENT
# ============================================================================

def validate_asset_input(symbol: str, quantity: float, price: float, avg_cost: float,
                        tax_rate: float, target_weight: float) -> Tuple[bool, str]:
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
        return False, get_text("error_empty_symbol")
    
    # Validate quantity
    if quantity < 0:
        return False, get_text("error_negative_quantity")
    
    # Validate price
    if price <= 0:
        return False, get_text("error_invalid_price")
    
    # Validate avg_cost
    if avg_cost < 0:
        return False, get_text("error_negative_avg_cost")
    
    # Validate tax_rate
    if tax_rate < 0 or tax_rate > 100:
        return False, get_text("error_invalid_tax_rate")
    
    # Validate target_weight
    if target_weight < 0 or target_weight > 100:
        return False, get_text("error_invalid_target_weight")
    
    return True, ""


def validate_commission_fields(buy_fixed: float, buy_pct: float, buy_min: float, buy_max: float,
                              sell_fixed: float, sell_pct: float, sell_min: float, sell_max: float) -> Tuple[bool, str]:
    """Validate commission input fields.
    
    Args:
        All commission parameters
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    fields = [
        (buy_fixed, get_text("fixed_fee_label") + " (Buy)"),
        (buy_pct, get_text("pct_fee_label") + " (Buy)"),
        (buy_min, get_text("min_fee_label") + " (Buy)"),
        (buy_max, get_text("max_fee_label") + " (Buy)"),
        (sell_fixed, get_text("fixed_fee_label") + " (Sell)"),
        (sell_pct, get_text("pct_fee_label") + " (Sell)"),
        (sell_min, get_text("min_fee_label") + " (Sell)"),
        (sell_max, get_text("max_fee_label") + " (Sell)"),
    ]
    
    for value, name in fields:
        if value < 0:
            return False, get_text("error_negative_commission").format(name)
        if "% Fee" in name or "Commissione %" in name:
            if value > 100:
                return False, get_text("error_invalid_pct_commission").format(name)
    
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


def get_portfolio_validation_status() -> Tuple[bool, str]:
    """Check current portfolio validation status.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(st.session_state.assets_data) == 0:
        return False, "Portfolio is empty. Add at least one asset."
    
    df = assets_to_dataframe(st.session_state.assets_data)
    return validate_assets_data(df)


# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.image("https://via.placeholder.com/150x50/4CAF50/FFFFFF?text=Portfolio+Tool", width=150)
    st.title(get_text("sidebar_title"))
    st.markdown("---")
    
    st.markdown(f"""
    ### {get_text("sidebar_about_title")}
    {get_text("sidebar_about_text")}
    
    ### {get_text("sidebar_how_to_title")}
    {get_text("sidebar_how_to_text")}
    
    ### {get_text("sidebar_note_title")}
    {get_text("sidebar_note_text")}
    """)


# ============================================================================
# MAIN APPLICATION
# ============================================================================

# Language selector in top-right corner
col_title, col_lang = st.columns([4, 1])
with col_title:
    st.title(f"📊 {get_text('app_title')}")
    st.markdown(get_text("app_subtitle"))
with col_lang:
    # Language selector dropdown
    languages = get_available_languages()
    current_lang_index = list(languages.keys()).index(st.session_state.language)
    selected_lang = st.selectbox(
        get_text("language_selector_label"),
        options=list(languages.keys()),
        format_func=lambda x: languages[x],
        index=current_lang_index,
        key="language_selector"
    )
    # Update language if changed
    if selected_lang != st.session_state.language:
        st.session_state.language = selected_lang
        st.rerun()

st.markdown("---")

# Create tabs for the three main sections
tab1, tab2, tab3 = st.tabs([get_text("tab_portfolio"), get_text("tab_analysis"), get_text("tab_settings")])


# ============================================================================
# TAB 1: TARGET & PORTFOLIO
# ============================================================================

with tab1:
    st.header(get_text("portfolio_config_title"))
    st.markdown(get_text("portfolio_config_description"))
    
    # Portfolio metadata
    col1, col2 = st.columns(2)
    with col1:
        st.text_input(
            get_text("portfolio_name_label"),
            key="portfolio_name_input",
            help=get_text("portfolio_name_help")
        )
    
    with col2:
        st.number_input(
            get_text("cash_available_label"),
            min_value=0.0,
            step=100.0,
            key="cash_available_input",
            help=get_text("cash_available_help")
        )
    
    st.markdown("---")
    
    # Asset creation/editing form
    st.subheader(get_text("edit_asset_title") if st.session_state.editing_asset_index is not None else get_text("add_asset_title"))
    
    # If editing, pre-populate form with existing asset data
    editing_asset = None
    if st.session_state.editing_asset_index is not None:
        editing_asset = st.session_state.assets_data[st.session_state.editing_asset_index]
    
    with st.form(key="asset_form", clear_on_submit=True):
        st.markdown(f"**{get_text('basic_info_section')}**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            form_symbol = st.text_input(
                get_text("asset_symbol_label"),
                value=editing_asset["Symbol"] if editing_asset else "",
                help=get_text("asset_symbol_help"),
                max_chars=20
            )
        
        with col2:
            form_quantity = st.number_input(
                get_text("quantity_label"),
                min_value=0.0,
                value=float(editing_asset["Quantity"]) if editing_asset else 0.0,
                step=0.1,
                format="%.4f",
                help=get_text("quantity_help")
            )
        
        with col3:
            form_price = st.number_input(
                get_text("current_price_label"),
                min_value=0.01,
                value=float(editing_asset["Price"]) if editing_asset else 100.0,
                step=0.01,
                format="%.2f",
                help=get_text("current_price_help")
            )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            form_avg_cost = st.number_input(
                get_text("avg_cost_label"),
                min_value=0.0,
                value=float(editing_asset["Avg Cost"]) if editing_asset else 100.0,
                step=0.01,
                format="%.2f",
                help=get_text("avg_cost_help")
            )
        
        with col2:
            form_tax_rate = st.number_input(
                get_text("tax_rate_label"),
                min_value=0.0,
                max_value=100.0,
                value=float(editing_asset["Tax Rate (%)"]) if editing_asset else 26.0,
                step=0.1,
                format="%.2f",
                help=get_text("tax_rate_help")
            )
        
        with col3:
            form_target_weight = st.number_input(
                get_text("target_weight_label"),
                min_value=0.0,
                max_value=100.0,
                value=float(editing_asset["Target Weight (%)"]) if editing_asset else 0.0,
                step=0.1,
                format="%.2f",
                help=get_text("target_weight_help")
            )
        
        # Commission fields in expander
        with st.expander(get_text("commission_section"), expanded=False):
            st.markdown(f"**{get_text('buy_commissions_title')}**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                form_buy_fixed = st.number_input(
                    get_text("fixed_fee_label"),
                    min_value=0.0,
                    value=float(editing_asset["Buy Fixed Fee"]) if editing_asset else 0.0,
                    step=0.01,
                    format="%.2f",
                    key="buy_fixed"
                )
            
            with col2:
                form_buy_pct = st.number_input(
                    get_text("pct_fee_label"),
                    min_value=0.0,
                    max_value=100.0,
                    value=float(editing_asset["Buy % Fee"]) if editing_asset else 0.0,
                    step=0.001,
                    format="%.3f",
                    key="buy_pct"
                )
            
            with col3:
                form_buy_min = st.number_input(
                    get_text("min_fee_label"),
                    min_value=0.0,
                    value=float(editing_asset["Buy Min Fee"]) if editing_asset else 0.0,
                    step=0.01,
                    format="%.2f",
                    key="buy_min"
                )
            
            with col4:
                form_buy_max = st.number_input(
                    get_text("max_fee_label"),
                    min_value=0.0,
                    value=float(editing_asset["Buy Max Fee"]) if editing_asset else 0.0,
                    step=0.01,
                    format="%.2f",
                    key="buy_max"
                )
            
            st.markdown(f"**{get_text('sell_commissions_title')}**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                form_sell_fixed = st.number_input(
                    get_text("fixed_fee_label"),
                    min_value=0.0,
                    value=float(editing_asset["Sell Fixed Fee"]) if editing_asset else 0.0,
                    step=0.01,
                    format="%.2f",
                    key="sell_fixed"
                )
            
            with col2:
                form_sell_pct = st.number_input(
                    get_text("pct_fee_label"),
                    min_value=0.0,
                    max_value=100.0,
                    value=float(editing_asset["Sell % Fee"]) if editing_asset else 0.0,
                    step=0.001,
                    format="%.3f",
                    key="sell_pct"
                )
            
            with col3:
                form_sell_min = st.number_input(
                    get_text("min_fee_label"),
                    min_value=0.0,
                    value=float(editing_asset["Sell Min Fee"]) if editing_asset else 0.0,
                    step=0.01,
                    format="%.2f",
                    key="sell_min"
                )
            
            with col4:
                form_sell_max = st.number_input(
                    get_text("max_fee_label"),
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
                submit_button = st.form_submit_button(get_text("update_asset_button"), type="primary", use_container_width=True)
            else:
                submit_button = st.form_submit_button(get_text("add_asset_button"), type="primary", use_container_width=True)
        
        with col2:
            if st.session_state.editing_asset_index is not None:
                cancel_button = st.form_submit_button(get_text("cancel_button"), use_container_width=True)
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
                        st.error(f"❌ {get_text('error_duplicate_symbol').format(form_symbol)}")
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
                            st.success(f"✅ {get_text('success_asset_updated').format(form_symbol)}")
                            st.session_state.editing_asset_index = None
                        else:
                            add_asset_to_portfolio(asset_data)
                            st.success(f"✅ {get_text('success_asset_added').format(form_symbol)}")
                        
                        st.rerun()
        
        if cancel_button:
            st.session_state.editing_asset_index = None
            st.rerun()
    
    st.markdown("---")
    
    # Display current assets
    st.subheader(get_text("current_portfolio_title"))
    
    if len(st.session_state.assets_data) == 0:
        st.info(get_text("no_assets_message"))
    else:
        # Display each asset as a card
        for i, asset in enumerate(st.session_state.assets_data):
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    # Asset header
                    current_value = asset["Quantity"] * asset["Price"]
                    st.markdown(f"### {asset['Symbol']}")
                    st.markdown(f"**{get_text('value_label')}:** {format_currency(current_value)} | "
                              f"**{get_text('target_label')}:** {asset['Target Weight (%)']}% | "
                              f"**{get_text('quantity_short_label')}:** {asset['Quantity']:.2f} @ {format_currency(asset['Price'])}")
                    
                    # Additional details in expander
                    with st.expander(get_text("details_expander"), expanded=False):
                        detail_col1, detail_col2, detail_col3 = st.columns(3)
                        
                        with detail_col1:
                            st.markdown(f"**{get_text('holdings_section')}**")
                            st.markdown(f"- {get_text('quantity_short_label')}: {asset['Quantity']:.2f}")
                            st.markdown(f"- {get_text('current_price_label').replace(' *', '')}: {format_currency(asset['Price'])}")
                            st.markdown(f"- {get_text('value_label')}: {format_currency(current_value)}")
                        
                        with detail_col2:
                            st.markdown(f"**{get_text('tax_target_section')}**")
                            st.markdown(f"- {get_text('avg_cost_label').replace(' *', '')}: {format_currency(asset['Avg Cost'])}")
                            st.markdown(f"- {get_text('tax_rate_label').replace(' *', '')}: {asset['Tax Rate (%)']}%")
                            st.markdown(f"- {get_text('target_weight_label').replace(' *', '')}: {asset['Target Weight (%)']}%")
                        
                        with detail_col3:
                            st.markdown(f"**{get_text('commissions_section')}**")
                            has_buy_comm = (asset['Buy Fixed Fee'] > 0 or asset['Buy % Fee'] > 0 or 
                                          asset['Buy Min Fee'] > 0 or asset['Buy Max Fee'] > 0)
                            has_sell_comm = (asset['Sell Fixed Fee'] > 0 or asset['Sell % Fee'] > 0 or 
                                           asset['Sell Min Fee'] > 0 or asset['Sell Max Fee'] > 0)
                            
                            if has_buy_comm:
                                st.markdown(f"- {get_text('buy_label')}: {format_currency(asset['Buy Fixed Fee'])} + {asset['Buy % Fee']}%")
                            else:
                                st.markdown(f"- {get_text('buy_label')}: {get_text('none_label')}")
                            
                            if has_sell_comm:
                                st.markdown(f"- {get_text('sell_label')}: {format_currency(asset['Sell Fixed Fee'])} + {asset['Sell % Fee']}%")
                            else:
                                st.markdown(f"- {get_text('sell_label')}: {get_text('none_label')}")
                
                with col2:
                    # Action buttons
                    st.markdown("<div style='padding-top: 8px;'></div>", unsafe_allow_html=True)
                    
                    if st.button(get_text("edit_button"), key=f"edit_{i}", use_container_width=True):
                        st.session_state.editing_asset_index = i
                        st.rerun()
                    
                    if st.button(get_text("delete_button"), key=f"delete_{i}", use_container_width=True, type="secondary"):
                        delete_asset_from_portfolio(i)
                        st.rerun()
                
                st.markdown("---")
        
        # Portfolio summary
        st.subheader(get_text("portfolio_summary_title"))
        
        df = assets_to_dataframe(st.session_state.assets_data)
        is_valid, error_msg = validate_assets_data(df)
        
        if is_valid:
            st.success(get_text("portfolio_valid_message"))
            
            total_value = sum(row["Quantity"] * row["Price"] for row in st.session_state.assets_data)
            total_target = df["Target Weight (%)"].sum()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(get_text("total_value_metric"), format_currency(total_value))
            with col2:
                st.metric(get_text("num_assets_metric"), len(df))
            with col3:
                st.metric(get_text("target_sum_metric"), f"{total_target:.2f}%")
        else:
            st.error(get_text("portfolio_error_message").format(error_msg))
            st.warning(get_text("fix_error_warning"))
    
    # Quick actions
    st.markdown("---")
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button(get_text("reset_button"), key="reset_button", help=get_text("reset_button_help")):
            st.session_state.assets_data = create_default_assets()
            st.session_state.editing_asset_index = None
            st.rerun()


# ============================================================================
# TAB 2: ANALYSIS
# ============================================================================

with tab2:
    st.header(get_text("analysis_title"))
    st.markdown(get_text("analysis_description"))
    
    # Check portfolio validation status before allowing analysis
    portfolio_valid, portfolio_error = get_portfolio_validation_status()
    
    if not portfolio_valid:
        st.warning(get_text("cannot_run_warning").format(portfolio_error))
        st.info(get_text("fix_portfolio_info"))
    
    if st.button(get_text("run_analysis_button"), type="primary", use_container_width=True, key="run_analysis_button", disabled=not portfolio_valid):
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
                
                with st.spinner(get_text("calculating_message")):
                    result = engine.rebalance(portfolio)
                
                st.session_state.rebalancing_result = result
                st.success(get_text("calculation_complete"))
                
            except Exception as e:
                st.error(get_text("calculation_error").format(str(e)))
                st.session_state.rebalancing_result = None
    
    if st.session_state.rebalancing_result is not None:
        # Validate portfolio before displaying results to prevent crashes
        df = assets_to_dataframe(st.session_state.assets_data)
        is_valid, error_msg = validate_assets_data(df)
        
        if not is_valid:
            # Portfolio became invalid after results were calculated
            st.error(get_text("portfolio_changed_error").format(error_msg))
            st.warning(get_text("portfolio_changed_warning"))
            st.info(get_text("results_invalid_info"))
        else:
            # Safe to display results
            try:
                result = st.session_state.rebalancing_result
                
                st.markdown("---")
                st.subheader(get_text("current_state_title"))
                st.markdown(get_text("current_state_description"))
                
                assets = dataframe_to_assets(df)
                portfolio = Portfolio(
                    assets=assets,
                    cash_available=st.session_state.cash_available_input,
                    name=st.session_state.portfolio_name_input,
                )
                
                engine = RebalancingEngine()
                engine._compute_current_state(portfolio)
                
                # Pass get_text function for translated table headers
                current_df = create_current_state_dataframe(portfolio, get_text)
                # Use consistent HTML rendering for all tables
                st.write(current_df.to_html(escape=False, index=False), unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(get_text("total_value_before_metric"), format_currency(result.total_value_before))
                with col2:
                    if st.session_state.cash_available_input > 0:
                        st.metric(get_text("available_cash_metric"), format_currency(st.session_state.cash_available_input))
                
                st.markdown("---")
                st.subheader(get_text("operations_title"))
                st.markdown(get_text("operations_description"))
                
                # Pass get_text function for translated table headers
                operations_df = create_operations_dataframe(result, get_text)
                # Use consistent HTML rendering for all tables
                st.write(operations_df.to_html(escape=False, index=False), unsafe_allow_html=True)
                
                st.markdown("---")
                st.subheader(get_text("cash_flow_title"))
                st.markdown(get_text("cash_flow_description"))
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        get_text("cash_from_sales_metric"),
                        format_currency(result.total_cash_in),
                        help=get_text("cash_from_sales_help")
                    )
                with col2:
                    st.metric(
                        get_text("cash_for_purchases_metric"),
                        format_currency(result.total_cash_out),
                        help=get_text("cash_for_purchases_help")
                    )
                with col3:
                    cash_flow = result.cash_flow
                    st.metric(
                        get_text("net_cash_flow_metric"),
                        format_currency(cash_flow),
                        delta=None,
                        help=get_text("net_cash_flow_help")
                    )
                
                if abs(cash_flow) < 1.0:
                    st.success(get_text("cash_balanced_message"))
                elif cash_flow < -1.0:
                    st.warning(get_text("cash_needed_warning").format(format_currency(abs(cash_flow))))
                else:
                    st.info(get_text("cash_leftover_info").format(format_currency(cash_flow)))
                
                st.markdown("---")
                st.subheader(get_text("cost_breakdown_title"))
                st.markdown(get_text("cost_breakdown_description"))
                
                total_tax = result.total_tax_paid
                commission_buy = result.total_commission_buy
                commission_sell = result.total_commission_sell
                total_commission = result.total_commission
                total_cost = total_tax + total_commission
                
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.metric(
                        get_text("total_cost_metric"),
                        format_currency(total_cost),
                        help=get_text("total_cost_help")
                    )
                
                st.markdown(f"**{get_text('cost_components_title')}**")
                
                breakdown_col1, breakdown_col2 = st.columns(2)
                
                with breakdown_col1:
                    st.markdown(f"**{get_text('transaction_fees_section')}**")
                    st.metric(get_text("buy_commissions_metric"), format_currency(commission_buy))
                    st.metric(get_text("sell_commissions_metric"), format_currency(commission_sell))
                    st.metric(get_text("total_commissions_metric"), format_currency(total_commission))
                
                with breakdown_col2:
                    st.markdown(f"**{get_text('capital_gains_section')}**")
                    st.metric(get_text("total_tax_metric"), format_currency(total_tax))
                    
                    if total_tax > 0.01:
                        st.markdown(get_text("tax_note_with_tax"))
                    else:
                        st.markdown(get_text("tax_note_no_tax"))
                
                st.info(get_text("cost_note"))
                
                st.markdown("---")
                st.subheader(get_text("post_rebalancing_title"))
                st.markdown(get_text("post_rebalancing_description"))
                
                # Pass get_text function for translated table headers
                post_df = create_post_rebalancing_dataframe(result, get_text)
                # Use consistent HTML rendering for all tables
                st.write(post_df.to_html(escape=False, index=False), unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(get_text("total_value_after_metric"), format_currency(result.total_value_after))
                with col2:
                    st.metric(get_text("max_deviation_metric"), format_percentage(result.max_deviation))
                
                if result.max_deviation < 0.01:
                    st.success(get_text("deviation_excellent"))
                elif result.max_deviation < 0.05:
                    st.info(get_text("deviation_good"))
                else:
                    st.warning(get_text("deviation_warning"))
                
                st.markdown("---")
                st.info(get_text("disclaimer_note"))
            
            except Exception as e:
                # Catch any unexpected errors gracefully
                st.error(get_text("display_error"))
                st.warning(get_text("verify_settings_warning"))
                # Optionally show technical details in an expander
                with st.expander(get_text("technical_details_expander")):
                    st.code(str(e))
    
    else:
        st.info(get_text("click_to_run_info"))


# ============================================================================
# TAB 3: SETTINGS
# ============================================================================

with tab3:
    st.header(get_text("settings_title"))
    st.markdown(get_text("settings_description"))
    
    st.markdown("---")
    
    st.subheader(get_text("rounding_section_title"))
    st.markdown(get_text("rounding_section_description"))
    
    # Use explicit value parameter to prevent reset during reruns
    apply_rounding = st.checkbox(
        get_text("apply_rounding_checkbox"),
        value=st.session_state.apply_rounding_checkbox,
        key="apply_rounding_checkbox",
        help=get_text("apply_rounding_help")
    )
    
    if st.session_state.apply_rounding_checkbox:
        # Use explicit value parameter to prevent reset during reruns
        st.radio(
            get_text("rounding_method_label"),
            options=["FLOOR", "ROUND", "CEIL"],
            index=["FLOOR", "ROUND", "CEIL"].index(st.session_state.rounding_policy_radio),
            key="rounding_policy_radio",
            help=get_text("rounding_method_help"),
            horizontal=True,
        )
        
        if st.session_state.rounding_policy_radio == "FLOOR":
            st.info(get_text("rounding_floor_info"))
        elif st.session_state.rounding_policy_radio == "ROUND":
            st.info(get_text("rounding_round_info"))
        else:
            st.info(get_text("rounding_ceil_info"))
        
        st.warning(get_text("rounding_warning"))
    
    st.markdown("---")
    
    st.subheader(get_text("algorithm_info_title"))
    st.markdown(get_text("algorithm_info_text"))
    
    st.markdown("---")
    
    with st.expander(get_text("assumptions_expander")):
        st.markdown(get_text("assumptions_text"))


# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <small>
    {get_text("footer_text")}
    </small>
</div>
""", unsafe_allow_html=True)
