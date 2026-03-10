"""
Options Pricing Page - Black-Scholes, Monte Carlo, and Binomial Tree models.
"""

import streamlit as st
import numpy as np
from typing import Tuple, Optional

from pricing.black_scholes import price as bs_price, greeks as bs_greeks
from pricing.monte_carlo import price as mc_price, price_with_ci
from pricing.binomial_tree import price as bt_price
from pricing.implied_volatility import implied_volatility
from utils.plotting import payoff_diagram, monte_carlo_paths
from utils.styles import inject_styles
from data.yahoo import get_stock_info, get_option_chain

st.set_page_config(page_title="Options Pricing", page_icon="Q", layout="wide")
inject_styles()

st.markdown('<h1 style="background: linear-gradient(135deg, #00D4FF, #7B2FFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.5rem;">Options Pricing</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #94A3B8; margin-top: -0.5rem;">Price options using Black-Scholes, Monte Carlo simulation, or Binomial Tree models.</p>', unsafe_allow_html=True)

# Initialize session state for market data
if 'spot_price' not in st.session_state:
    st.session_state.spot_price = 100.0
if 'market_vol' not in st.session_state:
    st.session_state.market_vol = 0.2

# Sidebar - Market Data
st.sidebar.header("Market Data")
ticker = st.sidebar.text_input("Ticker Symbol", value="AAPL", help="Enter a valid stock ticker")

col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("Fetch Data", use_container_width=True):
        with st.spinner("Fetching market data..."):
            try:
                spot, vol = get_stock_info(ticker)
                if spot:
                    st.session_state.spot_price = spot
                    st.session_state.market_vol = vol if vol else 0.2
                    st.sidebar.success(f"{ticker}: ${spot:.2f}")
                else:
                    st.sidebar.error("Could not fetch data")
            except Exception as e:
                st.sidebar.error(f"Error: {str(e)}")

# Sidebar - Option Parameters
st.sidebar.header("Option Parameters")

S = st.sidebar.number_input(
    "Spot Price ($)", 
    min_value=0.01, 
    value=st.session_state.spot_price,
    step=1.0,
    help="Current stock price"
)
K = st.sidebar.number_input(
    "Strike Price ($)", 
    min_value=0.01, 
    value=100.0,
    step=1.0,
    help="Option strike price"
)
T = st.sidebar.number_input(
    "Time to Expiry (years)", 
    min_value=0.001, 
    max_value=10.0,
    value=1.0,
    step=0.01,
    help="Time until option expiration"
)
r = st.sidebar.number_input(
    "Risk-Free Rate", 
    min_value=0.0, 
    max_value=1.0,
    value=0.05,
    step=0.005,
    format="%.3f",
    help="Annual risk-free interest rate"
)
sigma = st.sidebar.number_input(
    "Volatility (σ)", 
    min_value=0.001, 
    max_value=5.0,
    value=st.session_state.market_vol,
    step=0.01,
    format="%.3f",
    help="Annualized volatility"
)
option_type = st.sidebar.selectbox("Option Type", ("Call", "Put"))

# Main content - Tabs for different models
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Black-Scholes", 
    "Monte Carlo", 
    "Binomial Tree", 
    "Greeks", 
    "Implied Volatility"
])

with tab1:
    st.subheader("Black-Scholes Model (European Options)")
    
    try:
        price = bs_price(S, K, T, r, sigma, option_type)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(f"{option_type} Price", f"${price:.4f}")
        with col2:
            intrinsic = max(S - K, 0) if option_type == "Call" else max(K - S, 0)
            st.metric("Intrinsic Value", f"${intrinsic:.4f}")
        with col3:
            time_value = price - intrinsic
            st.metric("Time Value", f"${time_value:.4f}")
        
        st.markdown("---")
        st.markdown("#### Payoff Diagram")
        payoff_diagram(S, K, option_type, premium=price)
        
    except Exception as e:
        st.error(f"Error calculating price: {str(e)}")

with tab2:
    st.subheader("Monte Carlo Simulation (European Options)")
    
    col1, col2 = st.columns(2)
    with col1:
        n_sim = st.slider("Number of Simulations", 1000, 100000, 10000, step=1000)
    with col2:
        show_paths = st.checkbox("Show Sample Paths", value=True)
    
    if st.button("Run Simulation", type="primary"):
        with st.spinner("Running Monte Carlo simulation..."):
            try:
                price, ci_low, ci_high, std_err = price_with_ci(S, K, T, r, sigma, option_type, n_sim)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric(f"{option_type} Price", f"${price:.4f}")
                with col2:
                    st.metric("95% CI Lower", f"${ci_low:.4f}")
                with col3:
                    st.metric("95% CI Upper", f"${ci_high:.4f}")
                with col4:
                    st.metric("Std Error", f"${std_err:.6f}")
                
                bs_ref = bs_price(S, K, T, r, sigma, option_type)
                st.info(f"Black-Scholes Reference: ${bs_ref:.4f} | MC Error: {abs(price - bs_ref):.4f}")
                
                if show_paths:
                    st.markdown("#### Simulated Price Paths")
                    monte_carlo_paths(S, T, r, sigma, n_paths=50, n_steps=100)
                    
            except Exception as e:
                st.error(f"Simulation error: {str(e)}")

