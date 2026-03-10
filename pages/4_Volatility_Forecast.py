"""
Volatility Forecasting Page - ML-powered volatility prediction.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

from ml.vol_forecast import (
    fetch_price_history, 
    compute_features, 
    train_vol_model, 
    forecast_vol,
    calculate_garch_forecast
)
from data.yahoo import get_stock_info
from utils.styles import inject_styles

st.set_page_config(page_title="Volatility Forecasting", page_icon="Q", layout="wide")
inject_styles()

st.markdown('<h1 style="background: linear-gradient(135deg, #00D4FF, #7B2FFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.5rem;">Volatility Forecasting</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #94A3B8; margin-top: -0.5rem;">Machine learning and statistical models for volatility prediction.</p>', unsafe_allow_html=True)

# Sidebar
st.sidebar.header("Settings")
ticker = st.sidebar.text_input("Ticker Symbol", value="AAPL")
period = st.sidebar.selectbox(
    "Historical Period", 
    ["6mo", "1y", "2y", "5y"],
    index=2,
    help="Longer periods provide more training data"
)

model_type = st.sidebar.selectbox(
    "Model Type",
    ["Random Forest", "GARCH(1,1)", "Ensemble"],
    help="Select the forecasting model"
)

# Main content
tab1, tab2, tab3 = st.tabs(["Train Model", "Forecast", "Analysis"])

with tab1:
    st.subheader("Model Training")
    
    if st.button("Train Model", type="primary", use_container_width=True):
        with st.spinner(f"Fetching {period} of data for {ticker}..."):
            try:
                prices = fetch_price_history(ticker, period=period)
                
                if prices is None or len(prices) < 50:
                    st.error("Insufficient data. Please select a longer period or different ticker.")
                    st.stop()
                
                # Convert to Series if DataFrame
                if isinstance(prices, pd.DataFrame):
                    prices = prices.iloc[:, 0]
                
                st.success(f"Loaded {len(prices)} data points")
                
                # Compute features
                features = compute_features(prices)
                
                if features.empty or len(features) < 30:
                    st.error("Not enough data to compute features.")
                    st.stop()
                
                st.info(f"Computed {len(features)} feature samples")
                
                # Train model
                progress = st.progress(0, text="Training model...")
                
                if model_type == "Random Forest":
                    model, mse, feature_importance = train_vol_model(features, return_importance=True)
                    progress.progress(100, text="Training complete!")
                    
                    if model is not None:
                        st.session_state.vol_model = model
                        st.session_state.features = features
                        st.session_state.model_type = "RF"
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Test MSE", f"{mse:.6f}")
                        with col2:
                            st.metric("Test RMSE", f"{np.sqrt(mse):.4f}")
                        with col3:
                            st.metric("Features Used", len(feature_importance))
                        
                        # Feature importance
                        if feature_importance:
                            st.markdown("#### Feature Importance")
                            importance_df = pd.DataFrame(
                                list(feature_importance.items()),
                                columns=['Feature', 'Importance']
                            ).sort_values('Importance', ascending=True)
                            
                            import matplotlib.pyplot as plt
                            from utils.plotting import COLORS, apply_dark_style
                            
                            fig, ax = plt.subplots(figsize=(10, 6))
                            bars = ax.barh(importance_df['Feature'], importance_df['Importance'], 
                                          color=COLORS["primary"], edgecolor=COLORS["surface"])
                            ax.set_xlabel('Importance', fontsize=11, fontweight='medium')
                            ax.set_ylabel('Feature', fontsize=11, fontweight='medium')
                            ax.set_title('Feature Importance', fontsize=13, fontweight='bold', pad=15)
                            
                            apply_dark_style(ax, fig)
                            plt.tight_layout()
                            st.pyplot(fig)
                            plt.close()
                    else:
                        st.error("Model training failed.")
                
                elif model_type == "GARCH(1,1)":
                    returns = np.log(prices / prices.shift(1)).dropna()
                    garch_result = calculate_garch_forecast(returns)
                    progress.progress(100, text="Training complete!")
                    
                    if garch_result:
                        st.session_state.garch_result = garch_result
                        st.session_state.model_type = "GARCH"
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Omega", f"{garch_result['omega']:.6f}")
                        with col2:
                            st.metric("Alpha", f"{garch_result['alpha']:.4f}")
                        with col3:
                            st.metric("Beta", f"{garch_result['beta']:.4f}")
                        
                        st.markdown(f"**Long-run Volatility:** {garch_result['long_run_vol']:.2%}")
                        st.markdown(f"**Persistence:** {garch_result['persistence']:.4f}")
                    else:
                        st.warning("GARCH fitting failed. Try Random Forest instead.")
                
                else:  # Ensemble
                    # Train both models
                    model, mse, _ = train_vol_model(features, return_importance=True)
                    returns = np.log(prices / prices.shift(1)).dropna()
                    garch_result = calculate_garch_forecast(returns)
                    progress.progress(100, text="Training complete!")
                    
                    st.session_state.vol_model = model
                    st.session_state.garch_result = garch_result
                    st.session_state.features = features
                    st.session_state.model_type = "Ensemble"
                    
                    st.success("Ensemble model trained (RF + GARCH)")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")

with tab2:
    st.subheader("Volatility Forecast")
    
    if 'model_type' not in st.session_state:
        st.info("Train a model first to generate forecasts.")
    else:
        model_type_trained = st.session_state.model_type
        
        st.markdown(f"**Active Model:** {model_type_trained}")
        
        # Generate forecast
        if model_type_trained == "RF" and 'vol_model' in st.session_state:
            features = st.session_state.features
            model = st.session_state.vol_model
            
            recent_ret = features['ret'].iloc[-1]
            pred_vol = forecast_vol(model, [recent_ret])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                current_vol = features['vol'].iloc[-1]
                st.metric("Current Realized Vol", f"{current_vol:.2%}")
            with col2:
                st.metric("Predicted Vol (Next Period)", f"{pred_vol:.2%}")
            with col3:
                change = pred_vol - current_vol
                st.metric("Expected Change", f"{change:+.2%}")
            
        elif model_type_trained == "GARCH" and 'garch_result' in st.session_state:
            garch = st.session_state.garch_result
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("1-Day Forecast", f"{garch['forecast_1d']:.2%}")
            with col2:
                st.metric("5-Day Forecast", f"{garch['forecast_5d']:.2%}")
            with col3:
                st.metric("Long-Run Vol", f"{garch['long_run_vol']:.2%}")
        
        elif model_type_trained == "Ensemble":
            features = st.session_state.features
            model = st.session_state.vol_model
            garch = st.session_state.garch_result
            
            # RF forecast
            recent_ret = features['ret'].iloc[-1]
            rf_pred = forecast_vol(model, [recent_ret]) if model else None
            
            # GARCH forecast
            garch_pred = garch['forecast_1d'] if garch else None
            
            # Ensemble (simple average)
            if rf_pred and garch_pred:
                ensemble_pred = (rf_pred + garch_pred) / 2
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("RF Forecast", f"{rf_pred:.2%}")
                with col2:
                    st.metric("GARCH Forecast", f"{garch_pred:.2%}")
                with col3:
                    st.metric("Ensemble Forecast", f"{ensemble_pred:.2%}")
        
        # Historical volatility chart
        st.markdown("---")
        st.markdown("#### Historical Volatility")
        
        if 'features' in st.session_state:
            features = st.session_state.features
            
            import matplotlib.pyplot as plt
            from utils.plotting import COLORS, apply_dark_style
            
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(features.index, features['vol'] * 100, label='Realized Volatility', 
                   color=COLORS["primary"], linewidth=1.5)
            ax.axhline(y=features['vol'].mean() * 100, color=COLORS["accent"], linestyle='--', 
                      linewidth=1.5, label=f'Mean: {features["vol"].mean():.1%}')
            ax.fill_between(features.index, 
                           (features['vol'].mean() - features['vol'].std()) * 100,
                           (features['vol'].mean() + features['vol'].std()) * 100,
                           alpha=0.15, color=COLORS["secondary"], label='±1 Std Dev')
            ax.set_xlabel('Date', fontsize=11, fontweight='medium')
            ax.set_ylabel('Annualized Volatility (%)', fontsize=11, fontweight='medium')
            ax.set_title(f'Historical Volatility - {ticker}', fontsize=13, fontweight='bold', pad=15)
            ax.legend(loc='best', framealpha=0.9)
            
            apply_dark_style(ax, fig)
            plt.tight_layout()
            
            st.pyplot(fig)
            plt.close()

with tab3:
    st.subheader("Volatility Analysis")
    
    if 'features' not in st.session_state:
        st.info("Train a model first to see analysis.")
    else:
        features = st.session_state.features
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Volatility Statistics")
            
            stats = {
                "Mean": f"{features['vol'].mean():.2%}",
                "Std Dev": f"{features['vol'].std():.2%}",
                "Min": f"{features['vol'].min():.2%}",
                "Max": f"{features['vol'].max():.2%}",
                "Current": f"{features['vol'].iloc[-1]:.2%}",
                "Percentile": f"{(features['vol'] < features['vol'].iloc[-1]).mean():.1%}"
            }
            
            st.dataframe(pd.DataFrame(stats.items(), columns=['Metric', 'Value']), 
                        use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("#### Volatility Regimes")
            
            vol = features['vol']
            low_vol = vol.quantile(0.25)
            high_vol = vol.quantile(0.75)
            
            current = vol.iloc[-1]
            
            if current < low_vol:
                st.success("**Low Volatility Regime**")
                st.markdown("Market is calm. Options are relatively cheap.")
            elif current > high_vol:
                st.error("**High Volatility Regime**")
                st.markdown("Market is turbulent. Consider hedging strategies.")
            else:
                st.info("**Normal Volatility Regime**")
                st.markdown("Volatility is within typical range.")
            
            # Volatility percentile gauge
            pct = (vol < current).mean() * 100
            st.metric("Current Vol Percentile", f"{pct:.0f}th percentile")
        
        # Distribution
        st.markdown("---")
        st.markdown("#### Volatility Distribution")
        
        import matplotlib.pyplot as plt
        from utils.plotting import COLORS, apply_dark_style
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(features['vol'] * 100, bins=50, alpha=0.7, color=COLORS["primary"], edgecolor=COLORS["surface"])
        ax.axvline(x=features['vol'].iloc[-1] * 100, color=COLORS["accent"], linestyle='--', 
                  linewidth=2.5, label=f'Current: {features["vol"].iloc[-1]:.1%}')
        ax.set_xlabel('Annualized Volatility (%)', fontsize=11, fontweight='medium')
        ax.set_ylabel('Frequency', fontsize=11, fontweight='medium')
        ax.set_title('Volatility Distribution', fontsize=13, fontweight='bold', pad=15)
        ax.legend(loc='best', framealpha=0.9)
        
        apply_dark_style(ax, fig)
        plt.tight_layout()
        
        st.pyplot(fig)
        plt.close()

# Footer
st.markdown("---")
st.caption("Volatility Forecasting | Machine Learning Models")
