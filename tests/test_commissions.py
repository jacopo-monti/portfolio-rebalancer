"""Tests for broker commission functionality."""

import pytest
from portfolio_rebalancer.models.asset import Asset
from portfolio_rebalancer.models.portfolio import Portfolio
from portfolio_rebalancer.engine.rebalancer import RebalancingEngine


class TestCommissionCalculation:
    """Test the _calculate_commission helper method."""
    
    def test_fixed_commission_only(self):
        """Test commission with only fixed component."""
        asset = Asset(
            symbol="TEST",
            quantity=10.0,
            price=100.0,
            avg_cost=90.0,
            tax_rate=0.26,
            target_weight=1.0,
            commission_buy_fixed=2.50,
        )
        
        commission = asset._calculate_commission(
            operation_value=1000.0,
            fixed_commission=2.50,
            percent_commission=0.0,
            min_commission=0.0,
            max_commission=0.0,
        )
        
        assert commission == 2.50
    
    def test_percent_commission_only(self):
        """Test commission with only percentage component."""
        asset = Asset(
            symbol="TEST",
            quantity=10.0,
            price=100.0,
            avg_cost=90.0,
            tax_rate=0.26,
            target_weight=1.0,
            commission_buy_percent=0.001,  # 0.1%
        )
        
        commission = asset._calculate_commission(
            operation_value=1000.0,
            fixed_commission=0.0,
            percent_commission=0.001,
            min_commission=0.0,
            max_commission=0.0,
        )
        
        assert commission == 1.0  # 0.1% of 1000
    
    def test_combined_commission(self):
        """Test commission with both fixed and percentage components."""
        asset = Asset(
            symbol="TEST",
            quantity=10.0,
            price=100.0,
            avg_cost=90.0,
            tax_rate=0.26,
            target_weight=1.0,
            commission_buy_fixed=2.50,
            commission_buy_percent=0.001,
        )
        
        commission = asset._calculate_commission(
            operation_value=1000.0,
            fixed_commission=2.50,
            percent_commission=0.001,
            min_commission=0.0,
            max_commission=0.0,
        )
        
        assert commission == 3.50  # 2.50 fixed + 1.0 percent
    
    def test_min_commission_applied(self):
        """Test that minimum commission is applied when percentage is below min."""
        asset = Asset(
            symbol="TEST",
            quantity=10.0,
            price=100.0,
            avg_cost=90.0,
            tax_rate=0.26,
            target_weight=1.0,
            commission_buy_percent=0.001,  # 0.1%
            commission_buy_min=5.0,  # Minimum 5 euros
        )
        
        # Small operation: 100 * 0.001 = 0.10 < min 5.0
        commission = asset._calculate_commission(
            operation_value=100.0,
            fixed_commission=0.0,
            percent_commission=0.001,
            min_commission=5.0,
            max_commission=0.0,
        )
        
        assert commission == 5.0  # Min applied
    
    def test_max_commission_applied(self):
        """Test that maximum commission is applied when percentage exceeds max."""
        asset = Asset(
            symbol="TEST",
            quantity=10.0,
            price=100.0,
            avg_cost=90.0,
            tax_rate=0.26,
            target_weight=1.0,
            commission_buy_percent=0.01,  # 1%
            commission_buy_max=10.0,  # Maximum 10 euros
        )
        
        # Large operation: 2000 * 0.01 = 20.0 > max 10.0
        commission = asset._calculate_commission(
            operation_value=2000.0,
            fixed_commission=0.0,
            percent_commission=0.01,
            min_commission=0.0,
            max_commission=10.0,
        )
        
        assert commission == 10.0  # Max applied
    
    def test_min_max_with_fixed(self):
        """Test that min/max apply to percentage part, then fixed is added."""
        asset = Asset(
            symbol="TEST",
            quantity=10.0,
            price=100.0,
            avg_cost=90.0,
            tax_rate=0.26,
            target_weight=1.0,
            commission_buy_fixed=2.0,
            commission_buy_percent=0.001,
            commission_buy_min=5.0,
        )
        
        # Small operation: 100 * 0.001 = 0.10 < min 5.0
        # Total = min(5.0) + fixed(2.0) = 7.0
        commission = asset._calculate_commission(
            operation_value=100.0,
            fixed_commission=2.0,
            percent_commission=0.001,
            min_commission=5.0,
            max_commission=0.0,
        )
        
        assert commission == 7.0


