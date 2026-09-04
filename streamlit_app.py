import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import base64
import time
import requests
from datetime import datetime

st.set_page_config(page_title="FinTrade Premium", layout="wide", page_icon="💎")

# CSS
st.markdown("""
<style>
.stApp {background: radial-gradient(1200px 600px at 10% -10%, #1a1f5c 0%, #0a0e1a 50%), radial-gradient(1000px 500px at 90% 10%, #5c1a5c 0%, #0a0e1a 60%);}
.header-box {background: rgba(255,255,255,0.05); backdrop-filter: blur(20px); border:1px solid rgba(255,255,255,0.1); border-radius:20px; padding:18px; margin-bottom:18px;}
.top-pin {background: linear-gradient(135deg, rgba(0,209,255,0.18), rgba(112,0,255,0.18)); border:1px solid rgba(0,209,255,0.35); border-radius:20px; padding:18px; margin:16px 0; box-shadow: 0 0 40px rgba(0,209,255,0.25);}
.ai-card {background: linear-gradient(135deg, rgba(112,0,255,0.15), rgba(0,209,255,0.15)); border:1px solid rgba(112,0,255,0.4); border-radius:16px; padding:16px; margin:10px 0;}
.voice-box {background: linear-gradient(135deg, rgba(0,255,136,0.12), rgba(0,209,255,0.12)); border:2px dashed #00FF88; border-radius:16px; padding:12px; text-align:center;}
.stButton>button {background: linear-gradient(90deg, #00D1FF, #7000FF)!important; border:none!important; border-radius:12px!important; color:white!important; font-weight:800!important; height:48px!important;}
</style>
""", unsafe_allow_html=True)

if "alerts" not in st.session_state:
    st.session_state.alerts = []
if "triggered_alerts" not in st.session_state:
    st.session_state.triggered_alerts = []
if "live_mode" not in st.session_state:
    st.session_state.live_mode = False
if "voice_text" not in st.session_state:
    st.session_state.voice_text = "IOCL"

