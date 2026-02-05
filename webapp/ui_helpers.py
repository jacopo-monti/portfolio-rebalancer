"""UI helper utilities for the Streamlit web application.

This module provides utility functions for formatting, displaying data,
and converting between UI representations and core domain models.
"""

import pandas as pd
from typing import List, Dict, Any, Tuple
from portfolio_rebalancer.models import Asset, Portfolio


def create_default_assets() -> List[Dict[str, Any]]:
    """Create a default asset list for the demo.
    
    Returns:
        List of dictionaries representing default assets
    """
    return [
        {
            "Symbol": "VWCE",
            "Quantity": 50.0,
            "Price": 100.0,
            "Avg Cost": 95.0,
            "Tax Rate (%)": 26.0,
            "Target Weight (%)": 60.0,
            "Buy Fixed Fee": 0.0,
            "Buy % Fee": 0.0,
            "Buy Min Fee": 0.0,
            "Buy Max Fee": 0.0,
            "Sell Fixed Fee": 0.0,
            "Sell % Fee": 0.0,
            "Sell Min Fee": 0.0,
            "Sell Max Fee": 0.0,
        },
        {
            "Symbol": "AGGH",
            "Quantity": 30.0,
            "Price": 110.0,
            "Avg Cost": 108.0,
            "Tax Rate (%)": 26.0,
            "Target Weight (%)": 25.0,
            "Buy Fixed Fee": 0.0,
            "Buy % Fee": 0.0,
            "Buy Min Fee": 0.0,
            "Buy Max Fee": 0.0,
            "Sell Fixed Fee": 0.0,
            "Sell % Fee": 0.0,
            "Sell Min Fee": 0.0,
            "Sell Max Fee": 0.0,
        },
        {
            "Symbol": "EIMI",
            "Quantity": 20.0,
            "Price": 135.0,
            "Avg Cost": 130.0,
            "Tax Rate (%)": 26.0,
            "Target Weight (%)": 15.0,
            "Buy Fixed Fee": 0.0,
            "Buy % Fee": 0.0,
            "Buy Min Fee": 0.0,
            "Buy Max Fee": 0.0,
            "Sell Fixed Fee": 0.0,
            "Sell % Fee": 0.0,
            "Sell Min Fee": 0.0,
            "Sell Max Fee": 0.0,
        },
    ]


