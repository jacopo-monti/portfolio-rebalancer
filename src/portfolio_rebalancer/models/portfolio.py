"""Portfolio model representing a collection of assets."""

from dataclasses import dataclass, field
from typing import List

from portfolio_rebalancer.models.asset import Asset


@dataclass
class Portfolio:
    """Represents a financial portfolio containing multiple assets.
    
    Attributes:
        assets: List of Asset objects in the portfolio
        cash_available: Additional cash available to invest (default: 0.0)
        name: Optional portfolio name for identification
    """
    
    assets: List[Asset]
    cash_available: float = 0.0
    name: str = field(default="Portfolio")
    
    def __post_init__(self) -> None:
        """Validate portfolio after initialization."""
        if not self.assets:
            raise ValueError("Portfolio must contain at least one asset")
        
        # Validate cash_available is non-negative
        if self.cash_available < 0:
            raise ValueError(
                f"Cash available must be non-negative, got {self.cash_available}"
            )
        
        # Validate that target weights sum to 1.0 (with tolerance)
        total_target_weight = sum(asset.target_weight for asset in self.assets)
        tolerance = 1e-6
        
        if abs(total_target_weight - 1.0) > tolerance:
            raise ValueError(
                f"Target weights must sum to 1.0, got {total_target_weight:.6f}. "
                f"Sum of target weights: {total_target_weight}"
            )
        
        # Check for duplicate symbols
        symbols = [asset.symbol for asset in self.assets]
        if len(symbols) != len(set(symbols)):
            raise ValueError("Portfolio contains duplicate asset symbols")
    
    @property
    def total_value(self) -> float:
        """Calculate total portfolio value (V_tot = Σ Vᵢ)."""
        return sum(asset.current_value for asset in self.assets)
    
    @property
    def num_assets(self) -> int:
        """Get number of assets in portfolio (N)."""
        return len(self.assets)
    
    def get_asset(self, symbol: str) -> Asset:
        """Get asset by symbol.
        
        Args:
            symbol: Asset symbol to find
            
        Returns:
            Asset object with matching symbol
            
        Raises:
            ValueError: If asset not found
        """
        for asset in self.assets:
            if asset.symbol == symbol:
                return asset
        raise ValueError(f"Asset '{symbol}' not found in portfolio")
    
    def get_assets_to_buy(self) -> List[Asset]:
        """Get list of assets that need to be purchased (ΔQ > 0)."""
        return [asset for asset in self.assets if asset.delta_quantity > 0]
    
    def get_assets_to_sell(self) -> List[Asset]:
        """Get list of assets that need to be sold (ΔQ < 0)."""
        return [asset for asset in self.assets if asset.delta_quantity < 0]
