"""Tests for rebalancing engine."""

import pytest
from portfolio_rebalancer.models import Asset, Portfolio
from portfolio_rebalancer.engine import RebalancingEngine
from portfolio_rebalancer.policies import RoundingPolicy


class TestRebalancingEngine:
    """Tests for RebalancingEngine."""
    
    @pytest.fixture
    def simple_portfolio(self):
        """Create a simple test portfolio."""
        return Portfolio(
            assets=[
                Asset("A", 50.0, 100.0, 95.0, 0.26, 0.60),
                Asset("B", 30.0, 110.0, 108.0, 0.26, 0.25),
                Asset("C", 20.0, 135.0, 130.0, 0.26, 0.15),
            ]
        )
    
    def test_engine_initialization(self):
        """Test engine can be initialized."""
        engine = RebalancingEngine()
        assert engine is not None
        assert engine.rounding_policy is None
    
    def test_rebalance_returns_result(self, simple_portfolio):
        """Test that rebalancing returns a RebalancingResult."""
        engine = RebalancingEngine()
        result = engine.rebalance(simple_portfolio)
        
        assert result is not None
        assert result.total_value_before > 0
        assert len(result.assets) == 3
    
    def test_current_state_calculation(self, simple_portfolio):
        """Test Step 1: Current state calculation."""
        engine = RebalancingEngine()
        engine._compute_current_state(simple_portfolio)
        
        # Check values are computed
        total_value = simple_portfolio.total_value
        assert total_value == pytest.approx(11000.0)  # 5000 + 3300 + 2700
        
        # Check weights
        asset_a = simple_portfolio.get_asset("A")
        assert asset_a.current_value == 5000.0
        assert asset_a.current_weight == pytest.approx(5000.0 / 11000.0)
    
    def test_cash_flow_approximates_zero(self, simple_portfolio):
        """Test that cash flow after rebalancing is close to zero."""
        engine = RebalancingEngine()
        result = engine.rebalance(simple_portfolio)
        
        # Cash flow should be very small (within tolerance)
        assert abs(result.cash_flow) < 1.0  # Within €1
    
    def test_weights_close_to_target(self, simple_portfolio):
        """Test that post-rebalancing weights are close to targets."""
        engine = RebalancingEngine()
        result = engine.rebalance(simple_portfolio)
        
        # Check that max deviation is small
        assert result.max_deviation < 0.01  # Within 1%
    
    def test_determinism(self, simple_portfolio):
        """Test that same input produces same output (determinism)."""
        engine = RebalancingEngine()
        
        result1 = engine.rebalance(simple_portfolio)
        result2 = engine.rebalance(simple_portfolio)
        
        # Results should be identical
        for a1, a2 in zip(result1.assets, result2.assets):
            assert a1.delta_quantity == pytest.approx(a2.delta_quantity)
            assert a1.delta_value == pytest.approx(a2.delta_value)
    
    def test_rounding_policy_applied(self, simple_portfolio):
        """Test that rounding policy is applied."""
        engine = RebalancingEngine(rounding_policy=RoundingPolicy.ROUND)
        result = engine.rebalance(simple_portfolio)
        
        # All delta quantities should be integers
        for asset in result.assets:
            assert asset.delta_quantity == round(asset.delta_quantity)
