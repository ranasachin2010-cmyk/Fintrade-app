import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import plotly.graph_objects as go
from plotly.graph_objects import Candlestick, Scatter
import pandas as pd

st.set_page_config(page_title='V16.4', layout='wide')
st.markdown('<h1 style="color:#00D1FF">FinTrade V16.4 BUY SELL HOLD</h1>', unsafe_allow_html=True)

TICKER_MAP = {'ZOMATO':'ETERNAL.NS','PAYTM':'PAYTM.NS','IRCTC':'IRCTC.NS'}

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
    up = delta.clip(lower=0)
    down = delta.clip(upper=0)
    down = down * -1
    gain = up.rolling(14).mean()
    loss = down.rolling(14).mean()
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
    if last_ema20 < last_ema50:
        score = score - 1
        reasons.append('EMA20<EMA50 BEAR')
    if last_close > last_ema20:
        score = score + 1
        reasons.append('Price>EMA20')
    if last_close < last_ema20:
        score = score - 1
        reasons.append('Price<EMA20')
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
    return final, color, last_rsi, reasons, score

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['RELIANCE.NS','TCS.NS','ETERNAL.NS','PAYTM.NS','INFY.NS']

with st.sidebar:
    st.title('V16.4 SAFE')
    u = st.text_input('NSE Stock', value='Zomato').strip()
    ticker = resolve_ticker(u)
    st.caption('Resolved: ' + ticker)
    if st.button('Refresh'):
        st.cache_data.clear()
        st.rerun()

df = load_data(ticker, '6mo', '1d')
if df.empty:
    st.error(ticker + ' Not found')
    st.stop()

last = df.iloc[-1]
sup = float(df['Low'].tail(20).min())
res = float(df['High'].tail(20).max())
signal, color, rsi_val, reasons, score = get_signal(df)

card_html = '<div style="background:' + color + ';padding:15px;border-radius:15px;text-align:center"><h1 style="color:black">' + signal + ' ' + ticker + '</h1><p style="color:black">Score ' + str(score) + ' RSI ' + str(round(rsi_val,1)) + '</p></div>'
st.markdown(card_html, unsafe_allow_html=True)
st.write('Logic: ' + ' | '.join(reasons))
