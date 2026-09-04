import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import plotly.graph_objects as go
from plotly.graph_objects import Candlestick, Scatter
import pandas as pd
import numpy as np
from fpdf import FPDF
import urllib.parse

st.set_page_config(page_title='FinTrade V16.1 FIXED', layout='wide')
st.markdown('<h1 style="color:#00D1FF">💎 FinTrade V16.1 BUY SELL HOLD - FIXED</h1>', unsafe_allow_html=True)

TICKER_MAP = {
'ZOMATO':'ETERNAL.NS',
'ETERNAL':'ETERNAL.NS',
'PAYTM':'PAYTM.NS',
'IRCTC':'IRCTC.NS',
'LIC':'LICI.NS'
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
    gain = delta.where(delta>0,0).rolling(14).mean()
    loss = (-delta.where(delta<0,0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100/(1+rs))
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
        reasons.append('EMA20>EMA50')
    else:
        score = score - 1
        reasons.append('EMA20<EMA50')
    if last_close > last_ema20:
        score = score + 1
        reasons.append('Price>EMA20')
    else:
        score = score - 1
        reasons.append('Price<EMA20')
    if last_rsi > 60:
        score = score + 1
    elif last_rsi < 40:
        score = score - 1
    if last_macd > last_sig:
        score = score + 1
    else:
        score = score - 1
    if score >= 2:
        final = 'BUY'
        color = '#00FF00'
        emoji = '🟢'
    elif score <= -2:
        final = 'SELL'
        color = '#FF0000'
        emoji = '🔴'
    else:
        final = 'HOLD'
        color = '#FFD700'
        emoji = '
