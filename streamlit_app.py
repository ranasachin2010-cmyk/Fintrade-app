import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from fpdf import FPDF
import urllib.parse

st.set_page_config(page_title='FinTrade V14.1 FIXED', layout='wide')

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');
* { font-family: 'Poppins', sans-serif; }
.stApp { background: radial-gradient(circle at 20% 20%, #0a1628 0%, #000000 100%); }
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.05)!important;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px!important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    background: linear-gradient(90deg, #00D1FF, #FFD700)!important;
    color: black!important;
    font-weight: 800!important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="background: linear-gradient(90deg,#00D1FF,#FFD700);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:40px;">💎 FinTrade V14.1 PREMIUM INDIAN FIXED</h1>', unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_data(tick, per='6mo', interval='1d'):
    df = yf.download(tick, period=per, interval=interval, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def rsi_calc(data):
    d = data['Close'].diff()
    g = d.where(d>0,0).rolling(14).mean()
    l = (-d.where(d<0,0)).rolling(14).mean()
    return 100 - (100/(1+g/l))

# FIXED PDF - Ab koi bracket nahi tootega
def make_pdf(ticker, ltp, sup, res, trend):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial','B',16)
    title = 'FinTrade V14.1 ' + str(ticker)
    pdf.cell(0,10,title,ln=True,align='C')
    pdf.set_font('Arial','',12)
    pdf.ln(10)
    line1 = 'LTP ' + str(round(float(ltp),2))
    line2 = 'Support ' + str(round(float(sup),2)) + ' Resistance ' + str(round(float(res),2))
    line3 = 'Trend ' + str(trend)
    pdf.cell(0,10,line1,ln=True)
    pdf.cell(0,10,line2,ln=True)
    pdf.cell(0,10,line3,ln=True)
    return bytes(pdf.output())

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['RELIANCE.NS','TCS.NS','INFY.NS']

with st.sidebar:
    st.title('V14.1 FIXED')
    u = st.text_input('NSE Stock', value='RELIANCE').upper().strip()
    ticker = u if '.NS' in u else u + '.NS'
    clean = u.replace('.NS','')
    if st.button('Refresh'):
        st.cache_data.clear()
        st.rerun()

df = load_data(ticker, '6mo', '1d')
if df.empty:
    st.error('Stock not found')
    st.stop()

df['RSI'] = rsi_calc(df)
last = df.iloc[-1]
sup = float(df['Low'].tail(20).min())
res = float(df['High'].tail(20).max())
trend = 'BUY' if float(df['Close'].rolling(20).mean().iloc[-1]) > float(df['Close'].rolling(50).mean().iloc[-1]) else 'WAIT'

tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8 = st.tabs(['Indian Chart','5min','Compare','Option Chain','AI Forecast','Screener','Watchlist','PDF'])

with tab1:
    st.write(f'{ticker} LTP {float(last["Close"]):.2f} S {sup:.0f} R {res:.0f}')
    bse_sym = 'BSE:' + clean
    html_code = '<div style="height:600px;border:1px solid #00D1FF"><iframe src="https://s.tradingview.com/widgetembed/?symbol=' + bse_sym + '&interval=D&theme=dark&style=1&timezone=Asia/Kolkata" style="width:100%;height:100%;border:none"></iframe></div>'
    components.html(html_code, height=620)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']))
    fig.add_hline(y=sup, line_dash='dash', line_color='green')
    fig.add_hline
