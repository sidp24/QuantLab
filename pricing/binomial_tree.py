import numpy as np

def price(S, K, T, r, sigma, option_type, steps=100):
    dt = T / steps
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    p = (np.exp(r * dt) - d) / (u - d)
    # Stock price tree
    ST = np.zeros((steps + 1, steps + 1))
    for i in range(steps + 1):
        for j in range(i + 1):
            ST[j, i] = S * (u ** (i - j)) * (d ** j)
    # Option value tree
    option = np.zeros_like(ST)
    if option_type == "Call":
        option[:, steps] = np.maximum(ST[:, steps] - K, 0)
    else:
        option[:, steps] = np.maximum(K - ST[:, steps], 0)
    for i in range(steps - 1, -1, -1):
        for j in range(i + 1):
            option[j, i] = np.exp(-r * dt) * (p * option[j, i + 1] + (1 - p) * option[j + 1, i + 1])
    return option[0, 0]
