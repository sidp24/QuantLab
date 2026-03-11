

from typing import List, Dict, Optional, Tuple
import numpy as np
from dataclasses import dataclass


# Pre-built strategy templates
STRATEGY_TEMPLATES = {
    "Bull Call Spread": {
        "description": "Buy lower strike call, sell higher strike call. Limited profit/loss.",
        "legs": [
            {"type": "Call", "strike_pct": 1.0, "qty": 1},
            {"type": "Call", "strike_pct": 1.05, "qty": -1}
        ]
    },
    "Bear Put Spread": {
        "description": "Buy higher strike put, sell lower strike put. Bearish strategy.",
        "legs": [
            {"type": "Put", "strike_pct": 1.0, "qty": 1},
            {"type": "Put", "strike_pct": 0.95, "qty": -1}
        ]
    },
    "Long Straddle": {
        "description": "Buy ATM call and put. Profit from large moves in either direction.",
        "legs": [
            {"type": "Call", "strike_pct": 1.0, "qty": 1},
            {"type": "Put", "strike_pct": 1.0, "qty": 1}
        ]
    },
    "Short Straddle": {
        "description": "Sell ATM call and put. Profit from low volatility.",
        "legs": [
            {"type": "Call", "strike_pct": 1.0, "qty": -1},
            {"type": "Put", "strike_pct": 1.0, "qty": -1}
        ]
    },
    "Long Strangle": {
        "description": "Buy OTM call and put. Cheaper than straddle, needs bigger move.",
        "legs": [
            {"type": "Call", "strike_pct": 1.05, "qty": 1},
            {"type": "Put", "strike_pct": 0.95, "qty": 1}
        ]
    },
    "Iron Condor": {
        "description": "Sell OTM strangle, buy further OTM strangle. Limited risk neutral strategy.",
        "legs": [
            {"type": "Put", "strike_pct": 0.90, "qty": 1},
            {"type": "Put", "strike_pct": 0.95, "qty": -1},
            {"type": "Call", "strike_pct": 1.05, "qty": -1},
            {"type": "Call", "strike_pct": 1.10, "qty": 1}
        ]
    },
    "Butterfly Spread": {
        "description": "Buy 1 lower, sell 2 middle, buy 1 higher strike. Low cost, limited profit.",
        "legs": [
            {"type": "Call", "strike_pct": 0.95, "qty": 1},
            {"type": "Call", "strike_pct": 1.0, "qty": -2},
            {"type": "Call", "strike_pct": 1.05, "qty": 1}
        ]
    },
    "Covered Call": {
        "description": "Long stock + short call. Income generation strategy.",
        "legs": [
            {"type": "Call", "strike_pct": 1.05, "qty": -1}
        ],
        "includes_stock": True
    },
    "Protective Put": {
        "description": "Long stock + long put. Downside protection.",
        "legs": [
            {"type": "Put", "strike_pct": 0.95, "qty": 1}
        ],
        "includes_stock": True
    },
    "Calendar Spread": {
        "description": "Sell near-term, buy far-term same strike. Profit from time decay.",
        "legs": [
            {"type": "Call", "strike_pct": 1.0, "qty": -1},  # Near term (30 days)
            {"type": "Call", "strike_pct": 1.0, "qty": 1}   # Far term (60 days)
        ],
        "note": "Different expirations - near term short, far term long"
    }
}


@dataclass
class OptionLeg:
    """Represents a single option leg in a portfolio."""
    option_type: str  # "Call" or "Put"
    strike: float
    expiry: str
    quantity: int  # Positive = long, negative = short
    premium: float = 0.0
    
    def payoff(self, S: float) -> float:
        """Calculate payoff at expiration for given stock price."""
        if self.option_type == "Call":
            intrinsic = max(S - self.strike, 0)
        else:
            intrinsic = max(self.strike - S, 0)
        return self.quantity * intrinsic
    
    def pnl(self, S: float) -> float:
        """Calculate P&L including premium paid/received."""
        return self.payoff(S) - self.quantity * self.premium * 100


