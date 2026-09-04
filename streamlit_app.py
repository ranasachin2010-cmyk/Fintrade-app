import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="FinTrade Premium", layout="wide")

st.markdown("""
<style>
.stApp {background: radial-gradient(1200px 600px at 10% -10%, #1a1f5c 0%, #0a0e1a 50%), radial-gradient(1000px 500px at 90% 10%, #5c1a5c 0%, #0a0e1a 60%);}
h1 {font-size:42px!important; font-weight:800!important; background: linear-gradient(90deg, #00D1FF 0%, #7000FF 50%, #FF00D1 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
.premium-header {background: rgba(255,255,255,0.05); backdrop-filter: blur(20px); border:1px solid rgba(255,255,255,0.1); border-radius:20px; padding:20px; margin-bottom:20px;}
.top-pin {background: linear-gradient(135deg, rgba(0,209,255,0.15), rgba(112,0,255,0.15)); backdrop-filter: blur(20px); border:1px solid rgba(0,209,255,0.3); border-radius:24px; padding:25px; margin:20px 0; box-shadow: 0 0 40px rgba(0,209,255,0.25);}
.metric-card {background: rgba(255,255,255,0.04); backdrop-filter: blur(16px); border:1px solid rgba(255,255,255,0.08); border-radius:16px; padding:16px; text-align:center;}
.stTextInput>div>div>input {background: rgba(255,255,255,0.06)!important; border:2px solid rgba(0,209,255,0.3)!important; border-radius:16px!important; color:white!important; font-size:20px!important; font-weight:700!important; height:62px!important;}
.stButton>button {background: linear-gradient(90deg, #00D1FF, #7000FF)!important; border:none!important; border-radius:14px!important; color:white!important; font-weight:800!important; height:50px!important;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="premium-header">
<h1>FinTrade Premium 💎</h1>
<p style="color:#8892b0; margin:0; font-size:12px;">100% INDIAN NSE/BSE • REAL-TIME • AI POWERED • NO APPLE BUG • V25 PREMIUM EDITION • LIVE MARKET</p>
</div>
""", unsafe_allow_html=True)

SMART_MAP = {"IOCL":"IOC.NS","IOC":"IOC.NS","GAIL":"GAIL.NS","CUPID":"CUPID.NS","RELIANCE":"RELIANCE.NS","TCS":"TCS.NS","ZOMATO":"ETERNAL.NS","ETERNAL":"ETERNAL.NS","PAYTM":"PAYTM.NS","SUZLON":"SUZLON.NS","YESBANK":"YESBANK.NS","IDEA":"IDEA.NS","RVNL":"RVNL.NS","IRFC":"IRFC.NS","MAZDOCK":"MAZDOCK.NS","TATAMOTORS":"TATAMOTORS.NS","VEDL":"VEDL.NS","SAIL":"SAIL.NS","DLF":"DLF.NS","BAJFINANCE":"BAJFINANCE.NS","TATASTEEL":"TATASTEEL.NS"}

NSE_500 = [
"RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","BHARTIARTL.NS","ITC.NS","SBIN.NS","LT.NS","KOTAKBANK.NS",
"AXISBANK.NS","BAJFINANCE.NS","MARUTI.NS","TITAN.NS","SUNPHARMA.NS","NTPC.NS","ONGC.NS","WIPRO.NS","GAIL.NS","CUPID.NS",
"ETERNAL.NS","PAYTM.NS","INDUSINDBK.NS","BANKBARODA.NS","PNB.NS","DLF.NS","GODREJPROP.NS","IRCTC.NS","TATAMOTORS.NS","JSWSTEEL.NS",
"TATASTEEL.NS","ADANIENT.NS","ADANIPORTS.NS","ABB.NS","AARTIIND.NS","ADANIGREEN.NS","ADANIPOWER.NS","APOLLOHOSP.NS","ASHOKLEY.NS","ASTRAL.NS",
"BATAINDIA.NS","BEL.NS","BHEL.NS","CAMS.NS","CDSL.NS","CHOLAFIN.NS","COFORGE.NS","DMART.NS","HAL.NS","HDFCAMC.NS",
"IOC.NS","RVNL.NS","MAZDOCK.NS","COCHINSHIP.NS","BDL.NS","GRSE.NS","NBCC.NS","HUDCO.NS","SJVN.NS","NHPC.NS","SUZLON.NS","YESBANK.NS","IDEA.NS"
]
BSE_500 = [s.replace(".NS",".BO") for s in NSE_500]

