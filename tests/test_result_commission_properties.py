"""Tests for commission tracking properties in RebalancingResult."""

import pytest
from portfolio_rebalancer.models.asset import Asset
from portfolio_rebalancer.models.portfolio import Portfolio
from portfolio_rebalancer.engine.rebalancer import RebalancingEngine


class TestCommissionTracking:
    """Test commission tracking in RebalancingResult."""
    
    def test_commission_buy_only(self):
        """Test commission calculation for buy-only operations."""
        # Portfolio: buy new asset B
        asset_a = Asset(
            symbol="A",
            quantity=10.0,
            price=100.0,
            avg_cost=100.0,
            tax_rate=0.26,
            target_weight=0.5,
        )
        
        asset_b = Asset(
            symbol="B",
            quantity=0.0,
            price=100.0,
            avg_cost=0.0,
            tax_rate=0.26,
            target_weight=0.5,
            commission_buy_fixed=5.0,  # Fixed 5€ commission on buy
        )
        
        portfolio = Portfolio(assets=[asset_a, asset_b], cash_available=500.0)
        engine = RebalancingEngine()
        result = engine.rebalance(portfolio)
        
        # Should have buy commission but no sell commission
        assert result.total_commission_buy > 0
        assert result.total_commission_sell == 0.0
        assert result.total_commission == result.total_commission_buy
    
    def test_commission_sell_only(self):
        """Test commission calculation for sell-only operations."""
        # Portfolio: sell some of asset A
        asset_a = Asset(
            symbol="A",
            quantity=10.0,
            price=100.0,
            avg_cost=90.0,
            tax_rate=0.26,
            target_weight=0.5,
            commission_sell_fixed=3.0,  # Fixed 3€ commission on sell
        )
        
        asset_b = Asset(
            symbol="B",
            quantity=10.0,
            price=100.0,
            avg_cost=100.0,
            tax_rate=0.26,
            target_weight=0.5,
        )
        
        portfolio = Portfolio(assets=[asset_a, asset_b], cash_available=0.0)
        engine = RebalancingEngine()
        result = engine.rebalance(portfolio)
        
        # With balanced portfolio, no operations should occur
        # Let's make it unbalanced
        asset_a.target_weight = 0.3
        asset_b.target_weight = 0.7
        
        portfolio = Portfolio(assets=[asset_a, asset_b], cash_available=0.0)
        result = engine.rebalance(portfolio)
        
        # Should have sell commission
        assert result.total_commission_sell > 0
        # May or may not have buy commission depending on scaling
    
    def test_commission_buy_and_sell(self):
        """Test commission calculation with both buy and sell operations."""
        # Portfolio: 100% in A, rebalance to 50/50 with B
        asset_a = Asset(
            symbol="A",
            quantity=10.0,
            price=100.0,
            avg_cost=90.0,
            tax_rate=0.26,
            target_weight=0.5,
            commission_sell_fixed=2.50,
        )
        
        asset_b = Asset(
            symbol="B",
            quantity=0.0,
            price=100.0,
            avg_cost=0.0,
            tax_rate=0.26,
            target_weight=0.5,
            commission_buy_fixed=2.50,
        )
        
        portfolio = Portfolio(assets=[asset_a, asset_b], cash_available=0.0)
        engine = RebalancingEngine()
        result = engine.rebalance(portfolio)
        
        # Should have both buy and sell commissions
        assert result.total_commission_buy > 0
        assert result.total_commission_sell > 0
        assert result.total_commission == pytest.approx(
            result.total_commission_buy + result.total_commission_sell,
            abs=0.01
        )
    
    def test_commission_zero(self):
        """Test that zero commissions result in zero tracked commissions."""
        asset_a = Asset(
            symbol="A",
            quantity=10.0,
            price=100.0,
            avg_cost=90.0,
            tax_rate=0.26,
            target_weight=0.5,
            # No commissions specified (defaults to 0)
        )
        
        asset_b = Asset(
            symbol="B",
            quantity=0.0,
            price=100.0,
            avg_cost=0.0,
            tax_rate=0.26,
            target_weight=0.5,
            # No commissions specified (defaults to 0)
        )
        
        portfolio = Portfolio(assets=[asset_a, asset_b], cash_available=0.0)
        engine = RebalancingEngine()
        result = engine.rebalance(portfolio)
        
        # All commissions should be zero
        assert result.total_commission_buy == 0.0
        assert result.total_commission_sell == 0.0
        assert result.total_commission == 0.0
    
    def test_commission_percentage_based(self):
        """Test commission calculation with percentage-based commissions."""
        asset_a = Asset(
            symbol="A",
            quantity=10.0,
            price=100.0,
            avg_cost=90.0,
            tax_rate=0.26,
            target_weight=0.5,
            commission_sell_percent=0.001,  # 0.1% on sell
        )
        
        asset_b = Asset(
            symbol="B",
            quantity=0.0,
            price=100.0,
            avg_cost=0.0,
            tax_rate=0.26,
            target_weight=0.5,
            commission_buy_percent=0.001,  # 0.1% on buy
        )
        
        portfolio = Portfolio(assets=[asset_a, asset_b], cash_available=0.0)
        engine = RebalancingEngine()
        result = engine.rebalance(portfolio)
        
        # Should have both buy and sell commissions (percentage-based)
        assert result.total_commission_buy > 0
        assert result.total_commission_sell > 0
        assert result.total_commission > 0
