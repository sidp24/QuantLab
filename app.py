

import streamlit as st
from pricing.black_scholes import price as bs_price, greeks as bs_greeks
from pricing.monte_carlo import price as mc_price
from pricing.binomial_tree import price as bt_price
from utils.plotting import payoff_diagram, monte_carlo_paths
from data.yahoo import get_stock_info, get_option_chain
from portfolio import OptionLeg, Portfolio
import numpy as np

st.title("Options Pricing & Monte Carlo Engine")

# Ticker input and auto-population
st.sidebar.header("Market Data")
ticker = st.sidebar.text_input("Enter Ticker (e.g., AAPL)", value="AAPL")
auto_populate = st.sidebar.button("Fetch Market Data")

spot, vol = None, None
option_chain = None
if auto_populate and ticker:
	spot, vol = get_stock_info(ticker)
	option_chain = get_option_chain(ticker)
	st.sidebar.success(f"Fetched data for {ticker}")

st.sidebar.header("Option Parameters")
S = st.sidebar.number_input("Spot Price (S)", value=spot if spot else 100.0)
K = st.sidebar.number_input("Strike Price (K)", value=100.0)
T = st.sidebar.number_input("Time to Maturity (T, in years)", value=1.0)
r = st.sidebar.number_input("Risk-Free Rate (r)", value=0.05)
sigma = st.sidebar.number_input("Volatility (sigma)", value=vol if vol else 0.2)
option_type = st.sidebar.selectbox("Option Type", ("Call", "Put"))

model = st.sidebar.selectbox(
	"Pricing Model",
	("Black-Scholes (European)", "Monte Carlo (European)", "Binomial Tree (American)", "Show Greeks", "Portfolio", "Volatility Forecasting")
)

if model == "Black-Scholes (European)":
	price = bs_price(S, K, T, r, sigma, option_type)
	st.subheader(f"Black-Scholes {option_type} Price: {price:.2f}")
elif model == "Monte Carlo (European)":
	price = mc_price(S, K, T, r, sigma, option_type)
	st.subheader(f"Monte Carlo {option_type} Price: {price:.2f}")
	st.markdown("#### Monte Carlo Simulated Paths")
	monte_carlo_paths(S, T, r, sigma)
elif model == "Binomial Tree (American)":
	steps = st.sidebar.slider("Binomial Tree Steps", min_value=50, max_value=500, value=100, step=10)
	price = bt_price(S, K, T, r, sigma, option_type, steps)
	st.subheader(f"Binomial Tree {option_type} Price: {price:.2f}")
elif model == "Show Greeks":
	delta, gamma, vega, theta, rho = bs_greeks(S, K, T, r, sigma, option_type)
	st.subheader("Greeks (Black-Scholes)")
	st.write(f"Delta: {delta:.4f}")
	st.write(f"Gamma: {gamma:.4f}")
	st.write(f"Vega: {vega:.4f}")
	st.write(f"Theta: {theta:.4f}")
	st.write(f"Rho: {rho:.4f}")
elif model == "Portfolio":
	st.subheader("Option Portfolio Builder")
	if 'portfolio' not in st.session_state:
		st.session_state['portfolio'] = Portfolio()
	portfolio = st.session_state['portfolio']
	with st.form("Add Option Leg"):
		leg_type = st.selectbox("Leg Type", ("Call", "Put"))
		leg_strike = st.number_input("Leg Strike", value=K)
		leg_expiry = st.text_input("Leg Expiry", value="T+1Y")
		leg_qty = st.number_input("Quantity", value=1, step=1)
		submitted = st.form_submit_button("Add Leg")
		if submitted:
			leg = OptionLeg(leg_type, leg_strike, leg_expiry, leg_qty)
			portfolio.add_leg(leg)
			st.success("Leg added to portfolio.")
	st.markdown("### Portfolio Legs")
	for idx, leg in enumerate(portfolio.legs):
		st.write(f"{idx+1}. {leg.option_type} | Strike: {leg.strike} | Expiry: {leg.expiry} | Qty: {leg.quantity}")
		if st.button(f"Remove Leg {idx+1}"):
			portfolio.remove_leg(idx)
			st.experimental_rerun()
	st.markdown("### Combined Payoff Diagram")
	S_range = np.linspace(S * 0.5, S * 1.5, 100)
	payoff = portfolio.payoff_diagram(S_range)
	import matplotlib.pyplot as plt
	fig, ax = plt.subplots()
	ax.plot(S_range, payoff, label='Portfolio Payoff')
	ax.set_xlabel('Stock Price at Expiry')
	ax.set_ylabel('Payoff')
	ax.legend()
	st.pyplot(fig)

elif model == "Volatility Forecasting":
	st.subheader("Volatility Forecasting (ML)")
	from ml.vol_forecast import fetch_price_history, compute_features, train_vol_model, forecast_vol
	ticker_ml = st.text_input("Enter Ticker for ML Forecast", value=ticker)
	period = st.selectbox("History Period", ("6mo", "1y", "2y", "5y"), index=2)
	if st.button("Train Volatility Model"):
		prices = fetch_price_history(ticker_ml, period=period)
		# Convert DataFrame to Series if needed
		import pandas as pd
		if isinstance(prices, pd.DataFrame):
			prices = prices.iloc[:, 0]
		features = compute_features(prices)
		model, mse = train_vol_model(features)
		if model is not None and mse is not None and not features.empty:
			st.success(f"Model trained. Test MSE: {mse:.6f}")
			st.session_state['vol_model'] = model
			st.session_state['features'] = features
		else:
			st.warning("Not enough data to train the model. Please select a longer period or different ticker.")
			st.session_state['vol_model'] = None
			st.session_state['features'] = None
	if 'vol_model' in st.session_state and 'features' in st.session_state:
		if st.session_state['vol_model'] is not None and st.session_state['features'] is not None and not st.session_state['features'].empty:
			recent_ret = st.session_state['features']['ret'].iloc[-1]
			pred_vol = forecast_vol(st.session_state['vol_model'], [recent_ret])
			st.write(f"Predicted Volatility (next period): {pred_vol:.4f}")
			st.line_chart(st.session_state['features']['vol'], use_container_width=True)
		else:
			st.info("No volatility data or prediction available for the selected ticker and period.")

st.markdown("---")
st.markdown("#### Payoff Diagram")
payoff_diagram(S, K, option_type)

st.markdown("---")
st.markdown("Developed for quant finance & stochastic processes exploration.")
