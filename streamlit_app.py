import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
import time
import requests
import re
import numpy as np
from datetime import datetime

st.set_page_config(page_title="FinTrade Premium", layout="wide", page_icon="💎")

st.markdown("""
<style>
.stApp {background: radial-gradient(1200px 600px at 10% -10%, #1a1f5c 0%, #0a0e1a 50%), radial-gradient(1000px 500px at 90% 10%, #5c1a5c 0%, #0a0e1a 60%);}
.header-box {background: rgba(255,255,255,0.05); backdrop-filter: blur(20px); border:1px solid rgba(255,255,255,0.1); border-radius:20px; padding:18px; margin-bottom:16px;}
.top-pin {background: linear-gradient(135deg, rgba(0,209,255,0.18), rgba(112,0,255,0.18)); border:1px solid rgba(0,209,255,0.35); border-radius:20px; padding:16px; margin:14px 0;}
.stTextInput>div>div>input {background: rgba(255,255,255,0.06)!important; border:2px solid rgba(0,209,255,0.3)!important; border-radius:14px!important; color:white!important; font-size:20px!important; font-weight:700!important; height:58px!important;}
.stButton>button {background: linear-gradient(90deg, #00D1FF, #7000FF)!important; border:none!important; border-radius:12px!important; color:white!important; font-weight:800!important; height:50px!important;}
</style>
""", unsafe_allow_html=True)

if "alerts" not in st.session_state: st.session_state.alerts = []
if "triggered_alerts" not in st.session_state: st.session_state.triggered_alerts = []
if "live_mode" not in st.session_state: st.session_state.live_mode = False
if "tg_token" not in st.session_state: st.session_state.tg_token = ""
if "tg_chat" not in st.session_state: st.session_state.tg_chat = ""
if "last_trend" not in st.session_state: st.session_state.last_trend = ""
if "last_supertrend" not in st.session_state: st.session_state.last_supertrend = ""

def get_logo():
    try:
        with open("logo.png","rb") as f:
            d=base64.b64encode(f.read()).decode()
            return f'<img src="data:image/png;base64,{d}" width="60" style="border-radius:12px;">'
    except: return '<div style="font-size:40px;">💎</div>'

st.markdown(f"""<div class="header-box"><div style="display:flex; align-items:center; gap:16px;"><div>{get_logo()}</div><div><h1 style="margin:0; color:white; font-size:28px;">FinTrade Premium</h1><p style="margin:0; color:#8892b0; font-size:10px;">V36 MACD + SUPERTREND + AUTO TELEGRAM | NO VOICE | ADANI FIX | PINCH ZOOM</p></div></div></div>""", unsafe_allow_html=True)

SMART_MAP = {"IOCL":"IOC.NS","IOC":"IOC.NS","GAIL":"GAIL.NS","CUPID":"CUPID.NS","RELIANCE":"RELIANCE.NS","TCS":"TCS.NS","INFY":"INFY.NS","SBIN":"SBIN.NS","TATAMOTORS":"TATAMOTORS.NS","ADANITOTALGAS":"ATGL.NS","ADANI TOTAL GAS":"ATGL.NS","ATGL":"ATGL.NS","ADANIGREEN":"ADANIGREEN.NS","ADANI GREEN":"ADANIGREEN.NS","ADANIENT":"ADANIENT.NS","ADANIPORTS":"ADANIPORTS.NS","ADANIPOWER":"ADANIPOWER.NS","AWL":"AWL.NS","ZOMATO":"ETERNAL.NS","PAYTM":"PAYTM.NS","SUZLON":"SUZLON.NS","YESBANK":"YESBANK.NS","IDEA":"IDEA.NS","RVNL":"RVNL.NS","IRFC":"IRFC.NS"}
def resolve_ticker(txt):
    raw = txt.upper().strip()
    nospace = re.sub(r'[^A-Z0-9]', '', raw)
    if raw in SMART_MAP: return SMART_MAP[raw]
    if nospace in SMART_MAP: return SMART_MAP[nospace]
    if "ADANI" in raw:
        if "GAS" in raw: return "ATGL.NS"
        if "GREEN" in raw: return "ADANIGREEN.NS"
        if "POWER" in raw: return "ADANIPOWER.NS"
        if "PORT" in raw: return "ADANIPORTS.NS"
        if "ENT" in raw: return "ADANIENT.NS"
    return nospace + ".NS" if len(nospace)>1 else raw + ".NS"

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

