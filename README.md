# Options Pricing & Monte Carlo Engine

A web app for options pricing, portfolio analysis, and volatility forecasting, built for quant finance and stochastic processes exploration.

## Features
- **Options Pricing Models:**
  - Black-Scholes (European)
  - Monte Carlo Simulation (European)
  - Binomial Tree (American)
  - Greeks calculation
- **Portfolio & Strategy Analysis:**
  - Build multi-leg option portfolios (spreads, straddles, etc.)
  - Combined payoff diagrams
- **Real Market Data Integration:**
  - Fetch live prices and option chains using Yahoo Finance
  - Auto-populate parameters from ticker
- **Volatility Forecasting (ML):**
  - Train a machine learning model to forecast future volatility
  - Visualize historical and predicted volatility
- **Interactive UI:**
  - Streamlit-based web interface
  - Matplotlib/Plotly charts
  - User feedback and error handling

## Getting Started
1. **Clone the repository**
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   Or manually:
   ```bash
   pip install streamlit numpy scipy matplotlib yfinance pandas scikit-learn
   ```
3. **Run the app**
   ```bash
   streamlit run app.py
   ```
4. **Open in browser**
   Visit `http://localhost:8501`

## Project Structure
```
pricing/           # Option pricing models (Black-Scholes, Monte Carlo, Binomial Tree)
data/              # Market data fetching (Yahoo Finance)
utils/             # Plotting and shared utilities
ml/                # Machine learning models (volatility forecasting)
portfolio.py       # Portfolio and strategy analysis
app.py             # Main Streamlit app
```

## Usage
- Select pricing model and input parameters in the sidebar
- For market data, enter a ticker and fetch live data
- Build option portfolios and view combined payoffs
- Use Volatility Forecasting to train and predict future volatility

## Requirements
- Python 3.8+
- Internet connection (for market data)

## License
MIT

## Author
Developed by Siddharth Paul