with tab3:
    st.subheader("Binomial Tree Model (American Options)")
    
    steps = st.slider("Number of Steps", 10, 500, 100, step=10,
                      help="More steps = higher accuracy but slower computation")
    
    try:
        american_price = bt_price(S, K, T, r, sigma, option_type, steps, american=True)
        european_price = bt_price(S, K, T, r, sigma, option_type, steps, american=False)
        bs_ref = bs_price(S, K, T, r, sigma, option_type)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("American Option", f"${american_price:.4f}")
        with col2:
            st.metric("European Option", f"${european_price:.4f}")
        with col3:
            early_exercise_premium = american_price - european_price
            st.metric("Early Exercise Premium", f"${early_exercise_premium:.4f}")
        
        st.info(f"Black-Scholes Reference: ${bs_ref:.4f} | Tree Error: {abs(european_price - bs_ref):.4f}")
        
        # Show convergence
        if st.checkbox("Show Convergence Analysis"):
            import pandas as pd
            step_range = [10, 25, 50, 100, 200, 300, 500]
            prices = [bt_price(S, K, T, r, sigma, option_type, s, american=True) for s in step_range]
            
            df = pd.DataFrame({
                "Steps": step_range,
                "Price": prices,
                "Error vs BS": [abs(p - bs_ref) for p in prices]
            })
            st.dataframe(df, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error: {str(e)}")

with tab4:
    st.subheader("Option Greeks (Black-Scholes)")
    
    try:
        delta, gamma, vega, theta, rho = bs_greeks(S, K, T, r, sigma, option_type)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Delta (Δ)", f"{delta:.4f}", help="Price sensitivity to underlying")
        with col2:
            st.metric("Gamma (Γ)", f"{gamma:.4f}", help="Delta sensitivity to underlying")
        with col3:
            st.metric("Vega (ν)", f"{vega:.4f}", help="Price sensitivity to volatility")
        with col4:
            st.metric("Theta (Θ)", f"{theta:.4f}", help="Time decay per day")
        with col5:
            st.metric("Rho (ρ)", f"{rho:.4f}", help="Price sensitivity to interest rate")
        
        st.markdown("---")
        st.markdown("#### Greeks Interpretation")
        
        price = bs_price(S, K, T, r, sigma, option_type)
        
        st.markdown(f"""
        | Greek | Value | 1-Unit Change Impact |
        |-------|-------|---------------------|
        | **Delta** | {delta:.4f} | $1 stock move → ${abs(delta):.4f} option change |
        | **Gamma** | {gamma:.4f} | $1 stock move → {gamma:.4f} delta change |
        | **Vega** | {vega:.4f} | 1% vol change → ${vega/100:.4f} option change |
        | **Theta** | {theta:.4f} | 1 day passes → ${theta/365:.4f} option change |
        | **Rho** | {rho:.4f} | 1% rate change → ${rho/100:.4f} option change |
        """)
        
        # Greeks surface plot
        if st.checkbox("Show Greeks Surface"):
            from utils.plotting import greeks_surface
            greek_choice = st.selectbox("Select Greek", ["Delta", "Gamma", "Vega", "Theta"])
            greeks_surface(S, K, T, r, sigma, option_type, greek_choice.lower())
            
    except Exception as e:
        st.error(f"Error calculating Greeks: {str(e)}")

with tab5:
    st.subheader("Implied Volatility Calculator")
    st.markdown("Calculate the implied volatility from a market option price.")
    
    col1, col2 = st.columns(2)
    with col1:
        market_price = st.number_input(
            "Market Option Price ($)", 
            min_value=0.01, 
            value=10.0,
            step=0.1,
            help="Observed market price of the option"
        )
    
    if st.button("Calculate IV", type="primary"):
        with st.spinner("Solving for implied volatility..."):
            try:
                iv = implied_volatility(market_price, S, K, T, r, option_type)
                
                if iv is not None:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Implied Volatility", f"{iv:.2%}")
                    with col2:
                        # Verify by repricing
                        repriced = bs_price(S, K, T, r, iv, option_type)
                        st.metric("Repriced Value", f"${repriced:.4f}")
                    with col3:
                        st.metric("Pricing Error", f"${abs(repriced - market_price):.6f}")
                    
                    # Compare to historical vol
                    if st.session_state.market_vol:
                        diff = iv - st.session_state.market_vol
                        if abs(diff) > 0.05:
                            if diff > 0:
                                st.warning(f"IV ({iv:.1%}) is significantly higher than historical vol ({st.session_state.market_vol:.1%})")
                            else:
                                st.info(f"ℹ️ IV ({iv:.1%}) is lower than historical vol ({st.session_state.market_vol:.1%})")
                else:
                    st.error("Could not converge to a solution. Check that the market price is valid.")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.caption("Options Pricing Engine | Quantitative Finance Tools")