def send_telegram(token, chat_id, msg):
    try:
        url=f"https://api.telegram.org/bot{token}/sendMessage"
        r=requests.post(url, json={"chat_id":chat_id, "text":msg, "parse_mode":"Markdown"}, timeout=10)
        return r.status_code==200
    except: return False

# SUPERTREND FUNCTION
def calculate_supertrend(df, period=10, multiplier=3):
    hl2 = (df['High'] + df['Low']) / 2
    atr = (df['High'] - df['Low']).rolling(period).mean()
    # Better ATR
    tr1 = df['High'] - df['Low']
    tr2 = (df['High'] - df['Close'].shift()).abs()
    tr3 = (df['Low'] - df['Close'].shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()

    upper_band = hl2 + (multiplier * atr)
    lower_band = hl2 - (multiplier * atr)

    supertrend = [0]*len(df)
    direction = [1]*len(df)

    for i in range(1, len(df)):
        if df['Close'].iloc[i] <= lower_band.iloc[i-1]:
            direction[i] = -1
        elif df['Close'].iloc[i] >= upper_band.iloc[i-1]:
            direction[i] = 1
        else:
            direction[i] = direction[i-1]

        if direction[i] == 1:
            supertrend[i] = lower_band.iloc[i]
        else:
            supertrend[i] = upper_band.iloc[i]

    return pd.Series(supertrend, index=df.index), pd.Series(direction, index=df.index)

# MACD FUNCTION
def calculate_macd(close, fast=12, slow=26, signal=9):
    ema_fast = close.ewm(span=fast).mean()
    ema_slow = close.ewm(span=slow).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal).mean()
    hist = macd - signal_line
    return macd, signal_line, hist

st.markdown("#### ⚡ UNIVERSAL SEARCH - 500+ Stocks")
c1,c2,c3 = st.columns([5,1,1])
with c1: user_input = st.text_input("search", value="IOCL", placeholder="IOCL, Adani total gas...", label_visibility="collapsed")
with c2: st.button("SEARCH", use_container_width=True)
with c3: st.button("ALERTS", use_container_width=True)

raw=user_input.upper().strip()
ticker=resolve_ticker(raw)
df=load_data(ticker)
if df.empty and ".NS" in ticker:
    df=load_data(ticker.replace(".NS",".BO"))
    if not df.empty: ticker=ticker.replace(".NS",".BO")
if df.empty and "ADANI" in raw and "GAS" in raw:
    ticker="ATGL.NS"; df=load_data(ticker)
if df.empty: st.error(f"{raw} ({ticker}) not found"); st.stop()

last=float(df["Close"].dropna().iloc[-1])
live_price=get_live_price(ticker)
if live_price==0 or pd.isna(live_price): live_price=last
low_min=float(df["Low"].dropna().tail(20).min())
high_max=float(df["High"].dropna().tail(20).max())
if low_min==0: low_min=last*0.95
if high_max==0: high_max=last*1.05
tgt=last+(last-low_min)*1.5
if tgt<=last: tgt=high_max

close=df["Close"]
ema20=close.ewm(20).mean()
ema50=close.ewm(50).mean()
sig="BUY" if ema20.iloc[-1]>ema50.iloc[-1] and last>ema20.iloc[-1] else "SELL" if ema20.iloc[-1]<ema50.iloc[-1] else "HOLD"
sig_color="#00FF88" if sig=="BUY" else "#FF4D6A" if sig=="SELL" else "#FFAA00"
trend = "UPTREND" if ema20.iloc[-1] > ema50.iloc[-1] else "DOWNTREND"

# INDICATORS CALC
df_c = df.tail(100).copy()
macd_line, signal_line, hist = calculate_macd(df_c["Close"])
st_line, st_dir = calculate_supertrend(df_c)

