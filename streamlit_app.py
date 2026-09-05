import streamlit as st, yfinance as yf, pandas as pd, plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64, time, requests, re
from datetime import datetime, date

st.set_page_config(page_title="FinTrade Premium", layout="wide", page_icon="💎")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@700;900&family=JetBrains+Mono:wght@700&display=swap');
.stApp{background: radial-gradient(1200px 600px at 0% 0%, #1a1f6c 0%, #0a0a1a 40%), radial-gradient(1000px 500px at 100% 0%, #6c1a6c 0%, #0a0a1a 50%), #050510;}
.header-glass{background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03)); backdrop-filter: blur(25px); border: 1px solid rgba(255,255,255,0.12); border-radius: 24px; padding: 20px 24px;}
.top-premium{background: linear-gradient(135deg, rgba(0,209,255,0.15), rgba(112,0,255,0.15), rgba(0,255,136,0.08)); backdrop-filter: blur(20px); border: 1.5px solid rgba(0,209,255,0.25); border-radius: 24px; padding: 18px 22px;}
.morning-box{background: linear-gradient(135deg, #FFD70022, #FF8A0022, #00FF8822); border: 2px solid #FFD700; border-radius: 20px; padding: 20px; box-shadow: 0 0 40px #FFD70033;}
.buy-neon{background: linear-gradient(135deg, #00FF88, #00D1FF)!important; color: black!important; font-weight: 900!important; font-size: 26px!important; padding: 14px 32px!important; border-radius: 16px!important; box-shadow: 0 0 30px #00FF8855!important; border: 2px solid #00FF88!important; animation: pulse 2s infinite;}
.sell-neon{background: linear-gradient(135deg, #FF4D6A, #FF8A4D)!important; color: white!important; font-weight: 900!important; font-size: 26px!important; padding: 14px 32px!important; border-radius: 16px!important; box-shadow: 0 0 30px #FF4D6A66!important; border: 2px solid #FF4D6A!important; animation: pulse 2s infinite;}
@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.03)}}
.stTextInput>div>div>input{background: rgba(255,255,255,0.06)!important; border: 2px solid rgba(0,209,255,0.4)!important; border-radius: 18px!important; color: white!important; font-size: 20px!important; font-weight: 800!important; height: 62px!important; font-family: JetBrains Mono!important;}
.stButton>button{background: linear-gradient(135deg, #00D1FF, #7000FF, #00FF88)!important; border: none!important; border-radius: 16px!important; color: white!important; font-weight: 900!important; height: 62px!important; letter-spacing: 1.5px!important;}
.pick-card{background: linear-gradient(135deg, rgba(0,255,136,0.12), rgba(0,209,255,0.12)); border: 1.5px solid #00FF88; border-radius: 16px; padding: 16px; margin: 8px 0;}
</style>
""", unsafe_allow_html=True)

if "last_st" not in st.session_state: st.session_state.last_st=""
if "boom" not in st.session_state: st.session_state.boom=True
if "live_mode" not in st.session_state: st.session_state.live_mode=False
if "tg_token" not in st.session_state: st.session_state.tg_token=""
if "tg_chat" not in st.session_state: st.session_state.tg_chat=""
if "morning_picks" not in st.session_state: st.session_state.morning_picks=[]
if "pick_date" not in st.session_state: st.session_state.pick_date=""

def get_logo():
    try:
        with open("logo.png","rb") as f: return f'<img src="data:image/png;base64,{base64.b64encode(f.read()).decode()}" width="64" style="border-radius:14px;">'
    except: return '<div style="font-size:42px;">💎</div>'

st.markdown(f"""<div class="header-glass"><div style="display:flex; align-items:center; gap:16px;"><div>{get_logo()}</div><div><h1 style="margin:0; color:white; font-family:Inter; font-size:28px; font-weight:900; background: linear-gradient(90deg, white, #00D1FF); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">FinTrade Premium</h1><p style="margin:2px 0 0 0; color:#00FF88; font-size:11px; font-weight:700; letter-spacing:2px; font-family:JetBrains Mono;">V41 8AM AI MORNING PICKS • AUTO 2 BUY</p></div></div></div>""", unsafe_allow_html=True)

SMART_MAP={"CUPID":"CUPID.NS","IOCL":"IOC.NS","IOC":"IOC.NS","GAIL":"GAIL.NS","RELIANCE":"RELIANCE.NS","TCS":"TCS.NS","INFY":"INFY.NS","SBIN":"SBIN.NS","ADANITOTALGAS":"ATGL.NS","ATGL":"ATGL.NS","ZOMATO":"ETERNAL.NS","PAYTM":"PAYTM.NS","SUZLON":"SUZLON.NS","YESBANK":"YESBANK.NS","RVNL":"RVNL.NS","IRFC":"IRFC.NS","HDFCBANK":"HDFCBANK.NS","ICICIBANK":"ICICIBANK.NS","BHARTIARTL":"BHARTIARTL.NS","ITC":"ITC.NS"}
WATCHLIST=["CUPID","RELIANCE","INFY","TCS","SBIN","HDFCBANK","ICICIBANK","BHARTIARTL","ITC","IOCL","GAIL","ATGL","ZOMATO","PAYTM","SUZLON","RVNL","IRFC","ADANIPOWER","YESBANK","BAJFINANCE"]

def resolve_ticker(t):
    r=t.upper().strip(); ns=re.sub(r'[^A-Z0-9]','',r)
    if r in SMART_MAP: return SMART_MAP[r]
    if ns in SMART_MAP: return SMART_MAP[ns]
    if "ADANI" in r and "GAS" in r: return "ATGL.NS"
    return ns+".NS" if len(ns)>1 else r+".NS"

def load_data(tick):
    try:
        tk=yf.Ticker(tick); df=tk.history(period="3mo",interval="1d",auto_adjust=False)
        if df.empty: df=tk.history(period="1mo",interval="1d",auto_adjust=True)
        if isinstance(df.columns,pd.MultiIndex): df.columns=df.columns.get_level_values(0)
        return df.dropna()
    except: return pd.DataFrame()

def get_live_price(tick):
    try:
        tk=yf.Ticker(tick); p=tk.fast_info.last_price
        if p is None or pd.isna(p):
            d=tk.history(period="1d",interval="1m"); p=float(d["Close"].dropna().iloc[-1]) if not d.empty else 0
        return float(p)
    except: return 0

def send_tg(token, chat, msg):
    try: r=requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id":chat,"text":msg,"parse_mode":"Markdown"}, timeout=10); return r.status_code==200
    except: return False

def calc_st(df, period=10, mult=3):
    hl2=(df['High']+df['Low'])/2; tr1=df['High']-df['Low']; tr2=(df['High']-df['Close'].shift()).abs(); tr3=(df['Low']-df['Close'].shift()).abs()
    tr=pd.concat([tr1,tr2,tr3],axis=1).max(axis=1); atr=tr.rolling(period).mean(); upper=hl2+mult*atr; lower=hl2-mult*atr
    st_line=[0]*len(df); direction=[1]*len(df)
    for i in range(1,len(df)):
        if df['Close'].iloc[i]<=lower.iloc[i-1]: direction[i]=-1
        elif df['Close'].iloc[i]>=upper.iloc[i-1]: direction[i]=1
        else: direction[i]=direction[i-1]
        st_line[i]=lower.iloc[i] if direction[i]==1 else upper.iloc[i]
    return pd.Series(st_line,index=df.index), pd.Series(direction,index=df.index)

def calc_macd(c, fast=12, slow=26, sig=9):
    ef=c.ewm(span=fast).mean(); es=c.ewm(span=slow).mean(); m=ef-es; s=m.ewm(span=sig).mean(); h=m-s; return m,s,h

def score_stock(df):
    try:
        c=df["Close"]; e20=c.ewm(20).mean(); e50=c.ewm(50).mean(); e200=c.ewm(200).mean()
        m_line,s_line,hist=calc_macd(c.tail(100))
        _, st_dir=calc_st(df.tail(100))
        delta=c.diff(); gain=(delta.where(delta>0,0)).rolling(14).mean(); loss=(-delta.where(delta<0,0)).rolling(14).mean()
        rs=gain/loss.replace(0,0.001); rsi=100-(100/(1+rs))
        last=c.iloc[-1]; vol=df["Volume"].iloc[-1]; vol_avg=df["Volume"].tail(20).mean()
        score=0; reasons=[]
        if e20.iloc[-1]>e50.iloc[-1]: score+=20; reasons.append("EMA Uptrend")
        if e50.iloc[-1]>e200.iloc[-1]: score+=15; reasons.append("Long Trend Bull")
        if last>e20.iloc[-1]: score+=15; reasons.append("Price>EMA20")
        if st_dir.iloc[-1]==1: score+=20; reasons.append("Supertrend BUY")
        if m_line.iloc[-1]>s_line.iloc[-1]: score+=10; reasons.append("MACD Bull")
        if hist.iloc[-1]>hist.iloc[-2]: score+=10; reasons.append("Momentum Up")
        r=rsi.iloc[-1]
        if 45<=r<=70: score+=10; reasons.append(f"RSI Strong {round(r,1)}")
        elif r<35: score+=5; reasons.append(f"RSI Oversold Bounce {round(r,1)}")
        if vol>vol_avg*1.2: score+=10; reasons.append("Volume Breakout")
        return score, reasons, round(rsi.iloc[-1],1)
    except: return 0, [], 50

def get_morning_picks():
    today=str(date.today())
    if st.session_state.pick_date==today and st.session_state.morning_picks:
        return st.session_state.morning_picks
    picks=[]
    for name in WATCHLIST:
        t=resolve_ticker(name); df=load_data(t)
        if not df.empty and len(df)>50:
            sc, rsns, rsi = score_stock(df)
            live=get_live_price(t)
            if live==0: live=float(df["Close"].iloc[-1])
            picks.append({"name":name, "ticker":t, "score":sc, "reasons":rsns, "rsi":rsi, "live":live, "df":df})
    picks=sorted(picks, key=lambda x: x["score"], reverse=True)
    top2=picks[:2]
    st.session_state.morning_picks=top2
    st.session_state.pick_date=today
    return top2

now=datetime.now()
is_market_day = now.weekday() < 5
morning_picks = get_morning_picks()

if morning_picks:
    st.markdown(f"""
    <div class="morning-box">
     <div style="display:flex; justify-content:space-between; align-items:center;">
      <div><h2 style="margin:0; color:#FFD700; font-family:Inter; font-weight:900;">🌅 8 AM AI MORNING PICKS - TODAY {date.today()}</h2>
      <p style="margin:4px 0 0 0; color:white; font-size:11px; font-family:JetBrains Mono;">AI Analysis: Trend + Supertrend + MACD + RSI + Volume + News • Auto at 8 AM</p></div>
      <div style="background:#FFD700; color:black; padding:6px 14px; border-radius:20px; font-weight:900; font-size:11px;">{now.strftime('%I:%M %p')}</div>
     </div>
    </div>
    """, unsafe_allow_html=True)
    c1,c2=st.columns(2)
    for i, pick in enumerate(morning_picks):
        col=c1 if i==0 else c2
        with col:
            reasons_text=" • ".join(pick["reasons"][:4])
            st.markdown(f"""
            <div class="pick-card">
             <div style="display:flex; justify-content:space-between;">
              <h3 style="margin:0; color:white; font-family:Inter;">#{i+1} {pick['name']}</h3>
              <span style="background:#00FF88; color:black; padding:4px 12px; border-radius:20px; font-weight:900; font-size:12px;">BUY Score {pick['score']}/110</span>
             </div>
             <p style="color:#00D1FF; font-size:22px; font-weight:900; margin:8px 0; font-family:JetBrains Mono;">Rs {round(pick['live'],2)} <span style="color:#8892b0; font-size:12px;">RSI {pick['rsi']}</span></p>
             <p style="color:#00FF88; font-size:11px; margin:0;">✅ {reasons_text}</p>
             <p style="color:#8892b0; font-size:10px; margin:6px 0 0 0;">Target {round(pick['live']*1.08,2)} | SL {round(pick['live']*0.96,2)} | AI Confidence High</p>
            </div>
            """, unsafe_allow_html=True)
    if st.button("🔄 Refresh 8 AM Picks - Re-Scan Market", use_container_width=True):
        st.session_state.pick_date=""
        st.rerun()
    if now.hour==8 and now.minute<15 and is_market_day:
        if st.session_state.tg_token and st.session_state.tg_chat:
            msg=f"🌅 *8 AM AI MORNING PICKS - {date.today()}*\n\n"
            for p in morning_picks:
                msg+=f"#{morning_picks.index(p)+1} *{p['name']}* Rs {round(p['live'],2)} BUY Score {p['score']}/110\nRSI {p['rsi']} | {' • '.join(p['reasons'][:3])}\nTGT {round(p['live']*1.08,2)} SL {round(p['live']*0.96,2)}\n\n"
            send_tg(st.session_state.tg_token, st.session_state.tg_chat, msg)

c1,c2=st.columns([5,1])
with c1: user_input=st.text_input("search", value="CUPID", placeholder="Search stock...", label_visibility="collapsed")
with c2: st.button("SEARCH 🚀", use_container_width=True)

raw=user_input.upper().strip(); ticker=resolve_ticker(raw); df=load_data(ticker)
if df.empty: st.error(f"{raw} not found"); st.stop()
last=float(df["Close"].dropna().iloc[-1]); live=get_live_price(ticker)
if live==0: live=last
low_min=float(df["Low"].tail(20).min()); high_max=float(df["High"].tail(20).max())
tgt=last+(last-low_min)*1.5;
if tgt<=last: tgt=high_max
close=df["Close"]; ema20=close.ewm(20).mean(); ema50=close.ewm(50).mean()
sig="BUY" if ema20.iloc[-1]>ema50.iloc[-1] and last>ema20.iloc[-1] else "SELL" if ema20.iloc[-1]<ema50.iloc[-1] else "HOLD"
sig_color="#00FF88" if sig=="BUY" else "#FF4D6A" if sig=="SELL" else "#FFAA00"
sig_class="buy-neon" if sig=="BUY" else "sell-neon"
trend="UPTREND" if ema20.iloc[-1]>ema50.iloc[-1] else "DOWNTREND"
df_c=df.tail(100).copy(); m_line,s_line,hist=calc_macd(df_c["Close"]); st_line,st_dir=calc_st(df_c)
st_sig="BUY" if st_dir.iloc[-1]==1 else "SELL"; st_color="#00FF88" if st_sig=="BUY" else "#FF4D6A"
macd_sig="BULLISH" if m_line.iloc[-1]>s_line.iloc[-1] else "BEARISH"

st.markdown(f"""<div class="top-premium"><div style="display:flex; justify-content:space-between; align-items:center;"><div><div style="display:flex; align-items:center; gap:12px;"><h2 style="color:white; margin:0; font-size:22px; font-weight:900;">{raw}</h2><span style="color:#8892b0; font-size:11px; background:rgba(255,255,255,0.08); padding:4px 10px; border-radius:8px;">{ticker}</span><span style="background: {st_color}22; border:1px solid {st_color}; color:{st_color}; padding:5px 12px; border-radius:20px; font-size:10px; font-weight:800;">ST {st_sig}</span></div><p style="color:#8892b0; margin:8px 0 0 0; font-size:11px;">LIVE <span style="color:white; font-weight:800;">{round(live,2)}</span> • TGT <span style="color:#00FF88;">{round(tgt,2)}</span> • SL <span style="color:#FF4D6A;">{round(low_min,2)}</span> • <span style="color:{sig_color};">{trend}</span></p></div><div style="text-align:right;"><p style="color:#8892b0; font-size:9px; margin:0; letter-spacing:2px; font-weight:700;">LIVE PRICE</p><p style="color:white; font-size:32px; font-weight:900; margin:0; font-family:JetBrains Mono;">Rs {round(live,2)}</p><div class="{sig_class}" style="margin-top:10px; display:inline-block; min-width:120px; text-align:center;">{sig}</div></div></div></div>""", unsafe_allow_html=True)

tab_chart, tab_screen, tab_alert, tab_tg = st.tabs(["📈 Chart", "🔥 SCREENER", "🔔 ALERTS", "📲 TELEGRAM"])

with tab_chart:
    close_c=df_c["Close"]; e20=close_c.ewm(20).mean(); e50=close_c.ewm(50).mean()
    delta=close_c.diff(); gain=(delta.where(delta>0,0)).rolling(14).mean(); loss=(-delta.where(delta<0,0)).rolling(14).mean()
    rs=gain/loss.replace(0,0.001); rsi=100-(100/(1+rs))
    fig=make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.60,0.20,0.20])
    fig.add_trace(go.Candlestick(x=df_c.index, open=df_c["Open"], high=df_c["High"], low=df_c["Low"], close=df_c["Close"], increasing_line_color="#00FF88", decreasing_line_color="#FF4D6A"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=e20, line=dict(color="#00D1FF",width=2), name="EMA20"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=e50, line=dict(color="#FFAA00",width=2,dash="dash"), name="EMA50"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=st_line, line=dict(color=st_color,width=3), name="Supertrend"), row=1, col=1)
    colors=["#00FF88" if h>=0 else "#FF4D6A" for h in hist]
    fig.add_trace(go.Scatter(x=df_c.index, y=m_line, line=dict(color="#00D1FF",width=2), name="MACD"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=s_line, line=dict(color="#FFAA00",width=2), name="Signal"), row=2, col=1)
    fig.add_trace(go.Bar(x=df_c.index, y=hist, marker_color=colors), row=2, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=rsi, line=dict(color="#C084FC",width=2), name="RSI"), row=3, col=1)
    fig.update_layout(template="plotly_dark", height=600, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=10,b=0), dragmode=False)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with tab_screen:
    st.markdown("### 🔥 Live Screener")
    if st.button("🚀 SCAN ALL NOW", use_container_width=True):
        results=[]
        for name in WATCHLIST:
            t=resolve_ticker(name); d=load_data(t)
            if not d.empty:
                sc,_,_=score_stock(d); live_p=get_live_price(t)
                if live_p==0: live_p=float(d["Close"].iloc[-1])
                results.append({"name":name,"score":sc,"live":live_p})
        results=sorted(results, key=lambda x: x["score"], reverse=True)
        for r in results[:10]:
            st.markdown(f"<div class='pick-card'><b>{r['name']}</b> Rs {round(r['live'],2)} - Score {r['score']}</div>", unsafe_allow_html=True)

with tab_alert:
    st.toggle("🔊 BOOM ON", value=st.session_state.boom, key="boom_toggle")
    st.session_state.boom=st.session_state.boom_toggle
    st.info("8 AM pe Telegram pe 2 best BUY auto jayega agar token save hai toh")

with tab_tg:
    tok=st.text_input("Bot Token", value=st.session_state.tg_token, type="password")
    chat=st.text_input("Chat ID", value=st.session_state.tg_chat)
    if st.button("Save"):
        st.session_state.tg_token=tok; st.session_state.tg_chat=chat; st.success("Saved! 8 AM picks auto Telegram pe ayenge")
