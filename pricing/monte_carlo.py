

import numpy as np
from typing import Tuple, Optional


def price(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str,
    n_sim: int = 10000,
    seed: Optional[int] = None
) -> float:
    """
    Price a European option using Monte Carlo simulation.
    
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
    n_sim : int
        Number of simulations
    seed : int, optional
        Random seed for reproducibility
        
    Returns
    -------
    float
        Option price estimate
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Generate random terminal prices using GBM
    Z = np.random.standard_normal(n_sim)
    ST = S * np.exp((r - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * Z)
    
    # Calculate payoffs
    if option_type == "Call":
        payoff = np.maximum(ST - K, 0)
    else:
        payoff = np.maximum(K - ST, 0)
    
    # Discounted expected payoff
    return np.exp(-r * T) * np.mean(payoff)


def price_with_ci(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str,
    n_sim: int = 10000,
    confidence: float = 0.95,
    seed: Optional[int] = None
) -> Tuple[float, float, float, float]:
    """
    Price option with confidence interval using Monte Carlo.
    
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
    n_sim : int
        Number of simulations
    confidence : float
        Confidence level (default 0.95 for 95% CI)
    seed : int, optional
        Random seed
        
    Returns
    -------
    tuple
        (price, ci_lower, ci_upper, std_error)
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Generate random terminal prices
    Z = np.random.standard_normal(n_sim)
    ST = S * np.exp((r - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * Z)
    
    # Calculate payoffs
    if option_type == "Call":
        payoff = np.maximum(ST - K, 0)
    else:
        payoff = np.maximum(K - ST, 0)
    
    # Discounted payoffs
    discounted = np.exp(-r * T) * payoff
    
    # Statistics
    price_est = np.mean(discounted)
    std_dev = np.std(discounted, ddof=1)
    std_error = std_dev / np.sqrt(n_sim)
    
    # Confidence interval
    from scipy import stats
    z_score = stats.norm.ppf((1 + confidence) / 2)
    ci_lower = price_est - z_score * std_error
    ci_upper = price_est + z_score * std_error
    
    return (price_est, ci_lower, ci_upper, std_error)


def price_asian(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str,
    n_sim: int = 10000,
    n_steps: int = 252,
    averaging: str = "arithmetic",
    seed: Optional[int] = None
) -> float:
    """
    Price an Asian option (path-dependent) using Monte Carlo.
    
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
    n_sim : int
        Number of simulations
    n_steps : int
        Number of time steps (default 252 for daily)
    averaging : str
        'arithmetic' or 'geometric'
    seed : int, optional
        Random seed
        
    Returns
    -------
    float
        Asian option price estimate
    """
    if seed is not None:
        np.random.seed(seed)
    
    dt = T / n_steps
    
    # Generate paths
    Z = np.random.standard_normal((n_sim, n_steps))
    
    # Calculate price paths
    log_returns = (r - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * Z
    log_paths = np.cumsum(log_returns, axis=1)
    paths = S * np.exp(log_paths)
    
    # Include initial price in average
    paths_with_start = np.column_stack([np.full(n_sim, S), paths])
    
    # Calculate average
    if averaging == "arithmetic":
        avg_price = np.mean(paths_with_start, axis=1)
    else:  # geometric
        avg_price = np.exp(np.mean(np.log(paths_with_start), axis=1))
    
    # Payoff
    if option_type == "Call":
        payoff = np.maximum(avg_price - K, 0)
    else:
        payoff = np.maximum(K - avg_price, 0)
    
    return np.exp(-r * T) * np.mean(payoff)


def price_barrier(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str,
    barrier: float,
    barrier_type: str,
    n_sim: int = 10000,
    n_steps: int = 252,
    seed: Optional[int] = None
) -> float:
    """
    Price a barrier option using Monte Carlo.
    
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
    barrier : float
        Barrier level
    barrier_type : str
        'up-and-out', 'up-and-in', 'down-and-out', 'down-and-in'
    n_sim : int
        Number of simulations
    n_steps : int
        Number of time steps
    seed : int, optional
        Random seed
        
    Returns
    -------
    float
        Barrier option price estimate
    """
    if seed is not None:
        np.random.seed(seed)
    
    dt = T / n_steps
    
    # Generate paths
    Z = np.random.standard_normal((n_sim, n_steps))
    log_returns = (r - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * Z
    log_paths = np.log(S) + np.cumsum(log_returns, axis=1)
    paths = np.exp(log_paths)
    
    # Check barrier conditions
    if barrier_type == "up-and-out":
        knocked = np.any(paths >= barrier, axis=1)
        active = ~knocked
    elif barrier_type == "up-and-in":
        knocked = np.any(paths >= barrier, axis=1)
        active = knocked
    elif barrier_type == "down-and-out":
        knocked = np.any(paths <= barrier, axis=1)
        active = ~knocked
    elif barrier_type == "down-and-in":
        knocked = np.any(paths <= barrier, axis=1)
        active = knocked
    else:
        raise ValueError(f"Unknown barrier type: {barrier_type}")
    
    # Terminal prices
    ST = paths[:, -1]
    
    # Payoff (only for active options)
    if option_type == "Call":
        payoff = np.where(active, np.maximum(ST - K, 0), 0)
    else:
        payoff = np.where(active, np.maximum(K - ST, 0), 0)
    
    return np.exp(-r * T) * np.mean(payoff)


def generate_paths(
    S: float,
    T: float,
    r: float,
    sigma: float,
    n_paths: int = 50,
    n_steps: int = 100,
    seed: Optional[int] = None
) -> np.ndarray:
    """
    Generate stock price paths for visualization.
    
    Returns
    -------
    np.ndarray
        Array of shape (n_paths, n_steps + 1) with price paths
    """
    if seed is not None:
        np.random.seed(seed)
    
    dt = T / n_steps
    paths = np.zeros((n_paths, n_steps + 1))
    paths[:, 0] = S
    
    for i in range(1, n_steps + 1):
        z = np.random.standard_normal(n_paths)
        paths[:, i] = paths[:, i - 1] * np.exp(
            (r - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * z
        )
    
    return paths