super_trend_signal = "BUY" if st_dir.iloc[-1]==1 else "SELL"
super_color = "#00FF88" if super_trend_signal=="BUY" else "#FF4D6A"
macd_signal = "BULLISH" if macd_line.iloc[-1] > signal_line.iloc[-1] else "BEARISH"

st.markdown(f"""
<div class="top-pin">
<div style="display:flex; justify-content:space-between;">
<div>
<h2 style="color:white; margin:0; font-size:20px;">{raw} <span style="color:#8892b0; font-size:11px;">{ticker}</span> <span style="background:{sig_color}; color:black; padding:4px 12px; border-radius:20px; font-size:11px;">{sig}</span> <span style="background:{super_color}; color:black; padding:4px 10px; border-radius:20px; font-size:10px;">ST {super_trend_signal}</span> <span style="background:rgba(0,209,255,0.3); color:#00D1FF; padding:4px 10px; border-radius:20px; font-size:10px;">MACD {macd_signal}</span></h2>
<p style="color:#00D1FF; margin:6px 0 0 0; font-size:11px;">LIVE {round(live_price,2)} | Target {round(tgt,2)} | SL {round(low_min,2)} | {trend} | Supertrend {super_trend_signal}</p>
</div>
<div style="text-align:right;">
<p style="color:{sig_color}; font-size:26px; font-weight:900; margin:0;">Rs {round(live_price,2)}</p>
<p style="color:{super_color}; font-size:10px; margin:0;">● ST {super_trend_signal} + MACD</p>
</div>
</div>
</div>
""", unsafe_allow_html=True)

# AUTO TELEGRAM LOGIC - TREND FLIP DETECTION
auto_triggered = False
auto_msg = ""
if st.session_state.last_supertrend!= "" and st.session_state.last_supertrend!= super_trend_signal:
    auto_triggered = True
    auto_msg = f"🚨 *AUTO ALERT {raw}* Supertrend Flip! {st.session_state.last_supertrend} -> {super_trend_signal} LIVE Rs {round(live_price,2)} Target {round(tgt,2)} SL {round(low_min,2)}"

if st.session_state.last_trend!= "" and st.session_state.last_trend!= trend:
    auto_triggered = True
    auto_msg += f"\n📈 Trend Flip {st.session_state.last_trend} -> {trend}"

# Update last states
st.session_state.last_trend = trend
st.session_state.last_supertrend = super_trend_signal

if auto_triggered and st.session_state.tg_token and st.session_state.tg_chat:
    send_telegram(st.session_state.tg_token, st.session_state.tg_chat, auto_msg)
    st.toast(f"📲 Auto Telegram Sent: {super_trend_signal}", icon="🚀")

tab_chart, tab_ai, tab_alert, tab_tg = st.tabs(["📈 Chart MACD+ST", "🤖 AI", "🔔 ALERTS", "📲 TELEGRAM"])

