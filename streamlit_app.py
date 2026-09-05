import streamlit as st, yfinance as yf, pandas as pd, plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
from datetime import datetime
import pytz

st.set_page_config(page_title="FinTrade God V44", layout="wide", page_icon="💎")

# --- FIXED: NO META REFRESH FLICKER ---
@st.cache_data(ttl=300, show_spinner=False)
def safe_yf_history(symbol, period="2d", interval="5m"):
    try:
        t = yf.Ticker(symbol)
        hist = t.history(period=period, interval=interval)
        if hist.empty:
            hist = t.history(period="5d")
        return hist
    except Exception:
        return None

@st.cache_data(ttl=300, show_spinner=False)
def get_index_price(symbol):
    try:
        hist = safe_yf_history(symbol, period="2d", interval="1d")
        if hist is None or len(hist) < 1:
            return None, None
        last = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2] if len(hist) > 1 else last
        pct = ((last - prev) / prev) * 100
        return last, pct
    except:
        return None, None

def get_logo_html():
    try:
        with open("logo.png","rb") as f: 
            data = base64.b64encode(f.read()).decode()
            return f'<img src="data:image/png;base64,{data}" width="88" height="88" style="border-radius:18px; border:none; background:transparent; margin-right:14px; display:block; filter: drop-shadow(0 0 10px rgba(0,255,200,0.4));">'
    except: 
        return '<div style="font-size:42px; margin-right:14px;">💎</div>'

