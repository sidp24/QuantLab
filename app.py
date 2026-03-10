
"""
QuantLab - Options Pricing & Quantitative Finance Platform
Main application entry point and home page.
"""

import streamlit as st
from utils.styles import inject_styles, create_stat_card, create_feature_card

# Page configuration
st.set_page_config(
    page_title="QuantLab",
    page_icon="Q",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject global styles
inject_styles()

# Main header
st.markdown("""
<div class="quantlab-header">
    <div class="quantlab-logo">QuantLab</div>
    <div class="quantlab-tagline">Quantitative Finance & Options Analytics</div>
</div>
""", unsafe_allow_html=True)

# Stats row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(create_stat_card("3", "Pricing Models"), unsafe_allow_html=True)
with col2:
    st.markdown(create_stat_card("5", "Greeks"), unsafe_allow_html=True)
with col3:
    st.markdown(create_stat_card("10+", "Strategies"), unsafe_allow_html=True)
with col4:
    st.markdown(create_stat_card("2", "ML Models"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Feature cards
st.markdown("### Explore Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown(create_feature_card(
        "pricing",
        "Options Pricing",
        "Price options with Black-Scholes, Monte Carlo simulation, and Binomial Trees. Calculate Greeks and implied volatility with precision."
    ), unsafe_allow_html=True)
    
    st.markdown(create_feature_card(
        "portfolio",
        "Portfolio Builder",
        "Build multi-leg strategies with pre-built templates. Analyze combined payoffs, breakeven points, and P&L scenarios."
    ), unsafe_allow_html=True)

with col2:
    st.markdown(create_feature_card(
        "chain",
        "Option Chain Browser",
        "Real-time option chains from Yahoo Finance. Analyze volume, open interest, and visualize the IV smile."
    ), unsafe_allow_html=True)
    
    st.markdown(create_feature_card(
        "forecast",
        "Volatility Forecast",
        "Machine learning predictions with Random Forest and GARCH models. Detect volatility regimes and trends."
    ), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Quick start guide
st.markdown("### Quick Start")

st.markdown("""
<div class="glass-card">
    <p style="color: var(--text); margin: 0; line-height: 1.8;">
        <strong style="color: var(--primary);">1.</strong> Navigate using the sidebar to explore different tools<br>
        <strong style="color: var(--primary);">2.</strong> Enter market parameters or fetch live data from Yahoo Finance<br>
        <strong style="color: var(--primary);">3.</strong> Analyze results with interactive charts and metrics<br>
        <strong style="color: var(--primary);">4.</strong> Build and backtest option strategies with the portfolio builder
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("""
<div style="text-align: center; padding: 1rem 0;">
    <div style="font-size: 1.5rem; font-weight: 700; background: linear-gradient(135deg, #00D4FF, #7B2FFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">QuantLab</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div class="sidebar-header">Navigation</div>', unsafe_allow_html=True)

st.sidebar.page_link("pages/1_Options_Pricing.py", label="Options Pricing", use_container_width=True)
st.sidebar.page_link("pages/2_Portfolio_Builder.py", label="Portfolio Builder", use_container_width=True)
st.sidebar.page_link("pages/3_Option_Chain.py", label="Option Chain", use_container_width=True)
st.sidebar.page_link("pages/4_Volatility_Forecast.py", label="Vol Forecast", use_container_width=True)

st.sidebar.markdown('<div class="sidebar-header">About</div>', unsafe_allow_html=True)

st.sidebar.markdown("""
<div style="color: var(--text-muted); font-size: 0.85rem; line-height: 1.6;">
    Built for quantitative analysis and options trading research. 
    Powered by Python, NumPy, and Streamlit.
</div>
""", unsafe_allow_html=True)
