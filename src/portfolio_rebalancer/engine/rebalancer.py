"""Core rebalancing engine implementing the deterministic 8-step algorithm."""

from typing import Optional

from portfolio_rebalancer.models.asset import Asset
from portfolio_rebalancer.models.portfolio import Portfolio
from portfolio_rebalancer.models.result import RebalancingResult
from portfolio_rebalancer.policies.rounding import RoundingPolicy


class RebalancingEngine:
    """Core engine for portfolio rebalancing.
    
    Implements a deterministic 8-step algorithm:
    1. Compute current state (Vᵢ, ŵᵢ, V_tot)
    2. Compute deviations from target (Δwᵢ)
    3. Compute target values (ΔVᵢ)
    4. Convert to quantities (ΔQᵢ)
    5. Compute cash flow with taxation
    6. Close cash flow (proportional scaling)
    7. Simulate post-rebalancing state
    8. Apply rounding (optional)
    
    The engine is completely deterministic: same input always produces same output.
    """
    
    def __init__(self, rounding_policy: Optional[RoundingPolicy] = None):
        """Initialize the rebalancing engine.
        
        Args:
            rounding_policy: Optional rounding policy for integer shares
        """
        self.rounding_policy = rounding_policy
    
    def rebalance(self, portfolio: Portfolio) -> RebalancingResult:
        """Execute the complete rebalancing algorithm.
        
        Args:
            portfolio: Portfolio to rebalance
            
        Returns:
            RebalancingResult containing all operations and metadata
        """
        # Step 1: Compute current state
        self._compute_current_state(portfolio)
        total_value = portfolio.total_value
        
        # Step 2: Compute deviations
        self._compute_deviations(portfolio)
        
        # Step 3: Compute target values
        self._compute_target_values(portfolio, total_value)
        
        # Step 4: Convert to quantities
        self._compute_quantity_changes(portfolio)
        
        # Step 5: Compute cash flow
        cash_in, cash_out, cash_flow = self._compute_cash_flow(portfolio)
        
        # Step 6: Close cash flow
        self._close_cash_flow(portfolio, cash_flow, cash_out)
        
        # Recompute cash flow after adjustment
        cash_in, cash_out, cash_flow = self._compute_cash_flow(portfolio)
        
        # Step 7: Simulate post-rebalancing
        total_value_after = self._simulate_post_rebalancing(portfolio)
        
        # Step 8: Apply rounding (if policy specified)
        if self.rounding_policy:
            self._apply_rounding(portfolio, self.rounding_policy)
            # Recompute cash flow after rounding
            cash_in, cash_out, cash_flow = self._compute_cash_flow(portfolio)
            total_value_after = self._simulate_post_rebalancing(portfolio)
        
        # Create result
        result = RebalancingResult(
            assets=portfolio.assets,
            total_value_before=total_value,
            total_value_after=total_value_after,
            cash_flow=cash_flow,
            total_cash_in=cash_in,
            total_cash_out=cash_out,
            metadata={
                "rounding_policy": (
                    self.rounding_policy.value if self.rounding_policy else None
                )
            },
        )
        
        return result
    
    def _compute_current_state(self, portfolio: Portfolio) -> None:
        """Step 1: Compute current value and weights.
        
        For each asset i:
            Vᵢ = Qᵢ × Pᵢ
            ŵᵢ = Vᵢ / V_tot
        """
        # Compute values
        for asset in portfolio.assets:
            asset.current_value = asset.quantity * asset.price
        
        # Compute total
        total_value = portfolio.total_value
        
        # Compute weights
        if total_value > 0:
            for asset in portfolio.assets:
                asset.current_weight = asset.current_value / total_value
        else:
            for asset in portfolio.assets:
                asset.current_weight = 0.0
    
    def _compute_deviations(self, portfolio: Portfolio) -> None:
        """Step 2: Compute deviations from target weights.
        
        For each asset i:
            Δwᵢ = ŵᵢ − wᵢ
        
        Interpretation:
            Δwᵢ > 0 → overweight (sell)
            Δwᵢ < 0 → underweight (buy)
            Δwᵢ = 0 → at target
        """
        for asset in portfolio.assets:
            asset.deviation = asset.current_weight - asset.target_weight
    
    def _compute_target_values(self, portfolio: Portfolio, total_value: float) -> None:
        """Step 3: Compute target value changes in euros.
        
        For each asset i:
            ΔVᵢ = (wᵢ × V_tot) − Vᵢ
        
        This converts percentage deviations to euro values.
        """
        for asset in portfolio.assets:
            target_value = asset.target_weight * total_value
            asset.delta_value = target_value - asset.current_value
    
    def _compute_quantity_changes(self, portfolio: Portfolio) -> None:
        """Step 4: Convert euro values to quantities.
        
        For each asset i:
            ΔQᵢ = ΔVᵢ / Pᵢ
        
        Interpretation:
            ΔQᵢ > 0 → buy ΔQᵢ shares
            ΔQᵢ < 0 → sell |ΔQᵢ| shares
        """
        for asset in portfolio.assets:
            asset.delta_quantity = asset.delta_value / asset.price
    
    def _compute_cash_flow(self, portfolio: Portfolio) -> tuple[float, float, float]:
        """Step 5: Compute cash flow with taxation.
        
        For sales (ΔQ < 0):
            cash_in = |ΔQ| × P × (1 − T × max(0, P − PMC))
        
        For purchases (ΔQ > 0):
            cash_out = ΔQ × P
        
        Cash flow:
            CF = Σ cash_in − Σ cash_out
        
        Returns:
            Tuple of (total_cash_in, total_cash_out, cash_flow)
        """
        total_cash_in = 0.0
        total_cash_out = 0.0
        
        for asset in portfolio.assets:
            if asset.delta_quantity < 0:  # Selling
                qty_sold = abs(asset.delta_quantity)
                total_cash_in += asset.compute_cash_in(qty_sold)
            
            elif asset.delta_quantity > 0:  # Buying
                total_cash_out += asset.compute_cash_out(asset.delta_quantity)
        
        cash_flow = total_cash_in - total_cash_out
        return total_cash_in, total_cash_out, cash_flow
    
    def _close_cash_flow(self, portfolio: Portfolio, cash_flow: float, total_cash_out: float) -> None:
        """Step 6: Close cash flow using proportional scaling.
        
        If CF ≠ 0, scale purchases proportionally:
            ΔQᵢ,adjusted = ΔQᵢ × (1 + CF / Σ cash_out)    for ΔQᵢ > 0
        
        This ensures CF ≈ 0 without requiring external cash injection/withdrawal.
        
        Note: We use proportional scaling (not optimization) for simplicity and
        determinism. This is a deliberate design choice.
        """
        tolerance = 0.01  # €0.01 tolerance
        
        if abs(cash_flow) < tolerance:
            return  # Already balanced
        
        if total_cash_out == 0:
            return  # No purchases to scale
        
        # Scale factor for purchases
        scale_factor = 1 + cash_flow / total_cash_out
        
        # Apply only to purchases
        for asset in portfolio.assets:
            if asset.delta_quantity > 0:
                asset.delta_quantity *= scale_factor
                asset.delta_value = asset.delta_quantity * asset.price
    
    def _simulate_post_rebalancing(self, portfolio: Portfolio) -> float:
        """Step 7: Simulate portfolio state after rebalancing.
        
        For each asset i:
            Qᵢ,new = Qᵢ + ΔQᵢ
            Vᵢ,new = Qᵢ,new × Pᵢ
            ŵᵢ,new = Vᵢ,new / V_tot,new
        
        Returns:
            Total portfolio value after rebalancing
        """
        # Compute new values
        total_value_after = 0.0
        for asset in portfolio.assets:
            new_quantity = asset.quantity + asset.delta_quantity
            new_value = new_quantity * asset.price
            total_value_after += new_value
        
        return total_value_after
    
    def _apply_rounding(self, portfolio: Portfolio, policy: RoundingPolicy) -> None:
        """Step 8: Apply rounding to quantity changes.
        
        Rounds ΔQᵢ to integer values according to policy:
        - FLOOR: round down
        - ROUND: round to nearest integer
        - CEIL: round up
        
        Note: Rounding will cause:
        - Cash flow to deviate from zero
        - Post-rebalancing weights to deviate from targets
        
        These deviations are acceptable and reported to the user.
        """
        import math
        
        for asset in portfolio.assets:
            if policy == RoundingPolicy.FLOOR:
                asset.delta_quantity = math.floor(asset.delta_quantity)
            elif policy == RoundingPolicy.ROUND:
                asset.delta_quantity = round(asset.delta_quantity)
            elif policy == RoundingPolicy.CEIL:
                asset.delta_quantity = math.ceil(asset.delta_quantity)
            
            # Update delta_value after rounding
            asset.delta_value = asset.delta_quantity * asset.price
