"""Asset model representing a single financial instrument."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Asset:
    """Represents a single financial instrument in the portfolio.
    
    Attributes:
        symbol: Asset identifier (e.g., ticker symbol)
        quantity: Current number of shares/units owned (Qᵢ)
        price: Current market price per share (Pᵢ)
        avg_cost: Average cost basis per share (PMCᵢ)
        tax_rate: Capital gains tax rate as decimal (Tᵢ, e.g., 0.26 for 26%)
        target_weight: Desired portfolio weight as decimal (wᵢ, e.g., 0.60 for 60%)
        
    Derived attributes (computed by engine):
        current_value: Current value in portfolio (Vᵢ = Qᵢ × Pᵢ)
        current_weight: Current portfolio weight (ŵᵢ)
        deviation: Deviation from target (Δwᵢ = ŵᵢ − wᵢ)
        delta_value: Required value change (ΔVᵢ)
        delta_quantity: Required quantity change (ΔQᵢ)
    """
    
    # Input attributes
    symbol: str
    quantity: float
    price: float
    avg_cost: float
    tax_rate: float
    target_weight: float
    
    # Derived attributes (computed by engine)
    current_value: float = field(default=0.0, init=False)
    current_weight: float = field(default=0.0, init=False)
    deviation: float = field(default=0.0, init=False)
    delta_value: float = field(default=0.0, init=False)
    delta_quantity: float = field(default=0.0, init=False)
    
    def __post_init__(self) -> None:
        """Validate asset attributes after initialization."""
        if self.quantity < 0:
            raise ValueError(f"Quantity must be non-negative, got {self.quantity}")
        if self.price <= 0:
            raise ValueError(f"Price must be positive, got {self.price}")
        if self.avg_cost <= 0:
            raise ValueError(f"Average cost must be positive, got {self.avg_cost}")
        if not 0 <= self.tax_rate <= 1:
            raise ValueError(f"Tax rate must be between 0 and 1, got {self.tax_rate}")
        if not 0 <= self.target_weight <= 1:
            raise ValueError(
                f"Target weight must be between 0 and 1, got {self.target_weight}"
            )
    
    @property
    def capital_gain_per_share(self) -> float:
        """Calculate capital gain per share: Pᵢ − PMCᵢ."""
        return self.price - self.avg_cost
    
    @property
    def is_in_profit(self) -> bool:
        """Check if the asset is currently in profit."""
        return self.capital_gain_per_share > 0
    
    def compute_cash_in(self, quantity_sold: float) -> float:
        """Compute net cash from selling quantity, accounting for taxes.
        
        Formula: 
            Capital gain per share: G = P − PMC
            Tax per share: T_share = T × max(0, G)
            Cash in: cash_in = qty × (P − T_share)
        
        Which simplifies to:
            cash_in = qty × P × (1 − T × max(0, G) / P)
            cash_in = qty × (P − T × max(0, P − PMC))
        
        Args:
            quantity_sold: Number of shares to sell (positive value)
            
        Returns:
            Net cash received after capital gains tax
        """
        if quantity_sold <= 0:
            return 0.0
        
        taxable_gain_per_share = max(0, self.capital_gain_per_share)
        tax_per_share = self.tax_rate * taxable_gain_per_share
        net_price = self.price - tax_per_share
        return quantity_sold * net_price
    
    def compute_cash_out(self, quantity_bought: float) -> float:
        """Compute cash needed to buy quantity.
        
        Formula: cash_out = qty × P
        
        Args:
            quantity_bought: Number of shares to buy (positive value)
            
        Returns:
            Cash needed for purchase
        """
        if quantity_bought <= 0:
            return 0.0
        return quantity_bought * self.price