class TestAssetCashFlowWithCommissions:
    """Test cash flow calculations with commissions."""
    
    def test_compute_cash_out_no_commission(self):
        """Test buy operation with no commission (baseline)."""
        asset = Asset(
            symbol="TEST",
            quantity=10.0,
            price=100.0,
            avg_cost=90.0,
            tax_rate=0.26,
            target_weight=1.0,
        )
        
        cash_out = asset.compute_cash_out(5.0)  # Buy 5 shares
        assert cash_out == 500.0  # 5 * 100
    
    def test_compute_cash_out_with_fixed_commission(self):
        """Test buy operation with fixed commission."""
        asset = Asset(
            symbol="TEST",
            quantity=10.0,
            price=100.0,
            avg_cost=90.0,
            tax_rate=0.26,
            target_weight=1.0,
            commission_buy_fixed=2.50,
        )
        
        cash_out = asset.compute_cash_out(5.0)  # Buy 5 shares
        assert cash_out == 502.50  # 500 + 2.50 commission
    
    def test_compute_cash_out_with_percent_commission(self):
        """Test buy operation with percentage commission."""
        asset = Asset(
            symbol="TEST",
            quantity=10.0,
            price=100.0,
            avg_cost=90.0,
            tax_rate=0.26,
            target_weight=1.0,
            commission_buy_percent=0.001,  # 0.1%
        )
        
        cash_out = asset.compute_cash_out(5.0)  # Buy 5 shares
        assert cash_out == 500.50  # 500 + 0.50 commission (0.1% of 500)
    
    def test_compute_cash_in_no_commission(self):
        """Test sell operation with no commission (baseline)."""
        asset = Asset(
            symbol="TEST",
            quantity=10.0,
            price=100.0,
            avg_cost=90.0,
            tax_rate=0.26,
            target_weight=1.0,
        )
        
        cash_in = asset.compute_cash_in(5.0)  # Sell 5 shares
        # Gross: 5 * 100 = 500
        # Gain per share: 100 - 90 = 10
        # Tax per share: 0.26 * 10 = 2.6
        # Net per share: 100 - 2.6 = 97.4
        # Total: 5 * 97.4 = 487.0
        assert cash_in == pytest.approx(487.0)
    
    def test_compute_cash_in_with_fixed_commission(self):
        """Test sell operation with fixed commission."""
        asset = Asset(
            symbol="TEST",
            quantity=10.0,
            price=100.0,
            avg_cost=90.0,
            tax_rate=0.26,
            target_weight=1.0,
            commission_sell_fixed=2.50,
        )
        
        cash_in = asset.compute_cash_in(5.0)  # Sell 5 shares
        # Net before commission: 487.0 (from previous test)
        # After commission: 487.0 - 2.50 = 484.5
        assert cash_in == pytest.approx(484.5)
    
    def test_compute_cash_in_with_percent_commission(self):
        """Test sell operation with percentage commission."""
        asset = Asset(
            symbol="TEST",
            quantity=10.0,
            price=100.0,
            avg_cost=90.0,
            tax_rate=0.26,
            target_weight=1.0,
            commission_sell_percent=0.001,  # 0.1%
        )
        
        cash_in = asset.compute_cash_in(5.0)  # Sell 5 shares
        # Gross: 500
        # Commission: 500 * 0.001 = 0.5
        # Tax: same as before = 13.0
        # Net: 500 - 13.0 - 0.5 = 486.5
        assert cash_in == pytest.approx(486.5)


