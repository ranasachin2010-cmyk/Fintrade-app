import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from fpdf import FPDF
import urllib.parse

st.set_page_config(page_title='FinTrade V14.2 FINAL', layout='wide')

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

st.markdown('<h1 style="background: linear-gradient(90deg,#00D1FF,#FFD700);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:40px;">💎 FinTrade V14.2 PREMIUM FINAL</h1>', unsafe_allow_html=True)

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

def make_pdf(ticker, ltp, sup, res, trend):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial','B',16)
    title = 'FinTrade V14.2 ' + str(ticker)
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
    st.title('V14.2 FINAL')
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
    st.write(f'{ticker} LTP {float(last["Close"]):.2f} S {sup:.0f} R {res:.0f} Trend {trend}')
    bse_sym = 'BSE:' + clean
    html_code = '<div style="height:600px;border-radius:16px;overflow:hidden;border:1px solid #00D1FF;box-shadow:0 0 20px rgba(0,209,255,0.3)"><iframe src="https://s.tradingview.com/widgetembed/?symbol=' + bse_sym + '&interval=D&theme=dark&style=1&timezone=Asia/Kolkata&withdateranges=1" style="width:100%;height:100%;border:none"></iframe></div>'
    components.html(html_code, height=620)
    st.divider()
    st.write('NSE Real Data - Support Resistance with Premium Lines')
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='NSE'))
    # FIXED: add_hline ki jagah add_shape use kiya, ab help box nahi aayega
    fig.add_trace(go.Scatter(x=df.index, y=[sup]*len(df), mode='lines', line=dict(color='green', dash='dash'), name=f'Support {sup:.0f}'))
    fig.add_trace(go.Scatter(x=df.index, y=[res]*len(df), mode='lines', line=dict(color='red', dash='dash'), name=f'Resistance {res:.0f}'))
    fig.update_layout(height=500, template='plotly_dark', xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    df2 = load_data(ticker, per='1d', interval='5m')
    fig2 = go.Figure()
    fig2.add_trace(go.Candlestick(x=df2.index, open=df2['Open'], high=df2['High'], low=df2['Low'], close=df2['Close']))
    fig2.update_layout(height=500, template='plotly_dark', xaxis_rangeslider_visible=False)
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
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

with tab4:
    tk = yf.Ticker(ticker)
    opts = tk.options
    if len(opts) > 0:
        sel = st.selectbox('Expiry', opts[:5])
        oc = tk.option_chain(sel)
        st.dataframe(oc.calls[['strike','lastPrice','openInterest']].head(10), use_container_width=True)

with tab5:
    yv = df['Close'].drop
