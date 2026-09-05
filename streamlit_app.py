import streamlit as st, yfinance as yf, pandas as pd, plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64, requests, re
from datetime import date, datetime

st.set_page_config(page_title="FinTrade God", layout="wide", page_icon="💎")

# GOD LEVEL CSS - UNBELIEVABLE
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700&family=JetBrains+Mono:wght@800&display=swap');
.stApp{
 background: #020208;
 background-image:
   radial-gradient(at 0% 0%, hsla(212,100%,56%,0.25) 0px, transparent 50%),
   radial-gradient(at 20% 10%, hsla(273,100%,60%,0.25) 0px, transparent 50%),
   radial-gradient(at 90% 0%, hsla(158,100%,50%,0.20) 0px, transparent 50%),
   radial-gradient(at 80% 80%, hsla(48,100%,50%,0.15) 0px, transparent 50%);
}
.header-god{
 background: linear-gradient(180deg, rgba(255,255,255,0.09) 0%, rgba(255,255,255,0.02) 100%);
 backdrop-filter: blur(40px) saturate(180%);
 -webkit-backdrop-filter: blur(40px) saturate(180%);
 border: 1px solid rgba(255,255,255,0.1);
 border-radius: 28px;
 padding: 18px 26px;
 box-shadow: 0 20px 80px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.15), inset 0 -1px 0 rgba(255,255,255,0.05);
 position: relative;
 overflow: hidden;
}
.header-god::after{
 content:'';
 position: absolute;
 top: -50%; left: -50%;
 width: 200%; height: 200%;
 background: linear-gradient(120deg, transparent 20%, rgba(255,255,255,0.05) 50%, transparent 80%);
 animation: shimmer 4s infinite;
}
@keyframes shimmer{0%{transform: translateX(-100%) rotate(20deg)}100%{transform: translateX(100%) rotate(20deg)}}

