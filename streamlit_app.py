import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import base64
import time
import requests
from datetime import datetime

st.set_page_config(page_title="FinTrade Premium", layout="wide", page_icon="💎")

# CSS - PREMIUM
st.markdown("""
<style>
.stApp {background: radial-gradient(1200px 600px at 10% -10%, #1a1f5c 0%, #0a0e1a 50%), radial-gradient(1000px 500px at 90% 10%, #5c1a5c 0%, #0a0e1a 60%);}
.header-box {background: rgba(255,255,255,0.05); backdrop-filter: blur(20px); border:1px solid rgba(255,255,255,0.1); border-radius:20px; padding:18px; margin-bottom:18px;}
.top-pin {background: linear-gradient(135deg, rgba(0,209,255,0.18), rgba(112,0,255,0.18)); border:1px solid rgba(0,209,255,0.35); border-radius:20px; padding:18px; margin:16px 0; box-shadow: 0 0 40px rgba(0,209,255,0.25);}
.ai-card {background: linear-gradient(135deg, rgba(112,0,255,0.15), rgba(0,209,255,0.15)); border:1px solid rgba(112,0,255,0.4); border-radius:16px; padding:16px; margin:10px 0;}
.stTextInput>div>div>input, .stNumberInput>div>div>input {background: rgba(255,255,255,0.06)!important; border:2px solid rgba(0,209,255,0.3)!important; border-radius:14px!important; color:white!important; font-size:20px!important; font-weight:700!important; height:58px!important;}
.stButton>button {background: linear-gradient(90deg, #00D1FF, #7000FF)!important; border:none!important; border-radius:12px!important; color:white!important; font-weight:800!important; height:50px!important;}
</style>
""", unsafe_allow_html=True)

if "alerts" not in st.session_state:
    st.session_state.alerts = []
if "triggered_alerts" not in st.session_state:
    st.session_state.triggered_alerts = []
if "live_mode" not in st.session_state:
    st.session_state.live_mode = False
if "tg_token" not in st.session_state:
    st.session_state.tg_token = ""
if "tg_chat" not in st.session_state:
    st.session_state.tg_chat = ""

def get_logo():
    try:
        with open("logo.png","rb") as f:
            d=base64.b64encode(f.read()).decode()
            return f'<img src="data:image/png;base64,{d}" width="60" style="border-radius:12px;">'
    except:
        return '<div style="font-size:40px;">💎</div>'

st.markdown(f"""
<div class="header-box">
<div style="display:flex; align-items:center; gap:16px;">
<div>{get_logo()}</div>
<div>
<h1 style="margin:0; color:white; font-size:28px;">FinTrade Premium</h1>
<p style="margin:0; color:#8892b0; font-size:10px;">V33 NO VOICE EDITION | 100% INDIAN NSE/BSE | LIVE + AI POWERED + TELEGRAM</p>
</div>
</div>
</div>
""", unsafe_allow_html=True)

SMART_MAP = {"IOCL":"IOC.NS","IOC":"IOC.NS","GAIL":"GAIL.NS","CUPID":"CUPID.NS","RELIANCE":"RELIANCE.NS","TCS":"TCS.NS","ZOMATO":"ETERNAL.NS","ETERNAL":"ETERNAL.NS","PAYTM":"PAYTM.NS","SUZLON":"SUZLON.NS","YESBANK":"YESBANK.NS","IDEA":"IDEA.NS","RVNL":"RVNL.NS","IRFC":"IRFC.NS","MAZDOCK":"MAZDOCK.NS","TATAMOTORS":"TATAMOTORS.NS","SBIN":"SBIN.NS","INFY":"INFY.NS"}

def load_data(tick):
    try:
        t=yf.Ticker(tick)
        df=t.history(period="3mo", interval="1d", auto_adjust=False)
        if df.empty: df=t.history(period="1mo", interval="1d", auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex): df.columns=df.columns.get_level_values(0)
        df=df.dropna()
        if "Close" in df.columns: df=df[df["Close"]>0]
        return df
    except: return pd.DataFrame()

def get_live_price(tick):
    try:
        t=yf.Ticker(tick)
        p=t.fast_info.last_price
        if p is None or pd.isna(p):
            d=t.history(period="1d", interval="1m")
            p=float(d["Close"].dropna().iloc[-1]) if not d.empty else 0
        return float(p)
    except: return 0

