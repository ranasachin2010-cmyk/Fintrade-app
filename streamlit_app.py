import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import plotly.graph_objects as go
from plotly.graph_objects import Candlestick, Scatter
import pandas as pd
import numpy as np
from fpdf import FPDF
import urllib.parse

st.set_page_config(page_title='FinTrade V16.2', layout='wide')
st.markdown('<h1 style="color:#00D1FF">FinTrade V16.2 BUY SELL HOLD - NO EMOJI FIX</h1>', unsafe_allow_html=True)

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
    rsi = 100 - (100/(1+
