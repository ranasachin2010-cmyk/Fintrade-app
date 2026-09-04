import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from fpdf import FPDF
import urllib.parse

st.set_page_config(page_title='FinTrade V12.4 FINAL', layout='wide')

@st.cache_data(ttl=300)
def load_data(tick, per='6mo', interval='1d'):
    df = yf.download(tick, period=per, interval=interval, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def rsi_calc(data, w=14):
    d = data['Close'].diff()
    g = d.where(d > 0, 0).rolling(w).mean()
    l = (-d.where(d < 0, 0)).rolling(w).mean()
    return 100 - (100 / (1 + g / l))

def create_pdf(ticker, ltp, sup, res, trend):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f'FinTrade V12.4 - {ticker}', ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.ln(10)
    pdf.cell(0, 10, f'LTP: {float(ltp):.2f} S:{float(sup):.2f} R:{float(res):.2f} {trend}', ln=True)
    return bytes(pdf.output())

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['RELIANCE.NS','TCS.NS','INFY.NS']

with st.sidebar:
    st.title('V12.4 FINAL')
    user_input = st.text_input('NSE Stock', value='RELIANCE').upper().strip()
    ticker = user_input if '.NS' in user_input else user_input + '.NS'
    clean = user_input.replace('.NS','')
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
trend = 'BUY' if df['Close'].rolling(20).mean().iloc[-1] > df['Close'].rolling(50).mean().iloc[-1] else 'WAIT'

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(['TradingView NSE','5min','Compare','Option Chain','AI Forecast','Screener','Watchlist','PDF'])

with tab1:
    st.write(f'{ticker} LTP {last["Close"]:.2f} S {sup:.0f} R {res:.0f}')
    tv_symbol = f'NSE:{clean}'
    html = f'<div style="height:600px"><iframe src="https://s.tradingview.com/widgetembed/?symbol={tv_symbol}&interval=D&theme=dark&style=1&timezone=Asia/Kolkata" style="width:100%;height:100%;border:none"></iframe></div>'
    components.html(html, height=620)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']))
    fig.add_hline(y=sup, line_dash='dash', line_color='green')
    fig.add_hline(y=res, line_dash='dash', line_color='red')
    fig.update_layout(height=500, template='plotly_dark', xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    df2 = load_data(ticker, per='1d', interval='5m')
    if not df2.empty:
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
        d1['Norm'] = d1['Close']/d1['Close'].iloc[0]*100
        d2['Norm'] = d2['Close']/d2['Close'].iloc[0]*100
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=d1.index, y=d1['Norm'], name=s1))
        fig3.add_trace(go.Scatter(x=d2.index, y=d2['Norm'], name=s2))
        fig3.update_layout(height=400, template='plotly_dark')
        st.plotly_chart(fig3, use_container_width=True)

with tab4:
    try:
