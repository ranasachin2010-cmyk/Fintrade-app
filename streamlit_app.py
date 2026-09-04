import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from fpdf import FPDF
import urllib.parse

st.set_page_config(page_title="FinTrade V12.2 FIXED", layout="wide", page_icon="💎")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');
* { font-family: 'Poppins', sans-serif; }
.stApp { background: radial-gradient(circle at 20% 20%, #0a1628 0%, #000000 100%); }
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.05)!important;
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px!important;
    box-shadow: 0 8px 32px rgba(0,209,255,0.15);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="background: linear-gradient(90deg,#00D1FF,#FFD700);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:40px;">💎 FinTrade V12.2 - NSE FIXED FINAL</h1>', unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_data(tick, per="6mo", interval="1d"):
    df = yf.download(tick, period=per, interval=interval, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def rsi(data, w=14):
    d = data['Close'].diff()
    g = d.where(d > 0, 0).rolling(w).mean()
    l = (-d.where(d < 0, 0)).rolling(w).mean()
    return 100 - (100 / (1 + g / l))

def create_pdf(ticker, ltp, sup, res, trend):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 10, f"FinTrade V12.2 - {ticker}", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"LTP: {float(ltp):.2f} | S: {float(sup):.2f} R: {float(res):.2f}", ln=True)
    pdf.cell(0, 10, f"Trend: {trend}", ln=True)
    return bytes(pdf.output())

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"]

with st.sidebar:
    st.title("V12.2 FIXED")
    user_input = st.text_input("Search NSE Stock", value="RELIANCE").upper().strip()
    ticker = user_input if ".NS" in user_input or "^" in user_input else user_input + ".NS"
    clean = user_input.replace(".NS", "")
    voice_on = st.checkbox("Voice Alert ON", value=True)
    if st.button("Refresh"):
        st.cache_data.clear()
        st.rerun()

df = load_data(ticker, "6mo", "1d")
if df.empty:
    st.error(f"{ticker} not found")
    st.stop()

df['RSI'] = rsi(df)
df['SMA20'] = df['Close'].rolling(20).mean()
df['SMA50'] = df['Close'].rolling(50).mean()
last = df.iloc[-1]
sup = float(df['Low'].tail(20).min())
res = float(df['High'].tail(20).max())
trend = "STRONG BUY" if last['SMA20'] > last['SMA50'] else "WAIT"

# Voice Alert
alert_msg = ""
if abs(last['Close'] - res) / last['Close'] < 0.02:
    alert_msg = f"Alert {clean} near resistance {int(res)}"
elif abs(last['Close'] - sup) / last['Close'] < 0.02:
    alert_msg = f"Alert {clean} near support {int(sup)}"
if voice_on and alert_msg:
    components.html(f"<script>var msg=new SpeechSynthesisUtterance('{alert_msg}');window.speechSynthesis.speak(msg);</script><div style='background:#ff4444;color:white;padding:10px;border-radius:10px;text-align:center'><b>{alert_msg}</b></div>", height=60)

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["TradingView NSE", "5min", "Compare", "Option Chain", "AI Forecast", "Screener", "Watchlist", "PDF Share"])

with tab1:
    st.markdown(f"#### {ticker} - LTP {last['Close']:.2f}")

    # FIXED: IFRAME NSE CHART - 100% Works for Indian Market
    tv_symbol = f"NSE:{clean}"
    iframe_html = f"""
    <div style="height:600px; border-radius:16px; overflow:hidden; border:1px solid #00D1FF;">
      <iframe src="https://s.tradingview.com/widgetembed/?symbol={tv_symbol}&interval=D&theme=dark&style=1&timezone=Asia/Kolkata&withdateranges=1&hide_side_toolbar=0"
      style="width:100%; height:100%; border:none;" frameborder="0"></iframe>
    </div>
    """
    components.html(iframe_html, height=620)

    st.divider()
    # Backup Plotly - Ye wala kabhi fail nahi hoga
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name=ticker))
    fig.add_hline(y=sup, line_dash="dash", line_color="green", annotation_text=f"Support {sup:.0f}")
    fig.add_hline(y=res, line_dash="dash", line_color="red", annotation_text=f"Resistance {res:.0f}")
    # FIXED LINE - Yahi line 129 thi jo error de rahi thi
    fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Intraday 5min")
    df_intra = load_data(ticker, per="1d", interval="5m")
    if not df_intra.empty:
        fig2 = go.Figure()
        fig2.add_trace(go.Candlestick(x=df_intra.index, open=df_intra['Open'], high=df_intra['High'], low=df_intra['Low'], close=df_intra['Close']))
        fig2.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig2, use_container_width=True)

with tab3:
    c1, c2 = st.columns(2)
    s1 = c1.text_input("Stock 1", value="RELIANCE.NS")
    s2 = c2.text_input("Stock 2", value="TCS.NS")
    if st.button("Compare Now"):
        d1 = load_data(s1, "6mo")
        d2 = load_data(s2, "6mo")
        d1['Norm'] = d1['Close'] / d1['Close'].iloc[0] * 100
        d2['Norm'] = d2['Close'] / d2['Close'].iloc[0] * 100
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=d1.index, y=d1['Norm'], name=s1))
        fig3.add_trace(go.Scatter(x=d2.index, y=d2['Norm'], name=s2))
        fig3.update_layout(height=400, template="plotly_dark")
        st.plotly_chart(fig3, use_container_width=True)

with tab4:
    st.subheader("Option Chain")
    try:
        tk = yf.Ticker(ticker)
        exps = tk.options
        if exps:
            sel = st.selectbox("Expiry", exps[:5])
            oc = tk.option_chain(sel)
            pcr = oc.puts['openInterest'].sum() / oc.calls['openInterest'].sum() if oc.calls['openInterest'].sum()!= 0 else 0
            st.metric("PCR", f"{pcr:.2f}")
            c1, c2 = st.columns(2)
            with c1:
                st.dataframe(oc.calls[['strike', 'lastPrice', 'openInterest']].head(10), use_container_width=True)
            with c2:
                st.dataframe(oc.puts[['strike', 'lastPrice', 'openInterest']].head(10), use_container_width=True)
    except:
        st.write("Option Chain - NSE Website")

with tab5:
    st.subheader("AI 7D Forecast")
    y_vals = df['Close'].values
    x_vals = np.arange(len(y_vals))
    slope, intercept = np.polyfit