with tab_chart:
    close_c = df_c["Close"]
    ema20_c = close_c.ewm(20).mean()
    ema50_c = close_c.ewm(50).mean()
    delta = close_c.diff()
    gain = (delta.where(delta>0, 0)).rolling(14).mean()
    loss = (-delta.where(delta<0, 0)).rolling(14).mean()
    rs = gain / loss.replace(0, 0.001)
    rsi = 100 - (100 / (1 + rs))
    sup = float(df_c["Low"].tail(20).min())
    res = float(df_c["High"].tail(20).max())

    # 3 rows: Price+Supertrend, MACD, RSI
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.60, 0.20, 0.20],
                        subplot_titles=(f"{raw} {trend} | Supertrend {super_trend_signal} | Range {round(sup,2)}-{round(res,2)} | Pinch Zoom", f"MACD {macd_signal} - Bullish/Bearish Momentum", "RSI Momentum"))

    fig.add_trace(go.Candlestick(x=df_c.index, open=df_c["Open"], high=df_c["High"], low=df_c["Low"], close=df_c["Close"], name="Price", increasing_line_color="#00FF88", decreasing_line_color="#FF4D6A"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=ema20_c, line=dict(color="#00D1FF", width=2), name="Bullish EMA20"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=ema50_c, line=dict(color="#FFAA00", width=2, dash="dash"), name="Bearish EMA50"), row=1, col=1)
    # SUPERTREND LINES
    fig.add_trace(go.Scatter(x=df_c.index, y=st_line, line=dict(color=super_color, width=3), name=f"Supertrend {super_trend_signal}"), row=1, col=1)
    # Fill bullish/bearish supertrend background
    for i in range(1, len(df_c)):
        if st_dir.iloc[i]==1:
            fig.add_trace(go.Scatter(x=[df_c.index[i]], y=[df_c["Low"].iloc[i]], mode="markers", marker=dict(color="#00FF88", size=4, symbol="triangle-up"), showlegend=False), row=1, col=1)

    fig.add_hline(y=sup, line=dict(color="#00FF88", width=1, dash="dot"), annotation_text=f"Support {round(sup,2)}", row=1, col=1)
    fig.add_hline(y=res, line=dict(color="#FF4D6A", width=1, dash="dot"), annotation_text=f"Res {round(res,2)}", row=1, col=1)

    # MACD
    fig.add_trace(go.Scatter(x=df_c.index, y=macd_line, line=dict(color="#00D1FF", width=2), name="MACD Line"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=signal_line, line=dict(color="#FFAA00", width=2), name="Signal"), row=2, col=1)
    colors = ["#00FF88" if h>=0 else "#FF4D6A" for h in hist]
    fig.add_trace(go.Bar(x=df_c.index, y=hist, marker_color=colors, name="MACD Hist Bull/Bear"), row=2, col=1)

    # RSI
    fig.add_trace(go.Scatter(x=df_c.index, y=rsi, line=dict(color="#C084FC", width=2), name="RSI"), row=3, col=1)
    fig.add_hline(y=70, line=dict(color="#FF4D6A", dash="dash"), row=3, col=1)
    fig.add_hline(y=30, line=dict(color="#00FF88", dash="dash"), row=3, col=1)

    fig.update_layout(template="plotly_dark", height=850, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_rangeslider_visible=False, showlegend=True, legend=dict(orientation="h", y=1.01, x=0, font=dict(size=9)), margin=dict(l=0,r=0,t=35,b=0), dragmode="zoom", hovermode="x unified")
    config = {'scrollZoom': True, 'doubleClick': 'reset', 'modeBarButtonsToAdd': ['drawline','drawrect','eraseshape'], 'displaylogo': False}
    st.plotly_chart(fig, use_container_width=True, config=config)

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("📈 TREND", trend, delta=f"{sig}")
    with c2: st.metric("🔥 SUPERTREND", super_trend_signal, delta=f"Line {round(st_line.iloc[-1],2)}")
    with c3: st.metric("⚡ MACD", macd_signal, delta=f"{round(macd_line.iloc[-1],3)}")
    with c4: st.metric("💪 RSI", f"{round(rsi.iloc[-1],1)}", delta="Bull" if rsi.iloc[-1]>50 else "Bear")

    st.success(f"🔥 Supertrend = {super_trend_signal} ({super_color}) | MACD = {macd_signal} | Auto Telegram {'ON ✅' if st.session_state.tg_token else 'OFF - Telegram me Token dalo'}")
    st.info("👆 2 finger pinch = zoom | MACD green = bullish momentum, red = bearish | Supertrend green line = BUY, red = SELL")

    bse_sym = ticker.replace(".NS","").replace(".BO","")
    st.components.v1.iframe(f"https://s.tradingview.com/widgetembed/?symbol=BSE%3A{bse_sym}&interval=D&theme=dark&studies=Supertrend%40tv-basicstudies%2CMACD%40tv-basicstudies%2CRSI%40tv-basicstudies", height=500)

