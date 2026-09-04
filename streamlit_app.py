import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.graph_objects import Candlestick, Scatter
import pandas as pd

st.set_page_config(page_title='V17.3 ZOOM', layout='wide')
st.markdown('<h1 style="color:#00D1FF">FinTrade V17.3 - ZOOM FIXED</h1>', unsafe_allow_html=True)

TICKER_MAP = {'ZOMATO':'ETERNAL.NS','PAYTM':'PAYTM.NS'}

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

df = load_data(ticker)
if df.empty:
    st.error('No data')
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

# CARDS
html1 = '<div style="background:' + color + ';padding:20px;border-radius:15px;text-align:center"><h1 style="color:black">' + signal + ' ' + ticker + '</h1></div>'
st.markdown(html1, unsafe_allow_html=True)
st.write('Score ' + str(score) + ' | RSI ' + str(round(rsi_val,1)) + ' | LTP ' + str(round(last_close,2)))
st.write('Target ' + str(round(target,2)) + ' | SL ' + str(round(stoploss,2)) + ' | Support ' + str(round(sup,2)) + ' Resist ' + str(round(res,2)))

# CHART - ZOOM FIX
xs = df.index
fig = go.Figure()

cs = Candlestick()
cs.x = xs
cs.open = df['Open']
cs.high = df['High']
cs.low = df['Low']
cs.close = df['Close']
fig.add_trace(cs)

s1 = Scatter()
s1.x = xs
s1.y = [sup]*len(xs)
s1.mode = 'lines'
s1.name = 'Support'
s1.line = dict(color='green', dash='dash')
fig.add_trace(s1)

s2 = Scatter()
s2.x = xs
s2.y = [res]*len(xs)
s2.mode = 'lines'
s2.name = 'Resist'
s2.line = dict(color='red', dash='dash')
fig.add_trace(s2)

s3 = Scatter()
s3.x = xs
s3.y = [target]*len(xs)
s3.mode = 'lines'
s3.name = 'Target'
s3.line = dict(color='lime', width=2)
fig.add_trace(s3)

s4 = Scatter()
s4.x = xs
s4.y = [stoploss]*len(xs)
s4.mode = 'lines'
s4.name = 'SL'
s4.line = dict(color='orange', width=2)
fig.add_trace(s4)

s5 = Scatter()
s5.x = xs
s5.y = df['Close'].ewm(span=20).mean()
s5.mode = 'lines'
s5.name = 'EMA20'
s5.line = dict(color='yellow')
fig.add_trace(s5)

s6 = Scatter()
s6.x = xs
s6.y = df['Close'].ewm(span=50).mean()
s6.mode = 'lines'
s6.name = 'EMA50'
s6.line = dict(color='cyan')
fig.add_trace(s6)

# ZOOM FIX - Y AXIS
low_val = df['Low'].min()
high_val = df['High'].max()
pad = (high_val - low_val) * 0.1
fig.update_layout(height=650, template='plotly_dark', yaxis=dict(range=[low_val - pad, high_val + pad]))
fig.update_xaxes(rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)
st.success('V17.3 Chart Zoom Fixed!')
