import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from fpdf import FPDF
import urllib.parse

st.set_page_config(page_title="FinTrade V11.1 FIXED", layout="wide", page_icon="👑")
st.markdown('<h1 style="background: linear-gradient(90deg,#00D1FF,#FFD700);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:900;">👑 FinTrade V11.1 - PDF FIXED FINAL</h1>', unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_data(tick, per="6mo", interval="1d"):
    df = yf.download(tick, period=per, interval=interval, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def rsi(data,w=14):
    d=data['Close'].diff()
    g=(d.where(d>0,0)).rolling(w).mean()
    l=(-d.where(d<0,0)).rolling(w).mean()
    return 100-(100/(1+g/l))

def create_pdf(ticker, ltp, rsi_val, sup, res, trend):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 10, f"FinTrade V11 Report - {ticker}", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Date: {pd.Timestamp.now().strftime('%d-%m-%Y')}", ln=True)
    pdf.cell(0, 10, f"LTP: {float(ltp):.2f} | RSI: {float(rsi_val):.2f}", ln=True)
    pdf.cell(0, 10, f"Support: {float(sup):.2f} | Resistance: {float(res):.2f}", ln=True)
    pdf.cell(0, 10, f"Trend: {trend}", ln=True)
    # FIXED LINE - Naya fpdf2 direct bytes deta hai
    return bytes(pdf.output())

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ["RELIANCE.NS","TCS.NS","INFY.NS"]

with st.sidebar:
    st.title("V11.1 FIXED")
    user_input = st.text_input("NSE Stock", value="RELIANCE").upper().strip()
    ticker = user_input if ".NS" in user_input or "^" in user_input else user_input + ".NS"
    clean = user_input.replace(".NS","")
    voice_on = st.checkbox("Voice Alert ON", value=True)
    if st.button("Refresh"):
        st.cache_data.clear()
        st.rerun()

st.subheader("Market Dashboard LIVE")
m1,m2,m3,m4 = st.columns(4)
for idx, sym, name in [(0,"^NSEI","NIFTY"), (1,"^NSEBANK","BANKNIFTY"), (2,"^BSESN","SENSEX"), (3,"INR=X","USD/INR")]:
    try:
        d=load_data(sym, per="2d")
        l=d.iloc[-1]['Close']; p=d.iloc[-2]['Close']; ch=(l-p)/p*100
        [m1,m2,m3,m4][idx].metric(name, f"{l:.2f}", f"{ch:.2f}%")
    except:
        [m1,m2,m3,m4][idx].metric(name, "Loading")

st.divider()
tab1, tab2, tab3 = st.tabs(["TradingView PRO [1]", "PDF + WhatsApp [2]", "Voice + Intraday [3]"])

df = load_data(ticker, "6mo", "1d")
if df.empty:
    st.error(f"{ticker} not found")
    st.stop()

df['RSI']=rsi(df)
df['SMA20']=df['Close'].rolling(20).mean()
df['SMA50']=df['Close'].rolling(50).mean()
last=df.iloc[-1]
sup = float(df['Low'].tail(20).min())
res = float(df['High'].tail(20).max())
trend = "STRONG BUY" if last['SMA20']>last['SMA50'] else "WAIT"

alert_msg = ""
if abs(last['Close']-res)/last['Close'] < 0.02:
    alert_msg = f"Alert! {clean} near resistance {int(res)}"
elif abs(last['Close']-sup)/last['Close'] < 0.02:
    alert_msg = f"Alert! {clean} near support {int(sup)}"

if voice_on and alert_msg:
    components.html(f"<script>var msg=new SpeechSynthesisUtterance('{alert_msg}');window.speechSynthesis.speak(msg);</script><div style='background:#ff4444;color:white;padding:10px;border-radius:10px;text-align:center'><b>🔊 {alert_msg}</b></div>", height=60)

with tab1:
    st.subheader(f"TradingView PRO - {ticker}")
    tv_symbol = f"NSE:{clean}"
    tv_widget = """
    <div id="tradingview_chart" style="height:500px"></div>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
    new TradingView.widget({
      "autosize": true,
      "symbol": "%s",
      "interval": "D",
      "timezone": "Asia/Kolkata",
      "theme": "dark",
      "style": "1",
      "locale": "in",
      "container_id": "tradingview_chart",
      "width": "100%%",
      "height": 500
    });
    </script>
    """ % tv_symbol
    components.html(tv_widget, height=520)

with tab2:
    st.subheader("PDF + WhatsApp - FIXED")
    pdf_bytes = create_pdf(ticker, last['Close'], last['RSI'], sup, res, trend)
    colA, colB = st.columns(2)
    with colA:
        st.download_button("📥 Download PDF", data=pdf_bytes, file_name=f"{clean}_Report.pdf", mime="application/pdf", use_container_width=True)
    with colB:
        share_text = f"FinTrade V11: {ticker} LTP {float(last['Close']):.2f} S:{sup:.2f} R:{res:.2f} Trend {trend}"
        wa_link = f"https://wa.me/?text={urllib.parse.quote(share_text)}"
        st.link_button("📤 Share on WhatsApp", wa_link, use_container_width=True)
    st.success("✅ PDF Error Fixed! Ab download hoga")

with tab3:
    st.subheader("Voice + Intraday 5min")
    if voice_on:
        if st.button("🔊 Test Voice"):
            components.html(f"<script>var msg=new SpeechSynthesisUtterance('V11 fixed for {clean}');window.speechSynthesis.speak(msg);</script>", height=0)
    df_intra = load_data(ticker, per="1d", interval="5m")
    if not df_intra.empty:
        fig2=go.Figure()
        fig2.add_trace(go.Candlestick(x=df_intra.index, open=df_intra['Open'], high=df_intra['High'], low=df_intra['Low'], close=df_intra['Close']))
        fig2.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig2, use_container_width=True)