with tab_ai:
    st.markdown(f"### 🤖 AI + Supertrend + MACD")
    st.markdown(f"""
    - **Supertrend:** {super_trend_signal} at {round(st_line.iloc[-1],2)} - {'Price is above ST = Strong Bullish' if super_trend_signal=='BUY' else 'Price below ST = Strong Bearish'}
    - **MACD:** {macd_signal} - MACD {round(macd_line.iloc[-1],3)} vs Signal {round(signal_line.iloc[-1],3)} - Histogram {'Green = Buying pressure' if hist.iloc[-1]>0 else 'Red = Selling pressure'}
    - **RSI:** {round(rsi.iloc[-1],1)} - {'Momentum strong' if rsi.iloc[-1]>60 else 'Weak'}
    - **Range:** {round(sup,2)} - {round(res,2)}
    """)
    st.metric("Final Signal", f"{super_trend_signal} + {macd_signal}", delta=sig)

with tab_alert:
    st.markdown("### 🔔 LIVE + AUTO TELEGRAM")
    auto_on = st.checkbox("🤖 AUTO TELEGRAM ON - Trend flip pe auto message", value=True)
    st.session_state.live_mode = st.toggle("🟢 LIVE MODE 30 sec auto-check", value=st.session_state.live_mode)
    ca1,ca2,ca3 = st.columns(3)
    with ca1: atype=st.selectbox("Type", ["Above","Below","Target Hit","SL Hit","Supertrend Flip","MACD Cross"])
    with ca2:
        def_p=tgt if "Target" in atype else low_min if "SL" in atype else live_price
        aprice=st.number_input("Price", value=float(round(def_p,2)), step=0.05)
    with ca3: note=st.text_input("Note", value=f"{raw} {atype}")
    if st.button("➕ Add Alert"):
        na={"id":len(st.session_state.alerts)+1,"stock":raw,"ticker":ticker,"type":atype,"price":aprice,"note":note,"created":datetime.now().strftime("%H:%M:%S"),"active":True}
        st.session_state.alerts.append(na)
        st.success(f"Alert {atype} set!")
        if st.session_state.tg_token:
            send_telegram(st.session_state.tg_token, st.session_state.tg_chat, f"🔔 Alert Set {raw} {atype} {aprice} LIVE {round(live_price,2)} ST {super_trend_signal} MACD {macd_signal}")
    if auto_triggered and auto_on:
        st.warning(f"🤖 AUTO TRIGGER: {auto_msg}")
    if st.session_state.live_mode:
        st.info("🟢 LIVE + AUTO TELEGRAM ON - 30 sec me check - Trend flip pe auto Telegram jayega")
        time.sleep(30)
        st.rerun()

with tab_tg:
    st.markdown("### 📲 Telegram - Auto Setup")
    st.markdown("BotFather -> /newbot -> Token lo | @userinfobot se Chat ID lo")
    tok = st.text_input("Bot Token", value=st.session_state.tg_token, type="password")
    chat = st.text_input("Chat ID", value=st.session_state.tg_chat)
    if st.button("💾 Save Telegram"):
        st.session_state.tg_token=tok; st.session_state.tg_chat=chat; st.success("Saved! Auto Telegram ON")
    if st.button("📤 Test - Supertrend + MACD"):
        msg = f"✅ *{raw} TEST*\nLIVE Rs {round(live_price,2)}\nSupertrend: {super_trend_signal} {round(st_line.iloc[-1],2)}\nMACD: {macd_signal} {round(macd_line.iloc[-1],3)}\nRSI: {round(rsi.iloc[-1],1)}\nTrend: {trend}"
        if send_telegram(tok, chat, msg): st.success("✅ Gaya Telegram pe!"); st.balloons()
        else: st.error("❌ Token/Chat ID check")
    st.markdown("""
    **🤖 AUTO TELEGRAM kaise kaam karega?**
    - IOCL DOWNTREND se UPTREND hua -> Auto message: `Supertrend Flip SELL->BUY`
    - MACD BEARISH se BULLISH hua -> Auto message
    - LIVE MODE ON rakho, tab har 30 sec check hoga
    """)

st.caption("V36 - MACD + Supertrend + Auto Telegram - Two finger zoom + Bullish/Bearish")
