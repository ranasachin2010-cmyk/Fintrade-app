import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.graph_objects import Candlestick, Scatter
import pandas as pd

st.set_page_config(page_title='V18.5', layout='wide')
st.markdown('<h1 style="color:#00D1FF">FinTrade V18.5 - MINIMAL</h1>', unsafe_allow_html=True)
st.write('App started OK')

TICKER_MAP = {'ZOMATO':'ETERNAL.NS'}
NAME_MAP = {'ETERNAL.NS':'ZOMATO'}

def load_data(tick):
    try:
        t = yf.Ticker(tick)
        df = t.history(period='3mo', interval='1d', auto_adjust=True)
        if df.empty:
            df = yf.download(tick, period='3mo', interval='1d', auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return pd.DataFrame()

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

# SAFE ROUND - ONE PER LINE
ltp_r = round(last_close, 2)
tgt_r = round(target, 2)
sl_r = round(stoploss, 2)
rsi_r = round(rsi_val, 1)
sup_r = round(sup, 2)
res_r = round(res, 2)

# CARD - NO str() IN HTML, USE SIMPLE ST
st.markdown('---')
st.subheader(signal)
st.subheader(display_name)
st.write('LTP')
st.write(ltp_r)
st.write('Target')
st.write(tgt_r)
st.write('SL')
st.write(sl_r)
st.write('Score')
st.write(score)
st.write('RSI')
st.write(rsi_r)

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

s1 = Scatter()
s1.x = xs
s1.y = [sup]*len(xs)
s1.mode = 'lines'
s1.name = 'Support'
fig.add_trace(s1)

s2 = Scatter()
s2.x = xs
s2.y = [res]*len(xs)
s2.mode = 'lines'
s2.name = 'Resist'
fig.add_trace(s2)

s3 = Scatter()
s3.x = xs
s3.y = [target]*len(xs)
s3.mode = 'lines'
s3.name = 'Target'
fig.add_trace(s3)

s4 = Scatter()
s4.x = xs
s4.y = [stoploss]*len(xs)
s4.mode = 'lines'
s4.name = 'SL'
fig.add_trace(s4)

low_range = sup - 15
high_range = res + 15
fig.update_layout(height=600, template='plotly_dark', yaxis=dict(range=[low_range, high_range]))
fig.update_xaxes(rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

st.write('V18.5 Loaded OK - Chart above')
