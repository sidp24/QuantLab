"""
Unit Tests for Options Pricing Models
Tests Black-Scholes, Monte Carlo, and Binomial Tree implementations.
"""

import pytest
import numpy as np
from pricing.black_scholes import price as bs_price, greeks as bs_greeks, put_call_parity_check
from pricing.monte_carlo import price as mc_price, price_with_ci
from pricing.binomial_tree import price as bt_price
from pricing.implied_volatility import implied_volatility


class TestBlackScholes:
    """Test Black-Scholes pricing model."""
    
    # Test parameters
    S = 100.0  # Spot price
    K = 100.0  # Strike (ATM)
    T = 1.0    # 1 year to expiry
    r = 0.05   # 5% risk-free rate
    sigma = 0.2  # 20% volatility
    
    def test_call_price_positive(self):
        """Call price should be positive."""
        price = bs_price(self.S, self.K, self.T, self.r, self.sigma, "Call")
        assert price > 0
    
    def test_put_price_positive(self):
        """Put price should be positive."""
        price = bs_price(self.S, self.K, self.T, self.r, self.sigma, "Put")
        assert price > 0
    
    def test_call_greater_than_intrinsic(self):
        """Call price should be >= intrinsic value."""
        price = bs_price(110, 100, self.T, self.r, self.sigma, "Call")
        intrinsic = max(110 - 100, 0)
        assert price >= intrinsic
    
    def test_put_greater_than_intrinsic(self):
        """Put price should be >= intrinsic value."""
        price = bs_price(90, 100, self.T, self.r, self.sigma, "Put")
        intrinsic = max(100 - 90, 0)
        assert price >= intrinsic
    
    def test_put_call_parity(self):
        """Put-call parity should hold: C - P = S - K*e^(-rT)."""
        call = bs_price(self.S, self.K, self.T, self.r, self.sigma, "Call")
        put = bs_price(self.S, self.K, self.T, self.r, self.sigma, "Put")
        
        lhs = call - put
        rhs = self.S - self.K * np.exp(-self.r * self.T)
        
        assert abs(lhs - rhs) < 1e-10
    
    def test_call_converges_at_expiry(self):
        """At expiry, call should equal max(S-K, 0)."""
        price = bs_price(110, 100, 0, self.r, self.sigma, "Call")
        assert abs(price - 10) < 1e-10
    
    def test_put_converges_at_expiry(self):
        """At expiry, put should equal max(K-S, 0)."""
        price = bs_price(90, 100, 0, self.r, self.sigma, "Put")
        assert abs(price - 10) < 1e-10
    
    def test_call_delta_between_0_and_1(self):
        """Call delta should be between 0 and 1."""
        delta, _, _, _, _ = bs_greeks(self.S, self.K, self.T, self.r, self.sigma, "Call")
        assert 0 <= delta <= 1
    
    def test_put_delta_between_minus1_and_0(self):
        """Put delta should be between -1 and 0."""
        delta, _, _, _, _ = bs_greeks(self.S, self.K, self.T, self.r, self.sigma, "Put")
        assert -1 <= delta <= 0
    
    def test_gamma_positive(self):
        """Gamma should be positive for both calls and puts."""
        _, gamma_call, _, _, _ = bs_greeks(self.S, self.K, self.T, self.r, self.sigma, "Call")
        _, gamma_put, _, _, _ = bs_greeks(self.S, self.K, self.T, self.r, self.sigma, "Put")
        assert gamma_call > 0
        assert gamma_put > 0
    
    def test_vega_positive(self):
        """Vega should be positive."""
        _, _, vega, _, _ = bs_greeks(self.S, self.K, self.T, self.r, self.sigma, "Call")
        assert vega > 0


class TestMonteCarlo:
    """Test Monte Carlo pricing model."""
    
    S = 100.0
    K = 100.0
    T = 1.0
    r = 0.05
    sigma = 0.2
    
    def test_call_price_positive(self):
        """Call price should be positive."""
        price = mc_price(self.S, self.K, self.T, self.r, self.sigma, "Call", n_sim=10000, seed=42)
        assert price > 0
    
    def test_put_price_positive(self):
        """Put price should be positive."""
        price = mc_price(self.S, self.K, self.T, self.r, self.sigma, "Put", n_sim=10000, seed=42)
        assert price > 0
    
    def test_converges_to_black_scholes(self):
        """MC price should converge to BS with enough simulations."""
        mc = mc_price(self.S, self.K, self.T, self.r, self.sigma, "Call", n_sim=100000, seed=42)
        bs = bs_price(self.S, self.K, self.T, self.r, self.sigma, "Call")
        
        # Within 1% of BS price
        assert abs(mc - bs) / bs < 0.01
    
    def test_confidence_interval_contains_bs(self):
        """95% CI should usually contain the BS price."""
        price, ci_low, ci_high, _ = price_with_ci(
            self.S, self.K, self.T, self.r, self.sigma, "Call", n_sim=100000, seed=42
        )
        bs = bs_price(self.S, self.K, self.T, self.r, self.sigma, "Call")
        
        # BS should be within the CI
        assert ci_low <= bs <= ci_high
    
    def test_reproducibility_with_seed(self):
        """Same seed should produce same result."""
        price1 = mc_price(self.S, self.K, self.T, self.r, self.sigma, "Call", n_sim=1000, seed=42)
        price2 = mc_price(self.S, self.K, self.T, self.r, self.sigma, "Call", n_sim=1000, seed=42)
        assert price1 == price2