class Portfolio:
    """Multi-leg option portfolio with analysis capabilities."""
    
    def __init__(self):
        self.legs: List[OptionLeg] = []
        self.includes_stock: bool = False
        self.stock_quantity: int = 0
    
    def add_leg(self, leg: OptionLeg) -> None:
        """Add an option leg to the portfolio."""
        self.legs.append(leg)
    
    def remove_leg(self, idx: int) -> None:
        """Remove a leg by index."""
        if 0 <= idx < len(self.legs):
            self.legs.pop(idx)
    
    def clear(self) -> None:
        """Remove all legs."""
        self.legs = []
        self.includes_stock = False
        self.stock_quantity = 0
    
    def get_payoff(self, S: float) -> float:
        """Calculate total portfolio payoff at given stock price."""
        payoff = sum(leg.payoff(S) for leg in self.legs)
        if self.includes_stock:
            # Assume stock was bought at current price (simplified)
            payoff += self.stock_quantity * S
        return payoff
    
    def get_pnl(self, S: float) -> float:
        """Calculate total P&L including premiums."""
        pnl = sum(leg.pnl(S) for leg in self.legs)
        return pnl
    
    def payoff_diagram(self, S_range: np.ndarray) -> List[float]:
        """Calculate payoff across a range of stock prices."""
        return [self.get_payoff(S) for S in S_range]
    
    def pnl_diagram(self, S_range: np.ndarray) -> List[float]:
        """Calculate P&L across a range of stock prices."""
        return [self.get_pnl(S) for S in S_range]
    
    def calculate_metrics(
        self, 
        spot_price: float,
        r: float = 0.05,
        sigma: float = 0.2
    ) -> Dict:
        """
        Calculate key portfolio metrics.
        
        Returns
        -------
        dict
            Contains net_premium, max_profit, max_loss, breakeven points
        """
        # Net premium (positive = paid, negative = received)
        net_premium = sum(leg.premium * leg.quantity for leg in self.legs)
        
        # Calculate payoff range
        S_range = np.linspace(spot_price * 0.5, spot_price * 1.5, 1000)
        payoffs = self.payoff_diagram(S_range)
        pnls = [p - net_premium * 100 for p in payoffs]
        
        # Max profit and loss
        max_profit = max(pnls)
        max_loss = min(pnls)
        
        # Breakeven points (where P&L crosses zero)
        breakevens = []
        for i in range(1, len(pnls)):
            if pnls[i-1] * pnls[i] < 0:  # Sign change
                # Linear interpolation
                S_be = S_range[i-1] + (S_range[i] - S_range[i-1]) * abs(pnls[i-1]) / (abs(pnls[i-1]) + abs(pnls[i]))
                breakevens.append(S_be)
        
        return {
            'net_premium': net_premium,
            'max_profit': max_profit,
            'max_loss': max_loss,
            'breakeven': breakevens
        }
    
    def calculate_portfolio_greeks(
        self,
        spot_price: float,
        r: float = 0.05,
        sigma: float = 0.2
    ) -> Dict[str, float]:
        """
        Calculate aggregate portfolio Greeks.
        
        Returns
        -------
        dict
            Contains delta, gamma, vega, theta, rho
        """
        from pricing.black_scholes import greeks as bs_greeks
        
        total_greeks = {
            'delta': 0.0,
            'gamma': 0.0,
            'vega': 0.0,
            'theta': 0.0,
            'rho': 0.0
        }
        
        for leg in self.legs:
            # Parse expiry to get T
            try:
                days = int(leg.expiry.split()[0])
                T = days / 365
            except:
                T = 30 / 365  # Default to 30 days
            
            delta, gamma, vega, theta, rho = bs_greeks(
                spot_price, leg.strike, T, r, sigma, leg.option_type
            )
            
            total_greeks['delta'] += delta * leg.quantity
            total_greeks['gamma'] += gamma * leg.quantity
            total_greeks['vega'] += vega * leg.quantity
            total_greeks['theta'] += theta * leg.quantity
            total_greeks['rho'] += rho * leg.quantity
        
        # Add stock delta if included
        if self.includes_stock:
            total_greeks['delta'] += self.stock_quantity
        
        return total_greeks
    
    def probability_of_profit(
        self,
        spot_price: float,
        sigma: float = 0.2,
        T: float = 30/365,
        n_simulations: int = 10000
    ) -> float:
        """
        Estimate probability of profit using Monte Carlo simulation.
        
        Returns
        -------
        float
            Probability of profit (0 to 1)
        """
        np.random.seed(42)
        
        # Simulate terminal stock prices (GBM)
        Z = np.random.standard_normal(n_simulations)
        r = 0.05  # Risk-free rate assumption
        ST = spot_price * np.exp((r - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * Z)
        
        # Calculate P&L for each simulation
        net_premium = sum(leg.premium * leg.quantity for leg in self.legs)
        profitable = 0
        
        for s in ST:
            payoff = self.get_payoff(s)
            pnl = payoff - net_premium * 100
            if pnl > 0:
                profitable += 1
        
        return profitable / n_simulations

