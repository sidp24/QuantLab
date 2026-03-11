import streamlit as st
import numpy as np
import pandas as pd
from typing import List, Dict, Optional

from portfolio import OptionLeg, Portfolio, STRATEGY_TEMPLATES
from pricing.black_scholes import price as bs_price, greeks as bs_greeks
from utils.plotting import portfolio_payoff_diagram, portfolio_pnl_heatmap
from utils.styles import inject_styles

st.set_page_config(page_title="Portfolio Builder", page_icon="Q", layout="wide")
inject_styles()

st.markdown('<h1 style="background: linear-gradient(135deg, #00D4FF, #7B2FFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.5rem;">Portfolio Builder</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #94A3B8; margin-top: -0.5rem;">Build multi-leg option strategies and analyze payoff profiles.</p>', unsafe_allow_html=True)

# Initialize session state
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = Portfolio()

portfolio = st.session_state.portfolio

# Sidebar configuration
st.sidebar.header("Configuration")
spot_price = st.sidebar.number_input("Underlying Price ($)", min_value=0.01, value=100.0, step=1.0)
risk_free_rate = st.sidebar.number_input("Risk-Free Rate", min_value=0.0, max_value=0.5, value=0.05, step=0.005)
volatility = st.sidebar.number_input("Volatility (σ)", min_value=0.01, max_value=2.0, value=0.20, step=0.01)

# Main content
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Add Option Leg")

    # Strategy Templates
    st.markdown("#### Quick Templates")
    template_name = st.selectbox(
        "Load Strategy Template",
        ["Custom"] + list(STRATEGY_TEMPLATES.keys()),
        help="Pre-built strategies to get started"
    )

    if template_name != "Custom":
        if st.button("Load Template", use_container_width=True):
            template = STRATEGY_TEMPLATES[template_name]
            st.session_state.portfolio = Portfolio()
            for leg_data in template["legs"]:
                strike = spot_price * leg_data["strike_pct"]
                leg = OptionLeg(
                    option_type=leg_data["type"],
                    strike=strike,
                    expiry="30 days",
                    quantity=leg_data["qty"],
                    premium=bs_price(spot_price, strike, 30/365, risk_free_rate, volatility, leg_data["type"])
                )
                st.session_state.portfolio.add_leg(leg)
            st.success(f"Loaded: {template_name}")
            st.rerun()

    st.markdown("---")
    st.markdown("#### Manual Entry")

    with st.form("add_leg_form", clear_on_submit=True):
        leg_type = st.selectbox("Type", ["Call", "Put"])
        leg_strike = st.number_input("Strike ($)", min_value=0.01, value=spot_price, step=1.0)
        leg_expiry = st.selectbox("Expiry", ["7 days", "14 days", "30 days", "60 days", "90 days", "180 days", "365 days"])
        leg_qty = st.number_input("Quantity", min_value=-100, max_value=100, value=1, step=1,
                                   help="Positive = Long, Negative = Short")

        # Calculate premium
        days = int(leg_expiry.split()[0])
        T = days / 365
        premium = bs_price(spot_price, leg_strike, T, risk_free_rate, volatility, leg_type)
        st.info(f"Theoretical Premium: ${premium:.2f}")

        custom_premium = st.number_input("Premium (override)", min_value=0.0, value=premium, step=0.1)

        submitted = st.form_submit_button("Add Leg", use_container_width=True, type="primary")
        if submitted:
            leg = OptionLeg(leg_type, leg_strike, leg_expiry, leg_qty, custom_premium)
            portfolio.add_leg(leg)
            st.success("Leg added!")
            st.rerun()

    if st.button("Clear Portfolio", use_container_width=True):
        st.session_state.portfolio = Portfolio()
        st.rerun()

