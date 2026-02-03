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
    
    def test_rebalancing_with_commissions_increases_cash_need(self):
        """Test that commissions increase the cash needed for rebalancing."""
        # Create portfolio: 100% in asset A, target 50/50 split with new asset B
        asset_a = Asset(
            symbol="A",
            quantity=10.0,
            price=100.0,
            avg_cost=90.0,
            tax_rate=0.26,
            target_weight=0.5,
            commission_sell_fixed=2.50,  # Commission on sell
        )
        
        asset_b = Asset(
            symbol="B",
            quantity=0.0,
            price=100.0,
            avg_cost=0.0,  # New asset
            tax_rate=0.26,
            target_weight=0.5,
            commission_buy_fixed=2.50,  # Commission on buy
        )
        
        portfolio = Portfolio(assets=[asset_a, asset_b], cash_available=0.0)
        engine = RebalancingEngine()
        result = engine.rebalance(portfolio)
        
        # Without commissions:
        # - Current value: 1000 (10 * 100)
        # - Target: A=500, B=500
        # - Sell A: 5 shares = 500 gross, tax on gain = 5*(100-90)*0.26 = 13
        # - Cash in: 500 - 13 = 487
        # - Buy B: need 500, cash available 487 → need 13 more
        # - Cash flow: -13
        
        # With commissions (2.50 on each side):
        # - Sell A: 500 - 13 - 2.50 = 484.5
        # - Buy B: need 500 + 2.50 = 502.5
        # - Cash flow should be more negative (need more cash)
        
        assert result.cash_flow < -13.0  # More negative than without commissions
        assert result.total_cash_in < 487.0  # Less cash from sales due to commission
        assert result.total_cash_out > 500.0  # More cash for purchases due to commission
    
    def test_zero_commissions_preserves_original_behavior(self):
        """Test that zero commissions produce same results as before."""
        # Portfolio with zero commissions should behave identically to old system
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
        
        # Expected behavior (from existing test_engine.py logic):
        # - Sell 5 shares of A: cash_in = 5 * (100 - 0.26*10) = 487
        # - Buy 5 shares of B: cash_out = 500
        # - Cash flow = 487 - 500 = -13
        
        assert result.cash_flow == pytest.approx(-13.0, abs=0.01)
        assert result.total_cash_in == pytest.approx(487.0, abs=0.01)
        assert result.total_cash_out == pytest.approx(500.0, abs=0.01)


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
