import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from fpdf import FPDF
import urllib.parse

st.set_page_config(page_title='FinTrade V13 FINAL', layout='wide')
st.markdown('<h2 style="color:#00D1FF">FinTrade V13 - FINAL WORKING - No Delete</h2>', unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_data(tick, per='6mo', interval='1d'):
    df = yf.download(tick, period=per, interval=interval, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def rsi_calc(data):
    d = data['Close'].diff()
    g = d.where(d > 0, 0).rolling(14).mean()
    l = (-d.where(d < 0, 0)).rolling(14).mean()
    return 100 - (100 / (1 + g / l))

def make_pdf(ticker, ltp, sup, res):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f'FinTrade V13 {ticker}', ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.ln(5)
    pdf.cell(0, 10, f'LTP {float(ltp):.2f} Support {float(sup):.2f} Resistance {float(res):.2f}', ln=True)
    return bytes(pdf.output())

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['RELIANCE.NS','TCS.NS','INFY.NS','HDFCBANK.NS']

with st.sidebar:
    st.title('V13 FINAL')
    u = st.text_input('NSE Stock', value='RELIANCE').upper().strip()
    ticker = u if '.NS' in u else u + '.NS'
    clean = u.replace('.NS','')
    if st.button('Refresh'):
        st.cache_data.clear()
        st.rerun()

df = load_data(ticker, '6mo', '1d')
if df.empty:
    st.error('Stock not found, check symbol')
    st.stop()

df['RSI'] = rsi_calc(df)
df['SMA20'] = df['Close'].rolling(20).mean()
df['SMA50'] = df['Close'].rolling(50).mean()
last = df.iloc[-1]
sup = float(df['Low'].tail(20).min())
res = float(df['High'].tail(20).max())

t1,t2,t3,t4,t5,t6,t7,t8 = st.tabs(['TradingView NSE','5min','Compare','Option Chain','AI Forecast','Screener','Watchlist 52W','PDF Share'])

with t1:
    st.write(f'{ticker} LTP {float(last["Close"]):.2f} S {sup:.0f} R {res:.0f}')
    sym = f'NSE:{clean}'
    html = f'<div style="height:600px;border:1px solid #00D1FF"><iframe src="https://s.tradingview.com/widgetembed/?symbol={sym}&interval=D&theme=dark&style=1&timezone=Asia/Kolkata" style="width:100%;height:100%;border:none"></iframe></div>'
    components.html(html, height=620)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']))
    fig.add_hline(y=sup, line_dash='dash', line_color='green')
    fig.add_hline(y=res, line_dash='dash', line_color='red')
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
    if st.button('Compare Now'):
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
    st.write('Option Chain - NSE')
    tk = yf.Ticker(ticker)
    opts = tk.options
    if len(opts) > 0:
        sel = st.selectbox('Expiry', opts[:5])
        oc = tk.option_chain(sel)
        st.write('CALLS')
        st.dataframe(oc.calls[['strike','lastPrice','openInterest']].head(10), use_container_width=True)
        st.write('PUTS')
        st.dataframe(oc.puts[['strike','lastPrice','openInterest']].head(10), use_container_width=True)

with t5:
    st.write('AI 7 Day Forecast')
    yv = df['Close'].dropna().values
    xv = np.arange(len(yv))
    if len(yv) > 30:
        slope, inter = np.polyfit(xv, yv, 1)
        fx = np.arange(len(yv), len(yv)+7)
        fy = slope*fx+inter
        fd = pd.date_range(df.index[-1]+pd.Timedelta(days=1), periods=7, freq='B')
        f4 = go.Figure()
        f4.add_trace(go.Scatter(x=df.index, y=yv, name='Actual'))
        f4.add_trace(go.Scatter(x=fd, y=fy, name='Forecast', line=dict(dash='dash')))
        f4.update_layout(height=400, template='plotly_dark')
        st.plotly_chart(f4, use_container_width=True)

with t6:
    if st.button('Run Screener'):
        rows=[]
        for s in ['RELIANCE.NS','TCS.NS','INFY.NS','HDFCBANK.NS','SBIN.NS']:
            d = load_data(s)
            rows.append({'Stock':s,'LTP':round(float(d['Close'].iloc[-1]),2)})
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

with t7:
    if st.button('Check Watchlist 52W'):
        rows=[]
        for s in st.session_state.watchlist:
            d = load_data(s, per='1y')
            rows.append({'Stock':s,'LTP':round(float(d['Close'].iloc[-1]),2),'52W High':round(float(d['High'].max()),2),'52W Low':round(float(d['Low'].min()),2)})
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

with t8:
    pdfb = make_pdf(ticker, last['Close'], sup, res)
    st.download_button('Download PDF', data=pdfb, file_name=f'{clean}_Report.pdf', mime='application/pdf')
    txt = f'FinTrade V13 {ticker} LTP {float(last["Close"]):.2f} S {sup:.0f} R {res:.0f}'
    st.link_button('Share on WhatsApp', f'https://wa.me/?text={urllib.parse.quote(txt)}')