.pick-god{
 background: linear-gradient(135deg, rgba(0,255,136,0.10) 0%, rgba(0,209,255,0.08) 50%, rgba(112,0,255,0.08) 100%);
 backdrop-filter: blur(30px);
 border: 1.5px solid transparent;
 background-clip: padding-box;
 border-radius: 24px;
 padding: 20px 20px 16px 20px;
 position: relative;
 box-shadow: 0 12px 40px rgba(0,255,136,0.12), inset 0 1px 0 rgba(255,255,255,0.1);
 transition: all 0.4s cubic-bezier(0.23,1,0.32,1);
}
.pick-god::before{
 content:'';
 position: absolute;
 inset: 0;
 border-radius: 24px;
 padding: 1.5px;
 background: linear-gradient(135deg, #00FF88, #00D1FF, #7000FF);
 -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
 -webkit-mask-composite: xor;
 mask-composite: exclude;
 pointer-events: none;
}
.pick-god:hover{transform: translateY(-6px) scale(1.02); box-shadow: 0 20px 60px rgba(0,255,136,0.25);}

.top-god{
 background: linear-gradient(100deg, rgba(0,209,255,0.14) 0%, rgba(112,0,255,0.18) 40%, rgba(0,255,136,0.10) 100%);
 backdrop-filter: blur(40px) saturate(150%);
 border: 1px solid rgba(255,255,255,0.12);
 border-radius: 28px;
 padding: 24px 26px;
 box-shadow: 0 24px 80px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.05) inset;
 position: relative;
 overflow: hidden;
}
.top-god::before{
 content:'';
 position: absolute;
 top: 0; left: 0; right: 0; height: 1px;
 background: linear-gradient(90deg, transparent, #00D1FF, #00FF88, transparent);
}
.live-price{
 font-family: 'Space Grotesk', sans-serif;
 font-weight: 700;
 font-size: 38px;
 letter-spacing: -1.5px;
 background: linear-gradient(90deg, #fff 0%, #a5b4fc 100%);
 -webkit-background-clip: text;
 -webkit-text-fill-color: transparent;
 text-shadow: 0 0 30px rgba(255,255,255,0.3);
}
.buy-god{
 background: linear-gradient(135deg, #00FF88 0%, #00E5FF 100%)!important;
 color: #001a0a!important;
 font-family: 'Space Grotesk'!important;
 font-weight: 700!important;
 font-size: 15px!important;
 letter-spacing: 1.5px!important;
 padding: 14px 28px!important;
 border-radius: 14px!important;
 border: none!important;
 box-shadow: 0 0 30px rgba(0,255,136,0.5), 0 8px 24px rgba(0,255,136,0.3)!important;
 position: relative;
 overflow: hidden;
}
.sell-god{
 background: linear-gradient(135deg, #FF4D6A 0%, #FF8A4D 100%)!important;
 color: white!important;
 font-family: 'Space Grotesk'!important;
 font-weight: 700!important;
 font-size: 15px!important;
 letter-spacing: 1.5px!important;
 padding: 14px 28px!important;
 border-radius: 14px!important;
 border: none!important;
 box-shadow: 0 0 30px rgba(255,77,106,0.5)!important;
}
.stTextInput>div>div>input{
 background: rgba(255,255,255,0.06)!important;
 backdrop-filter: blur(20px)!important;
 border: 1.5px solid rgba(255,255,255,0.12)!important;
 border-radius: 20px!important;
 color: white!important;
 font-family: 'JetBrains Mono'!important;
 font-weight: 800!important;
 font-size: 18px!important;
 height: 64px!important;
 box-shadow: inset 0 1px 0 rgba(255,255,255,0.1), 0 8px 32px rgba(0,0,0,0.3)!important;
 transition: all 0.3s!important;
}
.stTextInput>div>div>input:focus{
 border-color: #00D1FF!important;
 box-shadow: 0 0 0 4px rgba(0,209,255,0.15), inset 0 1px 0 rgba(255,255,255,0.1)!important;
}
.stButton>button{
 background: linear-gradient(135deg, #00D1FF 0%, #7000FF 50%, #00FF88 100%)!important;
 border: none!important;
 border-radius: 18px!important;
 color: white!important;
 font-family: 'Space Grotesk'!important;
 font-weight: 700!important;
 height: 64px!important;
 letter-spacing: 1px!important;
 box-shadow: 0 10px 30px rgba(0,209,255,0.35)!important;
 transition: all 0.3s!important;
}
.stButton>button:hover{transform: translateY(-2px); box-shadow: 0 14px 40px rgba(0,209,255,0.5)!important;}
.score-ring{
 width: 56px; height: 56px;
 border-radius: 50%;
 background: conic-gradient(#00FF88 var(--p), rgba(255,255,255,0.1) 0);
 display: flex; align-items: center; justify-content: center;
 position: relative;
}
.score-ring::before{
 content:''; position: absolute; inset: 4px; background: #0a1220; border-radius: 50%;
}
.ticker-tape{
 background: rgba(0,0,0,0.4);
 border: 1px solid rgba(255,255,255,0.06);
 border-radius: 100px;
 padding: 8px 16px;
 font-family: JetBrains Mono;
 font-size: 10px;
 letter-spacing: 1px;
 color: #8892b0;
}
</style>
""", unsafe_allow_html=True)

if "morning_picks" not in st.session_state: st.session_state.morning_picks=[]
if "pick_date" not in st.session_state: st.session_state.pick_date=""
if "tg_token" not in st.session_state: st.session_state.tg_token=""
if "tg_chat" not in st.session_state: st.session_state.tg_chat=""

def get_logo():
    try:
        with open("logo.png","rb") as f: return f'<img src="data:image/png;base64,{base64.b64encode(f.read()).decode()}" width="58" style="border-radius:16px; box-shadow:0 0 20px #00D1FF88;">'
    except: return '<div style="font-size:38px; filter:drop-shadow(0 0 18px #00D1FF);">💎</div>'

# HEADER UNBELIEVABLE
st.markdown(f"""
<div class="header-god">
 <div style="display:flex; justify-content:space-between; align-items:center; position:relative; z-index:2;">
  <div style="display:flex; align-items:center; gap:18px;">
   <div>{get_logo()}</div>
   <div>
    <div style="display:flex; align-items:center; gap:10px;">
     <h1 style="margin:0; color:white; font-family:Space Grotesk; font-size:26px; font-weight:700; letter-spacing:-0.5px;">FinTrade</h1>
     <span style="background: linear-gradient(135deg,#00FF88,#00D1FF); -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-family:Space Grotesk; font-weight:700; font-size:26px;">Premium</span>
     <span style="background: rgba(0,255,136,0.15); border:1px solid #00FF88; color:#00FF88; font-size:8px; padding:3px 8px; border-radius:100px; font-family:JetBrains Mono; letter-spacing:1px; font-weight:800; margin-left:6px;">LIVE</span>
    </div>
    <div style="display:flex; gap:8px; margin-top:6px;">
     <span class="ticker-tape">● NIFTY 24,812 ▲ 0.8%</span>
     <span class="ticker-tape">MARKET OPEN • {datetime.now().strftime('%I:%M %p')}</span>
    </div>
   </div>
  </div>
  <div style="text-align:right; position:relative; z-index:2;">
   <p style="margin:0; color:#fff; font-family:JetBrains Mono; font-size:11px; letter-spacing:1px; opacity:0.6;">V42 GOD MODE</p>
   <p style="margin:2px 0 0 0; color:#00FF88; font-family:Space Grotesk; font-size:10px; font-weight:700; letter-spacing:2px;">UNBELIEVABLE UI • AI PICKS</p>
  </div>
 </div>
</div>
""", unsafe_allow_html=True)

SMART_MAP={"CUPID":"CUPID.NS","IOCL":"IOC.NS","IOC":"IOC.NS","GAIL":"GAIL.NS","RELIANCE":"RELIANCE.NS","TCS":"TCS.NS","INFY":"INFY.NS","SBIN":"SBIN.NS","ATGL":"ATGL.NS","ZOMATO":"ETERNAL.NS","PAYTM":"PAYTM.NS","SUZLON":"SUZLON.NS","YESBANK":"YESBANK.NS","RVNL":"RVNL.NS","IRFC":"IRFC.NS","HDFCBANK":"HDFCBANK.NS","ICICIBANK":"ICICIBANK.NS","BHARTIARTL":"BHARTIARTL.NS","ITC":"ITC.NS"}
WATCHLIST=["CUPID","RELIANCE","INFY","TCS","SBIN","HDFCBANK","ICICIBANK","BHARTIARTL","ITC","IOCL","GAIL","ATGL","ZOMATO","PAYTM","SUZLON","RVNL","IRFC","ADANIPOWER","YESBANK","BAJFINANCE"]

def resolve_ticker(t):
    r=t.upper().strip(); ns=re.sub(r'[^A-Z0-9]','',r)
    if r in SMART_MAP: return SMART_MAP[r]
    if ns in SMART_MAP: return SMART_MAP[ns]
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
        m_line,s_line,hist=calc_macd(c.tail(100)); _, st_dir=calc_st(df.tail(100))
        delta=c.diff(); gain=(delta.where(delta>0,0)).rolling(14).mean(); loss=(-delta.where(delta<0,0)).rolling(14).mean()
        rs=gain/loss.replace(0,0.001); rsi=100-(100/(1+rs))
        last=c.iloc[-1]; vol=df["Volume"].iloc[-1]; vol_avg=df["Volume"].tail(20).mean()
        score=0; reasons=[]
        if e20.iloc[-1]>e50.iloc[-1]: score+=20; reasons.append("EMA Uptrend")
        if e50.iloc[-1]>e200.iloc[-1]: score+=15; reasons.append("Long Bull")
        if last>e20.iloc[-1]: score+=15; reasons.append("Price>EMA20")
        if st_dir.iloc[-1]==1: score+=20; reasons.append("Supertrend BUY")
        if m_line.iloc[-1]>s_line.iloc[-1]: score+=10; reasons.append("MACD Bull")
        if hist.iloc[-1]>hist.iloc[-2]: score+=10; reasons.append("Momentum Up")
        r=rsi.iloc[-1]
        if 45<=r<=70: score+=10; reasons.append(f"RSI {round(r,1)}")
        if vol>vol_avg*1.2: score+=10; reasons.append("Vol Breakout")
        return score, reasons, round(rsi.iloc[-1],1)
    except: return 0, [], 50
def get_morning_picks():
    today=str(date.today())
    if st.session_state.pick_date==today and st.session_state.morning_picks: return st.session_state.morning_picks
    picks=[]
    for name in WATCHLIST:
        t=resolve_ticker(name); df=load_data(t)
        if not df.empty and len(df)>50:
            sc, rsns, rsi = score_stock(df); live=get_live_price(t)
            if live==0: live=float(df["Close"].iloc[-1])
            picks.append({"name":name, "score":sc, "reasons":rsns, "rsi":rsi, "live":live})
    picks=sorted(picks, key=lambda x: x["score"], reverse=True)[:2]
    st.session_state.morning_picks=picks; st.session_state.pick_date=today
    return picks

morning_picks=get_morning_picks()
if morning_picks:
    c1,c2=st.columns(2)
    for i, pick in enumerate(morning_picks):
        col=c1 if i==0 else c2
        pct=int(pick['score']/110*100)
        with col:
            st.markdown(f"""
            <div class="pick-god">
             <div style="display:flex; justify-content:space-between; align-items:flex-start;">
              <div>
               <div style="display:flex; align-items:center; gap:10px;">
                <span style="background: rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.12); color:#8892b0; font-size:9px; padding:4px 10px; border-radius:100px; font-family:JetBrains Mono; letter-spacing:1px;">#{i+1} TOP PICK</span>
                <span style="color:#00FF88; font-size:10px; font-family:JetBrains Mono;">● AI CONFIDENCE HIGH</span>
               </div>
               <h2 style="margin:12px 0 0 0; color:white; font-family:Space Grotesk; font-size:26px; font-weight:700; letter-spacing:-0.5px;">{pick['name']}</h2>
               <p style="margin:6px 0 0 0; color:#00D1FF; font-family:JetBrains Mono; font-size:24px; font-weight:800;">₹{round(pick['live'],2)} <span style="color:#8892b0; font-size:11px; font-weight:400;">RSI {pick['rsi']}</span></p>
               <p style="margin:10px 0 0 0; color:rgba(255,255,255,0.7); font-size:11px; font-family:Inter;">{' • '.join(pick['reasons'][:3])}</p>
              </div>
              <div style="text-align:center;">
               <div class="score-ring" style="--p:{pct}%;"><span style="position:relative; z-index:2; color:white; font-family:Space Grotesk; font-weight:700; font-size:14px;">{pick['score']}</span></div>
               <p style="margin:8px 0 0 0; color:#8892b0; font-size:8px; font-family:JetBrains Mono; letter-spacing:1px;">SCORE</p>
               <div style="margin-top:10px; background: rgba(0,255,136,0.15); border:1px solid #00FF88; color:#00FF88; font-size:9px; padding:5px 12px; border-radius:100px; font-family:Space Grotesk; font-weight:700; letter-spacing:1px;">BUY</div>
              </div>
             </div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
    if st.button("↻ Refresh God Picks", use_container_width=True):
        st.session_state.pick_date=""; st.rerun()

# SEARCH
c1,c2=st.columns([5.2,1])
with c1: user_input=st.text_input("search", value="CUPID", placeholder="Search NSE symbol... e.g. RELIANCE, TCS", label_visibility="collapsed")
with c2: st.button("SEARCH ↗", use_container_width=True)

raw=user_input.upper().strip(); ticker=resolve_ticker(raw); df=load_data(ticker)
if df.empty: st.error(f"{raw} not found"); st.stop()
last=float(df["Close"].dropna().iloc[-1]); live=get_live_price(ticker)
if live==0: live=last
low_min=float(df["Low"].tail(20).min())
tgt=last+(last-low_min)*1.5
if tgt<=last: tgt=float(df["High"].tail(20).max())
close=df["Close"]; ema20=close.ewm(20).mean(); ema50=close.ewm(50).mean()
sig="BUY" if ema20.iloc[-1]>ema50.iloc[-1] and last>ema20.iloc[-1] else "SELL" if ema20.iloc[-1]<ema50.iloc[-1] else "HOLD"
sig_class="buy-god" if sig=="BUY" else "sell-god"
trend="UPTREND" if ema20.iloc[-1]>ema50.iloc[-1] else "DOWNTREND"
df_c=df.tail(100).copy(); m_line,s_line,hist=calc_macd(df_c["Close"]); st_line,st_dir=calc_st(df_c)
st_sig="BUY" if st_dir.iloc[-1]==1 else "SELL"; st_color="#00FF88" if st_sig=="BUY" else "#FF4D6A"

st.markdown(f"""
<div class="top-god">
 <div style="display:flex; justify-content:space-between; align-items:center; position:relative; z-index:2;">
  <div>
   <div style="display:flex; align-items:center; gap:14px;">
    <h2 style="margin:0; color:white; font-family:Space Grotesk; font-size:28px; font-weight:700; letter-spacing:-1px;">{raw}</h2>
    <span style="background: rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.12); color:#8892b0; font-family:JetBrains Mono; font-size:10px; padding:5px 10px; border-radius:100px;">{ticker}</span>
    <span style="background: {st_color}18; border:1px solid {st_color}; color:{st_color}; font-family:Space Grotesk; font-size:10px; font-weight:700; padding:5px 12px; border-radius:100px; letter-spacing:1px;">ST {st_sig} • {trend}</span>
   </div>
   <div style="display:flex; gap:12px; margin-top:14px;">
    <div><p style="margin:0; color:#8892b0; font-size:9px; font-family:JetBrains Mono; letter-spacing:1px;">TARGET</p><p style="margin:2px 0 0 0; color:#00FF88; font-family:JetBrains Mono; font-weight:800; font-size:13px;">₹{round(tgt,2)}</p></div>
    <div style="width:1px; background: rgba(255,255,255,0.1);"></div>
    <div><p style="margin:0; color:#8892b0; font-size:9px; font-family:JetBrains Mono; letter-spacing:1px;">STOP LOSS</p><p style="margin:2px 0 0 0; color:#FF4D6A; font-family:JetBrains Mono; font-weight:800; font-size:13px;">₹{round(low_min,2)}</p></div>
    <div style="width:1px; background: rgba(255,255,255,0.1);"></div>
    <div><p style="margin:0; color:#8892b0; font-size:9px; font-family:JetBrains Mono; letter-spacing:1px;">LIVE</p><p style="margin:2px 0 0 0; color:white; font-family:JetBrains Mono; font-weight:800; font-size:13px;">₹{round(live,2)}</p></div>
   </div>
  </div>
  <div style="text-align:right;">
   <p style="margin:0; color:#8892b0; font-size:9px; font-family:JetBrains Mono; letter-spacing:2px;">LIVE PRICE</p>
   <p class="live-price">₹{round(live,2)}</p>
   <div class="{sig_class}" style="margin-top:14px; display:inline-block; min-width:130px; text-align:center;">{sig} ↗</div>
  </div>
 </div>
</div>
""", unsafe_allow_html=True)

tab_chart, tab_screen = st.tabs(["📈 Pro Chart", "🔥 Screener"])

with tab_chart:
    close_c=df_c["Close"]; e20=close_c.ewm(20).mean(); e50=close_c.ewm(50).mean()
    delta=close_c.diff(); gain=(delta.where(delta>0,0)).rolling(14).mean(); loss=(-delta.where(delta<0,0)).rolling(14).mean()
    rs=gain/loss.replace(0,0.001); rsi=100-(100/(1+rs))
    fig=make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.62,0.19,0.19])
    fig.add_trace(go.Candlestick(x=df_c.index, open=df_c["Open"], high=df_c["High"], low=df_c["Low"], close=df_c["Close"], increasing_line_color="#00FF88", decreasing_line_color="#FF4D6A", increasing_line_width=1, decreasing_line_width=1), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=e20, line=dict(color="#00D1FF",width=2), name="EMA20"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=e50, line=dict(color="#FFAA00",width=1.5,dash="dash"), name="EMA50"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=st_line, line=dict(color=st_color,width=2.5), name="Supertrend"), row=1, col=1)
    colors=["#00FF88" if h>=0 else "#FF4D6A" for h in hist]
    fig.add_trace(go.Scatter(x=df_c.index, y=m_line, line=dict(color="#00D1FF",width=2), name="MACD"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=s_line, line=dict(color="#FFAA00",width=1.5), name="Signal"), row=2, col=1)
    fig.add_trace(go.Bar(x=df_c.index, y=hist, marker_color=colors, marker_line_width=0), row=2, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=rsi, line=dict(color="#C084FC",width=2), name="RSI"), row=3, col=1)
    fig.add_hline(y=70, line=dict(color="rgba(255,77,106,0.5)",dash="dot",width=1), row=3, col=1); fig.add_hline(y=30, line=dict(color="rgba(0,255,136,0.5)",dash="dot",width=1), row=3, col=1)
    fig.update_layout(template="plotly_dark", height=620, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=10,b=0), dragmode=False, hovermode="x unified", legend=dict(orientation="h", y=1.01, x=0, font=dict(size=10, family="Space Grotesk")))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': True})

    clean_sym = raw.replace(".NS","").replace(".BO","").strip()
    tv_symbol = f"NSE:{clean_sym}"
    st.components.v1.iframe(f"https://s.tradingview.com/widgetembed/?symbol={tv_symbol}&interval=D&hidesidetoolbar=0&theme=dark&style=1&timezone=Asia%2FKolkata", height=520, scrolling=True)

with tab_screen:
    if st.button("🚀 GOD SCAN ALL", use_container_width=True):
        results=[]
        for name in WATCHLIST:
            t=resolve_ticker(name); d=load_data(t)
            if not d.empty:
                sc,_,_=score_stock(d); live_p=get_live_price(t)
                if live_p==0: live_p=float(d["Close"].iloc[-1])
                results.append({"name":name,"score":sc,"live":live_p})
        results=sorted(results, key=lambda x: x["score"], reverse=True)
        for r in results[:12]:
            st.markdown(f"<div class='pick-god' style='margin-bottom:10px;'><b style='color:white; font-family:Space Grotesk;'>{r['name']}</b> <span style='float:right; color:#00FF88; font-family:JetBrains Mono;'>₹{round(r['live'],2)} • {r['score']}</span></div>", unsafe_allow_html=True)
