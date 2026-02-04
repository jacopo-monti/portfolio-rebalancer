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
        total_cash_in: Total cash from sales (after tax and commission)
        total_cash_out: Total cash for purchases (including commission)
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
    def total_commission_buy(self) -> float:
        """Calculate total commissions paid on buy operations."""
        total_commission = 0.0
        for asset in self.assets:
            if asset.delta_quantity > 1e-6:  # Buying
                # Calculate what the cash out would be without commission
                purchase_cost = asset.delta_quantity * asset.price
                # Total cash out includes commission
                cash_out_with_commission = asset.compute_cash_out(asset.delta_quantity)
                # Commission is the difference
                commission = cash_out_with_commission - purchase_cost
                total_commission += commission
        return total_commission
    
    @property
    def total_commission_sell(self) -> float:
        """Calculate total commissions paid on sell operations."""
        total_commission = 0.0
        for asset in self.assets:
            if asset.delta_quantity < -1e-6:  # Selling
                qty_sold = abs(asset.delta_quantity)
                # Gross proceeds
                gross_proceeds = qty_sold * asset.price
                # Tax paid
                taxable_gain_per_share = max(0, asset.capital_gain_per_share)
                tax_paid = qty_sold * taxable_gain_per_share * asset.tax_rate
                # Actual cash in (after tax and commission)
                cash_in_after_all = asset.compute_cash_in(qty_sold)
                # Commission is: gross - tax - cash_in
                commission = gross_proceeds - tax_paid - cash_in_after_all
                total_commission += commission
        return total_commission
    
    @property
    def total_commission(self) -> float:
        """Calculate total commissions paid (buy + sell)."""
        return self.total_commission_buy + self.total_commission_sell
    
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
            "=" * 60,
            "",
            f"Valore totale: €{self.total_value_before:,.2f}",
            f"Operazioni: {self.num_buys} acquisti, {self.num_sells} vendite",
            f"Cash flow: €{self.cash_flow:,.2f}",
            f"Tasse pagate: €{self.total_tax_paid:,.2f}",
            f"Commissioni pagate: €{self.total_commission:,.2f}",
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
