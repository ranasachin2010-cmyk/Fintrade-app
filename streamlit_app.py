import streamlit as st, yfinance as yf, pandas as pd, plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64, time, requests, re

st.set_page_config(page_title="FinTrade Premium", layout="wide", page_icon="💎")

# ULTRA PREMIUM CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@700;900&family=JetBrains+Mono:wght@700&display=swap');
.stApp{
 background: radial-gradient(1200px 600px at 0% 0%, #1a1f6c 0%, #0a0a1a 40%),
             radial-gradient(1000px 500px at 100% 0%, #6c1a6c 0%, #0a0a1a 50%),
             #050510;
}
.header-glass{
 background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
 backdrop-filter: blur(25px);
 border: 1px solid rgba(255,255,255,0.12);
 border-radius: 24px;
 padding: 20px 24px;
 box-shadow: 0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.1);
}
.top-premium{
 background: linear-gradient(135deg, rgba(0,209,255,0.15), rgba(112,0,255,0.15), rgba(0,255,136,0.08));
 backdrop-filter: blur(20px);
 border: 1.5px solid rgba(0,209,255,0.25);
 border-radius: 24px;
 padding: 18px 22px;
 box-shadow: 0 10px 40px rgba(0,209,255,0.15), 0 0 0 1px rgba(255,255,255,0.05) inset;
 position: relative;
 overflow: hidden;
}
.top-premium::before{
 content: '';
 position: absolute;
 top: 0; left: -100%;
 width: 100%; height: 100%;
 background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
 animation: shine 3s infinite;
}
@keyframes shine{0%{left:-100%}100%{left:100%}}
.buy-neon{
 background: linear-gradient(135deg, #00FF88, #00D1FF)!important;
 color: black!important;
 font-weight: 900!important;
 font-family: 'Inter'!important;
 font-size: 26px!important;
 padding: 14px 32px!important;
 border-radius: 16px!important;
 box-shadow: 0 0 30px #00FF8855, 0 0 60px #00FF8833!important;
 border: 2px solid #00FF88!important;
 animation: pulse 2s infinite;
 text-transform: uppercase;
 letter-spacing: 1px;
}
.sell-neon{
 background: linear-gradient(135deg, #FF4D6A, #FF8A4D)!important;
 color: white!important;
 font-weight: 900!important;
 font-size: 26px!important;
 padding: 14px 32px!important;
 border-radius: 16px!important;
 box-shadow: 0 0 30px #FF4D6A66, 0 0 60px #FF4D6A33!important;
 border: 2px solid #FF4D6A!important;
 animation: pulse 2s infinite;
}
@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.03)}}
.stTextInput>div>div>input{
 background: rgba(255,255,255,0.06)!important;
 border: 2px solid rgba(0,209,255,0.4)!important;
 border-radius: 18px!important;
 color: white!important;
 font-size: 20px!important;
 font-weight: 800!important;
 height: 62px!important;
 font-family: 'JetBrains Mono'!important;
 box-shadow: 0 0 20px rgba(0,209,255,0.1) inset!important;
}
.stButton>button{
 background: linear-gradient(135deg, #00D1FF, #7000FF, #00FF88)!important;
 border: none!important;
 border-radius: 16px!important;
 color: white!important;
 font-weight: 900!important;
 height: 62px!important;
 font-size: 15px!important;
 letter-spacing: 1.5px!important;
 box-shadow: 0 8px 24px rgba(0,209,255,0.3)!important;
}
.trend-chip{
 background: rgba(0,255,136,0.15);
 border: 1px solid #00FF88;
 color: #00FF88;
 padding: 4px 12px;
 border-radius: 20px;
 font-size: 10px;
 font-weight: 800;
 letter-spacing: 1px;
}
</style>
""", unsafe_allow_html=True)

if "last_st" not in st.session_state: st.session_state.last_st=""
if "boom" not in st.session_state: st.session_state.boom=True
if "live_mode" not in st.session_state: st.session_state.live_mode=False
if "tg_token" not in st.session_state: st.session_state.tg_token=""
if "tg_chat" not in st.session_state: st.session_state.tg_chat=""

def get_logo():
    try:
        with open("logo.png","rb") as f: return f'<img src="data:image/png;base64,{base64.b64encode(f.read()).decode()}" width="64" style="border-radius:14px; box-shadow:0 0 20px #00D1FF66;">'
    except: return '<div style="font-size:42px; filter:drop-shadow(0 0 15px #00D1FF);">💎</div>'

st.markdown(f"""
<div class="header-glass">
 <div style="display:flex; align-items:center; justify-content:space-between;">
  <div style="display:flex; align-items:center; gap:16px;">
   <div>{get_logo()}</div>
   <div>
    <h1 style="margin:0; color:white; font-family:Inter; font-size:28px; font-weight:900; letter-spacing:-0.5px; background: linear-gradient(90deg, white, #00D1FF); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">FinTrade Premium</h1>
    <p style="margin:2px 0 0 0; color:#00FF88; font-size:11px; font-weight:700; letter-spacing:2px; font-family:JetBrains Mono;">V39 ULTRA PREMIUM • NO PROFIT • CLEAN • NEON</p>
   </div>
  </div>
  <div style="text-align:right;"><span class="trend-chip">● LIVE MARKET</span></div>
 </div>
</div>
""", unsafe_allow_html=True)

SMART_MAP={"CUPID":"CUPID.NS","IOCL":"IOC.NS","IOC":"IOC.NS","GAIL":"GAIL.NS","RELIANCE":"RELIANCE.NS","TCS":"TCS.NS","INFY":"INFY.NS","SBIN":"SBIN.NS","ADANITOTALGAS":"ATGL.NS","ATGL":"ATGL.NS","ZOMATO":"ETERNAL.NS","PAYTM":"PAYTM.NS","SUZLON":"SUZLON.NS","YESBANK":"YESBANK.NS","RVNL":"RVNL.NS","IRFC":"IRFC.NS"}
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

c1,c2=st.columns([5,1])
with c1: user_input=st.text_input("search", value="CUPID", placeholder="Search CUPID, IOCL, ADANI GAS...", label_visibility="collapsed")
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

# PREMIUM TOP CARD WITH NEON SIGNAL IN GREEN BOX
st.markdown(f"""
<div class="top-premium">
 <div style="display:flex; justify-content:space-between; align-items:center; position:relative; z-index:1;">
  <div>
   <div style="display:flex; align-items:center; gap:12px;">
    <h2 style="color:white; margin:0; font-size:22px; font-family:Inter; font-weight:900;">{raw}</h2>
    <span style="color:#8892b0; font-size:11px; font-family:JetBrains Mono; background:rgba(255,255,255,0.08); padding:4px 10px; border-radius:8px;">{ticker}</span>
    <span style="background: linear-gradient(135deg, {st_color}22, {st_color}11); border:1px solid {st_color}; color:{st_color}; padding:5px 12px; border-radius:20px; font-size:10px; font-weight:800;">ST {st_sig}</span>
   </div>
   <p style="color:#8892b0; margin:8px 0 0 0; font-size:11px; font-family:JetBrains Mono;">LIVE <span style="color:white; font-weight:800;">{round(live,2)}</span> • TGT <span style="color:#00FF88;">{round(tgt,2)}</span> • SL <span style="color:#FF4D6A;">{round(low_min,2)}</span> • <span style="color:{sig_color};">{trend}</span></p>
  </div>
  <div style="text-align:right;">
   <p style="color:#8892b0; font-size:9px; margin:0; letter-spacing:2px; font-weight:700;">LIVE PRICE</p>
   <p style="color:white; font-size:32px; font-weight:900; margin:0; font-family:JetBrains Mono; text-shadow:0 0 20px rgba(255,255,255,0.3);">Rs {round(live,2)}</p>
   <div class="{sig_class}" style="margin-top:10px; display:inline-block; min-width:120px; text-align:center;">{sig}</div>
   <p style="color:{st_color}; font-size:10px; margin:8px 0 0 0; font-weight:700; font-family:JetBrains Mono;">ST {st_sig} • MACD {macd_sig}</p>
  </div>
 </div>
</div>
""", unsafe_allow_html=True)

tab_chart, tab_alert, tab_tg = st.tabs(["📈 Chart + TradingView", "🔔 ALERTS + BOOM", "📲 TELEGRAM"])

with tab_chart:
    close_c=df_c["Close"]; e20=close_c.ewm(20).mean(); e50=close_c.ewm(50).mean()
    delta=close_c.diff(); gain=(delta.where(delta>0,0)).rolling(14).mean(); loss=(-delta.where(delta<0,0)).rolling(14).mean()
    rs=gain/loss.replace(0,0.001); rsi=100-(100/(1+rs)); sup=float(df_c["Low"].tail(20).min()); res=float(df_c["High"].tail(20).max())
    fig=make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.60,0.20,0.20], subplot_titles=(f"{raw} {trend} | ST {st_sig} | {round(sup,2)}-{round(res,2)}", f"MACD {macd_sig}", "RSI"))
    fig.add_trace(go.Candlestick(x=df_c.index, open=df_c["Open"], high=df_c["High"], low=df_c["Low"], close=df_c["Close"], name="Price", increasing_line_color="#00FF88", decreasing_line_color="#FF4D6A"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=e20, line=dict(color="#00D1FF",width=2), name="EMA20"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=e50, line=dict(color="#FFAA00",width=2,dash="dash"), name="EMA50"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=st_line, line=dict(color=st_color,width=3), name="Supertrend"), row=1, col=1)
    fig.add_hline(y=sup, line=dict(color="#00FF88",width=1,dash="dot"), annotation_text=f"Support {round(sup,2)}", row=1, col=1)
    fig.add_hline(y=res, line=dict(color="#FF4D6A",width=1,dash="dot"), annotation_text=f"Res {round(res,2)}", row=1, col=1)
    colors=["#00FF88" if h>=0 else "#FF4D6A" for h in hist]
    fig.add_trace(go.Scatter(x=df_c.index, y=m_line, line=dict(color="#00D1FF",width=2), name="MACD"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=s_line, line=dict(color="#FFAA00",width=2), name="Signal"), row=2, col=1)
    fig.add_trace(go.Bar(x=df_c.index, y=hist, marker_color=colors, name="Hist"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=rsi, line=dict(color="#C084FC",width=2), name="RSI"), row=3, col=1)
    fig.add_hline(y=70, line=dict(color="#FF4D6A",dash="dash"), row=3, col=1); fig.add_hline(y=30, line=dict(color="#00FF88",dash="dash"), row=3, col=1)
    fig.update_layout(template="plotly_dark", height=650, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_rangeslider_visible=False, showlegend=True, legend=dict(orientation="h", y=1.02, x=0, font=dict(size=9)), margin=dict(l=0,r=0,t=40,b=0), dragmode=False, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': True, 'doubleClick': 'reset', 'displaylogo': False})
    bse_sym=ticker.replace(".NS","").replace(".BO","")
    st.markdown("### 📊 TradingView Pro")
    st.components.v1.iframe(f"https://s.tradingview.com/widgetembed/?symbol=BSE%3A{bse_sym}&interval=D&theme=dark&studies=Supertrend%40tv-basicstudies%2CMACD%40tv-basicstudies%2CRSI%40tv-basicstudies", height=500)

with tab_alert:
    st.session_state.boom=st.toggle("🔊 BOOM Sound ON", value=st.session_state.boom)
    st.session_state.live_mode=st.toggle("🟢 LIVE + AUTO TELEGRAM", value=st.session_state.live_mode)
    if st.session_state.live_mode: time.sleep(30); st.rerun()

with tab_tg:
    tok=st.text_input("Token", value=st.session_state.tg_token, type="password")
    chat=st.text_input("Chat ID", value=st.session_state.tg_chat)
    if st.button("Save Premium Config"): st.session_state.tg_token=tok; st.session_state.tg_chat=chat; st.success("✅ Premium Saved!")

st.caption("V39 ULTRA PREMIUM - Neon BUY/SELL | Glassmorphic | Bloomberg Style")
