import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from fpdf import FPDF
import urllib.parse

st.set_page_config(page_title='FinTrade V15.1 FINAL', layout='wide')

st.markdown("""
<style>
.stApp { background: radial-gradient(circle at 20% 20%, #0a1628 0%, #000000 100%); }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="color:#00D1FF">💎 FinTrade V15.1 WATCHLIST KING - FINAL</h1>', unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_data(tick, per='6mo', interval='1d'):
    df = yf.download(tick, period=per, interval=interval, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def make_pdf(ticker, ltp, sup, res):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial','B',14)
    title = 'FinTrade ' + str(ticker)
    pdf.cell(0,10,title,ln=True,align='C')
    pdf.set_font('Arial','',11)
    pdf.ln(5)
    line = 'LTP ' + str(round(float(ltp),2))
    line = line + ' S ' + str(round(float(sup),2))
    line = line + ' R ' + str(round(float(res),2))
    pdf.cell(0,10,line,ln=True)
    out = pdf.output()
    return bytes(out)

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['RELIANCE.NS','TCS.NS','INFY.NS','HDFCBANK.NS','SBIN.NS']

with st.sidebar:
    st.title('V15.1 KING')
    u = st.text_input('NSE Stock', value='RELIANCE').upper().strip()
    ticker = u if '.NS' in u else u + '.NS'
    clean = u.replace('.NS','')
    if st.button('Refresh'):
        st.cache_data.clear()
        st.rerun()

df = load_data(ticker, '6mo', '1d')
if df.empty:
    st.error('Not found')
    st.stop()

last = df.iloc[-1]
sup = float(df['Low'].tail(20).min())
res = float(df['High'].tail(20).max())

t1,t2,t3,t4,t5,t6,t7,t8 = st.tabs(['Indian Chart','5min','Compare','Option Chain','AI','Screener','Watchlist KING','PDF'])

with t1:
    txt = ticker + ' LTP ' + str(round(float(last['Close']),2))
    st.write(txt)
    bse_sym = 'BSE:' + clean
    html_code = '<div style="height:600px;border:1px solid #00D1FF"><iframe src="https://s.tradingview.com/widgetembed/?symbol=' + bse_sym + '&interval=D&theme=dark&style=1&timezone=Asia/Kolkata" style="width:100%;height:100%;border:none"></iframe></div>'
    components.html(html_code, height=620)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']))
    fig.add_trace(go.Scatter(x=df.index, y=[sup]*len(df), mode='lines', line=dict(color='green', dash='dash'), name='Support'))
    fig.add_trace(go.Scatter(x=df.index, y=[res]*len(df), mode='lines', line=dict(color='red', dash='dash'), name='Resist'))
    fig.update_layout(height=500, template='plotly_dark', xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

with t2:
    df2 = load_data(ticker, per='1d', interval='5m')
    fig2 = go.Figure()
    fig2.add_trace(go.Candlestick(x=df2.index, open=df2['Open'], high=df2['High'], low=df2['Low'], close=df2['Close']))
    fig2.update_layout(height=500, template='plotly_dark', xaxis_rangeslider_visible=False)
    st.plotly_chart(fig2, use_container_width=True)

with t3:
    s1 = st.text_input('Stock 1', 'RELIANCE.NS')
    s2 = st.text_input('Stock 2', 'TCS.NS')
    if st.button('Compare'):
        d1 = load_data(s1, '6mo')
        d2 = load_data(s2, '6mo')
        d1['N'] = d1['Close']/d1['Close'].iloc[0]*100
        d2['N'] = d2['Close']/d2['Close'].iloc[0]*100
        f3 = go.Figure()
        f3.add_trace(go.Scatter(x=d1.index, y=d1['N'], name=s1))
        f3.add_trace(go.Scatter(x=d2.index, y=d2['N'], name=s2))
        f3.update_layout(height=400, template='plotly_dark')
        st.plotly_chart(f3, use_container_width=True)

with t4:
    tk = yf.Ticker(ticker)
    opts = tk.options
    if len(opts) > 0:
        sel = st.select
