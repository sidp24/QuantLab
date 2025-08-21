import yfinance as yf

def get_stock_info(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    spot = info.get('regularMarketPrice', None)
    vol = info.get('impliedVolatility', None)
    return spot, vol

def get_option_chain(ticker):
    stock = yf.Ticker(ticker)
    expiries = stock.options
    chains = {}
    for expiry in expiries:
        opt_chain = stock.option_chain(expiry)
        chains[expiry] = {
            'calls': opt_chain.calls,
            'puts': opt_chain.puts
        }
    return chains
