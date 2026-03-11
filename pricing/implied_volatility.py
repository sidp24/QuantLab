

import numpy as np
from scipy.optimize import brentq, newton
from typing import Optional
from pricing.black_scholes import price as bs_price


def implied_volatility(
    market_price: float,
    S: float,
    K: float,
    T: float,
    r: float,
    option_type: str,
    tol: float = 1e-6,
    max_iter: int = 100
) -> Optional[float]:
    """
    Calculate implied volatility using Brent's method.
    
    Parameters
    ----------
    market_price : float
        Observed market price of the option
    S : float
        Current stock price
    K : float
        Strike price
    T : float
        Time to expiration in years
    r : float
        Risk-free interest rate
    option_type : str
        'Call' or 'Put'
    tol : float
        Tolerance for convergence
    max_iter : int
        Maximum iterations
        
    Returns
    -------
    float or None
        Implied volatility, or None if no solution found
    """
    
    # Validate inputs
    if market_price <= 0 or S <= 0 or K <= 0 or T <= 0:
        return None
    
    # Check for arbitrage violations
    if option_type == "Call":
        intrinsic = max(S - K * np.exp(-r * T), 0)
        max_price = S
    else:
        intrinsic = max(K * np.exp(-r * T) - S, 0)
        max_price = K * np.exp(-r * T)
    
    if market_price < intrinsic or market_price > max_price:
        return None
    
    def objective(sigma: float) -> float:
        """Objective function: BS price - market price"""
        return bs_price(S, K, T, r, sigma, option_type) - market_price
    
    # Try Brent's method first (more robust)
    try:
        iv = brentq(objective, 0.001, 5.0, xtol=tol, maxiter=max_iter)
        return iv
    except ValueError:
        pass
    
    # Fall back to Newton's method with initial guess
    try:
        # Use simple initial guess based on ATM approximation
        initial_guess = np.sqrt(2 * np.pi / T) * market_price / S
        initial_guess = max(0.01, min(initial_guess, 2.0))
        
        iv = newton(objective, initial_guess, tol=tol, maxiter=max_iter)
        
        if 0.001 <= iv <= 5.0:
            return iv
    except (RuntimeError, ValueError):
        pass
    
    return None


def iv_surface(
    option_chain: dict,
    S: float,
    r: float
) -> dict:
    """
    Calculate IV surface from option chain data.
    
    Parameters
    ----------
    option_chain : dict
        Option chain with expiries as keys
    S : float
        Current stock price
    r : float
        Risk-free rate
        
    Returns
    -------
    dict
        IV surface data with strikes, expiries, and IVs
    """
    from datetime import datetime
    
    iv_data = {
        'calls': [],
        'puts': []
    }
    
    for expiry, chain in option_chain.items():
        # Calculate time to expiry
        try:
            expiry_date = datetime.strptime(expiry, "%Y-%m-%d")
            T = max((expiry_date - datetime.now()).days / 365, 0.001)
        except:
            continue
        
        # Process calls
        if 'calls' in chain:
            for _, row in chain['calls'].iterrows():
                strike = row.get('strike', 0)
                price = row.get('lastPrice', 0)
                if strike > 0 and price > 0:
                    iv = implied_volatility(price, S, strike, T, r, "Call")
                    if iv:
                        iv_data['calls'].append({
                            'strike': strike,
                            'expiry': expiry,
                            'T': T,
                            'iv': iv,
                            'moneyness': strike / S
                        })
        
        # Process puts
        if 'puts' in chain:
            for _, row in chain['puts'].iterrows():
                strike = row.get('strike', 0)
                price = row.get('lastPrice', 0)
                if strike > 0 and price > 0:
                    iv = implied_volatility(price, S, strike, T, r, "Put")
                    if iv:
                        iv_data['puts'].append({
                            'strike': strike,
                            'expiry': expiry,
                            'T': T,
                            'iv': iv,
                            'moneyness': strike / S
                        })
    
    return iv_data


def vega(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Calculate vega for Newton-Raphson IV solver."""
    import scipy.stats as si
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    return S * si.norm.pdf(d1) * np.sqrt(T)
