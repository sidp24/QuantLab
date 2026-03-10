"""
Binomial Tree Option Pricing Model
Implements Cox-Ross-Rubinstein model for European and American options.
"""

import numpy as np
from typing import Tuple, Optional


def price(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str,
    steps: int = 100,
    american: bool = True
) -> float:
    """
    Price an option using the binomial tree model.
    
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
    steps : int
        Number of time steps in the tree
    american : bool
        If True, price American option (allow early exercise)
        If False, price European option
        
    Returns
    -------
    float
        Option price
        
    Notes
    -----
    Uses the Cox-Ross-Rubinstein (CRR) parameterization:
    - u = exp(sigma * sqrt(dt))
    - d = 1/u
    - p = (exp(r*dt) - d) / (u - d)
    """
    dt = T / steps
    
    # CRR parameters
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    p = (np.exp(r * dt) - d) / (u - d)
    
    # Discount factor
    disc = np.exp(-r * dt)
    
    # Build price tree at maturity
    ST = np.zeros(steps + 1)
    for j in range(steps + 1):
        ST[j] = S * (u ** (steps - j)) * (d ** j)
    
    # Calculate option values at maturity
    if option_type == "Call":
        option = np.maximum(ST - K, 0)
    else:
        option = np.maximum(K - ST, 0)
    
    # Backward induction
    for i in range(steps - 1, -1, -1):
        for j in range(i + 1):
            # Continuation value
            option[j] = disc * (p * option[j] + (1 - p) * option[j + 1])
            
            # Early exercise value (for American options)
            if american:
                St = S * (u ** (i - j)) * (d ** j)
                if option_type == "Call":
                    exercise = max(St - K, 0)
                else:
                    exercise = max(K - St, 0)
                option[j] = max(option[j], exercise)
    
    return option[0]


def price_with_greeks(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str,
    steps: int = 100,
    american: bool = True
) -> Tuple[float, float, float, float]:
    """
    Price option and calculate Greeks using the binomial tree.
    
    Returns
    -------
    tuple
        (price, delta, gamma, theta)
    """
    # Price
    price_val = price(S, K, T, r, sigma, option_type, steps, american)
    
    # Delta: central difference
    dS = S * 0.01
    price_up = price(S + dS, K, T, r, sigma, option_type, steps, american)
    price_down = price(S - dS, K, T, r, sigma, option_type, steps, american)
    delta = (price_up - price_down) / (2 * dS)
    
    # Gamma: second derivative
    gamma = (price_up - 2 * price_val + price_down) / (dS ** 2)
    
    # Theta: time derivative (per day)
    if T > 1/365:
        price_t = price(S, K, T - 1/365, r, sigma, option_type, steps, american)
        theta = (price_t - price_val)  # Already per day
    else:
        theta = 0.0
    
    return (price_val, delta, gamma, theta)


def build_tree(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str,
    steps: int = 10,
    american: bool = True
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Build and return the full binomial tree for visualization.
    
    Returns
    -------
    tuple
        (stock_tree, option_tree) - 2D arrays representing the trees
    """
    dt = T / steps
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    p = (np.exp(r * dt) - d) / (u - d)
    disc = np.exp(-r * dt)
    
    # Stock price tree
    stock_tree = np.zeros((steps + 1, steps + 1))
    for i in range(steps + 1):
        for j in range(i + 1):
            stock_tree[j, i] = S * (u ** (i - j)) * (d ** j)
    
    # Option value tree
    option_tree = np.zeros_like(stock_tree)
    
    # Terminal values
    for j in range(steps + 1):
        if option_type == "Call":
            option_tree[j, steps] = max(stock_tree[j, steps] - K, 0)
        else:
            option_tree[j, steps] = max(K - stock_tree[j, steps], 0)
    
    # Backward induction
    for i in range(steps - 1, -1, -1):
        for j in range(i + 1):
            option_tree[j, i] = disc * (p * option_tree[j, i + 1] + (1 - p) * option_tree[j + 1, i + 1])
            
            if american:
                if option_type == "Call":
                    exercise = max(stock_tree[j, i] - K, 0)
                else:
                    exercise = max(K - stock_tree[j, i], 0)
                option_tree[j, i] = max(option_tree[j, i], exercise)
    
    return stock_tree, option_tree


def early_exercise_boundary(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str,
    steps: int = 100
) -> np.ndarray:
    """
    Calculate the early exercise boundary for American options.
    
    Returns
    -------
    np.ndarray
        Array of critical stock prices at each time step
    """
    dt = T / steps
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    p = (np.exp(r * dt) - d) / (u - d)
    disc = np.exp(-r * dt)
    
    # Build stock tree
    stock_tree = np.zeros((steps + 1, steps + 1))
    for i in range(steps + 1):
        for j in range(i + 1):
            stock_tree[j, i] = S * (u ** (i - j)) * (d ** j)
    
    # Build option tree
    option_tree = np.zeros_like(stock_tree)
    
    # Terminal values
    for j in range(steps + 1):
        if option_type == "Call":
            option_tree[j, steps] = max(stock_tree[j, steps] - K, 0)
        else:
            option_tree[j, steps] = max(K - stock_tree[j, steps], 0)
    
    # Track exercise boundary
    boundary = np.zeros(steps + 1)
    boundary[steps] = K  # At expiration, exercise at ATM
    
    # Backward induction
    for i in range(steps - 1, -1, -1):
        for j in range(i + 1):
            continuation = disc * (p * option_tree[j, i + 1] + (1 - p) * option_tree[j + 1, i + 1])
            
            if option_type == "Call":
                exercise = max(stock_tree[j, i] - K, 0)
            else:
                exercise = max(K - stock_tree[j, i], 0)
            
            if exercise > continuation and exercise > 0:
                boundary[i] = stock_tree[j, i]
            
            option_tree[j, i] = max(continuation, exercise)
    
    return boundary