class TestBinomialTree:
    """Test Binomial Tree pricing model."""
    
    S = 100.0
    K = 100.0
    T = 1.0
    r = 0.05
    sigma = 0.2
    
    def test_european_call_converges_to_bs(self):
        """European call should converge to BS with many steps."""
        bt = bt_price(self.S, self.K, self.T, self.r, self.sigma, "Call", steps=500, american=False)
        bs = bs_price(self.S, self.K, self.T, self.r, self.sigma, "Call")
        
        # Within 0.5% of BS price
        assert abs(bt - bs) / bs < 0.005
    
    def test_european_put_converges_to_bs(self):
        """European put should converge to BS with many steps."""
        bt = bt_price(self.S, self.K, self.T, self.r, self.sigma, "Put", steps=500, american=False)
        bs = bs_price(self.S, self.K, self.T, self.r, self.sigma, "Put")
        
        assert abs(bt - bs) / bs < 0.005
    
    def test_american_call_equals_european_no_dividend(self):
        """American call should equal European when no dividends."""
        american = bt_price(self.S, self.K, self.T, self.r, self.sigma, "Call", steps=200, american=True)
        european = bt_price(self.S, self.K, self.T, self.r, self.sigma, "Call", steps=200, american=False)
        
        # Should be essentially equal
        assert abs(american - european) < 0.01
    
    def test_american_put_geq_european(self):
        """American put should be >= European put."""
        american = bt_price(self.S, self.K, self.T, self.r, self.sigma, "Put", steps=200, american=True)
        european = bt_price(self.S, self.K, self.T, self.r, self.sigma, "Put", steps=200, american=False)
        
        assert american >= european - 0.001  # Small tolerance for numerical errors
    
    def test_more_steps_improves_accuracy(self):
        """More steps should improve accuracy."""
        bs = bs_price(self.S, self.K, self.T, self.r, self.sigma, "Call")
        
        error_50 = abs(bt_price(self.S, self.K, self.T, self.r, self.sigma, "Call", steps=50, american=False) - bs)
        error_200 = abs(bt_price(self.S, self.K, self.T, self.r, self.sigma, "Call", steps=200, american=False) - bs)
        
        assert error_200 < error_50


class TestImpliedVolatility:
    """Test Implied Volatility calculator."""
    
    S = 100.0
    K = 100.0
    T = 1.0
    r = 0.05
    
    def test_iv_recovery(self):
        """Should recover input volatility from BS price."""
        true_vol = 0.25
        market_price = bs_price(self.S, self.K, self.T, self.r, true_vol, "Call")
        
        iv = implied_volatility(market_price, self.S, self.K, self.T, self.r, "Call")
        
        assert iv is not None
        assert abs(iv - true_vol) < 0.001
    
    def test_iv_recovery_put(self):
        """Should recover volatility for puts."""
        true_vol = 0.30
        market_price = bs_price(self.S, self.K, self.T, self.r, true_vol, "Put")
        
        iv = implied_volatility(market_price, self.S, self.K, self.T, self.r, "Put")
        
        assert iv is not None
        assert abs(iv - true_vol) < 0.001
    
    def test_iv_none_for_invalid_price(self):
        """Should return None for prices that violate arbitrage."""
        # Price below intrinsic value (impossible)
        iv = implied_volatility(5.0, 110, 100, self.T, self.r, "Call")
        assert iv is None
    
    def test_iv_handles_deep_itm(self):
        """Should handle deep in-the-money options."""
        true_vol = 0.20
        market_price = bs_price(130, 100, self.T, self.r, true_vol, "Call")
        
        iv = implied_volatility(market_price, 130, 100, self.T, self.r, "Call")
        
        assert iv is not None
        assert abs(iv - true_vol) < 0.01


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_zero_vol_call(self):
        """Zero volatility call should equal discounted intrinsic."""
        price = bs_price(110, 100, 1, 0.05, 0.0001, "Call")
        expected = max(110 - 100 * np.exp(-0.05 * 1), 0)
        assert abs(price - expected) < 0.1
    
    def test_very_short_expiry(self):
        """Very short expiry should approach intrinsic."""
        price = bs_price(105, 100, 0.001, 0.05, 0.2, "Call")
        assert abs(price - 5) < 0.5
    
    def test_deep_otm(self):
        """Deep OTM option should have very low price."""
        price = bs_price(50, 100, 0.1, 0.05, 0.2, "Call")
        assert price < 0.01
    
    def test_high_volatility(self):
        """High volatility should increase option price."""
        low_vol = bs_price(100, 100, 1, 0.05, 0.1, "Call")
        high_vol = bs_price(100, 100, 1, 0.05, 0.5, "Call")
        assert high_vol > low_vol


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
