import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import base64
import time
from datetime import datetime

st.set_page_config(page_title="FinTrade Premium", layout="wide", page_icon="💎")

# CSS
st.markdown("""
<style>
.stApp {background: radial-gradient(1200px 600px at 10% -10%, #1a1f5c 0%, #0a0e1a 50%), radial-gradient(1000px 500px at 90% 10%, #5c1a5c 0%, #0a0e1a 60%);}
.header-box {background: rgba(255,255,255,0.05); backdrop-filter: blur(20px); border:1px solid rgba(255,255,255,0.1); border-radius:20px; padding:18px 22px; margin-bottom:20px;}
.top-pin {background: linear-gradient(135deg, rgba(0,209,255,0.18), rgba(112,0,255,0.18)); backdrop-filter: blur(20px); border:1px solid rgba(0,209,255,0.35); border-radius:20px; padding:18px; margin:18px 0; box-shadow: 0 0 40px rgba(0,209,255,0.25);}
.alert-card {background: linear-gradient(135deg, rgba(255,170,0,0.15), rgba(255,0,109,0.15)); border:1px solid rgba(255,170,0,0.4); border-radius:16px; padding:16px; margin:10px 0; animation: pulse 2s infinite;}
.triggered {background: linear-gradient(135deg, rgba(0,255,136,0.2), rgba(0,209,255,0.2)); border:2px solid #00FF88; box-shadow: 0 0 30px rgba(0,255,136,0.4);}
.stTextInput>div>div>input, .stNumberInput>div>div>input {background: rgba(255,255,255,0.06)!important; border:2px solid rgba(0,209,255,0.3)!important; border-radius:12px!important; color:white!important;}
.stButton>button {background: linear-gradient(90deg, #00D1FF, #7000FF)!important; border:none!important; border-radius:12px!important; color:white!important; font-weight:800!important; height:48px!important;}
@keyframes pulse {0% {box-shadow:0 0 0 0 rgba(255,170,0,0.4);} 70% {box-shadow:0 0 0 10px rgba(255,170,0,0);} 100% {box-shadow:0 0 0 0 rgba(255,170,0,0);}}
</style>
""", unsafe_allow_html=True)

# SESSION STATE FOR ALERTS
if "alerts" not in st.session_state:
    st.session_state.alerts = []
if "triggered_alerts" not in st.session_state:
    st.session_state.triggered_alerts = []
if "live_mode" not in st.session_state:
    st.session_state.live_mode = False

# HEADER
def get_logo_html():
    try:
        with open("logo.png", "rb") as f:
            data = base64.b64encode(f.read()).decode()
            return f'<img src="data:image/png;base64,{data}" width="65" style="border-radius:12px;">'
    except:
        return '<div style="font-size:42px;">💎</div>'

