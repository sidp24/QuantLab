

import numpy as np
import scipy.stats as si
from typing import Tuple


def price(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str
) -> float:
    """
    Calculate Black-Scholes option price.
    
    Parameters
    ----------
    S : float
        Current stock price
    K : float
        Strike price
    T : float
        Time to expiration in years
    r : float
        Risk-free interest rate (annualized)
    sigma : float
        Volatility (annualized)
    option_type : str
        'Call' or 'Put'
        
    Returns
    -------
    float
        Option price
        
    Examples
    --------
    >>> price(100, 100, 1, 0.05, 0.2, "Call")
    10.4506...
    """
    # Handle edge cases
    if T <= 0:
        if option_type == "Call":
            return max(S - K, 0)
        else:
            return max(K - S, 0)
    
    if sigma <= 0:
        if option_type == "Call":
            return max(S - K * np.exp(-r * T), 0)
        else:
            return max(K * np.exp(-r * T) - S, 0)
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if option_type == "Call":
        return S * si.norm.cdf(d1) - K * np.exp(-r * T) * si.norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * si.norm.cdf(-d2) - S * si.norm.cdf(-d1)


def greeks(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str
) -> Tuple[float, float, float, float, float]:
    """
    Calculate Black-Scholes Greeks.
    
    Parameters
    ----------
    S : float
        Current stock price
    K : float
        Strike price
    T : float
        Time to expiration in years
    r : float
        Risk-free interest rate
    sigma : float
        Volatility
    option_type : str
        'Call' or 'Put'
        
    Returns
    -------
    tuple
        (delta, gamma, vega, theta, rho)
        
    Notes
    -----
    - Delta: Price sensitivity to underlying price change
    - Gamma: Delta sensitivity to underlying price change
    - Vega: Price sensitivity to volatility change (per 1% vol change)
    - Theta: Price sensitivity to time (per day)
    - Rho: Price sensitivity to interest rate change (per 1% rate change)
    """
    if T <= 0 or sigma <= 0:
        # At expiration or zero vol, greeks are degenerate
        delta = 1.0 if (option_type == "Call" and S > K) else -1.0 if (option_type == "Put" and S < K) else 0.0
        return (delta, 0.0, 0.0, 0.0, 0.0)
    
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    # Delta
    if option_type == "Call":
        delta = si.norm.cdf(d1)
    else:
        delta = si.norm.cdf(d1) - 1  # or -si.norm.cdf(-d1)
    
    # Gamma (same for calls and puts)
    gamma = si.norm.pdf(d1) / (S * sigma * np.sqrt(T))
    
    # Vega (same for calls and puts, expressed per 1% change)
    vega = S * si.norm.pdf(d1) * np.sqrt(T) / 100
    
    # Theta (per day)
    if option_type == "Call":
        theta = (
            -S * si.norm.pdf(d1) * sigma / (2 * np.sqrt(T))
            - r * K * np.exp(-r * T) * si.norm.cdf(d2)
        ) / 365
    else:
        theta = (
            -S * si.norm.pdf(d1) * sigma / (2 * np.sqrt(T))
            + r * K * np.exp(-r * T) * si.norm.cdf(-d2)
        ) / 365
    
    # Rho (per 1% change)
    if option_type == "Call":
        rho = K * T * np.exp(-r * T) * si.norm.cdf(d2) / 100
    else:
        rho = -K * T * np.exp(-r * T) * si.norm.cdf(-d2) / 100
    
    return (delta, gamma, vega, theta, rho)


def delta_hedge_ratio(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str
) -> float:
    """
    Calculate the delta hedge ratio (shares needed to hedge 1 option).
    
    Returns
    -------
    float
        Number of shares to hold per option (negative for short)
    """
    d, _, _, _, _ = greeks(S, K, T, r, sigma, option_type)
    return -d  # Negative because we hedge opposite to delta


def put_call_parity_check(
    call_price: float,
    put_price: float,
    S: float,
    K: float,
    T: float,
    r: float,
    tol: float = 0.01
) -> Tuple[bool, float]:
    """
    Check put-call parity: C - P = S - K*e^(-rT)
    
    Returns
    -------
    tuple
        (is_valid, arbitrage_spread)
    """
    parity_lhs = call_price - put_price
    parity_rhs = S - K * np.exp(-r * T)
    spread = abs(parity_lhs - parity_rhs)
    
    return (spread < tol, spread)
