# QuantLab - Options Pricing & Quantitative Finance Platform

A comprehensive web application for options pricing, portfolio analysis, and volatility forecasting, built for quantitative finance exploration and education.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Features

### Options Pricing Models
- **Black-Scholes** - Closed-form European option pricing with full Greeks
- **Monte Carlo Simulation** - Path-dependent valuation with confidence intervals
- **Binomial Tree** - American option pricing with early exercise support
- **Implied Volatility** - Newton-Raphson & Brent solver for IV calculation

### Portfolio Builder
- Build multi-leg option strategies (spreads, straddles, condors)
- **10+ Pre-built strategy templates** including:
  - Bull/Bear Spreads
  - Long/Short Straddles & Strangles
  - Iron Condors
  - Butterfly Spreads
  - Covered Calls & Protective Puts
- Combined payoff diagrams with breakeven analysis
- Portfolio Greeks aggregation
- P&L scenario analysis

### Option Chain Browser
- Real-time data from Yahoo Finance
- Browse calls and puts by expiration
- Volume and open interest analysis
- Put/Call ratio indicators
- Implied volatility smile visualization

### Volatility Forecasting (ML)
- **Random Forest** regression model
- **GARCH(1,1)** statistical modeling (optional)
- Ensemble forecasting
- Volatility regime detection
- Feature importance analysis

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/quantlab.git
cd quantlab

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Application

```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501`

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t quantlab .
docker run -p 8501:8501 quantlab
```

## Project Structure

```
quantlab/
├── app.py                 # Main Streamlit app (home page)
├── pages/                 # Multi-page app structure
│   ├── 1_Options_Pricing.py
│   ├── 2_Portfolio_Builder.py
│   ├── 3_Option_Chain.py
│   └── 4_Volatility_Forecast.py
├── pricing/               # Option pricing models
│   ├── black_scholes.py   # BS pricing and Greeks
│   ├── monte_carlo.py     # MC simulation (European, Asian, Barrier)
│   ├── binomial_tree.py   # CRR binomial tree (American support)
│   └── implied_volatility.py
├── data/                  # Market data
│   └── yahoo.py           # Yahoo Finance API with caching
├── ml/                    # Machine learning models
│   └── vol_forecast.py    # RF & GARCH volatility forecasting
├── utils/                 # Utilities
│   └── plotting.py        # Visualization functions
├── portfolio.py           # Portfolio and strategy analysis
├── tests/                 # Unit tests
│   ├── test_pricing.py
│   └── test_portfolio.py
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Usage Examples

### Price a Call Option

```python
from pricing.black_scholes import price, greeks

# Parameters
S = 100     # Stock price
K = 105     # Strike
T = 0.5     # 6 months to expiry
r = 0.05    # Risk-free rate
sigma = 0.2 # Volatility

call_price = price(S, K, T, r, sigma, "Call")
delta, gamma, vega, theta, rho = greeks(S, K, T, r, sigma, "Call")
```

### Calculate Implied Volatility

```python
from pricing.implied_volatility import implied_volatility

market_price = 8.50
iv = implied_volatility(market_price, S=100, K=100, T=1.0, r=0.05, option_type="Call")
print(f"Implied Volatility: {iv:.2%}")
```

### Build an Iron Condor

```python
from portfolio import Portfolio, OptionLeg, STRATEGY_TEMPLATES

portfolio = Portfolio()

# Using template
template = STRATEGY_TEMPLATES["Iron Condor"]
for leg in template["legs"]:
    portfolio.add_leg(OptionLeg(
        option_type=leg["type"],
        strike=100 * leg["strike_pct"],
        expiry="30 days",
        quantity=leg["qty"],
        premium=2.0
    ))

# Calculate metrics
metrics = portfolio.calculate_metrics(spot_price=100)
print(f"Max Profit: ${metrics['max_profit']:.2f}")
print(f"Max Loss: ${metrics['max_loss']:.2f}")
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=pricing --cov=portfolio --cov-report=html
```

## Configuration

### Streamlit Config (`.streamlit/config.toml`)

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#FFFFFF"

[server]
port = 8501
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `STREAMLIT_SERVER_PORT` | Server port | 8501 |
| `STREAMLIT_SERVER_ADDRESS` | Server address | localhost |

## Technical Details

### Pricing Models

| Model | Type | Features |
|-------|------|----------|
| Black-Scholes | Analytical | European options, full Greeks |
| Monte Carlo | Simulation | European, Asian, Barrier options |
| Binomial Tree | Numerical | American options, early exercise |

### Greeks Implemented

- **Delta (Δ)** - Price sensitivity to underlying
- **Gamma (Γ)** - Delta sensitivity to underlying
- **Vega (ν)** - Price sensitivity to volatility
- **Theta (Θ)** - Time decay
- **Rho (ρ)** - Interest rate sensitivity

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Market data provided by [Yahoo Finance](https://finance.yahoo.com)
- Built with [Streamlit](https://streamlit.io)
- Options theory based on Hull's "Options, Futures, and Other Derivatives"

---

**Disclaimer**: This software is for educational purposes only. Do not use for actual trading decisions without proper validation. Past performance does not guarantee future results.

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
