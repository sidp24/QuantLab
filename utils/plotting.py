import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

def payoff_diagram(S, K, option_type):
    S_range = np.linspace(S * 0.5, S * 1.5, 100)
    if option_type == "Call":
        payoff = np.maximum(S_range - K, 0)
    else:
        payoff = np.maximum(K - S_range, 0)
    fig, ax = plt.subplots()
    ax.plot(S_range, payoff, label=f'{option_type} Payoff')
    ax.set_xlabel('Stock Price at Expiry')
    ax.set_ylabel('Payoff')
    ax.legend()
    st.pyplot(fig)

def monte_carlo_paths(S, T, r, sigma, n_paths=50, n_steps=100):
    dt = T / n_steps
    paths = np.zeros((n_paths, n_steps + 1))
    paths[:, 0] = S
    for i in range(1, n_steps + 1):
        z = np.random.standard_normal(n_paths)
        paths[:, i] = paths[:, i - 1] * np.exp((r - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * z)
    fig, ax = plt.subplots()
    ax.plot(paths.T, color='blue', alpha=0.3)
    ax.set_xlabel('Time Step')
    ax.set_ylabel('Stock Price')
    ax.set_title('Monte Carlo Simulated Paths')
    st.pyplot(fig)
