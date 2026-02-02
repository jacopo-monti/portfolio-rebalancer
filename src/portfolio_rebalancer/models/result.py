"""Result model for rebalancing operations."""

from dataclasses import dataclass, field
from typing import Dict, List

from portfolio_rebalancer.models.asset import Asset


@dataclass
class RebalancingResult:
    """Result of a portfolio rebalancing operation.
    
    Attributes:
        assets: List of assets with computed rebalancing operations
        total_value_before: Total portfolio value before rebalancing
        total_value_after: Total portfolio value after rebalancing
        cash_flow: Net cash flow (positive = surplus, negative = deficit)
        total_cash_in: Total cash from sales (after tax)
        total_cash_out: Total cash for purchases
        metadata: Additional information about the rebalancing
    """
    
    assets: List[Asset]
    total_value_before: float
    total_value_after: float
    cash_flow: float
    total_cash_in: float
    total_cash_out: float
    metadata: Dict[str, any] = field(default_factory=dict)
    
    @property
    def num_operations(self) -> int:
        """Count number of operations (buy + sell)."""
        return sum(1 for asset in self.assets if abs(asset.delta_quantity) > 1e-6)
    
    @property
    def num_buys(self) -> int:
        """Count number of buy operations."""
        return sum(1 for asset in self.assets if asset.delta_quantity > 1e-6)
    
    @property
    def num_sells(self) -> int:
        """Count number of sell operations."""
        return sum(1 for asset in self.assets if asset.delta_quantity < -1e-6)
    
    @property
    def total_tax_paid(self) -> float:
        """Calculate total capital gains tax paid."""
        total_tax = 0.0
        for asset in self.assets:
            if asset.delta_quantity < 0:  # Selling
                qty_sold = abs(asset.delta_quantity)
                taxable_gain = max(0, asset.capital_gain_per_share)
                total_tax += qty_sold * taxable_gain * asset.tax_rate
        return total_tax
    
    @property
    def max_deviation(self) -> float:
        """Get maximum absolute deviation from target after rebalancing."""
        if not self.assets:
            return 0.0
        
        # Compute post-rebalancing weights
        total_value = sum(
            (asset.quantity + asset.delta_quantity) * asset.price
            for asset in self.assets
        )
        
        max_dev = 0.0
        for asset in self.assets:
            new_value = (asset.quantity + asset.delta_quantity) * asset.price
            new_weight = new_value / total_value
            deviation = abs(new_weight - asset.target_weight)
            max_dev = max(max_dev, deviation)
        
        return max_dev
    
    def summary(self) -> str:
        """Generate a human-readable summary of the rebalancing result."""
        lines = [
            "=" * 60,
            "Ribilanciamento Portafoglio",
            "="ht 60,
            "",
            f"Valore totale: €{self.total_value_before:,.2f}",
            f"Operazioni: {self.num_buys} acquisti, {self.num_sells} vendite",
            f"Cash flow: €{self.cash_flow:,.2f}",
            f"Tasse pagate: €{self.total_tax_paid:,.2f}",
            f"Deviazione massima: {self.max_deviation * 100:.2f}%",
            "",
            "Operazioni:",
            "-" * 60,
        ]
        
        for asset in self.assets:
            if abs(asset.delta_quantity) > 1e-6:
                action = "Acquisto" if asset.delta_quantity > 0 else "Vendita"
                qty = abs(asset.delta_quantity)
                value = qty * asset.price
                lines.append(
                    f"{asset.symbol:8} {action:10} {qty:8.2f} quote "
                    f"(€{value:,.2f})"
                )
        
        lines.append("=" * 60)
        return "\n".join(lines)