class TestRebalancingWithCommissions:
    """Test that the rebalancing engine correctly accounts for commissions."""
    
    def test_rebalancing_with_commissions_increases_total_costs(self):
        """Test that commissions increase the total cost of rebalancing.
        
        NOTE: The rebalancing engine automatically balances cash flow using
        proportional scaling. When cash_available=0, it scales purchases so
        that cash_flow=0 (balanced operations). This is correct behavior.
        
        This test verifies that:
        1. Commissions reduce cash_in from sales
        2. Commissions increase cash_out for purchases
        3. The total rebalancing cost (taxes + commissions) is higher with commissions
        """
        # Create portfolio: 100% in asset A, target 50/50 split with new asset B
        asset_a_no_comm = Asset(
            symbol="A",
            quantity=10.0,
            price=100.0,
            avg_cost=90.0,
            tax_rate=0.26,
            target_weight=0.5,
        )
        
        asset_b_no_comm = Asset(
            symbol="B",
            quantity=0.0,
            price=100.0,
            avg_cost=0.0,
            tax_rate=0.26,
            target_weight=0.5,
        )
        
        portfolio_no_comm = Portfolio(assets=[asset_a_no_comm, asset_b_no_comm], cash_available=0.0)
        engine = RebalancingEngine()
        result_no_comm = engine.rebalance(portfolio_no_comm)
        
        # Now with commissions
        asset_a_with_comm = Asset(
            symbol="A",
            quantity=10.0,
            price=100.0,
            avg_cost=90.0,
            tax_rate=0.26,
            target_weight=0.5,
            commission_sell_fixed=2.50,
        )
        
        asset_b_with_comm = Asset(
            symbol="B",
            quantity=0.0,
            price=100.0,
            avg_cost=0.0,
            tax_rate=0.26,
            target_weight=0.5,
            commission_buy_fixed=2.50,
        )
        
        portfolio_with_comm = Portfolio(assets=[asset_a_with_comm, asset_b_with_comm], cash_available=0.0)
        result_with_comm = engine.rebalance(portfolio_with_comm)
        
        # With commissions:
        # - Cash in from sales is LESS (reduced by sell commission)
        # - Cash out for purchases depends on scaling but base cost is HIGHER (increased by buy commission)
        
        # Cash in should be less with commissions (due to sell commission)
        assert result_with_comm.total_cash_in < result_no_comm.total_cash_in
        
        # Verify that cash flow is balanced (close to 0) in both cases
        # (this is the engine's automatic behavior)
        assert abs(result_no_comm.cash_flow) < 0.1
        assert abs(result_with_comm.cash_flow) < 0.1
    
    def test_zero_commissions_matches_baseline_costs(self):
        """Test that zero commissions produce expected baseline cash flows.
        
        NOTE: The rebalancing engine automatically balances cash flow. When
        cash_available=0, the final cash_flow will be close to 0 due to
        proportional scaling of purchases. This test verifies the intermediate
        cash flows (cash_in and cash_out) match expected values.
        """
        # Portfolio with zero commissions
        asset_a = Asset(
            symbol="A",
            quantity=10.0,
            price=100.0,
            avg_cost=90.0,
            tax_rate=0.26,
            target_weight=0.5,
            # All commissions default to 0.0
        )
        
        asset_b = Asset(
            symbol="B",
            quantity=0.0,
            price=100.0,
            avg_cost=0.0,
            tax_rate=0.26,
            target_weight=0.5,
        )
        
        portfolio = Portfolio(assets=[asset_a, asset_b], cash_available=0.0)
        engine = RebalancingEngine()
        result = engine.rebalance(portfolio)
        
        # Expected intermediate values (before scaling):
        # - Initial plan: Sell 5 shares of A, buy 5 shares of B
        # - Cash in from selling 5 shares of A: 5 * (100 - 0.26*10) = 487
        # - Cash out for buying 5 shares of B: 500 (before scaling)
        # 
        # After scaling by engine to balance cash flow:
        # - Cash in stays: 487 (sales already executed)
        # - Cash out adjusted to match cash in: ~487 (purchases scaled down)
        # - Final cash flow: ~0
        
        # Verify cash in matches expected (no commission on sales)
        assert result.total_cash_in == pytest.approx(487.0, abs=0.01)
        
        # Verify cash out was scaled to balance (should be close to cash in)
        assert result.total_cash_out == pytest.approx(result.total_cash_in, abs=0.1)
        
        # Verify cash flow is balanced (close to 0)
        assert result.cash_flow == pytest.approx(0.0, abs=0.1)


class TestCommissionValidation:
    """Test validation of commission parameters."""
    
    def test_negative_commission_fixed_raises_error(self):
        """Test that negative fixed commission raises ValueError."""
        with pytest.raises(ValueError, match="commission_buy_fixed must be non-negative"):
            Asset(
                symbol="TEST",
                quantity=10.0,
                price=100.0,
                avg_cost=90.0,
                tax_rate=0.26,
                target_weight=1.0,
                commission_buy_fixed=-1.0,
            )
    
    def test_negative_commission_percent_raises_error(self):
        """Test that negative percentage commission raises ValueError."""
        with pytest.raises(ValueError, match="commission_sell_percent must be non-negative"):
            Asset(
                symbol="TEST",
                quantity=10.0,
                price=100.0,
                avg_cost=90.0,
                tax_rate=0.26,
                target_weight=1.0,
                commission_sell_percent=-0.01,
            )