def get_ai_analysis(df, raw, last, tgt, sup):
    try:
        close=df["Close"].dropna()
        vol = df["Volume"].iloc[-1] if "Volume" in df else 0
        avg_vol = df["Volume"].tail(20).mean() if "Volume" in df else 1
        vol_ratio = vol/avg_vol if avg_vol!=0 else 1
        ema20 = close.ewm(20).mean().iloc[-1]
        ema50 = close.ewm(50).mean().iloc[-1]
        sig = "BUY" if ema20>ema50 else "SELL" if ema20<ema50 else "HOLD"
        score = 85 if sig=="BUY" else 25 if sig=="SELL" else 50
        trend = "Strong Uptrend" if sig=="BUY" and vol_ratio>1.2 else "Weak Downtrend" if sig=="SELL" else "Sideways"
        reason = f"AI ne {len(close)} candles analyze kiye. EMA20 {round(ema20,2)}, EMA50 {round(ema50,2)}. Volume {vol_ratio:.1f}x. Support {round(sup,2)} strong."
        pred = f"Next 5 days me {raw} Rs {round(tgt*0.95,2)} - {round(tgt,2)} range."
        return {"score":score, "trend":trend, "reason":reason, "vol_ratio":round(vol_ratio,2), "pred":pred, "sig":sig}
    except:
        return {"score":50, "trend":"Neutral", "reason":"Data kam", "vol_ratio":1, "pred":"Wait", "sig":"HOLD"}

def send_telegram(token, chat_id, msg):
    try:
        url=f"https://api.telegram.org/bot{token}/sendMessage"
        r=requests.post(url, json={"chat_id":chat_id, "text":msg, "parse_mode":"Markdown"}, timeout=10)
        return r.status_code==200
    except: return False

# SEARCH - NO VOICE
st.markdown("#### ⚡ UNIVERSAL STOCK SEARCH")
c1,c2,c3 = st.columns([5,1,1])
with c1:
    user_input = st.text_input("search", value="IOCL", placeholder="IOCL, GAIL, CUPID, RELIANCE...", label_visibility="collapsed")
with c2:
    st.button("🔍 SEARCH", use_container_width=True)
with c3:
    st.button("🔔 ALERTS", use_container_width=True)

raw=user_input.upper().strip()
ticker=SMART_MAP.get(raw, raw+".NS" if ".NS" not in raw and ".BO" not in raw else raw)
df=load_data(ticker)
if df.empty:
    df=load_data(ticker.replace(".NS",".BO"))
    if not df.empty: ticker=ticker.replace(".NS",".BO")
if df.empty:
    st.error(f"{raw} not found")
    st.stop()

last=float(df["Close"].dropna().iloc[-1])
live_price=get_live_price(ticker)
if live_price==0 or pd.isna(live_price): live_price=last
low_min=float(df["Low"].dropna().tail(20).min())
high_max=float(df["High"].dropna().tail(20).max())
if low_min==0 or pd.isna(low_min): low_min=last*0.95
if high_max==0 or pd.isna(high_max): high_max=last*1.05
tgt=last+(last-low_min)*1.5
if tgt<=last: tgt=high_max
profit=((tgt-last)/last*100) if last!=0 else 0

ai=get_ai_analysis(df, raw, last, tgt, low_min)
sig=ai["sig"]
profit_show = -abs(profit) if sig=="SELL" else abs(profit)
sig_color="#00FF88" if sig=="BUY" else "#FF4D6A" if sig=="SELL" else "#FFAA00"

st.markdown(f"""
<div class="top-pin">
<div style="display:flex; justify-content:space-between; align-items:center;">
<div>
<h2 style="color:white; margin:0; font-size:22px;">{raw} <span style="color:#8892b0; font-size:12px;">{ticker}</span> <span style="background:{sig_color}; color:black; padding:4px 12px; border-radius:20px; font-size:11px;">{sig}</span> <span style="background:rgba(112,0,255,0.3); color:#C084FC; padding:4px 10px; border-radius:20px; font-size:11px;">AI {ai['score']}/100</span></h2>
<p style="color:#00D1FF; margin:6px 0 0 0; font-size:12px;">LIVE Rs {round(live_price,2)} | Target Rs {round(tgt,2)} | SL Rs {round(low_min,2)} | {ai['trend']}</p>
</div>
<div style="text-align:right;">
<p style="color:{sig_color}; font-size:28px; font-weight:900; margin:0;">Rs {round(live_price,2)}</p>
<p style="color:#00FF88; font-size:11px; margin:0;">● LIVE + AI</p>
</div>
</div>
</div>
""", unsafe_allow_html=True)

tab_chart, tab_ai, tab_alert, tab_tg = st.tabs(["📈 Chart", "🤖 AI ANALYSIS", "🔔 LIVE ALERTS", "📲 TELEGRAM BOT"])

with tab_chart:
    df_c=df.tail(80)
    fig=go.Figure(data=[go.Candlestick(x=df_c.index, open=df_c["Open"], high=df_c["High"], low=df_c["Low"], close=df_c["Close"], increasing_line_color="#00FF88", decreasing_line_color="#FF4D6A")])
    fig.update_layout(template="plotly_dark", height=440, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)
    st.components.v1.iframe(f"https://s.tradingview.com/widgetembed/?symbol=BSE%3A{ ticker.replace('.NS','').replace('.BO','') }&interval=D&theme=dark", height=380)

