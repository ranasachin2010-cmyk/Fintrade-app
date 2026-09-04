import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import plotly.graph_objects as go
from plotly.graph_objects import Candlestick, Scatter
import pandas as pd
import numpy as np

st.set_page_config(page_title='V16.3', layout='wide')
st.markdown('<h1 style="color:#00D1FF">FinTrade V16.3 BUY SELL HOLD</h1>', unsafe_allow_html=True)

TICKER_MAP = {
'ZOMATO':'ETERNAL.NS',
'PAYTM':'PAYTM.NS',
'IRCTC':'IRCTC.NS'
}

@st.cache_data(ttl=300)
def load_data(tick, per='6mo', interval='1d'):
    df = yf.download(tick, period=per, interval=interval, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def resolve_ticker(user_input):
    u = user_input.upper().strip()
    if u in TICKER_MAP:
        return TICKER_MAP[u]
    if '.NS' in u:
        return u
    return u + '.NS'

def get_signal(df):
    close = df['Close']
    ema20 = close.ewm(span=20).mean()
    ema50 = close.ewm(span=50).mean()
    delta = close.diff()
    # gain loss - NO NESTED BRACKET
    up = delta.clip(lower=0)
    down = delta.clip(upper=0)
    down = down * -1
    gain = up.rolling(14).mean()
    loss = down.rolling(14).mean()
    # RSI - NO NESTED BRACKET - 3 steps
    rs = gain / loss
    den = 1 + rs
    div = 100 / den
    rsi = 100 - div
    exp1 = close.ewm(span=12).mean()
    exp2 = close.ewm(span=26).mean()
    macd = exp1 - exp2
    sig = macd.ewm(span=9).mean()
    last_rsi = float(rsi.iloc[-1])
    last_close = float(close.iloc[-1])
    last_ema20 = float(ema20.iloc[-1])
    last_ema50 = float(ema50.iloc[-1])
    last_macd = float(macd.iloc[-1])
    last_sig = float(sig.iloc[-1])
    score = 0
    reasons = []
    if last_ema20 > last_ema50:
        score = score + 1
        reasons.append('EMA20>EMA50 BULL')
    else:
        score = score - 1
        reasons.append('EMA20<EMA50 BEAR')
    if last_close > last_ema20:
        score = score + 1
        reasons.append('Price>EMA20')
    else:
        score = score - 1
        reasons.append('Price<EMA20')
    if last_rsi > 60:
        score = score + 1
    elif
