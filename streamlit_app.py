import streamlit as st, yfinance as yf, pandas as pd, plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64, requests, re
from datetime import date, datetime
import pytz

st.set_page_config(page_title="FinTrade God V44.1 SMART", layout="wide", page_icon="💎")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700&family=JetBrains+Mono:wght@800&display=swap');
.stApp{background: #020208; background-image: radial-gradient(at 0% 0%, hsla(212,100%,56%,0.25) 0px, transparent 50%), radial-gradient(at 20% 10%, hsla(273,100%,60%,0.25) 0px, transparent 50%), radial-gradient(at 90% 0%, hsla(158,100%,50%,0.20) 0px, transparent 50%);}
.header-god{background: linear-gradient(135deg, #6A5AE0 0%, #7B6EF0 100%)!important; border:none!important; border-radius: 28px; padding: 18px 26px; box-shadow: 0 20px 80px rgba(106,90,224,0.35);}
.header-god img{background:transparent!important; border:none!important; box-shadow:none!important;}
.pick-god{background: linear-gradient(135deg, rgba(0,255,136,0.10) 0%, rgba(0,209,255,0.08) 50%, rgba(112,0,255,0.08) 100%); backdrop-filter: blur(30px); border:1.5px solid rgba(0,255,136,0.25); border-radius: 24px; padding: 20px 20px 14px 20px; box-shadow: 0 12px 40px rgba(0,255,136,0.12);}
.top-god{background: linear-gradient(100deg, rgba(0,209,255,0.14) 0%, rgba(112,0,255,0.18) 40%, rgba(0,255,136,0.10) 100%); backdrop-filter: blur(40px); border: 1px solid rgba(255,255,255,0.12); border-radius: 28px; padding: 24px 26px;}
.live-price{font-family: 'Space Grotesk'; font-weight: 700; font-size: 38px; background: linear-gradient(90deg, #fff 0%, #a5b4fc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
.buy-god{background: linear-gradient(135deg, #00FF88 0%, #00E5FF 100%)!important; color: #001a0a!important; font-weight: 700!important; font-size: 15px!important; padding: 14px 28px!important; border-radius: 14px!important; border: none!important;}
.stTextInput>div>div>input{background: rgba(255,255,255,0.06)!important; border: 1.5px solid rgba(255,255,255,0.12)!important; border-radius: 20px!important; color: white!important; font-family: JetBrains Mono!important; font-weight: 800!important; font-size: 18px!important; height: 64px!important;}
.stButton>button{background: linear-gradient(135deg, #00D1FF 0%, #7000FF 50%, #00FF88 100%)!important; border: none!important; border-radius: 18px!important; color: white!important; font-weight: 700!important; height: 64px!important;}
.score-ring{width: 56px; height: 56px; border-radius: 50%; background: conic-gradient(#00FF88 var(--p), rgba(255,255,255,0.1) 0); display: flex; align-items: center; justify-content: center; position: relative;}
.score-ring::before{content:''; position: absolute; inset: 4px; background: #0a1220; border-radius: 50%;}
.target-row{display: flex; justify-content: space-between; align-items: center; margin-top: 14px; padding: 10px 12px; background: linear-gradient(90deg, rgba(0,255,136,0.12), rgba(0,255,136,0.06)); border: 1px solid rgba(0,255,136,0.25); border-left: 3px solid #00FF88; border-radius: 12px;}
.win-badge{background: rgba(0,209,255,0.15); border:1px solid #00D1FF; color:#00D1FF; font-size:9px; padding:4px 10px; border-radius:100px; font-family:JetBrains Mono; font-weight:700; margin-top:8px; display:inline-block;}
.atr-badge{background: rgba(255,215,0,0.15); border:1px solid #FFD700; color:#FFD700; font-size:9px; padding:4px 10px; border-radius:100px; font-family:JetBrains Mono; font-weight:700; margin-left:6px;}
.index-chip{display:inline-flex; align-items:center; gap:6px; background: rgba(0,0,0,0.35); border:1px solid rgba(255,255,255,0.08); border-radius:100px; padding:8px 14px; font-family:JetBrains Mono; font-size:11px; color:#fff; margin-right:8px;}
.index-up{color:#00FF88; font-weight:800;}.index-down{color:#FF4D6A; font-weight:800;}
.bse-badge{background: linear-gradient(135deg, #FF6A00, #FFD700); color:black; font-weight:700; font-size:10px; padding:4px 10px; border-radius:100px;}
.auto-badge{background: rgba(0,255,136,0.15); border:1px solid #00FF88; color:#00FF88; font-size:8px; padding:3px 8px; border-radius:100px; font-family:JetBrains Mono;}
</style>
""", unsafe_allow_html=True)

if "morning_picks" not in st.session_state: st.session_state.morning_picks=[]
if "pick_date" not in st.session_state: st.session_state.pick_date=""
if "tg_token" not in st.session_state: st.session_state.tg_token=""
if "tg_chat" not in st.session_state: st.session_state.tg_chat=""
if "last_auto_sent" not in st.session_state: st.session_state.last_auto_sent=""

@st.cache_data(ttl=300, show_spinner=False)
def get_indices():
    indices = {"NIFTY50": "^NSEI", "SENSEX": "^BSESN", "BANKNIFTY": "^NSEBANK"}
    data = {}
    for name, sym in indices.items():
        try:
            tk = yf.Ticker(sym); hist = tk.history(period="2d", interval="1d")
            if not hist.empty:
                last = float(hist["Close"].iloc[-1]); prev = float(hist["Close"].iloc[-2]) if len(hist)>1 else last
                chg = ((last-prev)/prev*100) if prev!=0 else 0
                data[name] = {"price": last, "chg": chg}
            else: data[name] = {"price": 0, "chg": 0}
        except: data[name] = {"price": 0, "chg": 0}
    return data

@st.cache_data(ttl=300, show_spinner=False)
def load_data(tick, period="3mo"):
    try:
        tk=yf.Ticker(tick); df=tk.history(period=period,interval="1d",auto_adjust=False)
        if df.empty: df=tk.history(period="1mo",interval="1d",auto_adjust=True)
        if isinstance(df.columns,pd.MultiIndex): df.columns=df.columns.get_level_values(0)
        return df.dropna()
    except: return pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def get_live_price(tick):
    try:
        tk=yf.Ticker(tick)
        try:
            p = tk.fast_info.last_price
            if p is not None and not pd.isna(p) and p!=0:
                return float(p)
        except: pass
        d=tk.history(period="5d", interval="1d")
        if not d.empty:
            return float(d["Close"].iloc[-1])
        return 0
    except: return 0

def get_logo():
    try:
        with open("logo.png","rb") as f:
            return f'<img src="data:image/png;base64,{base64.b64encode(f.read()).decode()}" width="68" style="border-radius:16px; background:transparent; border:none;">'
    except: return '<div style="font-size:38px;">💎</div>'

def send_tg(token, chat, msg):
    try: requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id":chat,"text":msg,"parse_mode":"Markdown"}, timeout=10)
    except: pass

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

# --- V44.1 SMART ATR TARGET LOGIC ---
def get_smart_target(df, live, score):
    try:
        atr = float((df["High"] - df["Low"]).tail(14).mean())
        atr_pct = (atr / live * 100) if live>0 else 2.0
        # SMART LOGIC: Volatility * 2.5, but min 3.5% max 12%
        base_pct = atr_pct * 2.5
        # Score ke hisab se boost
        if score>=100: base_pct *= 1.2
        elif score>=90: base_pct *= 1.1
        profit_pct = round(min(max(base_pct, 3.5), 12.0), 1)
        target = live * (1 + profit_pct/100)
        sl = live * (1 - (profit_pct/2)/100) # SL = Target ka half
        return profit_pct, target, sl, atr_pct
    except:
        profit_pct = 8 if score>=90 else 5
        return profit_pct, live*1.08, live*0.96, 2.0

@st.cache_data(ttl=3600, show_spinner=False)
def backtest_winrate(ticker):
    try:
        df = load_data(ticker, period="6mo")
        if df.empty or len(df)<60: return 0, 0, 0
        wins=0; total=0
        for i in range(50, len(df)-10):
            slice_df = df.iloc[:i]
            if len(slice_df)<50: continue
            sc, _, _ = score_stock(slice_df)
            if sc>=80:
                total+=1
                entry = float(df["Close"].iloc[i])
                # Smart target for backtest too
                atr = float((slice_df["High"] - slice_df["Low"]).tail(14).mean())
                atr_pct = (atr / entry * 100) if entry>0 else 2
                target_pct = min(max(atr_pct*2.5, 3.5), 12)
                target = entry * (1 + target_pct/100)
                sl = entry * (1 - (target_pct/2)/100)
                future = df.iloc[i+1:i+11]
                for idx in range(len(future)):
                    if future["High"].iloc[idx] >= target:
                        wins+=1; break
                    if future["Low"].iloc[idx] <= sl:
                        break
        win_pct = int((wins/total*100)) if total>0 else 0
        return win_pct, wins, total
    except:
        return 0, 0, 0

indices_data = get_indices()
def fmt_chip(name, price, chg):
    arrow = "▲" if chg>=0 else "▼"; col = "index-up" if chg>=0 else "index-down"
    return f'<span class="index-chip">● {name} {int(price):,} <span class="{col}">{arrow} {abs(chg):.2f}%</span></span>'

st.markdown(f"""
<div class="header-god">
 <div style="display:flex; justify-content:space-between; align-items:center;">
  <div style="display:flex; align-items:center; gap:18px;">
   <div>{get_logo()}</div>
   <div>
    <div style="display:flex; align-items:center; gap:10px;">
     <h1 style="margin:0; color:white; font-family:Space Grotesk; font-size:26px; font-weight:700;">FinTrade</h1>
     <span style="background: linear-gradient(135deg,#00FF88,#00D1FF); -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-family:Space Grotesk; font-weight:700; font-size:26px;">Premium</span>
     <span class="bse-badge">BSE MODE</span>
     <span class="auto-badge">● V44.1 SMART ATR</span>
    </div>
    <div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:10px;">
     {fmt_chip("NIFTY50", indices_data.get("NIFTY50", {}).get("price", 0), indices_data.get("NIFTY50", {}).get("chg", 0))}
     {fmt_chip("SENSEX", indices_data.get("SENSEX", {}).get("price", 0), indices_data.get("SENSEX", {}).get("chg", 0))}
     {fmt_chip("BANKNIFTY", indices_data.get("BANKNIFTY", {}).get("price", 0), indices_data.get("BANKNIFTY", {}).get("chg", 0))}
    </div>
   </div>
  </div>
  <div style="text-align:right;"><p style="margin:0; color:#fff; font-family:JetBrains Mono; font-size:11px; opacity:0.6;">V44.1 SMART</p><p style="margin:2px 0 0 0; color:#FFD700; font-family:Space Grotesk; font-size:10px; font-weight:700;">ATR TARGET • REALISTIC</p></div>
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

def get_morning_picks():
    today=str(date.today())
    if st.session_state.pick_date==today and st.session_state.morning_picks: return st.session_state.morning_picks
    picks=[]
    for name in WATCHLIST:
        t=resolve_ticker(name); df=load_data(t)
        if not df.empty and len(df)>50:
            sc, rsns, rsi = score_stock(df); live=get_live_price(t)
            if live==0: live=float(df["Close"].iloc[-1])
            win_pct, wins, total = backtest_winrate(t)
            profit_pct, target, sl, atr_pct = get_smart_target(df, live, sc)
            picks.append({"name":name, "score":sc, "reasons":rsns, "rsi":rsi, "live":live, "target":target, "profit_pct":profit_pct, "sl":sl, "win_pct":win_pct, "wins":wins, "total":total, "atr_pct":atr_pct})
    picks=sorted(picks, key=lambda x: x["score"], reverse=True)[:2]
    st.session_state.morning_picks=picks; st.session_state.pick_date=today
    return picks

morning_picks=get_morning_picks()

ist = pytz.timezone('Asia/Kolkata')
now_ist = datetime.now(ist)
today_str = str(date.today())
if now_ist.hour == 9 and now_ist.minute >= 15 and now_ist.minute <= 20:
    if st.session_state.last_auto_sent!= today_str and st.session_state.tg_token and st.session_state.tg_chat and morning_picks:
        msg = f"🌅 *FinTrade V44.1 SMART ATR - {today_str}*\n\n"
        for i, p in enumerate(morning_picks, 1):
            msg += f"#{i} *{p['name']}* - ₹{round(p['live'],2)} Win {p['win_pct']}% ATR {p['atr_pct']:.1f}%\nTarget: ₹{round(p['target'],2)} (+{p['profit_pct']}%) SL: ₹{round(p['sl'],2)}\nScore: {p['score']}/110 BUY ✅\n\n"
        send_tg(st.session_state.tg_token, st.session_state.tg_chat, msg)
        st.session_state.last_auto_sent = today_str

if morning_picks:
    c1,c2=st.columns(2)
    for i, pick in enumerate(morning_picks):
        col=c1 if i==0 else c2
        pct=int(pick['score']/110*100)
        with col:
            st.markdown(f"""<div class="pick-god"><div style="display:flex; justify-content:space-between;"><div><span style="background: rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.12); color:#8892b0; font-size:9px; padding:4px 10px; border-radius:100px; font-family:JetBrains Mono;">#{i+1} TOP PICK</span><h2 style="margin:12px 0 0 0; color:white; font-family:Space Grotesk; font-size:26px; font-weight:700;">{pick['name']}</h2><p style="margin:6px 0 0 0; color:#00D1FF; font-family:JetBrains Mono; font-size:24px; font-weight:800;">₹{round(pick['live'],2)} <span style="color:#8892b0; font-size:11px;">RSI {pick['rsi']}</span></p><p style="margin:6px 0 0 0; color:rgba(255,255,255,0.7); font-size:11px;">{' • '.join(pick['reasons'][:3])}</p><span class="win-badge">📊 {pick['win_pct']}% Win ({pick['wins']}/{pick['total']})</span><span class="atr-badge">ATR {pick['atr_pct']:.1f}% • Smart</span></div><div style="text-align:center;"><div class="score-ring" style="--p:{pct}%;"><span style="position:relative; z-index:2; color:white; font-family:Space Grotesk; font-weight:700; font-size:14px;">{pick['score']}</span></div><div style="margin-top:10px; background: rgba(0,255,136,0.15); border:1px solid #00FF88; color:#00FF88; font-size:9px; padding:5px 12px; border-radius:100px; font-weight:700;">BUY</div></div></div><div class="target-row"><div><p style="margin:0; color:#8892b0; font-size:8px; font-family:JetBrains Mono;">SMART TARGET</p><p style="margin:2px 0 0 0; color:#00FF88; font-family:Space Grotesk; font-size:16px; font-weight:700;">₹{round(pick['target'],2)}</p></div><div style="text-align:center;"><p style="margin:0; color:#8892b0; font-size:8px; font-family:JetBrains Mono;">PROFIT</p><p style="margin:2px 0 0 0; color:#00FF88; font-family:JetBrains Mono; font-size:14px; font-weight:800; background: rgba(0,255,136,0.15); padding:3px 10px; border-radius:100px;">▲ +{pick['profit_pct']}%</p></div><div style="text-align:right;"><p style="margin:0; color:#8892b0; font-size:8px; font-family:JetBrains Mono;">STOP LOSS</p><p style="margin:2px 0 0 0; color:#FF4D6A; font-family:JetBrains Mono; font-size:12px; font-weight:700;">₹{round(pick['sl'],2)}</p></div></div></div>""", unsafe_allow_html=True)
    if st.button("↻ Refresh SMART ATR + Backtest", use_container_width=True):
        st.session_state.pick_date=""; st.rerun()

c1,c2=st.columns([5.2,1])
with c1: user_input=st.text_input("search", value="CUPID", placeholder="Search BSE symbol...", label_visibility="collapsed")
with c2: st.button("SEARCH ↗", use_container_width=True)

raw=user_input.upper().strip(); ticker=resolve_ticker(raw); df=load_data(ticker)
if df.empty: st.error(f"{raw} not found"); st.stop()
last=float(df["Close"].dropna().iloc[-1]); live=get_live_price(ticker)
if live==0: live=last
close=df["Close"]; ema20=close.ewm(20).mean(); ema50=close.ewm(50).mean()
sig="BUY" if ema20.iloc[-1]>ema50.iloc[-1] and last>ema20.iloc[-1] else "SELL" if ema20.iloc[-1]<ema50.iloc[-1] else "HOLD"
sig_class="buy-god" if sig=="BUY" else "sell-god"
df_c=df.tail(100).copy(); m_line,s_line,hist=calc_macd(df_c["Close"]); st_line,st_dir=calc_st(df_c)
st_sig="BUY" if st_dir.iloc[-1]==1 else "SELL"; st_color="#00FF88" if st_sig=="BUY" else "#FF4D6A"
profit_main, tgt, sl_main, atr_main = get_smart_target(df, live, 90)
win_pct_main, wins_main, total_main = backtest_winrate(ticker)

st.markdown(f"""<div class="top-god"><div style="display:flex; justify-content:space-between; align-items:center;"><div><div style="display:flex; align-items:center; gap:14px;"><h2 style="margin:0; color:white; font-family:Space Grotesk; font-size:28px; font-weight:700;">{raw}</h2><span style="background: rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.12); color:#8892b0; font-family:JetBrains Mono; font-size:10px; padding:5px 10px; border-radius:100px;">BSE:{raw}</span><span style="background: {st_color}18; border:1px solid {st_color}; color:{st_color}; font-family:Space Grotesk; font-size:10px; font-weight:700; padding:5px 12px; border-radius:100px;">ST {st_sig}</span><span style="background: rgba(255,215,0,0.15); border:1px solid #FFD700; color:#FFD700; font-family:JetBrains Mono; font-size:10px; padding:5px 10px; border-radius:100px;">ATR {atr_main:.1f}% • {win_pct_main}% Win</span></div><div style="display:flex; gap:16px; margin-top:16px;"><div style="background: linear-gradient(90deg, rgba(0,255,136,0.12), rgba(0,255,136,0.04)); border:1px solid rgba(0,255,136,0.25); border-left:3px solid #00FF88; border-radius:10px; padding:8px 14px;"><p style="margin:0; color:#8892b0; font-size:8px; font-family:JetBrains Mono;">SMART TARGET + PROFIT</p><p style="margin:2px 0 0 0; color:#00FF88; font-family:JetBrains Mono; font-weight:800; font-size:14px;">₹{round(tgt,2)} <span style="background: #00FF88; color:black; padding:2px 6px; border-radius:100px; font-size:10px;">▲ +{profit_main}%</span></p></div><div style="background: rgba(255,77,106,0.08); border:1px solid rgba(255,77,106,0.2); border-radius:10px; padding:8px 14px;"><p style="margin:0; color:#8892b0; font-size:8px; font-family:JetBrains Mono;">SMART SL</p><p style="margin:2px 0 0 0; color:#FF4D6A; font-family:JetBrains Mono; font-weight:700; font-size:13px;">₹{round(sl_main,2)}</p></div></div><p style="margin:12px 0 0 0; color:#FFD700; font-size:10px; font-family:JetBrains Mono;">🎯 ATR Based: Volatility {atr_main:.2f}% × 2.5 = {profit_main}% Target | Backtest: {wins_main}/{total_main} wins ({win_pct_main}%)</p></div><div style="text-align:right;"><p style="margin:0; color:#8892b0; font-size:9px; font-family:JetBrains Mono; letter-spacing:2px;">LIVE BSE PRICE</p><p class="live-price">₹{round(live,2)}</p><div class="{sig_class}" style="margin-top:14px; display:inline-block; min-width:130px; text-align:center;">{sig} ↗</div></div></div></div>""", unsafe_allow_html=True)

tab_bse, tab_chart, tab_tg = st.tabs(["📊 BSE TradingView PRO", "📈 Plotly", "📲 Telegram"])

with tab_bse:
    clean_sym = raw.replace(".NS","").replace(".BO","").strip()
    bse_symbol = f"BSE:{clean_sym}"
    st.markdown(f"""<div style="background: linear-gradient(90deg, #FF6A00, #FFD700); padding: 12px 16px; border-radius: 14px; margin-bottom:12px;"><span style="font-family:Space Grotesk; font-weight:700; color:black;">{bse_symbol} • ATR {atr_main:.1f}% • {win_pct_main}% Win • Smart Target</span></div>""", unsafe_allow_html=True)
    tv_bse_pro = f"https://s.tradingview.com/widgetembed/?frameElementId=tv_final&symbol={bse_symbol}&interval=D&hidesidetoolbar=0&symboledit=1&saveimage=1&toolbarbg=F1F3F6&studies=Supertrend%40tv-basicstudies%2CMACD%40tv-basicstudies%2CRSI%40tv-basicstudies&theme=dark&style=1&timezone=Asia%2FKolkata&withdateranges=1&show_popup_button=1"
    st.components.v1.iframe(tv_bse_pro, height=700, scrolling=False)

with tab_chart:
    close_c=df_c["Close"]; e20=close_c.ewm(20).mean(); e50=close_c.ewm(50).mean()
    delta=close_c.diff(); gain=(delta.where(delta>0,0)).rolling(14).mean(); loss=(-delta.where(delta<0,0)).rolling(14).mean()
    rs=gain/loss.replace(0,0.001); rsi=100-(100/(1+rs))
    fig=make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.62,0.19,0.19])
    fig.add_trace(go.Candlestick(x=df_c.index, open=df_c["Open"], high=df_c["High"], low=df_c["Low"], close=df_c["Close"], increasing_line_color="#00FF88", decreasing_line_color="#FF4D6A"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=e20, line=dict(color="#00D1FF",width=2), name="EMA20"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=e50, line=dict(color="#FFAA00",width=1.5,dash="dash"), name="EMA50"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=st_line, line=dict(color=st_color,width=2.5), name="Supertrend"), row=1, col=1)
    colors=["#00FF88" if h>=0 else "#FF4D6A" for h in hist]
    fig.add_trace(go.Scatter(x=df_c.index, y=m_line, line=dict(color="#00D1FF",width=2), name="MACD"), row=2, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=s_line, line=dict(color="#FFAA00",width=1.5), name="Signal"), row=2, col=1)
    fig.add_trace(go.Bar(x=df_c.index, y=hist, marker_color=colors), row=2, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=rsi, line=dict(color="#C084FC",width=2), name="RSI"), row=3, col=1)
    fig.update_layout(template="plotly_dark", height=620, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)

with tab_tg:
    st.markdown("### 📲 Telegram + Smart ATR")
    tok=st.text_input("Bot Token", value=st.session_state.tg_token, type="password")
    chat=st.text_input("Chat ID", value=st.session_state.tg_chat)
    if st.button("💾 Save & Test Now"):
        st.session_state.tg_token=tok; st.session_state.tg_chat=chat
        if morning_picks:
            msg = f"✅ *V44.1 SMART ATR Test - {today_str}*\n"
            for i, p in enumerate(morning_picks, 1):
                msg += f"#{i} *{p['name']}* ₹{round(p['live'],2)} ATR {p['atr_pct']:.1f}% Win {p['win_pct']}%\nTarget {p['profit_pct']}% SL {(p['profit_pct']/2):.1f}%\n"
            send_tg(tok, chat, msg)
            st.success("✅ Sent!")

st.warning("⚠️ Disclaimer: Educational only. ATR target = realistic volatility based. Past win rate!= future guarantee.")
st.caption(f"V44.1 SMART ATR • Realistic Target 3.5-12% • IST: {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d %b %I:%M %p')}")
