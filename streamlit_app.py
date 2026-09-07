# FinTrade V48.1 FINAL LOCKED + NIFTY500 - LIQUIDE THEME - 07 SEP 2026
# LOGIC 100% SAME V48.1 - ONLY UI = LIQUIDE STYLE WHITE + PURPLE
import streamlit as st, yfinance as yf, pandas as pd
import base64, re, json, os
from datetime import date, datetime, timedelta
import pytz, numpy as np
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="FinTrade Liquide Theme", layout="wide", page_icon="💜")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@600;700;800&family=Space+Grotesk:wght@700&display=swap');
.stApp{background:#F8F7FF!important; font-family: Inter!important;}
.header-god{background: linear-gradient(135deg, #4F20C7 0%, #8B5CF6 100%)!important; border-radius: 24px; padding: 18px 26px; box-shadow: 0 8px 24px rgba(79,32,199,0.2);}
.pick-god{background:#FFFFFF!important; border:1px solid #EDE9FE!important; border-radius: 20px!important; padding: 20px!important; box-shadow: 0 4px 16px rgba(0,0,0,0.06)!important;}
.top-god{background:#FFFFFF!important; border:1px solid #EDE9FE!important; border-radius: 20px!important; padding: 24px!important; box-shadow: 0 4px 16px rgba(0,0,0,0.06)!important;}
.portfolio-god{display:none!important;}
.live-price{font-family: Space Grotesk; font-weight: 800; font-size: 36px; color:#1E1B4B!important;}
.stTextInput>div>div>input{background:#FFFFFF!important; border:1.5px solid #DDD6FE!important; border-radius: 14px!important; color:#1E1B4B!important; font-weight:600!important; height:52px!important;}
.stButton>button{background:#4F20C7!important; border-radius:12px!important; color:white!important; font-weight:700!important; height:52px!important;}
.score-ring{width: 52px; height: 52px; border-radius: 50%; display:flex; align-items:center; justify-content:center; background:#EDE9FE; color:#4F20C7; font-weight:800; border: 3px solid #8B5CF6;}
.target-row{background:#F5F3FF!important; border:1px solid #EDE9FE!important; border-radius:12px!important; padding:12px!important; margin-top:14px;}
.ai-badge{background:#EDE9FE!important; color:#4F20C7!important; font-size:11px; padding:6px 12px; border-radius:8px; font-weight:800;}
.bse-badge,.auto-badge,.index-chip{display:none!important;}
.win-badge{background:#EDE9FE; color:#4F20C7; border:none; font-size:10px; padding:6px 12px; border-radius:8px; font-weight:600;}
.filter-badge{background:#FEE2E2; color:#991B1B; font-size:9px; padding:4px 8px; border-radius:100px;}
</style>
""", unsafe_allow_html=True)

HISTORY_FILE="picks_history.json"
if "morning_picks" not in st.session_state: st.session_state.morning_picks=[]
if "pick_date" not in st.session_state: st.session_state.pick_date=""

@st.cache_data(ttl=3600, show_spinner=False)
def get_indices():
    d={}
    for n,s in {"NIFTY50":"^NSEI"}.items():
        try:
            h=yf.Ticker(s).history(period="2d")
            last=float(h["Close"].iloc[-1]); prev=float(h["Close"].iloc[-2]) if len(h)>1 else last
            chg=(last-prev)/prev*100 if prev!=0 else 0
            d[n]={"price":last,"chg":chg}
        except: d[n]={"price":0,"chg":0}
    return d

@st.cache_data(ttl=600, show_spinner=False)
def load_data(tick, period="6mo"):
    try:
        tk=yf.Ticker(tick); df=tk.history(period=period,interval="1d",auto_adjust=False)
        if isinstance(df.columns,pd.MultiIndex): df.columns=df.columns.get_level_values(0)
        return df.dropna()
    except: return pd.DataFrame()

def get_logo():
    return '<div style="background:white; width:44px; height:44px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:22px;">💜</div>'

def calc_st(df):
    hl2=(df['High']+df['Low'])/2; tr1=df['High']-df['Low']; tr2=(df['High']-df['Close'].shift()).abs(); tr3=(df['Low']-df['Close'].shift()).abs()
    tr=pd.concat([tr1,tr2,tr3],axis=1).max(axis=1); atr=tr.rolling(10).mean(); upper=hl2+3*atr; lower=hl2-3*atr
    direction=[1]*len(df)
    for i in range(1,len(df)):
        if df['Close'].iloc[i]<=lower.iloc[i-1]: direction[i]=-1
        elif df['Close'].iloc[i]>=upper.iloc[i-1]: direction[i]=1
        else: direction[i]=direction[i-1]
    return pd.Series(direction,index=df.index)

def calc_macd(c):
    ef=c.ewm(12).mean(); es=c.ewm(26).mean(); m=ef-es; s=m.ewm(9).mean(); return m,s,m-s

@st.cache_data(ttl=86400, show_spinner=False)
def get_ai_prediction(ticker):
    try:
        df=yf.Ticker(ticker).history(period="1y",interval="1d")
        if isinstance(df.columns,pd.MultiIndex): df.columns=df.columns.get_level_values(0)
        df=df.dropna()
        if len(df)<120: return 50,"Low Data"
        close=df["Close"]; e20=close.ewm(20).mean(); e50=close.ewm(50).mean()
        delta=close.diff(); gain=(delta.where(delta>0,0)).rolling(14).mean(); loss=(-delta.where(delta<0,0)).rolling(14).mean()
        rs=gain/loss.replace(0,0.001); rsi=100-(100/(1+rs))
        high=df['High']; low=df['Low']; tr1=high-low; tr2=(high-close.shift()).abs(); tr3=(low-close.shift()).abs()
        tr=pd.concat([tr1,tr2,tr3],axis=1).max(axis=1); atr=tr.rolling(14).mean()
        plus_dm=high.diff(); minus_dm=-low.diff(); plus_dm[plus_dm<0]=0; minus_dm[minus_dm<0]=0
        plus_di=100*(plus_dm.rolling(14).mean()/atr); minus_di=100*(minus_dm.rolling(14).mean()/atr)
        dx=100*(abs(plus_di-minus_di)/(plus_di+minus_di).replace(0,0.001)); adx=dx.rolling(14).mean()
        df['rsi']=rsi; df['adx']=adx; df['ema_diff']=(e20-e50)/close*100; df['vol_ratio']=df['Volume']/df['Volume'].rolling(20).mean(); df['atr_pct']=atr/close*100; df['ret_5']=close.pct_change(5); df['close_20']=close/e20
        df_clean=df.dropna()
        if len(df_clean)<80: return 50,"Low Data"
        df_clean['future']=df_clean['Close'].shift(-10); df_clean['label']=(df_clean['future']>df_clean['Close']*1.04).astype(int); df_clean=df_clean.dropna()
        features=['rsi','adx','ema_diff','vol_ratio','atr_pct','ret_5','close_20']
        X=df_clean[features].iloc[:-10]; y=df_clean['label'].iloc[:-10]
        if len(X)<50: return 50,"Low Data"
        model=RandomForestClassifier(n_estimators=80,max_depth=6,random_state=42,n_jobs=-1); model.fit(X,y)
        prob_up=model.predict_proba(df_clean[features].iloc[-1:].values)[0][1]*100
        reason="Strong AI Buy" if prob_up>=70 else "AI Neutral" if prob_up>=55 else "AI Weak"
        return int(prob_up),reason
    except: return 50,"AI Error"

def score_stock(df, ai_prob):
    try:
        c=df["Close"]; e20=c.ewm(20).mean(); e50=c.ewm(50).mean(); e200=c.ewm(200).mean()
        m,s,h=calc_macd(c.tail(100)); st_dir=calc_st(df.tail(100))
        delta=c.diff(); gain=(delta.where(delta>0,0)).rolling(14).mean(); loss=(-delta.where(delta<0,0)).rolling(14).mean(); rs=gain/loss.replace(0,0.001); rsi=100-(100/(1+rs))
        last=c.iloc[-1]; vol=df["Volume"].iloc[-1]; vol_avg=df["Volume"].tail(20).mean()
        tr1=df['High']-df['Low']; tr2=(df['High']-df['Close'].shift()).abs(); tr3=(df['Low']-df['Close'].shift()).abs(); tr=pd.concat([tr1,tr2,tr3],axis=1).max(axis=1); atr=tr.rolling(14).mean()
        plus_dm=df['High'].diff(); minus_dm=-df['Low'].diff(); plus_dm[plus_dm<0]=0; minus_dm[minus_dm<0]=0
        plus_di=100*(plus_dm.rolling(14).mean()/atr); minus_di=100*(minus_dm.rolling(14).mean()/atr); dx=100*(abs(plus_di-minus_di)/(plus_di+minus_di).replace(0,0.001)); adx=dx.rolling(14).mean()
        adx_val=float(adx.iloc[-1]) if not adx.empty else 0
        score=0; reasons=[]; filters=[]
        if e20.iloc[-1]>e50.iloc[-1]: score+=20; reasons.append("EMA Uptrend")
        if e50.iloc[-1]>e200.iloc[-1]: score+=15; reasons.append("Long Bull")
        if last>e20.iloc[-1]: score+=15; reasons.append("Price>EMA20")
        if st_dir.iloc[-1]==1: score+=20; reasons.append("Supertrend BUY")
        if m.iloc[-1]>s.iloc[-1]: score+=10; reasons.append("MACD Bull")
        r=float(rsi.iloc[-1])
        if 50<=r<=66: score+=10; reasons.append(f"RSI {round(r,1)}"); filters.append("RSI✓")
        else: score-=15; filters.append(f"RSI {round(r,1)}")
        if adx_val>=22: score+=15; reasons.append(f"ADX {round(adx_val,1)}"); filters.append("ADX✓")
        else: score-=10; filters.append(f"ADX {round(adx_val,1)}")
        if vol>vol_avg*1.3: score+=10; filters.append("Vol✓")
        if ai_prob>=70: score+=15; reasons.append(f"AI {ai_prob}% UP"); filters.append(f"AI {ai_prob}%")
        elif ai_prob>=60: score+=5; filters.append(f"AI {ai_prob}%")
        else: score-=10; filters.append(f"AI Weak {ai_prob}%")
        return score,reasons,round(r,1),round(adx_val,1),filters
    except: return 0,[],50,0,[]

def get_smart_target(df, live, score):
    try:
        atr=float((df["High"]-df["Low"]).tail(14).mean()); atr_pct=(atr/live*100) if live>0 else 2.0; base=atr_pct*2.5
        if score>=110: base*=1.25
        profit=round(min(max(base,3.5),12.0),1); tgt=live*(1+profit/100); sl=live*(1-(profit/2)/100)
        return profit,tgt,sl,atr_pct
    except: return 8.0,live*1.08,live*0.96,2.0

def load_history():
    if not os.path.exists(HISTORY_FILE): return []
    try:
        with open(HISTORY_FILE,"r") as f: return json.load(f)
    except: return []
def save_history(picks):
    h=load_history(); today=str(date.today())
    if any(x.get("date")==today for x in h): return
    for p in picks: h.append({"date":today,"name":p.get("name"),"entry":round(float(p.get("live",0)),2),"target":round(float(p.get("target",0)),2),"sl":round(float(p.get("sl",0)),2),"profit_pct":p.get("profit_pct",0),"score":p.get("score",0),"ticker":p.get("ticker",""),"ai":p.get("ai_prob",0)})
    with open(HISTORY_FILE,"w") as f: json.dump(h[-60:],f,indent=2)

@st.cache_data(ttl=3600, show_spinner=False)
def evaluate_portfolio():
    history=load_history()
    if not history: return 0,0,0,[]
    last_30=[h for h in history if datetime.strptime(h["date"],"%Y-%m-%d").date()>= (date.today()-timedelta(days=30))]
    results=[]; wins=0
    for h in last_30:
        try:
            t=h.get("ticker"); df=yf.Ticker(t).history(period="1mo")
            if df.empty: results.append({**h,"status":"OPEN"}); continue
            future=df.tail(15); tgt=h["target"]; sl=h["sl"]; status="OPEN"
            for idx in range(len(future)):
                hi=float(future["High"].iloc[idx]); lo=float(future["Low"].iloc[idx])
                if hi>=tgt: status="WIN"; wins+=1; break
                if lo<=sl: status="LOSS"; break
            results.append({**h,"status":status})
        except: results.append({**h,"status":"OPEN"})
    total=len(results); win_pct=int(wins/total*100) if total>0 else 0
    return win_pct,wins,total,results

NIFTY500 = ["360ONE","3MINDIA","ABB","ACC","AIAENG","APLAPOLLO","AUBANK","AARTIIND","AAVAS","ABBOTINDIA","ADANIENSOL","ADANIENT","ADANIGREEN","ADANIPORTS","ADANIPOWER","ATGL","ABCAPITAL","ABFRL","ABSLAMC","ADVENZYMES","AEGISCHEM","AFFLE","AJANTPHARM","AKZOINDIA","ALKEM","ALKYLAMINE","ALOKINDS","AMBER","AMBUJACEM","ANANDRATHI","ANGELONE","ANURAS","APARINDS","APLLTD","APOLLOHOSP","APOLLOTYRE","APTUS","ASAHIINDIA","ASHOKLEY","ASIANPAINT","ASTERDM","ASTRAL","ATUL","AUROPHARMA","AVANTIFEED","DMART","AXISBANK","BEML","BLS","BSE","BAJAJ-AUTO","BAJAJFINSV","BAJFINANCE","BALKRISIND","BALRAMCHIN","BANDHANBNK","BANKBARODA","BANKINDIA","BATAINDIA","BAYERCROP","BERGEPAINT","BEL","BHARATFORG","BHEL","BPCL","BHARTIARTL","BIKAJI","BIOCON","BIRLACORPN","BSOFT","BLUEDART","BLUESTARCO","BBTC","BORORENEW","BOSCHLTD","BRIGADE","BRITANNIA","MAPMYINDIA","CCL","CESC","CGPOWER","CIEINDIA","CRISIL","CSBBANK","CAMPUS","CANFINHOME","CANBK","CAPLIPOINT","CGCL","CARBORUNDU","CASTROLIND","CEATLTD","CENTRALBK","CDSL","CENTURYPLY","CERA","CHALET","CHAMBLFERT","CHEMPLASTS","CHOLAHLDNG","CHOLAFIN
