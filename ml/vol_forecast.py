import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import yfinance as yf

def fetch_price_history(ticker, period='2y'):
    data = yf.download(ticker, period=period)
    # If DataFrame, extract 'Close' column
    if isinstance(data, pd.DataFrame):
        if 'Close' in data.columns:
            return data['Close'].dropna()
        else:
            # If no 'Close' column, try first column
            return data.iloc[:, 0].dropna()
    elif isinstance(data, pd.Series):
        return data.dropna()
    else:
        return pd.Series(dtype=float)

def compute_features(prices):
    if prices is None or not isinstance(prices, pd.Series) or prices.empty or len(prices) < 22:
        return pd.DataFrame(columns=['vol', 'ret'])
    returns = np.log(prices / prices.shift(1)).dropna()
    rolling_vol = returns.rolling(window=21).std() * np.sqrt(252)
    if returns.empty or rolling_vol.empty or not returns.index.equals(rolling_vol.index):
        return pd.DataFrame(columns=['vol', 'ret'])
    features = pd.DataFrame({'vol': rolling_vol, 'ret': returns})
    features = features.dropna()
    return features

def train_vol_model(features):
    if features is None or len(features) < 10:
        # Not enough data to train model
        return None, None
    X = features[['ret']].values
    y = features['vol'].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    return model, mse

def forecast_vol(model, recent_ret):
    return model.predict(np.array(recent_ret).reshape(-1, 1))[0]
