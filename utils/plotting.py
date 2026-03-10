"""
Plotting Utilities
Visualization functions for options analysis with dark theme styling.
"""

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from typing import Optional, List

# ===== DARK THEME CONFIGURATION =====
COLORS = {
    "primary": "#00D4FF",
    "secondary": "#7B2FFF", 
    "accent": "#FF6B6B",
    "success": "#00E676",
    "warning": "#FFD93D",
    "background": "#0A0E17",
    "surface": "#12161F",
    "grid": "#2A3142",
    "text": "#F8FAFC",
    "text_muted": "#94A3B8",
}

def apply_dark_style(ax, fig):
    """Apply dark theme styling to matplotlib axes and figure."""
    fig.patch.set_facecolor(COLORS["background"])
    ax.set_facecolor(COLORS["surface"])
    
    # Spine colors
    for spine in ax.spines.values():
        spine.set_color(COLORS["grid"])
        spine.set_linewidth(0.5)
    
    # Tick colors
    ax.tick_params(colors=COLORS["text_muted"], which='both')
    
    # Label colors
    ax.xaxis.label.set_color(COLORS["text"])
    ax.yaxis.label.set_color(COLORS["text"])
    ax.title.set_color(COLORS["text"])
    
    # Grid
    ax.grid(True, alpha=0.2, color=COLORS["grid"], linestyle='-', linewidth=0.5)
    
    # Legend
    legend = ax.get_legend()
    if legend:
        legend.get_frame().set_facecolor(COLORS["surface"])
        legend.get_frame().set_edgecolor(COLORS["grid"])
        for text in legend.get_texts():
            text.set_color(COLORS["text"])


def payoff_diagram(
    S: float,
    K: float,
    option_type: str,
    premium: float = 0.0,
    show_breakeven: bool = True
) -> None:
    """
    Display an option payoff diagram with dark theme styling.
    """
    S_range = np.linspace(S * 0.5, S * 1.5, 200)
    
    if option_type == "Call":
        payoff = np.maximum(S_range - K, 0)
        pnl = payoff - premium
        breakeven = K + premium if premium > 0 else K
    else:
        payoff = np.maximum(K - S_range, 0)
        pnl = payoff - premium
        breakeven = K - premium if premium > 0 else K
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot payoff and P&L
    ax.plot(S_range, payoff, color=COLORS["primary"], linewidth=2.5, label='Payoff at Expiration')
    if premium > 0:
        ax.plot(S_range, pnl, color=COLORS["secondary"], linewidth=2, linestyle='--', label='P&L (with premium)')
        ax.fill_between(S_range, pnl, 0, where=(pnl > 0), alpha=0.3, color=COLORS["success"])
        ax.fill_between(S_range, pnl, 0, where=(pnl < 0), alpha=0.3, color=COLORS["accent"])
    
    # Reference lines
    ax.axhline(y=0, color=COLORS["text_muted"], linewidth=1, alpha=0.5)
    ax.axvline(x=K, color=COLORS["warning"], linestyle='--', linewidth=1.5, alpha=0.8, label=f'Strike (K=${K:.2f})')
    ax.axvline(x=S, color=COLORS["primary"], linestyle=':', linewidth=1.5, alpha=0.8, label=f'Spot (S=${S:.2f})')
    
    if show_breakeven and premium > 0:
        ax.axvline(x=breakeven, color=COLORS["success"], linestyle='--', linewidth=1.5, 
                   label=f'Breakeven (${breakeven:.2f})')
    
    ax.set_xlabel('Stock Price at Expiry ($)', fontsize=11, fontweight='medium')
    ax.set_ylabel('Value ($)', fontsize=11, fontweight='medium')
    ax.set_title(f'{option_type} Option Payoff Diagram', fontsize=13, fontweight='bold', pad=15)
    ax.legend(loc='best', framealpha=0.9)
    
    apply_dark_style(ax, fig)
    plt.tight_layout()
    
    st.pyplot(fig)
    plt.close()