def assets_to_dataframe(assets_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Convert asset list to pandas DataFrame.
    
    Args:
        assets_data: List of asset dictionaries
        
    Returns:
        DataFrame with asset data
    """
    return pd.DataFrame(assets_data)


def dataframe_to_assets(df: pd.DataFrame) -> List[Asset]:
    """Convert DataFrame to Asset model objects.
    
    This function maps the UI representation (DataFrame with percentages)
    to the core domain model (Asset objects with decimal values).
    
    Args:
        df: DataFrame containing asset data
        
    Returns:
        List of Asset model objects
    """
    assets = []
    for _, row in df.iterrows():
        # Convert percentage values to decimals (divide by 100)
        asset = Asset(
            symbol=str(row["Symbol"]),
            quantity=float(row["Quantity"]),
            price=float(row["Price"]),
            avg_cost=float(row["Avg Cost"]),
            tax_rate=float(row["Tax Rate (%)"]) / 100.0,  # Convert % to decimal
            target_weight=float(row["Target Weight (%)"]) / 100.0,  # Convert % to decimal
            commission_buy_fixed=float(row["Buy Fixed Fee"]),
            commission_buy_percent=float(row["Buy % Fee"]) / 100.0,  # Convert % to decimal
            commission_buy_min=float(row["Buy Min Fee"]),
            commission_buy_max=float(row["Buy Max Fee"]),
            commission_sell_fixed=float(row["Sell Fixed Fee"]),
            commission_sell_percent=float(row["Sell % Fee"]) / 100.0,  # Convert % to decimal
            commission_sell_min=float(row["Sell Min Fee"]),
            commission_sell_max=float(row["Sell Max Fee"]),
        )
        assets.append(asset)
    return assets


def validate_assets_data(df: pd.DataFrame) -> Tuple[bool, str]:
    """Validate asset data from DataFrame.
    
    Args:
        df: DataFrame containing asset data
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if DataFrame is empty
    if df.empty:
        return False, "Portfolio must contain at least one asset"
    
    # Check for required columns
    required_columns = [
        "Symbol", "Quantity", "Price", "Avg Cost", 
        "Tax Rate (%)", "Target Weight (%)"
    ]
    for col in required_columns:
        if col not in df.columns:
            return False, f"Missing required column: {col}"
    
    # Check for duplicate symbols
    if df["Symbol"].duplicated().any():
        return False, "Duplicate asset symbols found"
    
    # Check that target weights sum to 100%
    total_target = df["Target Weight (%)"].sum()
    if abs(total_target - 100.0) > 0.01:
        return False, f"Target weights must sum to 100%, current sum: {total_target:.2f}%"
    
    # Check for positive prices
    if (df["Price"] <= 0).any():
        return False, "All prices must be positive"
    
    # Check for non-negative quantities
    if (df["Quantity"] < 0).any():
        return False, "Quantities must be non-negative"
    
    # Check for valid tax rates
    if (df["Tax Rate (%)"] < 0).any() or (df["Tax Rate (%)"] > 100).any():
        return False, "Tax rates must be between 0% and 100%"
    
    # Check for valid target weights
    if (df["Target Weight (%)"] < 0).any() or (df["Target Weight (%)"] > 100).any():
        return False, "Target weights must be between 0% and 100%"
    
    return True, ""


def format_currency(value: float) -> str:
    """Format a value as currency (euros).
    
    Args:
        value: Numeric value to format
        
    Returns:
        Formatted currency string
    """
    return f"€{value:,.2f}"


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """Format a decimal value as percentage.
    
    Args:
        value: Decimal value (e.g., 0.26 for 26%)
        decimal_places: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimal_places}f}%"


def create_current_state_dataframe(portfolio: Portfolio) -> pd.DataFrame:
    """Create a DataFrame showing current portfolio state.
    
    Args:
        portfolio: Portfolio object with computed current state
        
    Returns:
        DataFrame with current state information
    """
    data = []
    for asset in portfolio.assets:
        data.append({
            "Symbol": asset.symbol,
            "Quantity": f"{asset.quantity:.4f}",
            "Price": format_currency(asset.price),
            "Value": format_currency(asset.current_value),
            "Current Weight": format_percentage(asset.current_weight),
            "Target Weight": format_percentage(asset.target_weight),
            "Deviation": format_percentage(asset.deviation),
        })
    return pd.DataFrame(data)


def create_operations_dataframe(result) -> pd.DataFrame:
    """Create a DataFrame showing required rebalancing operations.
    
    Args:
        result: RebalancingResult object
        
    Returns:
        DataFrame with operations information
    """
    data = []
    for asset in result.assets:
        if abs(asset.delta_quantity) < 0.0001:
            action = "HOLD"
            quantity = "-"
            value = "-"
        else:
            action = "BUY" if asset.delta_quantity > 0 else "SELL"
            quantity = f"{abs(asset.delta_quantity):.4f}"
            value = format_currency(abs(asset.delta_value))
        
        # Calculate tax and net proceeds for sales
        tax_info = ""
        if asset.delta_quantity < 0 and asset.price > asset.avg_cost:
            qty_sold = abs(asset.delta_quantity)
            capital_gain = (asset.price - asset.avg_cost) * qty_sold
            tax_amount = capital_gain * asset.tax_rate
            tax_info = format_currency(tax_amount)
        
        data.append({
            "Symbol": asset.symbol,
            "Action": action,
            "Quantity": quantity,
            "Value": value,
            "Tax (if selling)": tax_info if tax_info else "-",
        })
    return pd.DataFrame(data)


def create_post_rebalancing_dataframe(result) -> pd.DataFrame:
    """Create a DataFrame showing post-rebalancing portfolio state.
    
    Args:
        result: RebalancingResult object
        
    Returns:
        DataFrame with post-rebalancing state
    """
    data = []
    for asset in result.assets:
        new_quantity = asset.quantity + asset.delta_quantity
        new_value = new_quantity * asset.price
        new_weight = new_value / result.total_value_after
        deviation = new_weight - asset.target_weight
        
        data.append({
            "Symbol": asset.symbol,
            "New Quantity": f"{new_quantity:.4f}",
            "New Value": format_currency(new_value),
            "New Weight": format_percentage(new_weight),
            "Target Weight": format_percentage(asset.target_weight),
            "Deviation": format_percentage(deviation),
        })
    return pd.DataFrame(data)