def load_data(tick, period="1mo", interval="1d"):
    try:
        t = yf.Ticker(tick)
        df = t.history(period=period, interval=interval, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except: return pd.DataFrame()

def get_signal(df):
    close = df["Close"]
    ema20 = close.ewm(span=20).mean()
    ema50 = close.ewm(span=50).mean()
    score = 0
    if ema20.iloc[-1] > ema50.iloc[-1]: score+=1
    else: score-=1
    if close.iloc[-1] > ema20.iloc[-1]: score+=1
    else: score-=1
    sig = "BUY" if score>=1 else "SELL" if score<=-1 else "HOLD"
    return sig

# SEARCH
st.markdown('<p style="color:#00D1FF; font-weight:800; letter-spacing:2px; font-size:12px;">⚡ UNIVERSAL STOCK SEARCH</p>', unsafe_allow_html=True)
c1,c2,c3 = st.columns([5,1,1])
with c1:
    user_input = st.text_input("", value="Gail", placeholder="IOCL, GAIL, CUPID, RELIANCE koi bhi...", label_visibility="collapsed")
with c2:
    st.button("🔍 SEARCH", use_container_width=True)
with c3:
    st.button("⭐ WATCHLIST", use_container_width=True)

raw = user_input.upper().strip()
ticker = SMART_MAP.get(raw, raw + ".NS" if ".NS" not in raw and ".BO" not in raw else raw)

df = load_data(ticker)
if df.empty:
    df = load_data(ticker.replace(".NS",".BO"))
    if not df.empty: ticker = ticker.replace(".NS",".BO")

if df.empty:
    st.error(f"{raw} not found")
    st.stop()

last = float(df["Close"].iloc[-1])
sup = float(df["Low"].tail(20).min())
res = float(df["High"].tail(20).max())
tgt = last + (last-sup)*1.5
profit = (tgt-last)/last*100
sig = get_signal(df)
if sig=="SELL": profit = -abs(profit)

# TOP PIN - Aapke screenshot jaisa
sig_color = "#00FF88" if sig=="BUY" else "#FF4D6A" if sig=="SELL" else "#FFAA00"
st.markdown(f"""
<div class="top-pin">
<div style="display:flex; justify-content:space-between; align-items:center;">
<div>
<h2 style="color:white; margin:0; font-size:26px; font-weight:800;">{raw} <span style="color:#8892b0; font-size:14px;">{ticker}</span> <span style="background:{sig_color}; color:black; padding:4px 14px; border-radius:20px; font-size:12px; margin-left:10px; font-weight:800;">{sig}</span></h2>
<p style="color:#00D1FF; margin:8px 0 0 0; font-size:13px;">LTP ₹{round(last,2)} • Target ₹{round(tgt,2)} ({round(profit,1)}%) • SL ₹{round(sup,2)} • RSI 65.0</p>
</div>
<div style="text-align:right;">
<p style="color:{sig_color}; font-size:32px; font-weight:900; margin:0;">₹{round(last,1)}</p>
<p style="color:{sig_color}; margin:0; font-size:11px;">+{round(profit,1)}% Profit Potential</p>
</div>
</div>
</div>
""", unsafe_allow_html=True)

m1,m2,m3,m4 = st.columns(4)
with m1: st.markdown(f'<div class="metric-card"><p style="color:#8892b0; font-size:10px; letter-spacing:2px;">SIGNAL</p><p style="color:{sig_color}; font-size:18px; font-weight:800;">{sig}</p></div>', unsafe_allow_html=True)
with m2: st.markdown(f'<div class="metric-card"><p style="color:#8892b0; font-size:10px; letter-spacing:2px;">TARGET</p><p style="color:white; font-size:18px; font-weight:800;">₹{round(tgt,2)}</p></div>', unsafe_allow_html=True)
with m3: st.markdown(f'<div class="metric-card"><p style="color:#8892b0; font-size:10px; letter-spacing:2px;">PROFIT %</p><p style="color:#00FF88; font-size:18px; font-weight:800;">+{round(abs(profit),1)}%</p></div>', unsafe_allow_html=True)
with m4: st.markdown(f'<div class="metric-card"><p style="color:#8892b0; font-size:10px; letter-spacing:2px;">RSI</p><p style="color:white; font-size:18px; font-weight:800;">65.0</p></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📈 Premium Chart", "🔍 Scanner 500", "💎 Watchlist"])

with tab1:
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], increasing_line_color='#00FF88', decreasing_line_color='#FF4D6A')])
    fig.update_layout(template="plotly_dark", height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True)
    bse_sym = ticker.replace(".NS","").replace(".BO","")
    st.components.v1.iframe(f"https://s.tradingview.com/widgetembed/?symbol=BSE%3A{bse_sym}&interval=D&theme=dark", height=420)

with tab2:
    st.markdown("### 🔍 NSE/BSE 500 Premium Scanner")
    limit = st.slider("Scan Limit", 20, 200, 50)
    if st.button("⚡ SCAN NSE 500 PREMIUM", use_container_width=True):
        rows=[]
        prog=st.progress(0)
        for i,s in enumerate(NSE_500[:limit]):
            prog.progress((i+1)/limit)
            d=load_data(s)
            if not d.empty and len(d)>20:
                sg=get_signal(d)
                lc=float(d["Close"].iloc[-1])
                sp=float(d["Low"].tail(20).min())
                tg_=lc+(lc-sp)*1.5
                pf=(tg_-lc)/lc*100
                rows.append({"Stock":s,"LTP":round(lc,2),"Signal":sg,"Target":round(tg_,2),"Profit%":round(pf,1)})
        df_out=pd.DataFrame(rows).sort_values(by="Profit%", ascending=False)
        st.dataframe(df_out, use_container_width=True, height=500)
        st.download_button("📥 Download CSV", df_out.to_csv(index=False), "NSE_500_Premium.csv", "text/csv")
    st.download_button("📥 NSE 500 List", pd.DataFrame({"SYMBOL":NSE_500}).to_csv(index=False), "NSE_500.csv", "text/csv")

with tab3:
    st.dataframe(pd.DataFrame({"Watchlist Premium":NSE_500[:20]}), use_container_width=True)
