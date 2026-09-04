import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from fpdf import FPDF
import urllib.parse

st.set_page_config(page_title='FinTrade V16 SIGNAL', layout='wide')
st.markdown('<h1 style="color:#00D1FF">💎 FinTrade V16 - BUY SELL HOLD SIGNAL</h1>', unsafe_allow_html=True)

TICKER_MAP = {
'ZOMATO':'ETERNAL.NS',
'ETERNAL':'ETERNAL.NS',
'PAYTM':'PAYTM.NS',
'IRCTC':'IRCTC.NS',
'MAMAEARTH':'MAMAEARTH.NS',
'NYKAA':'NYKAA.NS',
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
    if '.NS' in u or '^' in u:
        return u
    return u + '.NS'

def get_signal(df):
    close = df['Close']
    # EMA
    ema20 = close.ewm(span=20).mean()
    ema50 = close.ewm(span=50).mean()
    # RSI
    delta = close.diff()
    gain = delta.where(delta>0,0).rolling(14).mean()
    loss = (-delta.where(delta<0,0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100/(1+rs))
    # MACD
    exp1 = close.ewm(span=12).mean()
    exp2 = close.ewm(span=26).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=9).mean()

    last_rsi = float(rsi.iloc[-1])
    last_close = float(close.iloc[-1])
    last_ema20 = float(ema20.iloc[-1])
    last_ema50 = float(ema50.iloc[-1])
    last_macd = float(macd.iloc[-1])
    last_sig = float(signal_line.iloc[-1])

    score = 0
    reasons = []
    # 1. EMA trend
    if last_ema20 > last_ema50:
        score = score + 1
        reasons.append('EMA20 > EMA50 BULLISH')
    else:
        score = score - 1
        reasons.append('EMA20 < EMA50 BEARISH')
    # 2. Price vs EMA20
    if last_close > last_ema20:
        score = score + 1
        reasons.append('Price > EMA20')
    else:
        score = score - 1
        reasons.append('Price < EMA20')
    # 3. RSI
    if last_rsi > 60:
        score = score + 1
        reasons.append('RSI Strong ' + str(round(last_rsi,1)))
    elif last_rsi < 40:
        score = score - 1
        reasons.append('RSI Weak ' + str(round(last_rsi,1)))
    else:
        reasons.append('RSI Neutral ' + str(round(last_rsi,1)))
    # 4. MACD
    if last_macd > last_sig:
        score = score + 1
        reasons.append('MACD BULLISH')
    else:
        score = score - 1
        reasons.append('MACD BEARISH')

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
        emoji = '🟡'

    return final, color, emoji, last_rsi, reasons, score

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['RELIANCE.NS','TCS.NS','ETERNAL.NS','PAYTM.NS','INFY.NS']

with st.sidebar:
    st.title('V16 SIGNAL')
    u = st.text_input('NSE Stock', value='Zomato').strip()
    ticker = resolve_ticker(u)
    clean = ticker.replace('.NS','')
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

# GET SIGNAL
signal, color, emoji, rsi_val, reasons, score = get_signal(df)

# TOP SIGNAL CARD
st.markdown(f"""
<div style="background:{color};padding:15px;border-radius:15px;text-align:center">
<h1 style="color:black;margin:0">{emoji} {signal} - {ticker}</h1>
<p style="color:black;margin:0;font-weight:600">Score {score}/4 | RSI {rsi_val:.1f} | LTP {float(last['Close']):.2f}</p>
</div>
""", unsafe_allow_html=True)

st.write('Reason: ' + ' | '.join(reasons))

t1,t2,t3,t4,t5,t6,t7,t8 = st.tabs(['Indian Chart + Signal','5min','Compare','Option Chain','AI','Screener','Watchlist KING','PDF'])

with t1:
    bse_sym = 'BSE:' + clean
    html_code = '<div style="height:500px;border:2px solid ' + color + '"><iframe src="https://s.tradingview.com/widgetembed/?symbol=' + bse_sym + '&interval=D&theme=dark&style=1&timezone=Asia/Kolkata" style="width:100%;height:100%;border:none"></iframe></div>'
    components.html(html_code, height=520)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df