logo_html = get_logo_html()
st.markdown(f"""
<div class="header-box">
  <div style="display:flex; align-items:center; gap:16px;">
    <div>{logo_html}</div>
    <div>
      <h1 style="margin:0; font-size:30px; color:white;">FinTrade Premium</h1>
      <p style="margin:0; color:#8892b0; font-size:11px;">V31 LIVE ALERTS EDITION | 100% INDIAN NSE/BSE | REAL-TIME + BROWSER NOTIFICATION</p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

SMART_MAP = {"IOCL":"IOC.NS","IOC":"IOC.NS","GAIL":"GAIL.NS","CUPID":"CUPID.NS","RELIANCE":"RELIANCE.NS","TCS":"TCS.NS","ZOMATO":"ETERNAL.NS","ETERNAL":"ETERNAL.NS","PAYTM":"PAYTM.NS","SUZLON":"SUZLON.NS","YESBANK":"YESBANK.NS","IDEA":"IDEA.NS","RVNL":"RVNL.NS","IRFC":"IRFC.NS","MAZDOCK":"MAZDOCK.NS","TATAMOTORS":"TATAMOTORS.NS","SBIN":"SBIN.NS"}

def load_data(tick):
    try:
        t = yf.Ticker(tick)
        df = t.history(period="3mo", interval="1d", auto_adjust=False)
        if df.empty:
            df = t.history(period="1mo", interval="1d", auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.dropna()
        if "Close" in df.columns:
            df = df[df["Close"] > 0]
        return df
    except:
        return pd.DataFrame()

def get_live_price(tick):
    try:
        t = yf.Ticker(tick)
        # fast live price
        price = t.fast_info.last_price
        if price is None or pd.isna(price):
            df = t.history(period="1d", interval="1m")
            if not df.empty:
                price = float(df["Close"].dropna().iloc[-1])
            else:
                df = load_data(tick)
                price = float(df["Close"].dropna().iloc[-1]) if not df.empty else 0
        return float(price)
    except:
        return 0

def get_signal(df):
    try:
        close = df["Close"].dropna()
        if len(close) < 20: return "HOLD"
        ema20 = close.ewm(span=20).mean().iloc[-1]
        ema50 = close.ewm(span=50).mean().iloc[-1]
        last = close.iloc[-1]
        if ema20 > ema50 and last > ema20: return "BUY"
        elif ema20 < ema50: return "SELL"
        else: return "HOLD"
    except:
        return "HOLD"

# SEARCH
st.markdown("#### UNIVERSAL STOCK SEARCH")
c1, c2, c3 = st.columns([5,1,1])
with c1:
    user_input = st.text_input("search", value="IOCL", placeholder="IOCL, GAIL...", label_visibility="collapsed")
with c2:
    st.button("SEARCH", use_container_width=True)
with c3:
    if st.button("🔔 ALERTS", use_container_width=True):
        st.session_state.show_alerts = True

raw = user_input.upper().strip()
ticker = SMART_MAP.get(raw, raw + ".NS" if ".NS" not in raw and ".BO" not in raw else raw)
df = load_data(ticker)
if df.empty:
    df = load_data(ticker.replace(".NS",".BO"))
    if not df.empty: ticker = ticker.replace(".NS",".BO")
if df.empty:
    st.error("Data not found")
    st.stop()

last = float(df["Close"].dropna().iloc[-1])
live_price = get_live_price(ticker)
if live_price == 0 or pd.isna(live_price):
    live_price = last

low_min = float(df["Low"].dropna().tail(20).min())
high_max = float(df["High"].dropna().tail(20).max())
if low_min == 0 or pd.isna(low_min): low_min = last * 0.95
if high_max == 0 or pd.isna(high_max): high_max = last * 1.05
tgt = last + (last - low_min) * 1.5
if tgt <= last: tgt = high_max
profit = ((tgt - last) / last * 100) if last != 0 else 0
sig = get_signal(df)
profit_show = -abs(profit) if sig == "SELL" else abs(profit)
sig_color = "#00FF88" if sig == "BUY" else "#FF4D6A" if sig == "SELL" else "#FFAA00"

st.markdown(f"""
<div class="top-pin">
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <div>
      <h2 style="color:white; margin:0; font-size:22px;">{raw} <span style="color:#8892b0; font-size:12px;">{ticker}</span> <span style="background:{sig_color}; color:black; padding:4px 12px; border-radius:20px; font-size:11px;">{sig}</span> <span style="background:rgba(0,209,255,0.2); color:#00D1FF; padding:4px 10px; border-radius:20px; font-size:11px;">LIVE Rs {round(live_price,2)}</span></h2>
      <p style="color:#00D1FF; margin:6px 0 0 0; font-size:12px;">LTP Rs {round(last,2)} | Target Rs {round(tgt,2)} | SL Rs {round(low_min,2)}</p>
    </div>
    <div style="text-align:right;">
      <p style="color:{sig_color}; font-size:28px; font-weight:900; margin:0;">Rs {round(live_price,2)}</p>
      <p style="color:#00FF88; font-size:11px; margin:0;">● LIVE</p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# TABS
tab_chart, tab_alert, tab_scanner = st.tabs(["📈 Premium Chart", "🔔 LIVE PRICE ALERTS", "🔍 Scanner 500"])

with tab_chart:
    df_c = df.tail(80)
    fig = go.Figure(data=[go.Candlestick(x=df_c.index, open=df_c["Open"], high=df_c["High"], low=df_c["Low"], close=df_c["Close"], increasing_line_color="#00FF88", decreasing_line_color="#FF4D6A")])
    fig.update_layout(template="plotly_dark", height=460, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)
    bse_sym = ticker.replace(".NS","").replace(".BO","")
    st.components.v1.iframe(f"https://s.tradingview.com/widgetembed/?symbol=BSE%3A{bse_sym}&interval=D&theme=dark", height=380)

with tab_alert:
    st.markdown("### 🔔 Live Price Alerts - Ghanti Bajega!")
    
    col_live1, col_live2 = st.columns([2,1])
    with col_live1:
        st.session_state.live_mode = st.toggle("🟢 LIVE MODE ON (30 sec auto-check)", value=st.session_state.live_mode)
        st.caption("ON karo toh har 30 sec me price check hoga, target hit pe sound + popup ayega")
    with col_live2:
        if st.button("🔄 Check Now"):
            st.rerun()

    st.divider()
    st.markdown(f"**Current: {raw} - LIVE Rs {round(live_price,2)}**")
    
    c_a1, c_a2, c_a3, c_a4 = st.columns(4)
    with c_a1:
        alert_type = st.selectbox("Alert Type", ["Above", "Below", "Target Hit", "SL Hit"])
    with c_a2:
        default_price = tgt if "Target" in alert_type else low_min if "SL" in alert_type else live_price
        alert_price = st.number_input("Price Rs", value=float(round(default_price,2)), step=0.05)
    with c_a3:
        note = st.text_input("Note", value=f"{raw} {alert_type}")
    with c_a4:
        if st.button("➕ Add Alert", use_container_width=True):
            new_alert = {
                "id": len(st.session_state.alerts) + 1,
                "stock": raw,
                "ticker": ticker,
                "type": alert_type,
                "price": alert_price,
                "note": note,
                "created": datetime.now().strftime("%H:%M:%S"),
                "active": True
            }
            st.session_state.alerts.append(new_alert)
            st.success(f"Alert set: {raw} {alert_type} Rs {alert_price}")
            st.balloons()

    # CHECK ALERTS
    triggered_now = []
    for alert in st.session_state.alerts:
        if not alert["active"]: continue
        lp = get_live_price(alert["ticker"]) if alert["ticker"] == ticker else live_price
        # Simple check for current ticker
        if alert["ticker"] == ticker:
            if alert["type"] == "Above" and lp >= alert["price"]:
                triggered_now.append(alert)
            elif alert["type"] == "Below" and lp <= alert["price"]:
                triggered_now.append(alert)
            elif alert["type"] == "Target Hit" and lp >= alert["price"]:
                triggered_now.append(alert)
            elif alert["type"] == "SL Hit" and lp <= alert["price"]:
                triggered_now.append(alert)

    # SHOW TRIGGERED WITH SOUND
    if triggered_now:
        st.markdown("""
        <audio autoplay>
          <source src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" type="audio/ogg">
        </audio>
        """, unsafe_allow_html=True)
        
        for ta in triggered_now:
            st.markdown(f"""
            <div class="alert-card triggered">
              <h3 style="margin:0; color:#00FF88;">🔔 ALERT TRIGGERED! {ta['stock']}</h3>
              <p style="margin:5px 0; color:white;">{ta['note']} - Price Rs {round(live_price,2)} {ta['type']} Rs {ta['price']}</p>
              <p style="margin:0; color:#8892b0; font-size:11px;">Triggered at {datetime.now().strftime('%H:%M:%S')} - LTP {round(live_price,2)}</p>
            </div>
            """, unsafe_allow_html=True)
            st.toast(f"🔔 {ta['stock']} {ta['type']} Rs {ta['price']} HIT! LTP {round(live_price,2)}", icon="🔔")
            # Browser notification via JS
            st.components.v1.html(f"""
            <script>
            if (Notification.permission !== "granted") {{ Notification.requestPermission(); }}
            else {{
              new Notification("FinTrade Alert: {ta['stock']}", {{ body: "{ta['note']} - LTP Rs {round(live_price,2)} {ta['type']} {ta['price']}", icon: "https://cdn-icons-png.flaticon.com/512/1827/1827504.png" }});
            }}
            </script>
            """, height=0)
            ta["active"] = False
            st.session_state.triggered_alerts.append(ta)

    # ACTIVE ALERTS TABLE
    st.markdown("#### 📋 Active Alerts")
    if st.session_state.alerts:
        active = [a for a in st.session_state.alerts if a["active"]]
        if active:
            df_alert = pd.DataFrame(active)
            st.dataframe(df_alert[["id","stock","type","price","note","created"]], use_container_width=True)
            if st.button("🗑️ Clear All Alerts"):
                st.session_state.alerts = []
                st.rerun()
        else:
            st.info("No active alerts - All triggered!")
    else:
        st.info("Koi alert nahi hai - Upar se Add Alert karo. Example: IOCL Above 140")

    # TRIGGERED HISTORY
    if st.session_state.triggered_alerts:
        st.markdown("#### ✅ Triggered History")
        st.dataframe(pd.DataFrame(st.session_state.triggered_alerts), use_container_width=True)

    # AUTO REFRESH LOGIC
    if st.session_state.live_mode:
        st.info("🟢 LIVE MODE ON - Har 30 sec me auto-check ho raha hai... Page khula rakho, ghanti bajegi!")
        time.sleep(30)
        st.rerun()

with tab_scanner:
    st.markdown("#### Scanner 500")
    if st.button("SCAN"):
        st.write("Scanning...")

st.caption("V31 LIVE ALERTS - Sound + Popup + Browser Notification - IOCL Above 140 set karo, 140 cross karte hi ghanti!")
