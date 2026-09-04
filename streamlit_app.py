import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.graph_objects import Candlestick, Scatter
import pandas as pd

st.set_page_config(page_title='V18.7', layout='wide')
st.markdown('<h1 style="color:#00D1FF">FinTrade V18.7 - NO ERROR</h1>', unsafe_allow_html=True)
st.write('App started OK')

TICKER_MAP = {'ZOMATO':'ETERNAL.NS'}
NAME_MAP = {'ETERNAL.NS':'ZOMATO'}

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
    if last_ema20 > last_ema50:
        score = score + 1
    if last_ema20 < last_ema50:
        score = score - 1
    if last_close > last_ema20:
        score = score + 1
    if last_close < last_ema20:
        score = score - 1
    if last_rsi > 60:
        score = score + 1
    if last_rsi < 40:
        score = score - 1
    if last_macd > last_sig:
        score = score + 1
    if last_macd < last_sig:
        score = score - 1
    final = 'HOLD'
    color = '#FFD700'
    if score >= 2:
        final = 'BUY'
        color = '#00FF00'
    if score <= -2:
        final = 'SELL'
        color = '#FF0000'
    return final, color, last_rsi, score

st.sidebar.header('Settings')
ticker_input = st.sidebar.text_input('Stock', value='Zomato')
ticker = resolve_ticker(ticker_input)
display_name = get_display_name(ticker)
st.write('Ticker')
st.write(ticker)

df = load_data(ticker)
if df.empty:
    st.error('No data')
    st.stop()

last_close = float(df['Close'].iloc[-1])
sup = float(df['Low'].tail(20).min())
res
