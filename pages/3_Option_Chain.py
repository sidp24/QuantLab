"""
Option Chain Browser Page - Browse real-time option chains from Yahoo Finance.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from data.yahoo import get_stock_info, get_option_chain, get_historical_data
from pricing.implied_volatility import implied_volatility
from pricing.black_scholes import price as bs_price
from utils.styles import inject_styles

st.set_page_config(page_title="Option Chain", page_icon="Q", layout="wide")
inject_styles()

st.markdown('<h1 style="background: linear-gradient(135deg, #00D4FF, #7B2FFF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.5rem;">Option Chain Browser</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #94A3B8; margin-top: -0.5rem;">Browse real-time option chains and analyze market pricing.</p>', unsafe_allow_html=True)

# Sidebar
st.sidebar.header("Settings")
ticker = st.sidebar.text_input("Ticker Symbol", value="AAPL")
risk_free_rate = st.sidebar.number_input("Risk-Free Rate", min_value=0.0, max_value=0.5, value=0.05, step=0.005)

# Fetch data button
fetch_button = st.sidebar.button("Fetch Option Chain", use_container_width=True, type="primary")

# Main content
if fetch_button or 'chain_data' in st.session_state:
    if fetch_button:
        with st.spinner(f"Fetching data for {ticker}..."):
            try:
                spot, hist_vol = get_stock_info(ticker)
                chains = get_option_chain(ticker)
                
                if spot and chains:
                    st.session_state.chain_data = {
                        'ticker': ticker,
                        'spot': spot,
                        'hist_vol': hist_vol if hist_vol else 0.20,
                        'chains': chains,
                        'expiries': list(chains.keys())
                    }
                    st.success(f"Loaded {ticker} @ ${spot:.2f}")
                else:
                    st.error("Could not fetch option data. Please check the ticker symbol.")
                    st.stop()
            except Exception as e:
                st.error(f"Error fetching data: {str(e)}")
                st.stop()
    
    if 'chain_data' in st.session_state:
        data = st.session_state.chain_data
        spot = data['spot']
        hist_vol = data['hist_vol']
        
        # Display stock info
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Stock Price", f"${spot:.2f}")
        with col2:
            st.metric("Historical Vol", f"{hist_vol:.1%}")
        with col3:
            st.metric("Expirations", len(data['expiries']))
        with col4:
            # Calculate days to nearest expiry
            if data['expiries']:
                nearest = datetime.strptime(data['expiries'][0], "%Y-%m-%d")
                days_to_exp = (nearest - datetime.now()).days
                st.metric("Nearest Expiry", f"{days_to_exp} days")
        
        st.markdown("---")
        
        # Expiry selection
        selected_expiry = st.selectbox(
            "Select Expiration Date",
            data['expiries'],
            format_func=lambda x: f"{x} ({(datetime.strptime(x, '%Y-%m-%d') - datetime.now()).days} days)"
        )
        
        if selected_expiry:
            chain = data['chains'][selected_expiry]
            calls_df = chain['calls'].copy()
            puts_df = chain['puts'].copy()
            
            # Calculate time to expiry
            expiry_date = datetime.strptime(selected_expiry, "%Y-%m-%d")
            T = max((expiry_date - datetime.now()).days / 365, 0.001)
            
            # Tabs for calls and puts
            tab1, tab2, tab3 = st.tabs(["Calls", "Puts", "Analysis"])
            
            with tab1:
                st.subheader("Call Options")
                
                # Process calls
                if not calls_df.empty:
                    display_cols = ['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']
                    available_cols = [c for c in display_cols if c in calls_df.columns]
                    
                    calls_display = calls_df[available_cols].copy()
                    calls_display.columns = ['Strike', 'Last', 'Bid', 'Ask', 'Volume', 'Open Int', 'IV']
                    
                    # Highlight ITM options
                    def highlight_itm(row):
                        if row['Strike'] < spot:
                            return ['background-color: #90EE90'] * len(row)
                        return [''] * len(row)
                    
                    # Format percentages
                    calls_display['IV'] = calls_display['IV'].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "N/A")
                    
                    st.dataframe(
                        calls_display.style.apply(highlight_itm, axis=1),
                        use_container_width=True,
                        hide_index=True
                    )
                    st.caption("Green = In-The-Money")
                else:
                    st.info("No call options available for this expiration.")
            
            with tab2:
                st.subheader("Put Options")
                
                if not puts_df.empty:
                    display_cols = ['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']
                    available_cols = [c for c in display_cols if c in puts_df.columns]
                    
                    puts_display = puts_df[available_cols].copy()
                    puts_display.columns = ['Strike', 'Last', 'Bid', 'Ask', 'Volume', 'Open Int', 'IV']
                    
                    # Highlight ITM options
                    def highlight_itm_puts(row):
                        if row['Strike'] > spot:
                            return ['background-color: #90EE90'] * len(row)
                        return [''] * len(row)
                    
                    puts_display['IV'] = puts_display['IV'].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "N/A")
                    
                    st.dataframe(
                        puts_display.style.apply(highlight_itm_puts, axis=1),
                        use_container_width=True,
                        hide_index=True
                    )
                    st.caption("Green = In-The-Money")
                else:
                    st.info("No put options available for this expiration.")
            
            with tab3:
                st.subheader("Chain Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Volume Analysis")
                    
                    # Most active strikes
                    if not calls_df.empty and 'volume' in calls_df.columns:
                        calls_df['volume'] = pd.to_numeric(calls_df['volume'], errors='coerce').fillna(0)
                        top_calls = calls_df.nlargest(5, 'volume')[['strike', 'volume']]
                        top_calls.columns = ['Strike', 'Volume']
                        st.markdown("**Most Active Calls**")
                        st.dataframe(top_calls, use_container_width=True, hide_index=True)
                    
                    if not puts_df.empty and 'volume' in puts_df.columns:
                        puts_df['volume'] = pd.to_numeric(puts_df['volume'], errors='coerce').fillna(0)
                        top_puts = puts_df.nlargest(5, 'volume')[['strike', 'volume']]
                        top_puts.columns = ['Strike', 'Volume']
                        st.markdown("**Most Active Puts**")
                        st.dataframe(top_puts, use_container_width=True, hide_index=True)
                
                with col2:
                    st.markdown("#### Put/Call Analysis")
                    
                    total_call_vol = calls_df['volume'].sum() if 'volume' in calls_df.columns else 0
                    total_put_vol = puts_df['volume'].sum() if 'volume' in puts_df.columns else 0
                    
                    total_call_oi = calls_df['openInterest'].sum() if 'openInterest' in calls_df.columns else 0
                    total_put_oi = puts_df['openInterest'].sum() if 'openInterest' in puts_df.columns else 0
                    
                    st.metric("Call Volume", f"{int(total_call_vol):,}")
                    st.metric("Put Volume", f"{int(total_put_vol):,}")
                    
                    if total_call_vol > 0:
                        pcr = total_put_vol / total_call_vol
                        st.metric("Put/Call Ratio (Volume)", f"{pcr:.2f}")
                        
                        if pcr > 1.2:
                            st.warning("High P/C ratio - bearish sentiment")
                        elif pcr < 0.8:
                            st.info("Low P/C ratio - bullish sentiment")
                        else:
                            st.success("Neutral P/C ratio")
                    
                    if total_call_oi > 0:
                        pcr_oi = total_put_oi / total_call_oi
                        st.metric("Put/Call Ratio (OI)", f"{pcr_oi:.2f}")
                
                # Volatility Smile
                st.markdown("---")
                st.markdown("#### Implied Volatility Smile")
                
                if not calls_df.empty and 'impliedVolatility' in calls_df.columns:
                    import matplotlib.pyplot as plt
                    from utils.plotting import COLORS, apply_dark_style
                    
                    fig, ax = plt.subplots(figsize=(10, 5))
                    
                    # Plot call IV
                    calls_iv = calls_df[['strike', 'impliedVolatility']].dropna()
                    ax.plot(calls_iv['strike'], calls_iv['impliedVolatility'] * 100, 
                           '-o', color=COLORS["primary"], label='Calls IV', alpha=0.8, linewidth=2, markersize=5)
                    
                    # Plot put IV
                    if not puts_df.empty and 'impliedVolatility' in puts_df.columns:
                        puts_iv = puts_df[['strike', 'impliedVolatility']].dropna()
                        ax.plot(puts_iv['strike'], puts_iv['impliedVolatility'] * 100, 
                               '-o', color=COLORS["accent"], label='Puts IV', alpha=0.8, linewidth=2, markersize=5)
                    
                    ax.axvline(x=spot, color=COLORS["success"], linestyle='--', linewidth=1.5, label=f'Spot (${spot:.2f})')
                    ax.set_xlabel('Strike Price ($)', fontsize=11, fontweight='medium')
                    ax.set_ylabel('Implied Volatility (%)', fontsize=11, fontweight='medium')
                    ax.set_title(f'IV Smile - {ticker} ({selected_expiry})', fontsize=13, fontweight='bold', pad=15)
                    ax.legend(loc='best', framealpha=0.9)
                    
                    apply_dark_style(ax, fig)
                    plt.tight_layout()
                    
                    st.pyplot(fig)
                    plt.close()

else:
    st.info("Enter a ticker symbol and click 'Fetch Option Chain' to get started.")
    
    # Show example
    st.markdown("---")
    st.markdown("### How to Use")
    st.markdown("""
    1. Enter a valid stock ticker (e.g., AAPL, MSFT, TSLA)
    2. Click 'Fetch Option Chain' to load data
    3. Select an expiration date to view options
    4. Browse calls and puts, analyze volume and IV
    """)

# Footer
st.markdown("---")
st.caption("Option Chain Browser | Data from Yahoo Finance")