with col2:
    st.subheader("Portfolio Legs")

    if portfolio.legs:
        # Create DataFrame for display
        legs_data = []
        for i, leg in enumerate(portfolio.legs):
            position = "Long" if leg.quantity > 0 else "Short"
            cost = leg.premium * abs(leg.quantity) * 100  # per contract
            legs_data.append({
                "#": i + 1,
                "Position": position,
                "Type": leg.option_type,
                "Strike": f"${leg.strike:.2f}",
                "Expiry": leg.expiry,
                "Qty": leg.quantity,
                "Premium": f"${leg.premium:.2f}",
                "Cost/Credit": f"${cost:.2f}" if leg.quantity > 0 else f"(${abs(cost):.2f})"
            })

        df = pd.DataFrame(legs_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Remove leg buttons
        cols = st.columns(len(portfolio.legs))
        for i, col in enumerate(cols):
            with col:
                if st.button(f"Remove #{i+1}", key=f"remove_{i}"):
                    portfolio.remove_leg(i)
                    st.rerun()

        # Summary metrics
        st.markdown("---")
        st.markdown("#### Portfolio Summary")

        metrics = portfolio.calculate_metrics(spot_price, risk_free_rate, volatility)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Net Premium", f"${metrics['net_premium']:.2f}",
                     help="Total premium paid/received")
        with col2:
            st.metric("Max Profit", f"${metrics['max_profit']:.2f}" if metrics['max_profit'] != float('inf') else "Unlimited")
        with col3:
            st.metric("Max Loss", f"${metrics['max_loss']:.2f}" if metrics['max_loss'] != float('-inf') else "Unlimited")
        with col4:
            if metrics['breakeven']:
                st.metric("Breakeven", f"${metrics['breakeven'][0]:.2f}")
            else:
                st.metric("Breakeven", "N/A")

        # Portfolio Greeks
        st.markdown("#### Portfolio Greeks")
        greeks = portfolio.calculate_portfolio_greeks(spot_price, risk_free_rate, volatility)

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Delta", f"{greeks['delta']:.4f}")
        with col2:
            st.metric("Gamma", f"{greeks['gamma']:.4f}")
        with col3:
            st.metric("Vega", f"{greeks['vega']:.4f}")
        with col4:
            st.metric("Theta", f"{greeks['theta']:.4f}")
        with col5:
            st.metric("Rho", f"{greeks['rho']:.4f}")

    else:
        st.info("Add option legs to build your portfolio.")

# Payoff Analysis Section
st.markdown("---")
st.subheader("Payoff Analysis")

if portfolio.legs:
    tab1, tab2, tab3 = st.tabs(["Payoff Diagram", "P&L Scenarios", "Risk Analysis"])

    with tab1:
        col1, col2 = st.columns([3, 1])
        with col2:
            price_range = st.slider(
                "Price Range (%)",
                min_value=20, max_value=100, value=50,
                help="Range around spot price to analyze"
            )
            show_components = st.checkbox("Show Individual Legs", value=False)

        with col1:
            portfolio_payoff_diagram(
                portfolio,
                spot_price,
                price_range_pct=price_range/100,
                show_components=show_components
            )

    with tab2:
        st.markdown("#### P&L at Different Price Levels")

        # Generate scenarios
        price_points = [spot_price * mult for mult in [0.7, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2, 1.3]]
        scenarios = []

        for price in price_points:
            payoff = portfolio.get_payoff(price)
            net_premium = sum(leg.premium * leg.quantity for leg in portfolio.legs)
            pnl = payoff - net_premium * 100  # Convert to per-share
            pct_change = (price - spot_price) / spot_price * 100

            scenarios.append({
                "Stock Price": f"${price:.2f}",
                "% Change": f"{pct_change:+.1f}%",
                "Payoff": f"${payoff:.2f}",
                "Net P&L": f"${pnl:.2f}",
                "P&L %": f"{pnl / abs(net_premium * 100) * 100:+.1f}%" if net_premium != 0 else "N/A"
            })

        st.dataframe(pd.DataFrame(scenarios), use_container_width=True, hide_index=True)

    with tab3:
        st.markdown("#### Risk Metrics")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Position Characteristics**")

            net_delta = greeks['delta']
            if abs(net_delta) < 0.1:
                st.success("Delta Neutral (low directional risk)")
            elif net_delta > 0.5:
                st.warning("Bullish Position (positive delta)")
            elif net_delta < -0.5:
                st.warning("Bearish Position (negative delta)")

            if greeks['gamma'] > 0:
                st.info("Long Gamma (benefits from volatility)")
            else:
                st.info("Short Gamma (hurt by large moves)")

            if greeks['theta'] < 0:
                st.warning(f"Time Decay: ${abs(greeks['theta']):.2f}/day")
            else:
                st.success(f"Time Premium: ${greeks['theta']:.2f}/day")

        with col2:
            st.markdown("**Stress Test**")

            stress_scenarios = {
                "Stock +10%": spot_price * 1.10,
                "Stock -10%": spot_price * 0.90,
                "Stock +20%": spot_price * 1.20,
                "Stock -20%": spot_price * 0.80,
            }

            net_premium = sum(leg.premium * leg.quantity for leg in portfolio.legs)

            stress_results = []
            for scenario, price in stress_scenarios.items():
                payoff = portfolio.get_payoff(price)
                pnl = payoff - net_premium * 100
                stress_results.append({
                    "Scenario": scenario,
                    "P&L": f"${pnl:.2f}"
                })

            st.dataframe(pd.DataFrame(stress_results), use_container_width=True, hide_index=True)

    # Export functionality
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📥 Export to CSV"):
            csv_data = df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv_data,
                file_name="portfolio.csv",
                mime="text/csv"
            )

else:
    st.info("Build a portfolio to see payoff analysis.")

# Footer
st.markdown("---")
st.caption("Portfolio Builder | Quantitative Finance Tools")