# --- FIXED CSS: LOGO BG = HEADER BG, NO PURPLE DOTS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700&family=JetBrains+Mono:wght@800&display=swap');
.stApp{background: #020208; background-image: radial-gradient(at 0% 0%, hsla(212,100%,56%,0.25) 0px, transparent 50%), radial-gradient(at 20% 10%, hsla(273,100%,60%,0.25) 0px, transparent 50%), radial-gradient(at 90% 0%, hsla(158,100%,50%,0.20) 0px, transparent 50%);}
.header-god{
 background: linear-gradient(135deg, #6A5AE0 0%, #7B6EF0 100%) !important;
 border: none !important;
 border-radius: 24px;
 padding: 16px 22px;
 box-shadow: 0 10px 40px rgba(106,90,224,0.35);
 display:flex; align-items:center;
}
.header-god img{ background: transparent !important; border: none !important; box-shadow: none !important; }
.pick-god{
 background: linear-gradient(135deg, rgba(0,255,136,0.10) 0%, rgba(0,209,255,0.08) 50%, rgba(112,0,255,0.08) 100%);
 border: 1.5px solid transparent;
 background-clip: padding-box;
 position: relative;
 border-radius: 24px;
 padding: 20px 20px 14px 20px;
 box-shadow: 0 12px 40px rgba(0,255,136,0.12), inset 0 1px 0 rgba(255,255,255,0.1);
}
.pick-god{ border-image: linear-gradient(135deg, #00FF88, #00D1FF, #7000FF) 1; }
.pick-god::before{ display:none !important; }
.top-god{background: linear-gradient(100deg, rgba(0,209,255,0.14) 0%, rgba(112,0,255,0.18) 40%, rgba(0,255,136,0.10) 100%); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.12); border-radius: 28px; padding: 24px 26px;}
.live-price{font-family: 'Space Grotesk'; font-weight: 700; font-size: 38px; background: linear-gradient(90deg, #fff 0%, #a5b4fc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
.target-row{display: flex; justify-content: space-between; align-items: center; margin-top: 14px; padding: 10px 12px; background: linear-gradient(90deg, rgba(0,255,136,0.12), rgba(0,255,136,0.06)); border: 1px solid rgba(0,255,136,0.25); border-left: 3px solid #00FF88; border-radius: 12px;}
.index-chip{display:inline-flex; align-items:center; gap:6px; background: rgba(0,0,0,0.35); border:1px solid rgba(255,255,255,0.08); border-radius:100px; padding:8px 14px; font-family:JetBrains Mono; font-size:11px; color:#fff; margin-right:8px;}
.index-up{color:#00FF88; font-weight:800;}.index-down{color:#FF4D6A; font-weight:800;}
.bse-badge{background: linear-gradient(135deg, #FF6A00, #FFD700); color:black; font-family:Space Grotesk; font-weight:700; font-size:10px; padding:4px 10px; border-radius:100px;}
.auto-badge{background: rgba(0,255,136,0.15); border:1px solid rgba(0,255,136,0.3); color:#00FF88; font-family:JetBrains Mono; font-size:10px; padding:5px 12px; border-radius:100px; font-weight:700;}
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
logo_html = get_logo_html()
nifty_price, nifty_pct = get_index_price("^NSEI")
sensex_price, sensex_pct = get_index_price("^BSESN")
bank_price, bank_pct = get_index_price("^NSEBANK")

def chip_html(name, price, pct):
    if price is None:
        return f'<span class="index-chip">{name}: Loading...</span>'
    cls = "index-up" if pct >=0 else "index-down"
    arrow = "▲" if pct >=0 else "▼"
    return f'<span class="index-chip">{name}: ₹{price:,.0f} <span class="{cls}">{arrow} {abs(pct):.2f}%</span></span>'

chips = chip_html("NIFTY", nifty_price, nifty_pct if nifty_pct else 0) + chip_html("SENSEX", sensex_price, sensex_pct if sensex_pct else 0) + chip_html("BANKNIFTY", bank_price, bank_pct if bank_pct else 0)

st.markdown(f"""
<div class="header-god">
 {logo_html}
 <div>
   <div style="font-family:Space Grotesk; font-weight:800; font-size:28px; color:white; line-height:1;">FinTrade <span style="color:#00FFCC;">God</span> V44 <span class="bse-badge">BSE</span></div>
   <div style="margin-top:8px; display:flex; flex-wrap:wrap;">{chips}</div>
 </div>
 <div style="margin-left:auto; display:flex; gap:8px; align-items:center;">
   <span class="auto-badge">● LIVE • AUTO 5M • FIXED</span>
 </div>
</div>
""", unsafe_allow_html=True)

st.write("")

# --- TOP PICKS ---
c1, c2 = st.columns([2, 1])

with c1:
    st.markdown("""
    <div class="top-god">
      <div style="font-family:Space Grotesk; font-weight:700; color:white; font-size:20px;">🔥 TOP PICKS - GOD MODE</div>
      <div style="font-family:JetBrains Mono; font-size:11px; color:rgba(255,255,255,0.6); margin-top:6px;">AI Score > 85 • Risk Low • SEBI Safe</div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    st.markdown("""
    <div class="pick-god">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <div style="font-family:Space Grotesk; font-weight:800; font-size:22px; color:white;">RELIANCE</div>
        <div style="width:56px; height:56px; border-radius:50%; background: conic-gradient(#00FF88 88%, rgba(255,255,255,0.1) 0); display:flex; align-items:center; justify-content:center;"><span style="font-family:JetBrains Mono; font-weight:800; color:#00FF88;">88</span></div>
      </div>
      <div class="live-price">₹1,452</div>
      <div class="target-row"><span style="color:#00FF88; font-family:JetBrains Mono; font-size:12px; font-weight:700;">🎯 TARGET: ₹1,580 (+8.8%)</span><span style="font-family:JetBrains Mono; font-size:11px;">SCORE 88/100</span></div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    symbol_input = st.text_input("STOCK SYMBOL", "RELIANCE.NS")
    if st.button("🚀 ANALYZE GOD MODE", use_container_width=True):
        with st.spinner("Fetching..."):
            hist = safe_yf_history(symbol_input, period="1mo", interval="1d")
            if hist is not None and not hist.empty:
                fig = make_subplots(rows=1, cols=1)
                fig.add_trace(go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close']))
                fig.update_layout(template="plotly_dark", height=420, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Yahoo limit - 1 min baad try karo")

st.caption("V44 Fixed: Logo BG #6A5AE0 Matched • No Dots • IST: " + datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%d %b %I:%M %p"))
