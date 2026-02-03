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
                  Can be 0 if quantity is 0 (new asset to be bought only)
        tax_rate: Capital gains tax rate as decimal (Tᵢ, e.g., 0.26 for 26%)
        target_weight: Desired portfolio weight as decimal (wᵢ, e.g., 0.60 for 60%)
        
        # Broker commissions for buy operations
        commission_buy_fixed: Fixed commission for buy operations (e.g., 2.50)
        commission_buy_percent: Percentage commission for buy operations (e.g., 0.001 for 0.1%)
        commission_buy_min: Minimum commission for percentage-based buy commission
        commission_buy_max: Maximum commission for percentage-based buy commission
        
        # Broker commissions for sell operations
        commission_sell_fixed: Fixed commission for sell operations (e.g., 2.50)
        commission_sell_percent: Percentage commission for sell operations (e.g., 0.001 for 0.1%)
        commission_sell_min: Minimum commission for percentage-based sell commission
        commission_sell_max: Maximum commission for percentage-based sell commission
        
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
    
    # Broker commission attributes - Buy
    commission_buy_fixed: float = 0.0
    commission_buy_percent: float = 0.0
    commission_buy_min: float = 0.0
    commission_buy_max: float = 0.0
    
    # Broker commission attributes - Sell
    commission_sell_fixed: float = 0.0
    commission_sell_percent: float = 0.0
    commission_sell_min: float = 0.0
    commission_sell_max: float = 0.0
    
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
        
        # Allow avg_cost=0 only if quantity=0 (new asset to be bought only)
        if self.avg_cost <= 0:
            if self.quantity > 0:
                raise ValueError(
                    f"Average cost must be positive when quantity > 0, "
                    f"got avg_cost={self.avg_cost} with quantity={self.quantity}"
                )
            # If quantity=0 and avg_cost=0, it's a new asset to be bought only (OK)
        
        if not 0 <= self.tax_rate <= 1:
            raise ValueError(f"Tax rate must be between 0 and 1, got {self.tax_rate}")
        if not 0 <= self.target_weight <= 1:
            raise ValueError(
                f"Target weight must be between 0 and 1, got {self.target_weight}"
            )
        
        # Validate commission parameters
        if self.commission_buy_fixed < 0:
            raise ValueError(f"commission_buy_fixed must be non-negative, got {self.commission_buy_fixed}")
        if self.commission_buy_percent < 0:
            raise ValueError(f"commission_buy_percent must be non-negative, got {self.commission_buy_percent}")
        if self.commission_buy_min < 0:
            raise ValueError(f"commission_buy_min must be non-negative, got {self.commission_buy_min}")
        if self.commission_buy_max < 0:
            raise ValueError(f"commission_buy_max must be non-negative, got {self.commission_buy_max}")
        
        if self.commission_sell_fixed < 0:
            raise ValueError(f"commission_sell_fixed must be non-negative, got {self.commission_sell_fixed}")
        if self.commission_sell_percent < 0:
            raise ValueError(f"commission_sell_percent must be non-negative, got {self.commission_sell_percent}")
        if self.commission_sell_min < 0:
            raise ValueError(f"commission_sell_min must be non-negative, got {self.commission_sell_min}")
        if self.commission_sell_max < 0:
            raise ValueError(f"commission_sell_max must be non-negative, got {self.commission_sell_max}")
    
    @property
    def capital_gain_per_share(self) -> float:
        """Calculate capital gain per share: Pᵢ − PMCᵢ."""
        return self.price - self.avg_cost
    
    @property
    def is_in_profit(self) -> bool:
        """Check if the asset is currently in profit."""
        return self.capital_gain_per_share > 0
    
    def _calculate_commission(
        self,
        operation_value: float,
        fixed_commission: float,
        percent_commission: float,
        min_commission: float,
        max_commission: float,
    ) -> float:
        """Calculate total commission for an operation.
        
        Commission calculation:
        1. Calculate percentage-based commission: operation_value × percent
        2. Apply min/max bounds to percentage commission (if present)
        3. Add fixed commission
        
        Total commission = bounded_percentage_commission + fixed_commission
        
        Args:
            operation_value: Value of the operation (quantity × price)
            fixed_commission: Fixed commission amount
            percent_commission: Percentage commission rate (e.g., 0.001 for 0.1%)
            min_commission: Minimum commission for percentage part
            max_commission: Maximum commission for percentage part
            
        Returns:
            Total commission for the operation
        """
        # Calculate percentage commission
        percentage_commission = operation_value * percent_commission
        
        # Apply min/max bounds to percentage commission
        if min_commission > 0:
            percentage_commission = max(percentage_commission, min_commission)
        if max_commission > 0:
            percentage_commission = min(percentage_commission, max_commission)
        
        # Total commission = bounded percentage + fixed
        total_commission = percentage_commission + fixed_commission
        
        return total_commission
    
    def compute_cash_in(self, quantity_sold: float) -> float:
        """Compute net cash from selling quantity, accounting for taxes and commissions.
        
        Formula:
            Gross proceeds: qty × P
            Capital gain per share: G = P − PMC
            Tax per share: T_share = T × max(0, G)
            Sell commission: C_sell = f(qty × P, commission params)
            Cash in: cash_in = qty × P − qty × T_share − C_sell
        
        Which simplifies to:
            cash_in = qty × (P − T × max(0, P − PMC)) − C_sell
        
        Args:
            quantity_sold: Number of shares to sell (positive value)
            
        Returns:
            Net cash received after capital gains tax and sell commission
        """
        if quantity_sold <= 0:
            return 0.0
        
        # Gross proceeds
        gross_proceeds = quantity_sold * self.price
        
        # Tax calculation
        taxable_gain_per_share = max(0, self.capital_gain_per_share)
        tax_per_share = self.tax_rate * taxable_gain_per_share
        total_tax = quantity_sold * tax_per_share
        
        # Commission calculation
        sell_commission = self._calculate_commission(
            operation_value=gross_proceeds,
            fixed_commission=self.commission_sell_fixed,
            percent_commission=self.commission_sell_percent,
            min_commission=self.commission_sell_min,
            max_commission=self.commission_sell_max,
        )
        
        # Net cash in = gross proceeds - tax - commission
        cash_in = gross_proceeds - total_tax - sell_commission
        
        return cash_in
    
    def compute_cash_out(self, quantity_bought: float) -> float:
        """Compute cash needed to buy quantity, including commissions.
        
        Formula:
            Purchase cost: qty × P
            Buy commission: C_buy = f(qty × P, commission params)
            Cash out: cash_out = qty × P + C_buy
        
        Args:
            quantity_bought: Number of shares to buy (positive value)
            
        Returns:
            Total cash needed for purchase (including commission)
        """
        if quantity_bought <= 0:
            return 0.0
        
        # Purchase cost
        purchase_cost = quantity_bought * self.price
        
        # Commission calculation
        buy_commission = self._calculate_commission(
            operation_value=purchase_cost,
            fixed_commission=self.commission_buy_fixed,
            percent_commission=self.commission_buy_percent,
            min_commission=self.commission_buy_min,
            max_commission=self.commission_buy_max,
        )
        
        # Total cash out = purchase cost + commission
        cash_out = purchase_cost + buy_commission
        
        return cash_out
