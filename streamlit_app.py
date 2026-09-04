import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from fpdf import FPDF
import urllib.parse

st.set_page_config(page_title='FinTrade V15.2 ZOMATO FIX', layout='wide')
st.markdown('<h1 style="color:#00D1FF">💎 FinTrade V15.2 WATCHLIST KING - SMART FINDER</h1>', unsafe_allow_html=True)

# SMART TICKER MAP - New names
TICKER_MAP = {
'ZOMATO':'ETERNAL.NS',
'ETERNAL':'ETERNAL.NS',
'PAYTM':'PAYTM.NS',
'PAYTMLAB':'PAYTM.NS',
'IRCTC':'IRCTC.NS',
'MAMA':'MAMAEARTH.NS',
'MAMAEARTH':'MAMAEARTH.NS',
'NYKAA':'NYKAA.NS',
'POLICY':'POLICYBZR.NS',
'POLICYBZR':'POLICYBZR.NS',
'DELHIVERY':'DELHIVERY.NS',
'LIC':'LICI.NS',
'ADANI':'ADANIENT.NS'
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

def make_pdf(ticker, ltp):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial','B',14)
    title = 'FinTrade ' + str(ticker)
    pdf.cell(0,10,title,ln=True,align='C')
    pdf.set_font('Arial','',11)
    pdf.ln(5)
    line = 'LTP ' + str(round(float(ltp),2))
    pdf.cell(0,10,line,ln=True)
    out = pdf.output()
    return bytes(out)

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['RELIANCE.NS','TCS.NS','ETERNAL.NS','PAYTM.NS','INFY.NS']

with st.sidebar:
    st.title('V15.2 SMART')
    u = st.text_input('NSE Stock (Zomato, Paytm ok)', value='RELIANCE').strip()
    ticker = resolve_ticker(u)
    clean = ticker.replace('.NS','')
    st.caption('Resolved: ' + ticker)
    if st.button('Refresh'):
        st.cache_data.clear()
        st.rerun()

df = load_data(ticker, '6mo', '1d')
if df.empty:
    st.error(ticker + ' Not found. Try: ETERNAL for Zomato, PAYTM, IRCTC, LICI')
    # Try fallback - search
    fallback = u.upper().strip() + '.NS'
    df2 = load_data(fallback, '6mo', '1d')
    if not df2.empty:
        st.warning('Found as ' + fallback + ' - Please use that')
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
        sel = st.selectbox('Expiry', opts[:5])
        oc = tk.option_chain(sel)
        df_calls = oc.calls
        st.write('CALLS')
        st.dataframe(df_calls.head(10), use_container_width=True)
        df_puts = oc.puts
        st.write('PUTS')
        st.dataframe(df_puts.head(10), use_container_width=True)

with t5:
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
        for s in ['RELIANCE.NS','TCS.NS','INFY.NS','HDFCBANK.NS']:
            d = load_data(s)
            val = round(float(d['Close'].iloc[-1]),2)
            rows.append({'Stock':s,'LTP':val})
        df_rows = pd.DataFrame(rows)
        st.dataframe(df_rows, use_container_width=True)

with t7:
    st.write('WATCHLIST KING - Smart Finder')
    new_stock = st.text_input('Add Stock e.g. Zomato, Paytm, Irctc').upper().strip()
    if st.button('Add to Watchlist'):
        if new_stock:
            full = resolve_ticker(new_stock)
            if full not in st.session_state.watchlist:
                st.session_state.watchlist.append(full)
                st.success(full + ' Added')
                st.rerun()
    if st.button('Load Watchlist 52W'):
        rows=[]
        for s in st.session_state.watchlist:
            d = load_data(s, per='1y')
            if not d.empty:
                ltp = round(float(d['Close'].iloc[-1]),2)
                high = round(float(d['High'].max()),2)
                low = round(float(d['Low'].min()),2)
                rows.append({'Stock':s,'LTP':ltp,'High52':high,'Low52':low})
        df_final = pd.DataFrame(rows)
        st.dataframe(df_final, use_container_width=True)
        st.balloons()
    st.write(', '.join(st.session_state.watchlist))

with t8:
    pdfb = make_pdf(ticker, last['Close'])
    st.download_button('Download PDF', data=pdfb, file_name='Report.pdf', mime='application/pdf')
    txt_msg = 'FinTrade ' + ticker
    link = 'https://wa.me/?text=' + urllib.parse.quote(txt_msg)
    st.link_button('WhatsApp Share', link)