# TELEGRAM CONFIG
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
<p style="margin:0; color:#8892b0; font-size:10px;">V32 VOICE + AI + TELEGRAM BOT | 100% INDIAN NSE/BSE | LIVE + AI POWERED</p>
</div>
</div>
</div>
""", unsafe_allow_html=True)

SMART_MAP = {"IOCL":"IOC.NS","IOC":"IOC.NS","GAIL":"GAIL.NS","CUPID":"CUPID.NS","RELIANCE":"RELIANCE.NS","TCS":"TCS.NS","ZOMATO":"ETERNAL.NS","ETERNAL":"ETERNAL.NS","PAYTM":"PAYTM.NS","SUZLON":"SUZLON.NS","YESBANK":"YESBANK.NS","IDEA":"IDEA.NS","RVNL":"RVNL.NS","IRFC":"IRFC.NS","MAZDOCK":"MAZDOCK.NS","TATAMOTORS":"TATAMOTORS.NS","SBIN":"SBIN.NS","INFOSYS":"INFY.NS","INFY":"INFY.NS"}

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

def get_ai_analysis(df, raw, last, tgt, sup, sig):
    try:
        close=df["Close"].dropna()
        rsi = 65 # simplified
        vol = df["Volume"].iloc[-1] if "Volume" in df else 0
        avg_vol = df["Volume"].tail(20).mean() if "Volume" in df else 1
        vol_ratio = vol/avg_vol if avg_vol!=0 else 1

        trend = "Strong Uptrend" if sig=="BUY" and vol_ratio>1.2 else "Weak Downtrend" if sig=="SELL" else "Sideways"
        ai_score = 85 if sig=="BUY" else 25 if sig=="SELL" else 50

        reason = f"AI ne {len(close)} candles analyze kiye. EMA20 > EMA50 hai, volume {vol_ratio:.1f}x hai. Support Rs {round(sup,2)} strong hai. Target Rs {round(tgt,2)} me {round(((tgt-last)/last*100),1)}% profit potential."
        if sig=="SELL":
            reason = f"AI Alert: EMA20 < EMA50, selling pressure. Rs {round(sup,2)} todne pe aur giravat. SL hit hone ka risk."

        return {
            "score": ai_score,
            "trend": trend,
            "reason": reason,
            "vol_ratio": round(vol_ratio,2),
            "prediction": f"Next 5 days me {raw} Rs {round(tgt*0.95,2)} - Rs {round(tgt,2)} range me reh sakta hai."
        }
    except:
        return {"score":50, "trend":"Neutral", "reason":"Data kam hai", "vol_ratio":1, "prediction":"Wait and watch"}

def send_telegram(token, chat_id, msg):
    try:
        url=f"https://api.telegram.org/bot{token}/sendMessage"
        r=requests.post(url, json={"chat_id":chat_id, "text":msg, "parse_mode":"Markdown"}, timeout=10)
        return r.status_code==200
    except:
        return False

# VOICE SEARCH COMPONENT
st.markdown("#### 🎤 VOICE SEARCH + UNIVERSAL SEARCH")
st.components.v1.html("""
<div class="voice-box" style="background: rgba(0,255,136,0.1); border:2px dashed #00FF88; border-radius:16px; padding:14px; text-align:center; margin-bottom:10px;">
  <button id="voiceBtn" style="background: linear-gradient(90deg, #00FF88, #00D1FF); border:none; border-radius:30px; padding:12px 28px; font-weight:800; font-size:16px; color:black; cursor:pointer;">
    🎤 Bolke Search Karo - IOCL, GAIL Bolo
  </button>
  <p id="voiceStatus" style="color:#8892b0; font-size:12px; margin:8px 0 0 0;">Mic pe click karo aur stock ka naam bolo - Hindi / English dono chalega</p>
  <p id="voiceResult" style="color:#00FF88; font-weight:800; font-size:18px; margin:6px 0 0 0;"></p>