def monte_carlo_paths(
    S: float,
    T: float,
    r: float,
    sigma: float,
    n_paths: int = 50,
    n_steps: int = 100
) -> None:
    """
    Display Monte Carlo simulated stock price paths with dark theme.
    """
    dt = T / n_steps
    paths = np.zeros((n_paths, n_steps + 1))
    paths[:, 0] = S
    
    np.random.seed(42)  # For reproducibility in display
    for i in range(1, n_steps + 1):
        z = np.random.standard_normal(n_paths)
        paths[:, i] = paths[:, i - 1] * np.exp(
            (r - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * z
        )
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    time_axis = np.linspace(0, T, n_steps + 1)
    
    for i in range(n_paths):
        ax.plot(time_axis, paths[i], color=COLORS["primary"], alpha=0.15, linewidth=0.8)
    
    # Mean path
    mean_path = np.mean(paths, axis=0)
    ax.plot(time_axis, mean_path, color=COLORS["accent"], linewidth=2.5, label='Mean Path')
    
    # Confidence bands
    std_path = np.std(paths, axis=0)
    ax.fill_between(time_axis, mean_path - 2*std_path, mean_path + 2*std_path,
                   alpha=0.2, color=COLORS["secondary"], label='±2σ Band')
    
    ax.axhline(y=S, color=COLORS["success"], linestyle='--', linewidth=1.5, label=f'Initial S=${S:.2f}')
    
    ax.set_xlabel('Time (years)', fontsize=11, fontweight='medium')
    ax.set_ylabel('Stock Price ($)', fontsize=11, fontweight='medium')
    ax.set_title('Monte Carlo Simulated Stock Price Paths', fontsize=13, fontweight='bold', pad=15)
    ax.legend(loc='best', framealpha=0.9)
    
    apply_dark_style(ax, fig)
    plt.tight_layout()
    
    st.pyplot(fig)
    plt.close()


def portfolio_payoff_diagram(
    portfolio,
    spot_price: float,
    price_range_pct: float = 0.5,
    show_components: bool = False
) -> None:
    """
    Display portfolio payoff diagram with dark theme styling.
    """
    S_min = spot_price * (1 - price_range_pct)
    S_max = spot_price * (1 + price_range_pct)
    S_range = np.linspace(S_min, S_max, 200)
    
    # Total portfolio payoff
    total_payoff = np.array(portfolio.payoff_diagram(S_range))
    
    # Net premium
    net_premium = sum(leg.premium * leg.quantity for leg in portfolio.legs)
    pnl = total_payoff - net_premium * 100  # Per 100 shares
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Component colors from gradient
    component_colors = ['#00D4FF', '#7B2FFF', '#FF6B6B', '#FFD93D', '#00E676', '#FF9F43', '#A55EEA', '#26DE81']
    
    # Plot individual components
    if show_components:
        for i, leg in enumerate(portfolio.legs):
            component_payoff = []
            for S in S_range:
                component_payoff.append(leg.payoff(S))
            pos = "Long" if leg.quantity > 0 else "Short"
            color = component_colors[i % len(component_colors)]
            ax.plot(S_range, component_payoff, '--', alpha=0.6, color=color, linewidth=1.5,
                   label=f'{pos} {leg.option_type} K=${leg.strike:.0f}')
    
    # Plot total P&L
    ax.plot(S_range, pnl, color=COLORS["primary"], linewidth=3, label='Portfolio P&L')
    
    # Fill profit/loss regions
    ax.fill_between(S_range, pnl, 0, where=(pnl > 0), alpha=0.25, color=COLORS["success"])
    ax.fill_between(S_range, pnl, 0, where=(pnl < 0), alpha=0.25, color=COLORS["accent"])
    
    # Reference lines
    ax.axhline(y=0, color=COLORS["text_muted"], linewidth=1, alpha=0.5)
    ax.axvline(x=spot_price, color=COLORS["warning"], linestyle='--', linewidth=1.5, 
               alpha=0.8, label=f'Spot (${spot_price:.2f})')
    
    # Mark strikes
    for leg in portfolio.legs:
        ax.axvline(x=leg.strike, color=COLORS["grid"], linestyle=':', alpha=0.4)
    
    # Find and mark breakeven points
    for i in range(1, len(pnl)):
        if pnl[i-1] * pnl[i] < 0:  # Sign change
            S_be = S_range[i-1] + (S_range[i] - S_range[i-1]) * abs(pnl[i-1]) / (abs(pnl[i-1]) + abs(pnl[i]))
            ax.plot(S_be, 0, 'o', color=COLORS["success"], markersize=10, markeredgecolor=COLORS["text"], markeredgewidth=2)
            ax.annotate(f'BE: ${S_be:.2f}', (S_be, 0), textcoords="offset points",
                       xytext=(0, 15), ha='center', fontsize=9, fontweight='bold', color=COLORS["text"])
    
    ax.set_xlabel('Stock Price at Expiry ($)', fontsize=11, fontweight='medium')
    ax.set_ylabel('Profit/Loss ($)', fontsize=11, fontweight='medium')
    ax.set_title('Portfolio Payoff Diagram', fontsize=13, fontweight='bold', pad=15)
    ax.legend(loc='best', framealpha=0.9)
    
    apply_dark_style(ax, fig)
    plt.tight_layout()
    
    st.pyplot(fig)
    plt.close()


def portfolio_pnl_heatmap(
    portfolio,
    spot_price: float,
    vol_range: tuple = (0.1, 0.5),
    time_range: tuple = (0.01, 1.0)
) -> None:
    """
    Display P&L heatmap across volatility and time dimensions with dark theme.
    """
    from pricing.black_scholes import price as bs_price
    from matplotlib.colors import LinearSegmentedColormap
    
    vols = np.linspace(vol_range[0], vol_range[1], 20)
    times = np.linspace(time_range[0], time_range[1], 20)
    
    pnl_grid = np.zeros((len(vols), len(times)))
    
    for i, vol in enumerate(vols):
        for j, t in enumerate(times):
            portfolio_value = 0
            for leg in portfolio.legs:
                try:
                    days = int(leg.expiry.split()[0])
                    T = max(days / 365 - (time_range[1] - t), 0.001)
                except:
                    T = max(t, 0.001)
                
                price = bs_price(spot_price, leg.strike, T, 0.05, vol, leg.option_type)
                portfolio_value += leg.quantity * price
            
            initial_value = sum(leg.premium * leg.quantity for leg in portfolio.legs)
            pnl_grid[i, j] = (portfolio_value - initial_value) * 100
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Custom colormap for dark theme
    custom_cmap = LinearSegmentedColormap.from_list('pnl', 
        [COLORS["accent"], COLORS["surface"], COLORS["success"]])
    
    im = ax.imshow(pnl_grid, aspect='auto', cmap=custom_cmap, 
                   extent=[times[0], times[-1], vols[0], vols[-1]],
                   origin='lower')
    
    ax.set_xlabel('Time to Expiry (years)', fontsize=11, fontweight='medium')
    ax.set_ylabel('Volatility', fontsize=11, fontweight='medium')
    ax.set_title('Portfolio P&L Heatmap', fontsize=13, fontweight='bold', pad=15)
    
    cbar = plt.colorbar(im, ax=ax, label='P&L ($)')
    cbar.ax.yaxis.label.set_color(COLORS["text"])
    cbar.ax.tick_params(colors=COLORS["text_muted"])
    
    apply_dark_style(ax, fig)
    plt.tight_layout()
    
    st.pyplot(fig)
    plt.close()


def greeks_surface(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str,
    greek: str = "delta"
) -> None:
    """
    Display a Greeks surface plot with dark theme styling.
    """
    from pricing.black_scholes import greeks as bs_greeks
    
    spot_range = np.linspace(S * 0.7, S * 1.3, 30)
    vol_range = np.linspace(0.05, 0.5, 30)
    
    greek_idx = {"delta": 0, "gamma": 1, "vega": 2, "theta": 3}
    idx = greek_idx.get(greek, 0)
    
    greek_surface = np.zeros((len(vol_range), len(spot_range)))
    
    for i, vol in enumerate(vol_range):
        for j, spot in enumerate(spot_range):
            try:
                greeks_vals = bs_greeks(spot, K, T, r, vol, option_type)
                greek_surface[i, j] = greeks_vals[idx]
            except:
                greek_surface[i, j] = 0
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Custom gradient colormap
    from matplotlib.colors import LinearSegmentedColormap
    custom_cmap = LinearSegmentedColormap.from_list('greeks', 
        [COLORS["secondary"], COLORS["surface"], COLORS["primary"]])
    
    im = ax.imshow(greek_surface, aspect='auto', cmap=custom_cmap,
                   extent=[spot_range[0], spot_range[-1], vol_range[0], vol_range[-1]],
                   origin='lower')
    
    ax.axvline(x=K, color=COLORS["warning"], linestyle='--', linewidth=1.5, label='Strike')
    ax.axvline(x=S, color=COLORS["success"], linestyle=':', linewidth=1.5, label='Current Spot')
    
    ax.set_xlabel('Spot Price ($)', fontsize=11, fontweight='medium')
    ax.set_ylabel('Volatility', fontsize=11, fontweight='medium')
    ax.set_title(f'{greek.capitalize()} Surface - {option_type}', fontsize=13, fontweight='bold', pad=15)
    ax.legend(loc='upper right', framealpha=0.9)
    
    cbar = plt.colorbar(im, ax=ax, label=greek.capitalize())
    cbar.ax.yaxis.label.set_color(COLORS["text"])
    cbar.ax.tick_params(colors=COLORS["text_muted"])
    
    apply_dark_style(ax, fig)
    plt.tight_layout()
    
    st.pyplot(fig)
    plt.close()


def volatility_cone(
    prices,
    windows: List[int] = [10, 21, 63, 126, 252]
) -> None:
    """
    Display a volatility cone showing historical vol percentiles.
    """
    import pandas as pd
    
    returns = np.log(prices / prices.shift(1)).dropna()
    
    vol_data = {}
    for window in windows:
        rolling_vol = returns.rolling(window=window).std() * np.sqrt(252)
        vol_data[window] = {
            'min': rolling_vol.min(),
            'p25': rolling_vol.quantile(0.25),
            'median': rolling_vol.quantile(0.50),
            'p75': rolling_vol.quantile(0.75),
            'max': rolling_vol.max(),
            'current': rolling_vol.iloc[-1]
        }
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = range(len(windows))
    
    mins = [vol_data[w]['min'] for w in windows]
    p25s = [vol_data[w]['p25'] for w in windows]
    medians = [vol_data[w]['median'] for w in windows]
    p75s = [vol_data[w]['p75'] for w in windows]
    maxs = [vol_data[w]['max'] for w in windows]
    currents = [vol_data[w]['current'] for w in windows]
    
    ax.fill_between(x, mins, maxs, alpha=0.2, color='blue', label='Min-Max Range')
    ax.fill_between(x, p25s, p75s, alpha=0.4, color='blue', label='25-75 Percentile')
    ax.plot(x, medians, 'b-', linewidth=2, label='Median')
    ax.plot(x, currents, 'ro-', linewidth=2, markersize=8, label='Current')
    
    ax.set_xticks(x)
    ax.set_xticklabels([f'{w}d' for w in windows])
    ax.set_xlabel('Lookback Window', fontsize=12)
    ax.set_ylabel('Annualized Volatility', fontsize=12)
    ax.set_title('Volatility Cone', fontsize=14)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
    # Format y-axis as percentage
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
    
    st.pyplot(fig)
    plt.close()
