import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.graph_objects import Candlestick, Scatter
import pandas as pd

st.set_page_config(page_title='V18 FINAL', layout='wide')
st.markdown('<h1 style="color:#00D1FF">FinTrade V18 FINAL - BUY SELL + SCREENER</h1>', unsafe_allow_html=True)

TICKER_MAP = {'ZOMATO':'ETERNAL.NS','PAYTM':'PAYTM.NS','IRCTC':'IRCTC.NS','BHARTI':'BHARTIARTL.NS'}
NAME_MAP = {'ETERNAL.NS':'ZOMATO','PAYTM.NS':'PAYTM','IRCTC.NS':'IRCTC','BHARTIARTL.NS':'BHARTI'}

@st.cache_data(ttl=300)
def load_data(tick):
    df = yf.download(tick, period='3mo', interval='1d', auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def resolve_ticker(u):
    uu = u.upper().strip()
    if uu in TICKER_MAP:
        return TICKER_MAP[uu]
    if '.NS' in uu:
        return uu
    return uu + '.NS'

def get_display_name(tick):
    if tick in NAME_MAP:
        return NAME_MAP[tick]
    return tick.replace('.NS','')

def get_signal(df):
    close = df['Close']
    ema20 = close.ewm(span=20).mean()
    ema50 = close.ewm(span=50).mean()
    delta = close.diff()
    up = delta.clip(lower=0)
    down = delta.clip(upper=0)
    down = down * -1
    gain = up.rolling(14).mean()
    loss = down.rolling(14).mean()
    loss = loss.replace(0, 0.001)
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
