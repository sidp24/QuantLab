"""
Yahoo Finance Data Module
Fetch market data using yfinance with caching and error handling.
"""

import yfinance as yf
import streamlit as st
import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict
from datetime import datetime, timedelta


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_info(ticker: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Fetch current stock price and historical volatility.
    
    Parameters
    ----------
    ticker : str
        Stock ticker symbol
        
    Returns
    -------
    tuple
        (spot_price, historical_volatility) or (None, None) on error
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get spot price
        spot = info.get('regularMarketPrice') or info.get('currentPrice')
        
        if spot is None:
            # Try to get from recent history
            hist = stock.history(period="5d")
            if not hist.empty:
                spot = hist['Close'].iloc[-1]
        
        # Calculate historical volatility from recent data
        hist = stock.history(period="1y")
        if not hist.empty and len(hist) > 20:
            returns = np.log(hist['Close'] / hist['Close'].shift(1)).dropna()
            vol = returns.std() * np.sqrt(252)  # Annualized
        else:
            vol = None
        
        return spot, vol
        
    except Exception as e:
        st.warning(f"Error fetching data for {ticker}: {str(e)}")
        return None, None


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_option_chain(ticker: str) -> Optional[Dict]:
    """
    Fetch full option chain for a ticker.
    
    Parameters
    ----------
    ticker : str
        Stock ticker symbol
        
    Returns
    -------
    dict or None
        Dictionary with expiry dates as keys, containing calls and puts DataFrames
    """
    try:
        stock = yf.Ticker(ticker)
        expiries = stock.options
        
        if not expiries:
            return None
        
        chains = {}
        for expiry in expiries:
            try:
                opt_chain = stock.option_chain(expiry)
                chains[expiry] = {
                    'calls': opt_chain.calls,
                    'puts': opt_chain.puts
                }
            except Exception:
                continue
        
        return chains if chains else None
        
    except Exception as e:
        st.warning(f"Error fetching option chain for {ticker}: {str(e)}")
        return None


@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_historical_data(
    ticker: str,
    period: str = "1y",
    interval: str = "1d"
) -> Optional[pd.DataFrame]:
    """
    Fetch historical price data.
    
    Parameters
    ----------
    ticker : str
        Stock ticker symbol
    period : str
        Data period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    interval : str
        Data interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        
    Returns
    -------
    DataFrame or None
        OHLCV data indexed by date
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval)
        
        if hist.empty:
            return None
        
        return hist
        
    except Exception as e:
        st.warning(f"Error fetching historical data for {ticker}: {str(e)}")
        return None


def calculate_realized_volatility(
    prices: pd.Series,
    window: int = 21,
    annualize: bool = True
) -> pd.Series:
    """
    Calculate rolling realized volatility.
    
    Parameters
    ----------
    prices : Series
        Price series
    window : int
        Rolling window in days
    annualize : bool
        If True, annualize the volatility (multiply by sqrt(252))
        
    Returns
    -------
    Series
        Rolling volatility
    """
    returns = np.log(prices / prices.shift(1))
    vol = returns.rolling(window=window).std()
    
    if annualize:
        vol = vol * np.sqrt(252)
    
    return vol


def get_risk_free_rate() -> float:
    """
    Fetch current risk-free rate (3-month Treasury).
    
    Returns
    -------
    float
        Current risk-free rate as decimal
    """
    try:
        # Use 3-month Treasury rate
        treasury = yf.Ticker("^IRX")
        hist = treasury.history(period="5d")
        
        if not hist.empty:
            rate = hist['Close'].iloc[-1] / 100  # Convert from percentage
            return rate
        
        return 0.05  # Default fallback
        
    except Exception:
        return 0.05  # Default fallback


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_company_info(ticker: str) -> Optional[Dict]:
    """
    Fetch company information.
    
    Returns
    -------
    dict or None
        Company information dictionary
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return {
            'name': info.get('longName', ticker),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('forwardPE', 0),
            'dividend_yield': info.get('dividendYield', 0),
            'beta': info.get('beta', 1),
            '52w_high': info.get('fiftyTwoWeekHigh', 0),
            '52w_low': info.get('fiftyTwoWeekLow', 0),
            'avg_volume': info.get('averageVolume', 0)
        }
        
    except Exception:
        return None


def get_earnings_dates(ticker: str) -> Optional[pd.DataFrame]:
    """
    Fetch upcoming and past earnings dates.
    
    Returns
    -------
    DataFrame or None
        Earnings dates with estimates
    """
    try:
        stock = yf.Ticker(ticker)
        earnings = stock.earnings_dates
        
        if earnings is not None and not earnings.empty:
            return earnings
        
        return None
        
    except Exception:
        return None
