"""
Machine Learning Volatility Forecasting Module
Implements Random Forest and GARCH models for volatility prediction.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import yfinance as yf
from typing import Tuple, Optional, Dict, List, Any
import warnings


def fetch_price_history(
    ticker: str,
    period: str = '2y'
) -> Optional[pd.Series]:
    """
    Fetch historical price data for volatility analysis.
    
    Parameters
    ----------
    ticker : str
        Stock ticker symbol
    period : str
        Data period (e.g., '6mo', '1y', '2y', '5y')
        
    Returns
    -------
    Series or None
        Closing prices indexed by date
    """
    try:
        data = yf.download(ticker, period=period, progress=False)
        
        if data.empty:
            return None
        
        # Extract Close column
        if isinstance(data, pd.DataFrame):
            if 'Close' in data.columns:
                return data['Close'].dropna()
            elif len(data.columns) > 0:
                return data.iloc[:, 0].dropna()
        elif isinstance(data, pd.Series):
            return data.dropna()
        
        return None
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


def compute_features(
    prices: pd.Series,
    vol_window: int = 21,
    feature_windows: List[int] = [5, 10, 21, 63]
) -> pd.DataFrame:
    """
    Compute features for volatility prediction.
    
    Parameters
    ----------
    prices : Series
        Price series
    vol_window : int
        Window for target volatility calculation
    feature_windows : list
        Windows for feature calculations
        
    Returns
    -------
    DataFrame
        Features DataFrame with columns: vol (target), ret, and various technical indicators
    """
    if prices is None or not isinstance(prices, pd.Series) or prices.empty:
        return pd.DataFrame(columns=['vol', 'ret'])
    
    if len(prices) < max(feature_windows) + vol_window + 1:
        return pd.DataFrame(columns=['vol', 'ret'])
    
    # Log returns
    returns = np.log(prices / prices.shift(1))
    
    # Target: forward-looking realized volatility
    rolling_vol = returns.rolling(window=vol_window).std() * np.sqrt(252)
    
    features = pd.DataFrame(index=prices.index)
    features['vol'] = rolling_vol
    features['ret'] = returns
    
    # Lagged returns
    for lag in [1, 2, 3, 5]:
        features[f'ret_lag_{lag}'] = returns.shift(lag)
    
    # Rolling volatility features (lagged to avoid look-ahead)
    for window in feature_windows:
        features[f'vol_{window}d'] = returns.rolling(window=window).std().shift(1) * np.sqrt(252)
    
    # Rolling mean returns
    for window in feature_windows:
        features[f'ret_mean_{window}d'] = returns.rolling(window=window).mean().shift(1)
    
    # Rolling skewness and kurtosis
    features['skew_21d'] = returns.rolling(window=21).skew().shift(1)
    features['kurt_21d'] = returns.rolling(window=21).kurt().shift(1)
    
    # Absolute returns (proxy for volatility)
    features['abs_ret'] = np.abs(returns).shift(1)
    features['abs_ret_5d'] = np.abs(returns).rolling(5).mean().shift(1)
    
    # Range-based volatility (Parkinson)
    if 'High' in prices.index.names or hasattr(prices, 'High'):
        pass  # Would add range-based vol here if OHLC data available
    
    # Remove rows with NaN
    features = features.dropna()
    
    return features


def train_vol_model(
    features: pd.DataFrame,
    test_size: float = 0.2,
    n_estimators: int = 100,
    return_importance: bool = False
) -> Tuple[Optional[RandomForestRegressor], Optional[float], Optional[Dict]]:
    """
    Train a Random Forest model for volatility forecasting.
    
    Parameters
    ----------
    features : DataFrame
        Features DataFrame with 'vol' as target column
    test_size : float
        Proportion of data for testing
    n_estimators : int
        Number of trees in the forest
    return_importance : bool
        Whether to return feature importance
        
    Returns
    -------
    tuple
        (model, mse, feature_importance) or (None, None, None) on error
    """
    if features is None or len(features) < 30:
        return (None, None, None) if return_importance else (None, None)
    
    # Separate features and target
    feature_cols = [c for c in features.columns if c != 'vol']
    X = features[feature_cols].values
    y = features['vol'].values
    
    # Use time-series aware split (don't shuffle)
    split_idx = int(len(X) * (1 - test_size))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    # Train model
    model = RandomForestRegressor(
        n_estimators=n_estimators,
        max_depth=10,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1
    )
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    
    # Feature importance
    importance = None
    if return_importance:
        importance = dict(zip(feature_cols, model.feature_importances_))
    
    if return_importance:
        return (model, mse, importance)
    return (model, mse)


def forecast_vol(
    model: RandomForestRegressor,
    recent_features: List[float]
) -> float:
    """
    Generate volatility forecast using trained model.
    
    Parameters
    ----------
    model : RandomForestRegressor
        Trained model
    recent_features : list
        Recent feature values (should match training features)
        
    Returns
    -------
    float
        Predicted volatility
    """
    return model.predict(np.array(recent_features).reshape(1, -1))[0]


def calculate_garch_forecast(
    returns: pd.Series,
    p: int = 1,
    q: int = 1
) -> Optional[Dict]:
    """
    Fit GARCH(p,q) model and generate forecasts.
    
    Parameters
    ----------
    returns : Series
        Log returns series
    p : int
        GARCH order (lags of squared residuals)
    q : int
        GARCH order (lags of variance)
        
    Returns
    -------
    dict or None
        GARCH parameters and forecasts
    """
    try:
        from arch import arch_model
        
        # Scale returns for numerical stability
        returns_scaled = returns * 100
        
        # Fit GARCH model
        model = arch_model(returns_scaled, vol='Garch', p=p, q=q, rescale=False)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = model.fit(disp='off')
        
        # Extract parameters
        omega = result.params.get('omega', 0)
        alpha = result.params.get('alpha[1]', 0)
        beta = result.params.get('beta[1]', 0)
        
        # Calculate long-run volatility
        if alpha + beta < 1:
            long_run_var = omega / (1 - alpha - beta)
            long_run_vol = np.sqrt(long_run_var * 252) / 100  # Annualize and descale
        else:
            long_run_vol = returns.std() * np.sqrt(252)
        
        # Generate forecast
        forecast = result.forecast(horizon=5)
        variance_forecast = forecast.variance.iloc[-1].values
        
        # Convert to annualized volatility
        vol_forecast_1d = np.sqrt(variance_forecast[0] * 252) / 100
        vol_forecast_5d = np.sqrt(variance_forecast[-1] * 252) / 100
        
        return {
            'omega': omega,
            'alpha': alpha,
            'beta': beta,
            'persistence': alpha + beta,
            'long_run_vol': long_run_vol,
            'forecast_1d': vol_forecast_1d,
            'forecast_5d': vol_forecast_5d,
            'conditional_vol': result.conditional_volatility.iloc[-1] / 100 * np.sqrt(252)
        }
        
    except ImportError:
        # arch package not installed, return simple estimate
        recent_vol = returns.iloc[-21:].std() * np.sqrt(252)
        return {
            'omega': 0,
            'alpha': 0.1,
            'beta': 0.85,
            'persistence': 0.95,
            'long_run_vol': recent_vol,
            'forecast_1d': recent_vol,
            'forecast_5d': recent_vol,
            'conditional_vol': recent_vol
        }
    except Exception as e:
        print(f"GARCH fitting error: {e}")
        return None


def ensemble_forecast(
    prices: pd.Series,
    rf_weight: float = 0.5,
    garch_weight: float = 0.5
) -> Optional[float]:
    """
    Generate ensemble volatility forecast combining RF and GARCH.
    
    Parameters
    ----------
    prices : Series
        Price series
    rf_weight : float
        Weight for Random Forest forecast
    garch_weight : float
        Weight for GARCH forecast
        
    Returns
    -------
    float or None
        Ensemble volatility forecast
    """
    # Compute features
    features = compute_features(prices)
    if features.empty:
        return None
    
    # Train RF model
    model, mse, _ = train_vol_model(features, return_importance=True)
    if model is None:
        return None
    
    # RF forecast
    feature_cols = [c for c in features.columns if c != 'vol']
    recent_features = features[feature_cols].iloc[-1].values
    rf_forecast = model.predict(recent_features.reshape(1, -1))[0]
    
    # GARCH forecast
    returns = np.log(prices / prices.shift(1)).dropna()
    garch_result = calculate_garch_forecast(returns)
    
    if garch_result is None:
        return rf_forecast
    
    garch_forecast = garch_result['forecast_1d']
    
    # Ensemble
    ensemble = rf_weight * rf_forecast + garch_weight * garch_forecast
    
    return ensemble


def volatility_regime(
    vol_series: pd.Series,
    current_vol: float
) -> Dict:
    """
    Determine current volatility regime.
    
    Returns
    -------
    dict
        Regime information (low/normal/high, percentile, etc.)
    """
    percentile = (vol_series < current_vol).mean() * 100
    
    if percentile < 25:
        regime = "low"
        description = "Low volatility regime - market is calm"
    elif percentile > 75:
        regime = "high"
        description = "High volatility regime - market is turbulent"
    else:
        regime = "normal"
        description = "Normal volatility regime"
    
    return {
        'regime': regime,
        'percentile': percentile,
        'description': description,
        'mean_vol': vol_series.mean(),
        'current_vol': current_vol,
        'z_score': (current_vol - vol_series.mean()) / vol_series.std()
    }
