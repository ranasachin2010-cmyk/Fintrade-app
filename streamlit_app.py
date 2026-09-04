import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.graph_objects import Candlestick, Scatter
import pandas as pd

st.set_page_config(page_title='V17.1 FIXED', layout='wide')
st.markdown('<h1 style="color:#00D1FF">FinTrade V17.1 - SIGNAL + TARGET + SL - FIXED</h1>', unsafe_allow_html=True)

TICKER_MAP = {'ZOMATO':'ETERNAL.NS','PAYTM':'PAYTM.NS','IRCTC':'IRCTC.NS'}

@st.cache_data(ttl=300)
def load_data(tick):
    df = yf.download(tick, period='6mo', interval='1d', auto_adjust=True, progress=False)
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

ticker_input = st.sidebar.text_input('NSE Stock', value='Zomato')
ticker = resolve_ticker(ticker_input)
st.sidebar.write('Resolved: ' + ticker)

df = load_data(ticker)
if df.empty:
    st.error('No data for ' + ticker)
    st.stop()

last_close = float(df['Close'].iloc[-1])
sup = float(df['Low'].tail(20).min())
res = float(df['High'].tail(20).max())
signal, color, rsi_val, score = get_signal(df)

target = res
stoploss = sup
if signal == 'BUY':
    diff = last_close - sup
    target = last_close + diff * 1.5
    stoploss = sup
if signal == 'SELL':
    target = sup
    stoploss = res

# SHOW CARDS - Always visible
st.markdown('<div style="background:' + color + ';padding:20px;border-radius:15px;text-align:center"><h1 style="color:black;margin:0">' + signal + ' ' + ticker + '</h1><p style="color:black">Score ' + str(score) + ' RSI ' + str(round(rsi_val,1)) + ' LTP ' + str(round(last_close,2)) + '</p></div>', unsafe_allow_html=True)

colA, colB, colC = st.columns(3)
colA.metric('Target', str(round(target,2)))
colB.metric('Stoploss', str(round(stoploss,2)))
colC.metric('Support/Resist', str(round(sup,2)) + ' / ' + str(round(res,2)))

# CHART
xs = df.index
fig = go.Figure()
cs = Candlestick()
cs.x = xs
cs.open = df['Open']
cs.high = df['High']
cs.low = df['Low']
cs.close = df['Close']
fig.add_trace(cs)
fig.add_trace(Scatter(x=xs, y=[sup]*len(xs), mode='lines', line=dict(color='green', dash='dash'), name='Support'))
fig.add_trace(Scatter(x=xs, y=[res]*len(xs), mode='lines', line=dict(color='red', dash='dash'), name='Resist'))
fig.add_trace(Scatter(x=xs, y=[target]*len(xs), mode='lines', line=dict(color='lime', width=2), name='Target'))
fig.add_trace(Scatter(x=xs, y=[stoploss]*len(xs), mode='lines', line=dict(color='orange', width=2), name='SL'))
fig.add_trace(Scatter(x=xs, y=df
