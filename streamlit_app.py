import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from fpdf import FPDF
import urllib.parse

st.set_page_config(page_title='FinTrade V13.1 NSE FIX', layout='wide')
st.markdown('<h2 style="color:#00D1FF">FinTrade V13.1 - 100% INDIAN NSE/BSE FIXED</h2>', unsafe_allow_html=True)
st.info('Fix: TradingView NSE block karta hai Apple dikhata hai, isliye ab BSE + Plotly NSE use kiya hai - 100% Indian!')

@st.cache_data(ttl=300)
def load_data(tick, per='6mo', interval='1d'):
    df = yf.download(tick, period=per, interval=interval, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def make_pdf(ticker, ltp, sup, res):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f'FinTrade {ticker}', ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.ln(5)
    pdf.cell(0, 10, f'LTP {float(ltp):.2f} S {float(sup):.2f} R {float(res):.2f}', ln=True)
    return bytes(pdf.output())

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['RELIANCE.NS','TCS.NS','INFY.NS','HDFCBANK.NS']

with st.sidebar:
    u = st.text_input('NSE Stock likho', value='RELIANCE').upper().strip()
    ticker = u if '.NS' in u else u + '.NS'
    clean = u.replace('.NS','')
    if st.button('Refresh'):
        st.cache_data.clear()
        st.rerun()

df = load_data(ticker, '6mo', '1d')
if df.empty:
    st.error('Stock nahi mila')
    st.stop()

last = df.iloc[-1]
sup = float(df['Low'].tail(20).min())
res = float(df['High'].tail(20).max())

t1,t2,t3,t4,t5,t6,t7,t8 = st.tabs(['Indian Chart','5min','Compare','Option Chain','AI Forecast','Screener','Watchlist','PDF'])

with t1:
    st.subheader(f'{ticker} - LTP {float(last["Close"]):.2f} - 100% NSE Data from Yahoo')

    # FIX 1: BSE symbol for TradingView - BSE data is FREE, NSE is paid on TradingView
    # RELIANCE ka BSE code same hai, price same hai
    bse_symbol = f'BSE:{clean}'
    st.write(f'TradingView (BSE Free Data - {bse_symbol}) - NSE/BSE price same hota hai')
    html_bse = f'<div style="height:600px;border:1px solid #00D1FF"><iframe src="https://s.tradingview.com/widgetembed/?symbol={bse_symbol}&interval=D&theme=dark&style=1&timezone=Asia/Kolkata&hidesidetoolbar=0&withdateranges=1" style="width:100%;height:100%;border:none"></iframe></div>'
    components.html(html_bse, height=620)

    st.divider()
    st.write('Main Chart - 100% NSE Data (Yahoo Finance - Ye kabhi Apple nahi dikhayega)')
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='NSE'))
    fig.add_hline(y=sup, line_dash='dash', line_color='green', annotation_text=f'Support {sup:.0f}')
    fig.add_hline(y=res, line_dash='dash', line_color='red', annotation_text=f'Resist {res:.0f}')
    fig.update_layout(height=550, template='plotly_dark', xaxis_rangeslider_visible=False, title=f'{ticker} - REAL NSE DATA')
    st.plotly_chart(fig, use_container_width=True)
    st.success('Ye wala chart hamesha Indian hi dikhayega, Apple kabhi nahi!')

with t2:
    df2 = load_data(ticker, per='1d', interval='5m')
    f2 = go.Figure()
    f2.add_trace(go.Candlestick(x=df2.index, open=df2['Open'], high=df2['High'], low=df2['Low'], close=df2['Close']))
    f2.update_layout(height=500, template='plotly_dark', xaxis_rangeslider_visible=False)
    st.plotly_chart(f2, use_container_width=True)

with t3:
    s1 = st.text_input('Stock 1', 'RELIANCE.NS')
    s2 = st.text_input('Stock 2', 'TCS.NS')
    if st.button('Compare'):
        d1 = load_data(s1, '6mo'); d2 = load_data(s2, '6mo')
        d1['N'] = d1['Close']/d1['Close'].iloc[0]*100; d2['N'] = d2['Close']/d2['Close'].iloc[0]*100
        f3 = go.Figure(); f3.add_trace(go.Scatter(x=d1.index, y=d1['N'], name=s1)); f3.add_trace(go.Scatter(x=d2.index, y=d2['N'], name=s2))
        f3.update_layout(height=400, template='plotly_dark'); st.plotly_chart(f3, use_container_width=True)

with t4:
    tk = yf.Ticker(ticker); opts = tk.options
    if len(opts) > 0:
        sel = st.selectbox('Expiry', opts[:5]); oc = tk.option_chain(sel)
        st.dataframe(oc.calls[['strike','lastPrice','openInterest']].head(10), use_container_width=True)

with t5:
    yv = df['Close'].dropna().values; xv = np.arange(len(yv))
    if len(yv) > 30:
        slope, inter = np.polyfit(xv, yv, 1); fx = np.arange(len(yv), len(yv)+7); fy = slope*fx+inter
        fd = pd.date_range(df.index[-1]+pd.Timedelta(days=1), periods=7, freq='B')
        f4 = go.Figure(); f4.add_trace(go.Scatter(x=df.index, y=yv, name='Actual')); f4.add_trace(go.Scatter(x=fd, y=fy, name='Forecast', line=dict(dash='dash')))
        f4.update_layout(height=400, template='plotly_dark'); st.plotly_chart(f4, use_container_width=True)

with t6:
    if st.button('Run Screener'):
        rows=[];
        for s in ['RELIANCE.NS','TCS.NS','INFY.NS','HDFCBANK.NS']: d=load_data(s); rows.append({'Stock':s,'LTP':round(float(d['Close'].iloc[-1]),2)})
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

with t7:
    if st.button('Check Watchlist'):
        rows=[];
        for s in st.session_state.watchlist: d=load_data(s, per='1y'); rows.append({'Stock':s,'LTP':round(float(d['Close'].iloc[-1]),2),'52W High':round(float(d['High'].max()),2)})
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

with t8:
    pdfb = make_pdf(ticker, last['Close'], sup, res)
    st.download_button('Download PDF', data=pdfb, file_name=f'{clean}_Report.pdf', mime='application/pdf')
    txt = f'FinTrade {ticker} LTP {float(last["Close"]):.2f}'
    st.link_button('WhatsApp Share', f'https://wa.me/?text={urllib.parse.quote(txt)}')
