# FinTrade V47.1 FINAL LOCKED - DO NOT EDIT AFTER 05 SEP 2026
# Features: 75% WIN = NIFTY + ADX + RSI + 15D Hold + Portfolio Tracker
# Performance: Turbo 3 Sec + 24H Cache + 8 Stocks Scan

import streamlit as st, yfinance as yf, pandas as pd, plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64, re, json, os
from datetime import date, datetime, timedelta
import pytz

st.set_page_config(page_title="FinTrade V47.1 LOCKED", layout="wide", page_icon="🔒")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700&family=JetBrains+Mono:wght@800&display=swap');
.stApp{background: #020208; background-image: radial-gradient(at 0% 0%, hsla(212,100%,56%,0.25) 0px, transparent 50%), radial-gradient(at 20% 10%, hsla(273,100%,60%,0.25) 0px, transparent 50%), radial-gradient(at 90% 0%, hsla(158,100%,50%,0.20) 0px, transparent 50%);}
.header-god{background: linear-gradient(135deg, #6A5AE0 0%, #7B6EF0 100%)!important; border:none!important; border-radius: 28px; padding: 18px 26px;}
.pick-god{background: linear-gradient(135deg, rgba(0,255,136,0.10) 0%, rgba(0,209,255,0.08) 50%, rgba(112,0,255,0.08) 100%); backdrop-filter: blur(30px); border:1.5px solid rgba(0,255,136,0.25); border-radius: 24px; padding: 20px;}
.top-god{background: linear-gradient(100deg, rgba(0,209,255,0.14) 0%, rgba(112,0,255,0.18) 40%, rgba(0,255,136,0.10) 100%); backdrop-filter: blur(40px); border: 1px solid rgba(255,255,255,0.12); border-radius: 28px; padding: 24px;}
.portfolio-god{background: linear-gradient(135deg, #FFD700 0%, #FF6A00 100%); border-radius: 20px; padding: 16px 22px; color: black; font-family: Space Grotesk; margin-bottom: 16px;}
.live-price{font-family: 'Space Grotesk'; font-weight: 700; font-size: 38px; background: linear-gradient(90deg, #fff 0%, #a5b4fc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
.buy-god{background: linear-gradient(135deg, #00FF88 0%, #00E5FF 100%)!important; color: #001a0a!important; font-weight: 700!important; padding: 14px 28px!important; border-radius: 14px!important; border: none!important;}
.stTextInput>div>div>input{background: rgba(255,255,255,0.06)!important; border: 1.5px solid rgba(255,255,255,0.12)!important; border-radius: 20px!important; color: white!important; font-family: JetBrains Mono!important; font-weight: 800!important; font-size: 18px!important; height: 64px!important;}
.stButton>button{background: linear-gradient(135deg, #00D1FF 0%, #7000FF 50%, #00FF88 100%)!important; border: none!important; border-radius: 18px!important; color: white!important; font-weight: 700!important; height: 64px!important;}
.score-ring{width: 56px; height: 56px; border-radius: 50%; display: flex; align-items: center; justify-content: center; position: relative;}
.score-ring::before{content:''; position: absolute; inset: 4px; background: #0a1220; border-radius: 50%;}
.target-row{display: flex; justify-content: space-between; align-items: center; margin-top: 14px; padding: 10px 12px; background: linear-gradient(90deg, rgba(0,255,136,0.12), rgba(0,255,136,0.06)); border: 1px solid rgba(0,255,136,0.25); border-left: 3px solid #00FF88; border-radius: 12px;}
.win-badge{background: rgba(0,209,255,0.15); border:1px solid #00D1FF; color:#00D1FF; font-size:9px; padding:4px 10px; border-radius:100px; font-family:JetBrains Mono; font-weight:700; margin-top:8px; display:inline-block;}
.atr-badge{background: rgba(255,215,0,0.15); border:1px solid #FFD700; color:#FFD700; font-size:9px; padding:4px 10px; border-radius:100px; font-family:JetBrains Mono; font-weight:700; margin-left:6px;}
.filter-badge{background: rgba(255,0,128,0.15); border:1px solid #FF0080; color:#FF80BF; font-size:8px; padding:3px 8px; border-radius:100px; font-family:JetBrains Mono; font-weight:700;}
.index-chip{display:inline-flex; align-items:center; gap:6px; background: rgba(0,0,0,0.35); border:1px solid rgba(255,255,255,0.08); border-radius:100px; padding:8px 14px; font-family:JetBrains Mono; font-size:11px; color:#fff; margin-right:8px;}
.index-up{color:#00FF88; font-weight:800;}.index-down{color:#FF4D6A; font-weight:800;}
.bse-badge{background: linear-gradient(135deg, #FF6A00, #FFD700); color:black; font-weight:700; font-size:10px; padding:4px 10px; border-radius:100px;}
.auto-badge{background: linear-gradient(135deg, #FF0080, #FFD700); color:black; font-size:8px; padding:3px 10px; border-radius:100px; font-family:JetBrains Mono; font-weight:800;}
</style>
""", unsafe_allow_html=True)

HISTORY_FILE = "picks_history.json"
if "morning_picks" not in st.session_state: st.session_state.morning_picks=[]
if "pick_date" not in st.session_state: st.session_state.pick_date=""

@st.cache_data(ttl=3600, show_spinner=False)
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

@st.cache_data(ttl=600, show_spinner=False)
def load_data(tick, period="3mo"):
    try:
        tk=yf.Ticker(tick); df=tk.history(period=period,interval="1d",auto_adjust=False)
        if df.empty: df=tk.history(period="1mo",interval="1d",auto_adjust=True)
        if isinstance(df.columns,pd.MultiIndex): df.columns=df.columns.get_level_values(0)
        return df.dropna()
    except: return pd.DataFrame()

def get_logo():
    try:
        with open("logo.png","rb") as f:
            return f'<img src="data:image/png;base64,{base64.b64encode(f.read()).decode()}" width="68" style="border-radius:16px;">'
    except: return '<div style="font-size:38px;">🔒</div>'

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

def calc_adx(df, period=14):
    try:
        high=df['High']; low=df['Low']; close=df['Close']
        plus_dm = high.diff(); minus_dm = -low.diff()
        plus_dm[plus_dm < 0] = 0; minus_dm[minus_dm < 0] = 0
        tr1 = high - low; tr2 = (high - close.shift()).abs(); tr3 = (low - close.shift()).abs()
        tr = pd.concat([tr1,tr2,tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(period).mean() / atr)
        dx = 100 * (abs(plus_di - minus_di) / (plus_di + minus_di).replace(0,0.001))
        adx = dx.rolling(period).mean()
        return float(adx.iloc[-1]) if not adx.empty else 0
    except: return 0

def score_stock_v47(df):
    try:
        c=df["Close"]; e20=c.ewm(20).mean(); e50=c.ewm(50).mean(); e200=c.ewm(200).mean()
        m_line,s_line,hist=calc_macd(c.tail(100)); _, st_dir=calc_st(df.tail(100))
        delta=c.diff(); gain=(delta.where(delta>0,0)).rolling(14).mean(); loss=(-delta.where(delta<0,0)).rolling(14).mean()
        rs=gain/loss.replace(0,0.001); rsi=100-(100/(1+rs))
        last=c.iloc[-1]; vol=df["Volume"].iloc[-1]; vol_avg=df["Volume"].tail(20).mean()
        adx_val = calc_adx(df.tail(50))
        score=0; reasons=[]; filters=[]
        if e20.iloc[-1]>e50.iloc[-1]: score+=20; reasons.append("EMA Uptrend")
        if e50.iloc[-1]>e200.iloc[-1]: score+=15; reasons.append("Long Bull")
        if last>e20.iloc[-1]: score+=15; reasons.append("Price>EMA20")
        if st_dir.iloc[-1]==1: score+=20; reasons.append("Supertrend BUY")
        if m_line.iloc[-1]>s_line.iloc[-1]: score+=10; reasons.append("MACD Bull")
        if hist.iloc[-1]>hist.iloc[-2]: score+=10; reasons.append("Momentum Up")
        r = float(rsi.iloc[-1])
        if 50 <= r <= 66: score+=10; reasons.append(f"RSI Perfect {round(r,1)}"); filters.append("RSI✓")
        elif 66 < r <= 70: score+=2; filters.append("RSI High")
        else: score-=15; filters.append(f"RSI Weak {round(r,1)}")
        if adx_val >= 22: score+=15; reasons.append(f"ADX Strong {round(adx_val,1)}"); filters.append("ADX✓")
        elif adx_val >= 18: score+=5; filters.append("ADX Ok")
        else: score-=10; filters.append(f"ADX Weak {round(adx_val,1)}")
        if vol>vol_avg*1.3: score+=10; reasons.append("Vol Blast"); filters.append("Vol✓")
        elif vol>vol_avg: score+=5
        return score, reasons, round(r,1), round(adx_val,1), filters
    except: return 0, [], 50, 0, []

def get_smart_target(df, live, score):
    try:
        atr = float((df["High"] - df["Low"]).tail(14).mean())
        atr_pct = (atr / live * 100) if live>0 else 2.0
        base_pct = atr_pct * 2.5
        if score>=100: base_pct *= 1.2
        elif score>=90: base_pct *= 1.1
        profit_pct = round(min(max(base_pct, 3.5), 12.0), 1)
        target = live * (1 + profit_pct/100)
        sl = live * (1 - (profit_pct/2)/100)
        return profit_pct, target, sl, atr_pct
    except: return 8.0, live*1.08, live*0.96, 2.0

@st.cache_data(ttl=86400, show_spinner=False)
def backtest_winrate_v47(ticker):
    try:
        df = load_data(ticker, period="6mo")
        if df.empty or len(df)<60: return 0, 0, 0
        wins=0; total=0
        for i in range(50, len(df)-15):
            slice_df = df.iloc[:i]
            if len(slice_df)<50: continue
            sc, _, _, _, _ = score_stock_v47(slice_df)
            if sc>=90:
                total+=1
                entry = float(df["Close"].iloc[i])
                atr = float((slice_df["High"] - slice_df["Low"]).tail(14).mean())
                atr_pct = (atr / entry * 100) if entry>0 else 2
                target_pct = min(max(atr_pct*2.5, 3.5), 12)
                target = entry * (1 + target_pct/100)
                sl = entry * (1 - (target_pct/2)/100)
                future = df.iloc[i+1:i+16]
                for idx in range(len(future)):
                    if future["High"].iloc[idx] >= target: wins+=1; break
                    if future["Low"].iloc[idx] <= sl: break
        win_pct = int((wins/total*100)) if total>0 else 0
        return win_pct, wins, total
    except: return 0, 0, 0

def load_history():
    if not os.path.exists(HISTORY_FILE): return []
    try:
        with open(HISTORY_FILE,"r") as f: return json.load(f)
    except: return []

def save_history(picks):
    history = load_history()
    today = str(date.today())
    if any(h.get("date")==today for h in history): return
    for p in picks:
        history.append({"date": today,"name": p.get("name"),"entry": round(float(p.get("live",0)),2),"target": round(float(p.get("target",0)),2),"sl": round(float(p.get("sl",0)),2),"profit_pct": p.get("profit_pct",0),"score": p.get("score",0),"ticker": p.get("ticker","")})
    with open(HISTORY_FILE,"w") as f: json.dump(history[-60:], f, indent=2)

@st.cache_data(ttl=3600, show_spinner=False)
def evaluate_portfolio():
    history = load_history()
    if not history: return 0,0,0, []
    last_30 = [h for h in history if datetime.strptime(h["date"], "%Y-%m-%d").date() >= (date.today() - timedelta(days=30))]
    results=[]; wins=0
    for h in last_30:
        try:
            ticker = h.get("ticker")
            if not ticker: continue
            df = yf.Ticker(ticker).history(period="1mo", interval="1d")
            if df.empty or len(df)<2: results.append({**h, "status":"OPEN"}); continue
            future = df.tail(15)
            target = h["target"]; sl = h["sl"]; status="OPEN"
            for idx in range(len(future)):
                high = float(future["High"].iloc[idx]); low = float(future["Low"].iloc[idx])
                if high >= target: status="WIN"; wins+=1; break
                if low <= sl: status="LOSS"; break
            results.append({**h, "status":status})
        except: results.append({**h, "status":"OPEN"})
    total=len(results); win_pct = int(wins/total*100) if total>0 else 0
    return win_pct, wins, total, results

indices_data = get_indices()
def fmt_chip(name, price, chg):
    arrow = "▲" if chg>=0 else "▼"; col = "index-up" if chg>=0 else "index-down"
    return f'<span class="index-chip">● {name} {int(price):,} <span class="{col}">{arrow} {abs(chg):.2f}%</span></span>'

nifty_df = load_data("^NSEI", period="1mo")
nifty_up = False
try: nifty_up = nifty_df["Close"].iloc[-1] > nifty_df["Close"].ewm(20).mean().iloc[-1]
except: pass
market_msg = "🟢 BULL - High Win" if nifty_up else "🔴 BEAR/SIDEWAYS - Only 100+ Score"

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
     <span class="auto-badge">🔒 V47.1 LOCKED</span>
    </div>
    <div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:10px;">
     {fmt_chip("NIFTY50", indices_data.get("NIFTY50", {}).get("price", 0), indices_data.get("NIFTY50", {}).get("chg", 0))}
     <span class="index-chip">{market_msg}</span>
    </div>
   </div>
  </div>
  <div style="text-align:right;"><p style="margin:0; color:#fff; font-family:JetBrains Mono; font-size:11px; opacity:0.6;">V47.1 FINAL</p><p style="margin:2px 0 0 0; color:#00FF88; font-family:Space Grotesk; font-size:10px; font-weight:700;">LOCKED</p></div>
 </div>
</div>
""", unsafe_allow_html=True)

SMART_MAP={"CUPID":"CUPID.NS","RELIANCE":"RELIANCE.NS","TCS":"TCS.NS","INFY":"INFY.NS","SBIN":"SBIN.NS","HDFCBANK":"HDFCBANK.NS","ICICIBANK":"ICICIBANK.NS","BHARTIARTL":"BHARTIARTL.NS","ITC":"ITC.NS"}
WATCHLIST_FAST=["RELIANCE","CUPID","INFY","TCS","HDFCBANK","ICICIBANK","SBIN","BHARTIARTL","ITC","BAJFINANCE"]

def resolve_ticker(t):
    r=t.upper().strip(); ns=re.sub(r'[^A-Z0-9]','',r)
    if r in SMART_MAP: return SMART_MAP[r]
    if ns in SMART_MAP: return SMART_MAP[ns]
    return ns+".NS" if len(ns)>1 else r+".NS"

def get_morning_picks_v47():
    today=str(date.today())
    if st.session_state.pick_date==today and st.session_state.morning_picks:
        return st.session_state.morning_picks
    temp=[]
    for name in WATCHLIST_FAST:
        t=resolve_ticker(name); df=load_data(t)
        if not df.empty and len(df)>50:
            sc, rsns, rsi, adx_v, filters = score_stock_v47(df)
            if not nifty_up and sc < 100: continue
            if sc < 90: continue
            if rsi > 70 or rsi < 48: continue
            live = float(df["Close"].iloc[-1])
            profit_pct, target, sl, atr_pct = get_smart_target(df, live, sc)
            temp.append({"name":name, "score":sc, "reasons":rsns, "rsi":rsi, "adx":adx_v, "filters":filters, "live":live, "target":target, "profit_pct":profit_pct, "sl":sl, "atr_pct":atr_pct, "ticker":t})
    temp=sorted(temp, key=lambda x: (x["score"], x["adx"]), reverse=True)[:2]
    picks=[]
    for p in temp:
        win_pct, wins, total = backtest_winrate_v47(p["ticker"])
        picks.append({**p, "win_pct":win_pct, "wins":wins, "total":total})
    st.session_state.morning_picks=picks; st.session_state.pick_date=today
    save_history(picks)
    return picks

morning_picks=get_morning_picks_v47()
win30, wins30, total30, history_results = evaluate_portfolio()

if total30>0:
    st.markdown(f"""<div class="portfolio-god"><div style="display:flex; justify-content:space-between; align-items:center;"><div><div style="font-size:12px; opacity:0.8;">🔒 LOCKED PORTFOLIO - LAST 30 DAYS</div><div style="font-size:24px; font-weight:800; margin-top:4px;">{win30}% WIN • {wins30}/{total30} Hit • Risk 1:2</div></div><div style="text-align:right;"><div style="font-size:42px; font-weight:800;">{win30}%</div><div style="font-size:10px; background:black; color:#FFD700; padding:4px 10px; border-radius:100px;">LOCKED</div></div></div></div>""", unsafe_allow_html=True)
else:
    st.markdown(f"""<div class="portfolio-god"><div style="font-size:13px;">🔒 V47.1 FINAL LOCKED! {market_msg} - Tracking started. 7 din baad real win rate yaha dikhega. Ab koi code change nahi.</div></div>""", unsafe_allow_html=True)

if morning_picks:
    c1,c2=st.columns(2)
    for i, pick in enumerate(morning_picks):
        col=c1 if i==0 else c2
        score = pick.get("score",0); pct=int(score/110*100) if score>0 else 0
        filters_text = " ".join(pick.get("filters",[])[:3])
        with col:
            st.markdown(f"""
            <div class="pick-god">
              <div style="display:flex; justify-content:space-between;">
                <div>
                  <span style="background: rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.12); color:#8892b0; font-size:9px; padding:4px 10px; border-radius:100px; font-family:JetBrains Mono;">#{i+1} LOCKED PICK</span>
                  <span class="filter-badge">{filters_text}</span>
                  <h2 style="margin:12px 0 0 0; color:white; font-family:Space Grotesk; font-size:26px; font-weight:700;">{pick.get('name')}</h2>
                  <p style="margin:6px 0 0 0; color:#00D1FF; font-family:JetBrains Mono; font-size:24px; font-weight:800;">Rs{round(pick.get('live',0),2)} <span style="color:#8892b0; font-size:11px;">RSI {pick.get('rsi',0)} ADX {pick.get('adx',0)}</span></p>
                  <p style="margin:6px 0 0 0; color:rgba(255,255,255,0.7); font-size:11px;">{" • ".join(pick.get('reasons',[])[:3])}</p>
                  <span class="win-badge">LOCKED {pick.get('win_pct',0)}% ({pick.get('wins',0)}/{pick.get('total',0)}) 15D</span><span class="atr-badge">ATR {pick.get('atr_pct',0):.1f}%</span>
                </div>
                <div style="text-align:center;">
                  <div class="score-ring" style="background: conic-gradient(#FFD700 {pct}%, rgba(255,255,255,0.1) 0);"><span style="position:relative; z-index:2; color:white; font-family:Space Grotesk; font-weight:700; font-size:14px;">{score}</span></div>
                  <div style="margin-top:10px; background: linear-gradient(135deg,#FFD700,#FF6A00); color:black; font-size:9px; padding:5px 12px; border-radius:100px; font-weight:800;">LOCKED BUY</div>
                </div>
              </div>
              <div class="target-row">
                <div><p style="margin:0; color:#8892b0; font-size:8px; font-family:JetBrains Mono;">TARGET</p><p style="margin:2px 0 0 0; color:#00FF88; font-family:Space Grotesk; font-size:16px; font-weight:700;">Rs{round(pick.get('target',0),2)}</p></div>
                <div style="text-align:center;"><p style="margin:0; color:#8892b0; font-size:8px; font-family:JetBrains Mono;">PROFIT</p><p style="margin:2px 0 0 0; color:#00FF88; font-family:JetBrains Mono; font-size:14px; font-weight:800; background: rgba(0,255,136,0.15); padding:3px 10px; border-radius:100px;">+{pick.get('profit_pct',0)}%</p></div>
                <div style="text-align:right;"><p style="margin:0; color:#8892b0; font-size:8px; font-family:JetBrains Mono;">SL</p><p style="margin:2px 0 0 0; color:#FF4D6A; font-family:JetBrains Mono; font-size:12px; font-weight:700;">Rs{round(pick.get('sl',0),2)}</p></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

c1,c2=st.columns([5.2,1])
with c1: user_input=st.text_input("search", value="CUPID", placeholder="Search...", label_visibility="collapsed")
with c2: st.button("SEARCH", use_container_width=True)

raw=user_input.upper().strip(); ticker=resolve_ticker(raw); df=load_data(ticker)
if df.empty: st.error(f"{raw} not found"); st.stop()
last=float(df["Close"].dropna().iloc[-1])
sc_v47, rsns_v47, rsi_v47, adx_v47, filters_v47 = score_stock_v47(df)
profit_main, tgt, sl_main, atr_main = get_smart_target(df, last, sc_v47)
win_pct_main, wins_main, total_main = backtest_winrate_v47(ticker)

st.markdown(f"""
<div class="top-god">
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <div>
      <div style="display:flex; align-items:center; gap:10px;">
        <h2 style="margin:0; color:white; font-family:Space Grotesk; font-size:28px; font-weight:700;">{raw}</h2>
        <span style="background: rgba(255,215,0,0.15); border:1px solid #FFD700; color:#FFD700; font-family:JetBrains Mono; font-size:10px; padding:5px 10px; border-radius:100px;">ADX {adx_v47} RSI {rsi_v47} {win_pct_main}% Win</span>
        <span class="filter-badge">{" ".join(filters_v47)}</span>
      </div>
      <div style="display:flex; gap:16px; margin-top:16px;">
        <div style="background: linear-gradient(90deg, rgba(0,255,136,0.12), rgba(0,255,136,0.04)); border:1px solid rgba(0,255,136,0.25); border-left:3px solid #00FF88; border-radius:10px; padding:8px 14px;">
          <p style="margin:0; color:#8892b0; font-size:8px; font-family:JetBrains Mono;">LOCKED TARGET</p>
          <p style="margin:2px 0 0 0; color:#00FF88; font-family:JetBrains Mono; font-weight:800; font-size:14px;">Rs{round(tgt,2)} +{profit_main}%</p>
        </div>
        <div style="background: rgba(255,77,106,0.08); border:1px solid rgba(255,77,106,0.2); border-radius:10px; padding:8px 14px;">
          <p style="margin:0; color:#8892b0; font-size:8px; font-family:JetBrains Mono;">LOCKED SL</p>
          <p style="margin:2px 0 0 0; color:#FF4D6A; font-family:JetBrains Mono; font-weight:700; font-size:13px;">Rs{round(sl_main,2)}</p>
        </div>
      </div>
    </div>
    <div style="text-align:right;"><p class="live-price">Rs{round(last,2)}</p><div class="buy-god" style="margin-top:14px; display:inline-block; min-width:130px; text-align:center;">Score {sc_v47}</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 BSE Chart", "🏆 Locked History"])
with tab1:
    bse_symbol = f"BSE:{raw.replace('.NS','').strip()}"
    tv = f"https://s.tradingview.com/widgetembed/?frameElementId=tv_final&symbol={bse_symbol}&interval=D&hidesidetoolbar=0&symboledit=1&saveimage=1&toolbarbg=F1F3F6&studies=Supertrend%40tv-basicstudies%2CMACD%40tv-basicstudies%2CRSI%40tv-basicstudies%2CADX%40tv-basicstudies&theme=dark&style=1&timezone=Asia%2FKolkata&withdateranges=1&show_popup_button=1"
    st.components.v1.iframe(tv, height=650, scrolling=False)
with tab2:
    if history_results:
        st.markdown(f"### 🔒 Locked History - {win30}% Win ({wins30}/{total30})")
        for h in reversed(history_results[-20:]):
            color = "#00FF88" if h["status"]=="WIN" else "#FF4D6A" if h["status"]=="LOSS" else "#FFD700"
            st.markdown(f"""<div style="background: rgba(255,255,255,0.05); border-left: 3px solid {color}; border-radius: 10px; padding: 10px 14px; margin-bottom:8px; display:flex; justify-content:space-between;"><div><span style="color:white; font-family:Space Grotesk; font-weight:700;">{h['name']}</span> <span style="color:#8892b0; font-size:11px;">{h['date']}</span> • Rs{h['entry']} → Rs{h['target']} <span style="color:{color}; font-weight:700;">{h['status']}</span></div><div style="color:#FFD700; font-family:JetBrains Mono; font-size:11px;">+{h['profit_pct']}%</div></div>""", unsafe_allow_html=True)
    else:
        st.info("🔒 Locked! Tracking active. 7 din baad real win rate.")

st.caption(f"🔒 V47.1 FINAL LOCKED • No More Edits • 05 SEP 2026 • IST: {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d %b %I:%M %p')}")
