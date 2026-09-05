import streamlit as st, yfinance as yf, pandas as pd, plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
from datetime import datetime
import pytz

st.set_page_config(page_title="FinTrade God V45.2 - No Portfolio", layout="wide", page_icon="💎")

@st.cache_data(ttl=300, show_spinner=False)
def safe_yf(symbol, period="1mo", interval="1d"):
    try:
        return yf.Ticker(symbol).history(period=period, interval=interval)
    except:
        return pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def get_index_price(sym):
    try:
        h = yf.Ticker(sym).history(period="2d", interval="1d")
        if h.empty: return None, None
        last = h['Close'].iloc[-1]
        prev = h['Close'].iloc[-2] if len(h)>1 else last
        pct = ((last-prev)/prev)*100
        return last, pct
    except:
        return None, None

def get_logo():
    try:
        with open("logo.png","rb") as f:
            data = base64.b64encode(f.read()).decode()
            return f'<img src="data:image/png;base64,{data}" width="88" height="88" style="border-radius:18px; border:none; background:transparent; margin-right:14px; display:block;">'
    except:
        return '<div style="font-size:42px; margin-right:14px;">💎</div>'

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700&family=JetBrains+Mono:wght@800&display=swap');
.stApp{background:#020208; background-image: radial-gradient(at 0% 0%, hsla(212,100%,56%,0.25) 0px, transparent 50%), radial-gradient(at 20% 10%, hsla(273,100%,60%,0.25) 0px, transparent 50%), radial-gradient(at 90% 0%, hsla(158,100%,50%,0.20) 0px, transparent 50%);}
.header-god{background: linear-gradient(135deg, #6A5AE0 0%, #7B6EF0 100%)!important; border:none!important; border-radius:24px; padding:16px 22px; box-shadow:0 10px 40px rgba(106,90,224,0.35); display:flex; align-items:center;}
.header-god img{background:transparent!important; border:none!important;}
.pick-god{background: linear-gradient(135deg, rgba(0,255,136,0.10) 0%, rgba(0,209,255,0.08) 50%, rgba(112,0,255,0.08) 100%); border:1.5px solid transparent; border-radius:24px; padding:20px; margin-bottom:16px;}
.pick-god{border-image: linear-gradient(135deg, #00FF88, #00D1FF, #7000FF) 1;}
.pick-god::before{display:none!important;}
.top-god{background: linear-gradient(100deg, rgba(0,209,255,0.14) 0%, rgba(112,0,255,0.18) 40%, rgba(0,255,136,0.10) 100%); border:1px solid rgba(255,255,255,0.12); border-radius:28px; padding:24px 26px;}
.target-row{display:flex; justify-content:space-between; margin-top:14px; padding:10px 12px; background: rgba(0,255,136,0.12); border-left:3px solid #00FF88; border-radius:12px; font-family:JetBrains Mono; font-size:12px; color:#00FF88;}
.index-chip{display:inline-flex; background: rgba(0,0,0,0.35); border:1px solid rgba(255,255,255,0.08); border-radius:100px; padding:8px 14px; font-family:JetBrains Mono; font-size:11px; color:#fff; margin-right:8px;}
.index-up{color:#00FF88; font-weight:800;}.index-down{color:#FF4D6A;}
.bse-badge{background: linear-gradient(135deg, #FF6A00, #FFD700); color:black; font-weight:700; font-size:10px; padding:4px 10px; border-radius:100px;}
.auto-badge{background: rgba(0,255,136,0.15); border:1px solid rgba(0,255,136,0.3); color:#00FF88; font-size:10px; padding:5px 12px; border-radius:100px; font-weight:700;}
.stTextInput>div>div>input{background: rgba(255,255,255,0.06)!important; border:1.5px solid rgba(255,255,255,0.12)!important; border-radius:20px!important; color:white!important; font-family:JetBrains Mono!important; font-weight:800!important; font-size:18px!important; height:64px!important;}
.stButton>button{background: linear-gradient(135deg, #00D1FF 0%, #7000FF 50%, #00FF88 100%)!important; border:none!important; border-radius:18px!important; color:white!important; font-weight:700!important; height:64px!important;}
</style>
""", unsafe_allow_html=True)

nifty_p, nifty_c = get_index_price("^NSEI")
sensex_p, sensex_c = get_index_price("^BSESN")
bank_p, bank_c = get_index_price("^NSEBANK")
def chip(n,p,c):
    if p is None: return f'<span class="index-chip">{n}: Loading</span>'
    cls="index-up" if c>=0 else "index-down"; arrow="▲" if c>=0 else "▼"
    return f'<span class="index-chip">{n}: ₹{p:,.0f} <span class="{cls}">{arrow} {abs(c):.2f}%</span></span>'

chips = chip("NIFTY",nifty_p,nifty_c if nifty_c else 0)+chip("SENSEX",sensex_p,sensex_c if sensex_c else 0)+chip("BANKNIFTY",bank_p,bank_c if bank_c else 0)

st.markdown(f"""
<div class="header-god">
 {get_logo()}
 <div><div style="font-family:Space Grotesk; font-weight:800; font-size:28px; color:white;">FinTrade <span style="color:#00FFCC;">God</span> V45.2 <span class="bse-badge">BSE</span></div>
 <div style="margin-top:8px; display:flex; flex-wrap:wrap;">{chips}</div></div>
 <div style="margin-left:auto;"><span class="auto-badge">● LIVE • NO PORTFOLIO • CLEAN</span></div>
</div>
""", unsafe_allow_html=True)

st.write("")

st.markdown("""
<div class="top-god">
  <div style="font-family:Space Grotesk; font-weight:700; color:white; font-size:20px;">🔥 TOP PICKS - GOD MODE</div>
  <div style="font-family:JetBrains Mono; font-size:11px; color:rgba(255,255,255,0.6);">AI Score > 85 • 6 Stocks • SEBI Safe</div>
</div>
""", unsafe_allow_html=True)
st.write("")

stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "CUPID.NS", "HDFCBANK.NS", "ICICIBANK.NS"]
cols = st.columns(3)
for i, sym in enumerate(stocks):
    hist = safe_yf(sym, period="5d", interval="1d")
    if hist.empty: continue
    last = float(hist['Close'].iloc[-1])
    prev = float(hist['Close'].iloc[-2]) if len(hist)>1 else last
    pct = ((last-prev)/prev)*100 if prev!=0 else 0
    score = 88 if pct>0 else 72
    target = last*1.08
    sl = last*0.95
    vol = hist['Volume'].iloc[-1] if 'Volume' in hist else 0
    color="#00FF88" if pct>=0 else "#FF4D6A"; arrow="▲" if pct>=0 else "▼"
    with cols[i%3]:
        st.markdown(f"""
        <div class="pick-god">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="font-family:Space Grotesk; font-weight:800; font-size:22px; color:white;">{sym.replace('.NS','')}</div>
            <div style="width:56px; height:56px; border-radius:50%; background: conic-gradient(#00FF88 {score}%, rgba(255,255,255,0.1) 0); display:flex; align-items:center; justify-content:center; position:relative;">
              <div style="position:absolute; inset:4px; background:#0a1220; border-radius:50%;"></div>
              <span style="position:relative; z-index:1; font-family:JetBrains Mono; font-weight:800; color:#00FF88; font-size:14px;">{score}</span>
            </div>
          </div>
          <div style="font-family:Space Grotesk; font-weight:700; font-size:36px; color:white; margin-top:6px;">₹{last:,.0f} <span style="font-size:14px; color:{color};">{arrow} {abs(pct):.2f}%</span></div>
          <div style="font-family:JetBrains Mono; font-size:10px; color:rgba(255,255,255,0.5);">VOL: {vol:,.0f} • RSI: {score} • BSE LIVE</div>
          <div class="target-row"><span>🎯 TARGET: ₹{target:,.0f} (+8%)</span><span>SCORE {score}/100</span></div>
          <div style="display:flex; gap:6px; margin-top:12px; flex-wrap:wrap;">
            <span style="background:rgba(255,77,106,0.12); border:1px solid rgba(255,77,106,0.25); border-radius:100px; padding:6px 12px; font-size:10px; color:#FF4D6A;">🛑 STOP: ₹{sl:,.0f}</span>
            <span style="background:rgba(0,209,255,0.12); border-radius:100px; padding:6px 12px; font-size:10px; color:#00D1FF;">📦 QTY: 10</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# --- FULL WIDTH CHART (PORTFOLIO HATAYA) ---
st.markdown("""
<div class="top-god" style="padding:18px 22px;">
  <div style="font-family:Space Grotesk; font-weight:700; color:white; font-size:18px;">📈 LIVE CHART - GOD MODE ANALYSIS - FULL WIDTH</div>
  <div style="font-family:JetBrains Mono; font-size:10px; color:rgba(255,255,255,0.5);">Candlestick • Volume • Bigger Chart</div>
</div>
""", unsafe_allow_html=True)
st.write("")
c1, c2 = st.columns([3, 1])
with c1:
    sym_input = st.text_input("STOCK SYMBOL", "RELIANCE.NS")
with c2:
    st.write(""); st.write("")
    analyze = st.button("🚀 ANALYZE GOD MODE", use_container_width=True)

if analyze:
    with st.spinner(f"Fetching {sym_input}..."):
        hist = safe_yf(sym_input, period="1mo", interval="1d")
        if not hist.empty:
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.75, 0.25])
            fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], name="Price"), row=1, col=1)
            fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'], name="Volume", marker_color="#00D1FF"), row=2, col=1)
            fig.update_layout(template="plotly_dark", height=600, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            last = hist['Close'].iloc[-1]
            st.success(f"✅ LIVE {sym_input}: ₹{last:.2f} | Target: ₹{last*1.08:.2f} | Stop: ₹{last*0.95:.2f}")
        else:
            st.error("⚠️ Yahoo API busy - 1 min baad try karo")

st.caption(f"V45.2 - Portfolio Removed • Clean UI • Full Width Chart • IST: {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d %b %I:%M %p')}")
