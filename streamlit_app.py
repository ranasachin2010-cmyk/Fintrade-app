import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.graph_objects import Candlestick, Scatter
import pandas as pd

st.set_page_config(page_title='V18.8', layout='wide')
st.markdown('<h1 style="color:#00D1FF">FinTrade V18.8 - FIXED</h1>', unsafe_allow_html=True)
st.write('App started OK')

TICKER_MAP = {'ZOMATO':'ETERNAL.NS','PAYTM':'PAYTM.NS'}
NAME_MAP = {'ETERNAL.NS':'ZOMATO','PAYTM.NS':'PAYTM'}

def load_data(tick):
    t = yf.Ticker(tick)
    df = t.history(period='3mo', interval='1d', auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def resolve_ticker(u):
    uu = u.upper().strip()
    if uu in TICKER_MAP:
        return TICKER_MAP[uu]
    if '.NS' in uu:
