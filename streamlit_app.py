import streamlit as st, yfinance as yf, pandas as pd, plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64, time, requests, re
from datetime import datetime

st.set_page_config(page_title="FinTrade Premium", layout="wide", page_icon="💎")
st.markdown("""<style>.stApp{background: radial-gradient(1200px 600px at 10% -10%, #1a1f5c 0%, #0a0e1a 50%), radial-gradient(1000px 500px at 90% 10%, #5c1a5c 0%, #0a0e1a 60%);}.header-box{background: rgba(255,255,255,0.05); backdrop-filter: blur(20px); border:1px solid rgba(255,255,255,0.1); border-radius:20px; padding:18px; margin-bottom:16px;}.top-pin{background: linear-gradient(135deg, rgba(0,209,255,0.18), rgba(112,0,255,0.18)); border:1px solid rgba(0,209,255,0.35); border-radius:20px; padding:16px; margin:14px 0;}.stTextInput>div>div>input{background: rgba(255,255,255,0.06)!important; border:2px solid rgba(0,209,255,0.3)!important; border-radius:14px!important; color:white!important; font-size:20px!important; font-weight:700!important; height:58px!important;}.stButton>button{background: linear-gradient(90deg, #00D1FF, #7000FF)!important; border:none!important; border-radius:12px!important; color:white!important; font-weight:800!important; height:50px!important;}</style>""", unsafe_allow_html=True)

if "alerts" not in st.session_state: st.session_state.alerts=[]
if "live_mode" not in st.session_state: st.session_state.live_mode=False
if "tg_token" not in st.session_state: st.session_state.tg_token=""
if "tg_chat" not in st.session_state: st.session_state.tg_chat=""
if "last_st" not in st.session_state: st.session_state.last_st=""
if "boom" not in st.session_state: st.session_state.boom=True

def get_logo():
    try:
        with open("logo.png","rb") as f:
            return f'<img src="data:image/png;base64,{base64.b64encode(f.read()).decode()}" width="60" style="border-radius:12px;">'
    except:
        return '<div style="font-size:40px;">💎</div>'

st.markdown(f"""<div class="header-box"><div style="display:flex; align-items:center; gap:16px;"><div>{get_logo()}</div><div><h1 style="margin:0; color:white; font-size:28px;">FinTrade Premium</h1><p style="margin:0; color:#8892b0; font-size:10px;">V37.4 FINAL - TradingView BACK + No Toolbar + No Box</p></div></div></div>""", unsafe_allow_html=True)

SMART_MAP={"IOCL":"IOC.NS","IOC":"IOC.NS","GAIL":"GAIL.NS","CUPID":"CUPID.NS","RELIANCE":"RELIANCE.NS","TCS":"TCS.NS","INFY":"INFY.NS","SBIN":"SBIN.NS","ADANITOTALGAS":"ATGL.NS","ATGL":"ATGL.NS","ADANIGREEN":"ADANIGREEN.NS","ADANIENT":"ADANIENT.NS","ADANIPORTS":"ADANIPORTS.NS","ADANIPOWER":"ADANIPOWER.NS","ZOMATO":"ETERNAL.NS","PAYTM":"PAYTM.NS","SUZLON":"SUZLON.NS","YESBANK":"YESBANK.NS","RVNL":"RVNL.NS","IRFC":"IRFC.NS"}

def resolve_ticker(t):
    r=t.upper().strip()
    ns=re.sub(r'[^A-Z0-9]','',r)
    if r in SMART_MAP: return SMART_MAP[r]
    if ns in SMART_MAP: return SMART_MAP[ns]
    if "ADANI" in r and "GAS" in r: return "ATGL.NS"
    return ns+".NS" if len(ns)>1 else r+".NS"

def load_data(tick):
    try:
        tk=yf.Ticker(tick)
        df=tk.history(period="3mo",interval="1d",auto_adjust=False)
        if df.empty: df=tk.history(period="1mo",interval="1d",auto_adjust=True)
        if isinstance(df.columns,pd.MultiIndex): df.columns=df.columns.get_level_values(0)
        return df.dropna()
    except:
        return pd.DataFrame()

def get_live_price(tick):
    try:
        tk=yf.Ticker(tick)
        p=tk.fast_info.last_price
        if p is None or pd.isna(p):
            d=tk.history(period="1d",interval="1m")
            p=float(d["Close"].dropna().iloc[-1]) if not d.empty else 0
        return float(p)
    except:
        return 0

def send_tg(token, chat, msg):
    try:
        r=requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id":chat,"text":msg,"parse_mode":"Markdown"}, timeout=10)
        return r.status_code==200
    except:
        return False

def calc_st(df, period=10, mult=3):
    hl2=(df['High']+df['Low'])/2
    tr1=df['High']-df['Low']
    tr2=(df['High']-df['Close'].shift()).abs()
    tr3=(df['Low']-df['Close'].shift()).abs()
    tr=pd.concat([tr1,tr2,tr3],axis=1).max(axis=1)
    atr=tr.rolling(period).mean()
    upper=hl2+mult*atr
    lower=hl2-mult*atr
    st_line=[0]*len(df)
    direction=[1]*len(df)
    for i in range(1,len(df)):
        if df['Close'].iloc[i]<=lower.iloc[i-1]: direction[i]=-1
        elif df['Close'].iloc[i]>=upper.iloc[i-1]: direction[i]=1
        else: direction[i]=direction[i-1]
        st_line[i]=lower.iloc[i] if direction[i]==1 else upper.iloc[i]
    return pd.Series(st_line,index=df.index), pd.Series(direction,index=df.index)

def calc_macd(c, fast=12, slow=26, sig=9):
    ef=c.ewm(span=fast).mean()
    es=c.ewm(span=slow).mean()
    m=ef-es
    s=m.ewm(span=sig).mean()
    h=m-s
    return m,s,h

c1,c2=st.columns([5,1])
with c1:
    user_input=st.text_input("search", value="IOCL", placeholder="IOCL, Adani total gas...", label_visibility="collapsed")
with c2:
    st.button("SEARCH", use_container_width=True)

raw=user_input.upper().strip()
ticker=resolve_ticker(raw)
df=load_data(ticker)
if df.empty:
    if "ADANI" in raw and "GAS" in raw:
        ticker="ATGL.NS"
        df=load_data(ticker)
if df.empty:
    st.error(f"{raw} not found")
    st.stop()

last=float(df["Close"].dropna().iloc[-1])
live=get_live_price(ticker)
if live==0: live=last
low_min=float(df["Low"].tail(20).min())
high_max=float(df["High"].tail(20).max())
tgt=last+(last-low_min)*1.5
if tgt<=last: tgt=high_max

close=df["Close"]
ema20=close.ewm(20).mean()
ema50=close.ewm(50).mean()
sig="BUY" if ema20.iloc[-1]>ema50.iloc[-1] and last>ema20.iloc[-1] else "SELL" if ema20.iloc[-1]<ema50.iloc[-1] else "HOLD"
sig_color="#00FF88" if sig=="BUY" else "#FF4D6A" if sig=="SELL" else "#FFAA00"
trend="UPTREND" if ema20.iloc[-1]>ema50.iloc[-1] else "DOWNTREND"

df_c=df.tail(100).copy()
m_line,s_line,hist=calc_macd(df_c["Close"])
st_line,st_dir=calc_st(df_c)
st_sig="BUY" if st_dir.iloc[-1]==1 else "SELL"
st_color="#00FF88" if st_sig=="BUY" else "#FF4D6A"
macd_sig="BULLISH" if m_line.iloc[-1]>s_line.iloc[-1] else "BEARISH"

if st.session_state.last_st!="" and st.session_state.last_st!=st_sig:
    if st.session_state.tg_token and st.session_state.tg_chat:
        send_tg(st.session_state.tg_token, st.session_state.tg_chat, f"🚨 {raw} {st.session_state.last_st}->{st_sig} LIVE {round(live,2)}")
    if st.session_state.boom:
        st.markdown('<audio autoplay><source src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" type="audio/ogg"></audio>', unsafe_allow_html=True)
st.session_state.last_st=st_sig

st.markdown(f"""<div class="top-pin"><div style="display:flex; justify-content:space-between;"><div><h2 style="color:white; margin:0; font-size:20px;">{raw} <span style="color:#8892b0; font-size:11px;">{ticker}</span> <span style="background:{sig_color}; color:black; padding:4px 12px; border-radius:20px; font-size:11px;">{sig}</span> <span style="background:{st_color}; color:black; padding:4px 10px; border-radius:20px; font-size:10px;">ST {st_sig}</span></h2><p style="color:#00D1FF; margin:6px 0 0 0; font-size:11px;">LIVE {round(live,2)} | Target {round(tgt,2)} | SL {round(low_min,2)}</p></div><div style="text-align:right;"><p style="color:{sig_color}; font-size:26px; font-weight:900; margin:0;">Rs {round(live,2)}</p></div></div></div>""", unsafe_allow_html=True)

tab_chart, tab_profit, tab_alert, tab_tg = st.tabs(["📈 Chart + TradingView", "💰 Profit", "🔔 ALERTS", "📲 TELEGRAM"])

with tab_chart:
    close_c=df_c["Close"]
    e20=close_c.ewm(20).mean()
    e50=close_c.ewm(50).mean()
    delta=close_c.diff()
    gain=(delta.where(delta>0,0)).rolling(14).mean()
    loss=(-delta.where(delta<0,0)).rolling(14).mean()
    rs=gain/loss.replace(0,0.001)
    rsi=100-(100/(1+rs))
    sup=float(df_c["Low"].tail(20).min())
    res=float(df_c["High"].tail(20).max())
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
    fig.add_hline(y=70, line=dict(color="#FF4D6A",dash="dash"), row=3, col=1)
    fig.add_hline(y=30, line=dict(color="#00FF88",dash="dash"), row=3, col=1)
    fig.update_layout(template="plotly_dark", height=650, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_rangeslider_visible=False, showlegend=True, legend=dict(orientation="h", y=1.02, x=0, font=dict(size=9)), margin=dict(l=0,r=0,t=40,b=0), dragmode=False, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': True, 'doubleClick': 'reset', 'displaylogo': False})
    bse_sym=ticker.replace(".NS","").replace(".BO","")
    st.markdown("### 📊 TradingView Live - IOCL")
    st.components.v1.iframe(f"https://s.tradingview.com/widgetembed/?symbol=BSE%3A{bse_sym}&interval=D&theme=dark&studies=Supertrend%40tv-basicstudies%2CMACD%40tv-basicstudies%2CRSI%40tv-basicstudies", height=500)
    st.success("✅ TradingView wapas aa gaya! No toolbar, No box")

with tab_profit:
    qty=st.number_input("Qty", min_value=1, value=100, step=1)
    buy_val=live*qty
    target_val=tgt*qty
    profit=target_val-buy_val
    st.metric("Profit at Target", f"Rs {round(profit,2)}", delta=f"{round((profit/buy_val)*100,2)}%")

with tab_alert:
    st.session_state.boom=st.toggle("🔊 BOOM Sound ON", value=st.session_state.boom)
    st.session_state.live_mode=st.toggle("🟢 LIVE + AUTO TELEGRAM", value=st.session_state.live_mode)
    if st.session_state.live_mode:
        time.sleep(30)
        st.rerun()

with tab_tg:
    tok=st.text_input("Token", value=st.session_state.tg_token, type="password")
    chat=st.text_input("Chat ID", value=st.session_state.tg_chat)
    if st.button("Save"):
        st.session_state.tg_token=tok
        st.session_state.tg_chat=chat
        st.success("Saved!")

st.caption("V37.4 FINAL - TradingView BACK - Clean chart")
