import numpy as np

def price(S, K, T, r, sigma, option_type, n_sim=10000):
    np.random.seed(42)
    Z = np.random.standard_normal(n_sim)
    ST = S * np.exp((r - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * Z)
    if option_type == "Call":
        payoff = np.maximum(ST - K, 0)
    else:
        payoff = np.maximum(K - ST, 0)
    return np.exp(-r * T) * np.mean(payoff)