with tab_ai:
    st.markdown(f"""
    <div class="ai-card">
      <h3 style="margin:0; color:#C084FC;">🤖 AI Analysis for {raw}</h3>
      <p style="color:white; margin:10px 0;"><b>Trend:</b> {ai['trend']} | <b>Score:</b> {ai['score']}/100 | <b>Volume:</b> {ai['vol_ratio']}x</p>
      <p style="color:#8892b0; font-size:13px;">{ai['reason']}</p>
      <p style="color:#00D1FF; font-weight:700;">🔮 {ai['pred']}</p>
    </div>
    """, unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    with c1: st.metric("AI SCORE", f"{ai['score']}/100")
    with c2: st.metric("TREND", ai['trend'])
    with c3: st.metric("VOLUME", f"{ai['vol_ratio']}x")

with tab_alert:
    st.markdown("### 🔔 Live Price Alerts")
    st.session_state.live_mode = st.toggle("🟢 LIVE MODE ON (30 sec auto-check)", value=st.session_state.live_mode)
    
    ca1,ca2,ca3 = st.columns(3)
    with ca1:
        atype=st.selectbox("Type", ["Above","Below","Target Hit","SL Hit"])
    with ca2:
        def_p=tgt if "Target" in atype else low_min if "SL" in atype else live_price
        aprice=st.number_input("Price Rs", value=float(round(def_p,2)), step=0.05)
    with ca3:
        note=st.text_input("Note", value=f"{raw} {atype}")

    if st.button("➕ Add Alert", use_container_width=True):
        na={"id":len(st.session_state.alerts)+1,"stock":raw,"ticker":ticker,"type":atype,"price":aprice,"note":note,"created":datetime.now().strftime("%H:%M:%S"),"active":True}
        st.session_state.alerts.append(na)
        st.success(f"Alert set: {raw} {atype} {aprice}")
        if st.session_state.tg_token and st.session_state.tg_chat:
            send_telegram(st.session_state.tg_token, st.session_state.tg_chat, f"🔔 Alert Set: {raw} {atype} Rs {aprice} LIVE Rs {round(live_price,2)}")
        st.balloons()

    triggered=[]
    for al in st.session_state.alerts:
        if not al["active"]: continue
        if al["ticker"]==ticker:
            if al["type"]=="Above" and live_price>=al["price"]: triggered.append(al)
            elif al["type"]=="Below" and live_price<=al["price"]: triggered.append(al)
            elif al["type"]=="Target Hit" and live_price>=al["price"]: triggered.append(al)
            elif al["type"]=="SL Hit" and live_price<=al["price"]: triggered.append(al)

    if triggered:
        st.markdown('<audio autoplay><source src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" type="audio/ogg"></audio>', unsafe_allow_html=True)
        for ta in triggered:
            st.error(f"🔔 TRIGGERED! {ta['stock']} {ta['type']} Rs {ta['price']} - LTP {round(live_price,2)}")
            st.toast(f"🔔 {ta['stock']} HIT!", icon="🔔")
            if st.session_state.tg_token and st.session_state.tg_chat:
                send_telegram(st.session_state.tg_token, st.session_state.tg_chat, f"🚨 ALERT TRIGGERED {ta['stock']} {ta['type']} {ta['price']} LIVE {round(live_price,2)}")
            ta["active"]=False
            st.session_state.triggered_alerts.append(ta)

    if st.session_state.alerts:
        active=[a for a in st.session_state.alerts if a["active"]]
        if active:
            st.dataframe(pd.DataFrame(active)[["id","stock","type","price","note","created"]], use_container_width=True)

    if st.session_state.live_mode:
        st.info("🟢 LIVE ON - 30 sec me auto refresh...")
        time.sleep(30)
        st.rerun()

with tab_tg:
    st.markdown("### 📲 Telegram Bot Setup - 2 min")
    st.markdown("Telegram pe @BotFather -> /newbot -> Token lo, @userinfobot se Chat ID lo")
    tok = st.text_input("Bot Token", value=st.session_state.tg_token, type="password")
    chat = st.text_input("Chat ID", value=st.session_state.tg_chat)
    if st.button("💾 Save Telegram"):
        st.session_state.tg_token=tok
        st.session_state.tg_chat=chat
        st.success("Saved!")
    if st.button("📤 Test Telegram"):
        if send_telegram(tok, chat, f"✅ Test - {raw} LIVE Rs {round(live_price,2)}"):
            st.success("✅ Telegram pe gaya!")
            st.balloons()
        else:
            st.error("❌ Token/Chat ID check karo")

st.caption("V33 - Voice removed - Clean Premium - Logo + AI + Live Alerts + Telegram")
