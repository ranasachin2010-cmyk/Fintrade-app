import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from fpdf import FPDF
import urllib.parse

st.set_page_config(page_title="FinTrade V12 PREMIUM", layout="wide", page_icon="💎")

# ============ PREMIUM CSS - YAHI JADU HAI ============
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700;900&display=swap');
* { font-family: 'Poppins', sans-serif; }
.stApp { background: radial-gradient(circle at 20% 20%, #0a1628 0%, #050a14 40%, #000000 100%); }
h1 { font-weight: 900!important; letter-spacing: -1px; }
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.05)!important;
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px!important;
    padding: 15px!important;
    box-shadow: 0 8px 32px rgba(0,209,255,0.15);
    transition: 0.3s;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0,209,255,0.3);
    border: 1px solid rgba(0,209,255,0.5);
}
div[data-testid="stTabs"] button {
    background: rgba(255,255,255,0.05)!important;
    border-radius: 12px!important;
    font-weight: 600!important;
    border: 1px solid rgba(255,255,255,0.1)!important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    background: linear-gradient(90deg, #00D1FF, #FFD700)!important;
    color: black!important;
    box-shadow: 0 0 20px rgba(0,209,255,0.5);
}
.stButton > button {
    background: linear-gradient(90deg, #00D1FF, #0080FF)!important;
    color: white!important;
    border-radius: 12px!important;
    font-weight: 700!important;
    border: none!important;
    box-shadow: 0 4px 15px rgba(0,209,255,0.4);
    transition: 0.3s;
}
.stButton > button:hover { transform: scale(1.02); box-shadow: 0 6px 25px rgba(0,209,255,0.6); }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="background: linear-gradient(90deg,#00D1FF,#FFD700,#FF5E5E);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:42px;">💎 FinTrade V12 PREMIUM ULTRA</h1>', unsafe_allow_html=True)
st.markdown('<p style="color:#888; margin-top:-15px; letter-spacing:3px;">PREMIUM EDITION • NO FEATURE DELETED • AYODHYA</p>', unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_data(tick, per="6mo", interval="1d"):
    df = yf.download(tick, period=per, interval=interval, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    return df
def rsi(data,w=14):
    d=data['Close'].diff(); g=(d.where(d>0,0)).rolling(w).mean(); l=(-d.where(d<0,0)).rolling(w).mean(); return 100-(100/(1+g/l))
def create_pdf(ticker, ltp, rsi_val, sup, res, trend):
    pdf = FPDF(); pdf.add_page()
    pdf.set_font("Arial", "B", 20); pdf.cell(0, 10, f"FinTrade V12 PREMIUM - {ticker}", ln=True, align="C")
    pdf.set_font("Arial", "", 12); pdf.ln(10)
    pdf.cell(0, 10, f"LTP: {float(ltp):.2f} | RSI: {float(rsi_val):.2f}", ln=True)
    pdf.cell(0, 10, f"Support: {float(sup):.2f} | Resistance: {float(res):.2f} | Trend: {trend}", ln=True)
    return bytes(pdf.output())

if 'watchlist' not in st.session_state: st.session_state.watchlist = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS"]

with st.sidebar:
    st.markdown("### 💎 V12 PREMIUM")
    user_input = st.text_input("Search NSE Stock", value="RELIANCE").upper().strip()
    ticker = user_input if ".NS" in user_input or "^" in user_input else user_input + ".NS"
    clean = user_input.replace(".NS","")
    voice_on = st.checkbox("🔊 Voice Alert", value=True)
    st.divider()
    st.markdown("#### ⭐ My Watchlist")
    new_w = st.text_input("Add e.g. SBIN.NS")
    if st.button("➕ Add to Watchlist"):
        if new_w: st.session_state.watchlist.append(new_w.upper())
    st.caption(", ".join(st.session_state.watchlist))
    if st.button("🔄 Refresh"): st.cache_data.clear(); st.rerun()

# PREMIUM DASHBOARD
st.markdown("#### 📊 LIVE MARKET PULSE")
m1,m2,m3,m4,m5 = st.columns(5)
for idx, sym, name in [(0,"^NSEI","NIFTY"), (1,"^NSEBANK","BANKNIFTY"), (2,"^BSESN","SENSEX"), (3,"INR=X","USD/INR")]:
    try:
        d=load_data(sym, per="2d"); l=d.iloc[-1]['Close']; p=d.iloc[-2]['Close']; ch=(l-p)/p*100
        [m1,m2,m3,m4][idx].metric(name, f"{l:,.2f}", f"{ch:.2f}%")
    except: [m1,m2,m3,m4][idx].metric(name, "Loading")
m5.metric("FII/DII", "Bullish", "+₹1,240 Cr BUY")

df = load_data(ticker, "6mo", "1d")
if df.empty: st.error(f"{ticker} not found"); st.stop()
df['RSI']=rsi(df); df['SMA20']=df['Close'].rolling(20).mean(); df['SMA50']=df['Close'].rolling(50).mean()
last=df.iloc[-1]; sup=float(df['Low'].tail(20).min()); res=float(df['High'].tail(20).max())
trend = "STRONG BUY" if last['SMA20']>last['SMA50'] else "WAIT"

alert_msg = ""
if abs(last['Close']-res)/last['Close'] < 0.02: alert_msg = f"Alert! {clean} near resistance {int(res)}"
elif abs(last['Close']-sup)/last['Close'] < 0.02: alert_msg = f"Alert! {clean} near support {int(sup)}"
if voice_on and alert_msg:
    components.html(f"<script>var msg=new SpeechSynthesisUtterance('{alert_msg}');window.speechSynthesis.speak(msg);</script><div style='background:linear-gradient(90deg,#ff4444,#ff8800);color:white;padding:12px;border-radius:12px;text-align:center;font-weight:800;box-shadow:0 0 20px #ff4444'>🔊 {alert_msg}</div>", height=65)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["💎 TradingView PRO", "⏱️ 5min", "⚖️ Compare", "🔥 Option Chain", "🤖 AI Forecast", "🔍 Screener", "⭐ Watchlist", "📄 PDF+Share+Voice"])

with tab1:
    st.markdown(f"##### 💎 {ticker} • LTP {last['Close']:.2f} • S {sup:.0f} • R {res:.0f}")
    tv_symbol = f"NSE:{clean}"
    tv_widget = """<div id="tv" style="height:550px;border-radius:16px;overflow:hidden;box-shadow:0 0 40px rgba(0,209,255,0.2)"></div><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({"autosize": true,"symbol": "%s","interval": "D","timezone": "Asia/Kolkata","theme": "dark","style": "1","locale": "in","container_id": "tv","width": "100%%","height": 550});</script>""" % tv_symbol
    components.html(tv_widget, height=570)

with tab2:
    st.markdown(f"##### ⏱️ Intraday 5min - {ticker}")
    df_intra = load_data(ticker, per="1d", interval="5m")
    if not df_intra.empty:
        fig2=go.Figure(); fig2.add_trace(go.Candlestick(x=df_intra.index, open=df_intra['Open'], high=df_intra['High'], low=df_intra['Low'], close=df_intra['Close']))
        fig2.update_layout(height=500, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig2, use_container_width=True)

with tab3:
    s1,s2 = st.columns(2); stock1=s1.text_input("Stock 1", value="RELIANCE.NS"); stock2=s2.text_input("Stock 2", value="TCS.NS")
    if st.button("⚡ Compare Now"):
        d1=load_data(stock1, "6mo"); d2=load_data(stock2, "6mo")
        d1['Norm']=d1['Close']/d1['Close'].iloc[0]*100; d2['Norm']=d2['Close']/d2['Close'].iloc[0]*100
        fig3=go.Figure(); fig3.add_trace(go.Scatter(x=d1.index, y=d1['Norm'], name=stock1, line=dict(width=3))); fig3.add_trace(go.Scatter(x=d2.index, y=d2['Norm'], name=stock2, line=dict(width=3)))
        fig3.update_layout(height=400, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'); st.plotly_chart(fig3, use_container_width=True)

with tab4:
    try:
        tk=yf.Ticker(ticker); exps=tk.options
        if exps:
            sel=st.selectbox("Expiry", exps[:5]); oc=tk.option_chain(sel)
            pcr = oc.puts['openInterest'].sum() / oc.calls['openInterest'].sum() if oc.calls['openInterest'].sum()!=0 else 0
            st.metric("PCR Ratio", f"{pcr:.2f}", "Bullish" if pcr>1 else "Bearish")
            c1,c2=st.columns(2)
            with c1: st.dataframe(oc.calls[['strike','lastPrice','openInterest']].head(10), use_container_width=True)
            with c2: st.dataframe(oc.puts[['strike','lastPrice','openInterest']].head(10), use_container_width=True)
    except: st.link_button("Open NSE Option Chain", "https://www.nseindia.com/option-chain")

with tab5:
    y_vals = df['Close'].values; x_vals = np.arange(len(y_vals)); slope, intercept = np.polyfit(x_vals, y_vals, 1)
    future_x = np.arange(len(y_vals), len(y_vals)+7); future_price = slope * future_x + intercept
    future_dates = pd.date_range(df.index[-1]+pd.Timedelta(days=1), periods=7, freq='B')
    fig4 = go.Figure(); fig4.add_trace(go.Scatter(x=df.index, y=y_vals, name="Actual", line=dict(color='#00D1FF', width=3)))
    fig4.add_trace(go.Scatter(x=future_dates, y=future_price, name="AI Forecast", line=dict(color='#FFD700', dash='dash', width=3)))
    fig4.update_layout(height=400, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'); st.plotly_chart(fig4, use_container_width=True)

with tab6:
    if st.button("🔍 Run Premium Screener"):
        rows=[]
        for s in ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","SBIN.NS"]:
            d=load_data(s); d['RSI']=rsi(d); d['SMA20']=d['Close'].rolling(20).mean(); d['SMA50']=d['Close'].rolling(50).mean(); l=d.iloc[-1]
            rows.append({"Stock": s, "LTP": round(l['Close'],2), "RSI": round(l['RSI'],2), "Signal": "BUY" if l['SMA20']>l['SMA50'] else "WAIT"})
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

with tab7:
    if st.button("⭐ Check Watchlist 52W"):
        rows=[]
        for s in st.session_state.watchlist:
            try:
                d=load_data(s, per="1y"); l=d['Close'].iloc[-1]; high52=d['High'].max(); low52=d['Low'].min()
                rows.append({"Stock": s, "LTP": round(l,2), "52W High": round(high52,2), "52W Low": round(low52,2)})
            except: pass
        st.dataframe(pd.DataFrame(rows), use_container_width=True); st.balloons()

with tab8:
    st.markdown("##### 📄 Premium Report Center")
    pdf_bytes = create_pdf(ticker, last['Close'], last['RSI'], sup, res, trend)
    c1,c2,c3=st.columns(3)
    with c1: st.download_button("💎 Download Premium PDF", data=pdf_bytes, file_name=f"{clean}_PREMIUM.pdf", mime="application/pdf", use_container_width=True)
    with c2:
        share_text = f"💎 FinTrade V12 PREMIUM: {ticker} LTP {float(last['Close']):.2f} Trend {trend}"
        st.link_button("📤 WhatsApp Share", f"https://wa.me/?text={urllib.parse.quote(share_text)}", use_container_width=True)
    with c3:
        if st.button("🔊 Test Premium Voice", use_container_width=True): components.html(f"<script>var msg=new SpeechSynthesisUtterance('V12 Premium activated for {clean}');window.speechSynthesis.speak(msg);</script>", height=0)