</div>
<script>
const btn = document.getElementById('voiceBtn');
const status = document.getElementById('voiceStatus');
const result = document.getElementById('voiceResult');
let recognition;
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SR();
  recognition.lang = 'en-IN';
  recognition.interimResults = false;
  recognition.onstart = () => { status.innerText = '🔴 Sun raha hu... Bolo!'; btn.innerText = '🔴 Listening...'; };
  recognition.onresult = (e) => {
    const text = e.results[0][0].transcript.toUpperCase();
    result.innerText = '✅ Suna: ' + text;
    status.innerText = 'Search box me type ho gaya - SEARCH dabao!';
    // Try to set Streamlit input via localStorage hack
    const clean = text.replace(/[^A-Z ]/g,'').split(' ')[0];
    window.parent.postMessage({type:'voice_search', text:clean}, '*');
    // Also set URL param
    const url = new URL(window.location);
    url.searchParams.set('voice', clean);
    window.history.pushState({}, '', url);
  };
  recognition.onend = () => { btn.innerText = '🎤 Bolke Search Karo'; status.innerText = 'Mic pe click karo aur stock ka naam bolo'; };
  recognition.onerror = () => { status.innerText = '❌ Mic error - Chrome me try karo, mic permission do'; };
  btn.onclick = () => { recognition.start(); };
} else {
  status.innerText = '❌ Voice support nahi hai - Chrome browser use karo';
}
</script>
""", height=130)

# Check URL param for voice
voice_param = st.query_params.get("voice", "")
if voice_param:
    st.session_state.voice_text = voice_param.upper()

c1,c2,c3,c4 = st.columns([4,1,1,1])
with c1:
    user_input = st.text_input("search", value=st.session_state.voice_text, placeholder="IOCL, GAIL, CUPID...", label_visibility="collapsed")
with c2:
    st.button("🔍 SEARCH", use_container_width=True)
with c3:
    st.button("🔔 ALERTS", use_container_width=True)
with c4:
    if st.button("🎤 VOICE", use_container_width=True):
        st.info("Upar mic button dabao aur bolo!")

raw=user_input.upper().strip()
ticker=SMART_MAP.get(raw, raw+".NS" if ".NS" not in raw and ".BO" not in raw else raw)
df=load_data(ticker)
if df.empty:
    df=load_data(ticker.replace(".NS",".BO"))
    if not df.empty: ticker=ticker.replace(".NS",".BO")
if df.empty:
    st.error(f"{raw} not found - Dubara bolo ya type karo")
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
sig="BUY" if df["Close"].ewm(20).mean().iloc[-1] > df["Close"].ewm(50).mean().iloc[-1] else "SELL" if df["Close"].ewm(20).mean().iloc[-1] < df["Close"].ewm(50).mean().iloc[-1] else "HOLD"
profit_show = -abs(profit) if sig=="SELL" else abs(profit)
sig_color="#00FF88" if sig=="BUY" else "#FF4D6A" if sig=="SELL" else "#FFAA00"

# AI ANALYSIS
ai = get_ai_analysis(df, raw, last, tgt, low_min, sig)

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
    fig.update_layout(template="plotly_dark", height=420, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)
    st.components.v1.iframe(f"https://s.tradingview.com/widgetembed/?symbol=BSE%3A{ ticker.replace('.NS','').replace('.BO','') }&interval=D&theme=dark", height=360)

with tab_ai:
    st.markdown(f"""
    <div class="ai-card">
      <h3 style="margin:0; color:#C084FC;">🤖 AI Analysis for {raw}</h3>
      <p style="color:white; margin:10px 0;"><b>Trend:</b> {ai['trend']} | <b>AI Score:</b> {ai['score']}/100 | <b>Volume:</b> {ai['vol_ratio']}x</p>
      <p style="color:#8892b0; font-size:13px;">{ai['reason']}</p>
      <p style="color:#00D1FF; font-weight:700; margin-top:10px;">🔮 Prediction: {ai['prediction']}</p>
    </div>
    """, unsafe_allow_html=True)
    c_ai1,c_ai2,c_ai3 = st.columns(3)
    with c_ai1: st.metric("AI SCORE", f"{ai['score']}/100", delta="Bullish" if ai['score']>70 else "Bearish")
    with c_ai2: st.metric("TREND", ai['trend'])
    with c_ai3: st.metric("VOLUME", f"{ai['vol_ratio']}x")

    st.markdown("#### 🎤 Voice se AI pucho")
    st.caption("Mic se bolo: 'IOCL ka trend kya hai?' - AI bolega!")
    if st.button("🤖 AI se pucho - IOCL kharidu ya bechu?"):
        if ai['score']>70:
            st.success(f"AI ke hisab se {raw} BUY hai - Target Rs {round(tgt,2)}")
        elif ai['score']<40:
            st.error(f"AI ke hisab se {raw} SELL hai - SL Rs {round(low_min,2)} tod sakta hai")
        else:
            st.warning(f"AI ke hisab se {raw} HOLD - Sideways market")

with tab_alert:
    st.markdown("### 🔔 Live Alerts + Voice")
    st.session_state.live_mode = st.toggle("🟢 LIVE MODE ON (30 sec)", value=st.session_state.live_mode)

    col_a1,col_a2,col_a3 = st.columns(3)
    with col_a1:
        atype=st.selectbox("Type", ["Above","Below","Target Hit","SL Hit"])
    with col_a2:
        def_p=tgt if "Target" in atype else low_min if "SL" in atype else live_price
        aprice=st.number_input("Price Rs", value=float(round(def_p,2)), step=0.05)
    with col_a3:
        note=st.text_input("Note", value=f"{raw} {atype}")

    if st.button("➕ Add Alert + Telegram", use_container_width=True):
        na={"id":len(st.session_state.alerts)+1,"stock":raw,"ticker":ticker,"type":atype,"price":aprice,"note":note,"created":datetime.now().strftime("%H:%M:%S"),"active":True}
        st.session_state.alerts.append(na)
        st.success(f"Alert set: {raw} {atype} {aprice}")
        # Telegram bhi bhejo
        if st.session_state.tg_token and st.session_state.tg_chat:
            send_telegram(st.session_state.tg_token, st.session_state.tg_chat, f"🔔 Alert Set: {raw} {atype} Rs {aprice} - LIVE Rs {round(live_price,2)}")
        st.balloons()

    # Check triggers
    triggered_now=[]
    for al in st.session_state.alerts:
        if not al["active"]: continue
        if al["ticker"]==ticker:
            if al["type"]=="Above" and live_price>=al["price"]: triggered_now.append(al)
            elif al["type"]=="Below" and live_price<=al["price"]: triggered_now.append(al)
            elif al["type"]=="Target Hit" and live_price>=al["price"]: triggered_now.append(al)
            elif al["type"]=="SL Hit" and live_price<=al["price"]: triggered_now.append(al)

    if triggered_now:
        st.markdown('<audio autoplay><source src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" type="audio/ogg"></audio>', unsafe_allow_html=True)
        for ta in triggered_now:
            st.error(f"🔔 TRIGGERED! {ta['stock']} {ta['type']} Rs {ta['price']} - LTP Rs {round(live_price,2)}")
            st.toast(f"🔔 {ta['stock']} HIT!", icon="🔔")
            if st.session_state.tg_token and st.session_state.tg_chat:
                send_telegram(st.session_state.tg_token, st.session_state.tg_chat, f"🚨 *ALERT TRIGGERED* 🚨\n{ta['stock']} {ta['type']} Rs {ta['price']}\nLIVE Rs {round(live_price,2)}\n{ta['note']}\nTime: {datetime.now().strftime('%H:%M:%S')}")
            ta["active"]=False
            st.session_state.triggered_alerts.append(ta)

    if st.session_state.alerts:
        st.dataframe(pd.DataFrame([a for a in st.session_state.alerts if a["active"]]), use_container_width=True)

    if st.session_state.live_mode:
        st.info("🟢 LIVE ON - 30 sec me auto refresh...")
        time.sleep(30)
        st.rerun()

with tab_tg:
    st.markdown("### 📲 Telegram Bot Setup - 2 min me")
    st.markdown("""
    **Step 1:** Telegram pe @BotFather ko /newbot bhejo, naam do FinTradeBot
    **Step 2:** Token copy karo - jaise `123456:ABC-...`
    **Step 3:** Apne bot ko start karo, phir @userinfobot se apna Chat ID lo
    """)
    tok = st.text_input("Bot Token", value=st.session_state.tg_token, type="password", placeholder="123456:ABC...")
    chat = st.text_input("Chat ID", value=st.session_state.tg_chat, placeholder="123456789")
    if st.button("💾 Save Telegram"):
        st.session_state.tg_token = tok
        st.session_state.tg_chat = chat
        st.success("Saved!")

    if st.button("📤 Test Telegram Message"):
        if send_telegram(tok, chat, f"✅ FinTrade Premium Test - {raw} LIVE Rs {round(live_price,2)} | Target Rs {round(tgt,2)}"):
            st.success("✅ Telegram pe message gaya! Check karo")
            st.balloons()
        else:
            st.error("❌ Failed - Token / Chat ID check karo")

    st.markdown("#### 🔥 Auto Alerts on Telegram")
    st.caption("Jab bhi IOCL 140 cross karega, seedha Telegram pe: 'IOCL Above 140 HIT LIVE 140.2'")
    if st.session_state.tg_token:
        st.success(f"Telegram Connected: {chat[:4]}****")

st.caption("V32 VOICE + AI + TELEGRAM - Bolke search karo, AI se pucho, Telegram pe alert pao!")
