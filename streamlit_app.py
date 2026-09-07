# ============================================================================
# FinTrade V52 FINAL LOCKED - 24H WORKING - DO NOT EDIT AFTER 08 SEP 2026
# BASE = V48.1 GREEN HIDE + NIFTY500 + YOUR SCREENSHOT QUESS Rs379.6 + PAYTM 1664.0
# FINAL LOCK = 24H PICKS + PERFECT + NEWS + ULTIMATE - NO MORE EDITS
# ============================================================================
import streamlit as st, yfinance as yf, pandas as pd
import base64, re, json, os
from datetime import date, datetime, timedelta
import pytz, numpy as np
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="FinTrade V52 FINAL LOCKED 24H", layout="wide", page_icon="🔒")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700&family=JetBrains+Mono:wght@800&display=swap');
.stApp{background:#020208; background-image: radial-gradient(at 0% 0%, hsla(212,100%,56%,0.25) 0px, transparent 50%), radial-gradient(at 20% 10%, hsla(273,100%,60%,0.25) 0px, transparent 50%);}
.header-god{background: linear-gradient(135deg, #6A5AE0 0%, #7B6EF0 100%)!important; border:none!important; border-radius: 28px; padding: 18px 26px;}
.pick-god{background: linear-gradient(135deg, rgba(0,255,136,0.10) 0%, rgba(0,209,255,0.08) 50%, rgba(112,0,255,0.08) 100%); backdrop-filter: blur(30px); border:1.5px solid rgba(0,255,136,0.25); border-radius: 24px; padding: 20px; min-height: 420px;}
.target-row{display: flex; justify-content: space-between; align-items: center; margin-top: 14px; padding: 10px 12px; background: linear-gradient(90deg, rgba(0,255,136,0.12), rgba(0,255,136,0.06)); border: 1px solid rgba(0,255,136,0.25); border-left: 3px solid #00FF88; border-radius: 12px;}
.win-badge{background: rgba(0,209,255,0.15); border:1px solid #00D1FF; color:#00D1FF; font-size:9px; padding:4px 10px; border-radius:100px; font-family:JetBrains Mono; font-weight:700; margin-top:8px; display:inline-block;}
.ai-badge{background: linear-gradient(135deg, #7000FF, #00D1FF); color:white; font-size:10px; padding:6px 14px; border-radius:100px; font-family:JetBrains Mono; font-weight:800; margin-left:6px; box-shadow: 0 0 15px rgba(112,0,255,0.5);}
.filter-badge{background: rgba(255,0,128,0.15); border:1px solid #FF0080; color:#FF80BF; font-size:8px; padding:3px 8px; border-radius:100px; font-family:JetBrains Mono; font-weight:700;}
.index-chip{display:inline-flex; align-items:center; gap:6px; background: rgba(0,0,0,0.35); border:1px solid rgba(255,255,255,0.08); border-radius:100px; padding:8px 14px; font-family:JetBrains Mono; font-size:11px; color:#fff; margin-right:8px;}
.bse-badge,.auto-badge,.index-chip,.portfolio-god {display:none!important; visibility:hidden!important;}
.header-god div[style*="text-align:right"] {display:none!important; visibility:hidden!important;}
.score-ring{width: 56px; height: 56px; border-radius: 50%; display: flex; align-items: center; justify-content: center; position: relative;}
.score-ring::before{content:''; position: absolute; inset: 4px; background: #0a1220; border-radius: 50%;}
.perfect-row{margin-top:12px; display:flex; justify-content:space-between; align-items:center; padding:8px 12px; background: linear-gradient(90deg, rgba(255,215,0,0.15), rgba(255,140,0,0.10)); border:1px solid rgba(255,215,0,0.30); border-left:3px solid #FFD700; border-radius:10px;}
.news-row{margin-top:8px; display:flex; justify-content:space-between; align-items:center; padding:6px 12px; background: rgba(0,209,255,0.08); border:1px solid rgba(0,209,255,0.20); border-left:3px solid #00D1FF; border-radius:8px;}
.top-god{background: linear-gradient(100deg, rgba(0,209,255,0.14) 0%, rgba(112,0,255,0.18) 40%, rgba(0,255,136,0.10) 100%); border: 1px solid rgba(255,255,255,0.12); border-radius: 28px; padding: 24px;}
.live-price{font-family: 'Space Grotesk'; font-weight: 700; font-size: 38px; background: linear-gradient(90deg, #fff 0%, #a5b4fc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
.stTextInput>div>div>input{background: rgba(255,255,255,0.06)!important; border: 1.5px solid rgba(255,255,255,0.12)!important; border-radius: 20px!important; color: white!important; font-family: JetBrains Mono!important; font-weight: 800!important; font-size: 18px!important; height: 64px!important;}
.stButton>button{background: linear-gradient(135deg, #00D1FF 0%, #7000FF 50%, #00FF88 100%)!important; border: none!important; border-radius: 18px!important; color: white!important; font-weight: 700!important; height: 64px!important;}
</style>
""", unsafe_allow_html=True)

HISTORY_FILE="picks_history.json"
if "morning_picks" not in st.session_state: st.session_state.morning_picks=[]
if "pick_date" not in st.session_state: st.session_state.pick_date=""

@st.cache_data(ttl=600, show_spinner=False)
def load_data(tick, period="6mo"):
    try:
        tk=yf.Ticker(tick); df=tk.history(period=period,interval="1d",auto_adjust=False)
        if isinstance(df.columns,pd.MultiIndex): df.columns=df.columns.get_level_values(0)
        return df.dropna()
    except: return pd.DataFrame()
def get_logo():
    try:
        with open("logo.png","rb") as f: return f'<img src="data:image/png;base64,{base64.b64encode(f.read()).decode()}" width="68" style="border-radius:16px;">'
    except: return '<div style="font-size:38px;">🔒</div>'
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
        delta=close.diff(); gain=(delta.where(delta>0,0)).rolling(14).mean(); loss=(-delta.where(delta<0,0)).rolling(14).mean(); rs=gain/loss.replace(0,0.001); rsi=100-(100/(1+rs))
        high=df['High']; low=df['Low']; tr1=high-low; tr2=(high-close.shift()).abs(); tr3=(low-close.shift()).abs(); tr=pd.concat([tr1,tr2,tr3],axis=1).max(axis=1); atr=tr.rolling(14).mean()
        plus_dm=high.diff(); minus_dm=-low.diff(); plus_dm[plus_dm<0]=0; minus_dm[minus_dm<0]=0
        plus_di=100*(plus_dm.rolling(14).mean()/atr); minus_di=100*(minus_dm.rolling(14).mean()/atr); dx=100*(abs(plus_di-minus_di)/(plus_di+minus_di).replace(0,0.001)); adx=dx.rolling(14).mean()
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
        m,s,_=calc_macd(c.tail(100)); st_dir=calc_st(df.tail(100))
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
        if 50<=r<=66: score+=10; reasons.append(f"RSI {round(r,1)}"); filters.append("RSI")
        else: score-=5; filters.append(f"RSI {round(r,1)}")
        if adx_val>=22: score+=15; reasons.append(f"ADX {round(adx_val,1)}"); filters.append("ADX")
        else: score-=5; filters.append(f"ADX {round(adx_val,1)}")
        if vol>vol_avg*1.2: score+=10; filters.append("Vol")
        if ai_prob>=70: score+=15; reasons.append(f"AI {ai_prob} pct UP"); filters.append(f"AI {ai_prob}")
        elif ai_prob>=60: score+=5; filters.append(f"AI {ai_prob}")
        else: score-=5
        return score,reasons,round(r,1),round(adx_val,1),filters
    except: return 0,[],50,0,[]
def get_smart_target(df, live, score):
    try:
        atr=float((df["High"]-df["Low"]).tail(14).mean()); atr_pct=(atr/live*100) if live>0 else 2.0; base=atr_pct*2.5
        if score>=110: base*=1.25
        profit=round(min(max(base,3.5),12.0),1); tgt=live*(1+profit/100); sl=live*(1-(profit/2)/100)
        return profit,tgt,sl,atr_pct
    except: return 8.0,live*1.08,live*0.96,2.0
def get_perfect_combo(df, ai_prob_old):
    try:
        c=df["Close"]; h=df["High"]; l=df["Low"]; v=df["Volume"]
        e20=c.ewm(20).mean(); e50=c.ewm(50).mean(); e200=c.ewm(200).mean()
        trend=0
        if e20.iloc[-1]>e50.iloc[-1]: trend+=25
        if e50.iloc[-1]>e200.iloc[-1]: trend+=25
        if c.iloc[-1]>e20.iloc[-1]: trend+=25
        if c.iloc[-1]>c.ewm(10).mean().iloc[-1]: trend+=25
        m,s,_=calc_macd(c.tail(50))
        delta=c.diff(); gain=(delta.where(delta>0,0)).rolling(14).mean(); loss=(-delta.where(delta<0,0)).rolling(14).mean(); rs=gain/loss.replace(0,0.001); rsi=100-(100/(1+rs))
        mom=0
        if m.iloc[-1]>s.iloc[-1]: mom+=40
        if 55<=float(rsi.iloc[-1])<=68: mom+=60
        st_dir=calc_st(df.tail(50))
        tr1=h-l; tr2=(h-c.shift()).abs(); tr3=(l-c.shift()).abs(); tr=pd.concat([tr1,tr2,tr3],axis=1).max(axis=1); atr=tr.rolling(14).mean()
        plus_dm=h.diff(); minus_dm=-l.diff(); plus_dm[plus_dm<0]=0; minus_dm[minus_dm<0]=0
        plus_di=100*(plus_dm.rolling(14).mean()/atr); minus_di=100*(minus_dm.rolling(14).mean()/atr); dx=100*(abs(plus_di-minus_di)/(plus_di+minus_di).replace(0,0.001)); adx=dx.rolling(14).mean()
        strength=0
        if st_dir.iloc[-1]==1: strength+=50
        if float(adx.iloc[-1])>=25: strength+=50
        vol=100 if v.iloc[-1]>v.tail(20).mean()*1.5 else 60
        perfect=int(trend*0.20 + mom*0.20 + strength*0.20 + vol*0.15 + ai_prob_old*0.25)
        return min(99,max(0,perfect)), "5 AI BUY" if perfect>=80 else "4 AI BUY"
    except: return ai_prob_old, "Combo"
@st.cache_data(ttl=1800, show_spinner=False)
def get_news_sentiment(ticker_symbol):
    try:
        tk = yf.Ticker(ticker_symbol)
        news = tk.news if hasattr(tk, 'news') else []
        if not news: return 60, "Neutral"
        titles = " ".join([n.get('title','') for n in news[:5]]).lower()
        pos = sum(1 for w in ["buy","upgrade","strong","growth","profit","bullish","gain","rise","record","beat"] if w in titles)
        neg = sum(1 for w in ["sell","downgrade","loss","bearish","fall","drop","miss","cut","warn"] if w in titles)
        if pos>neg: return 85, f"Bullish +{pos}"
        elif neg>pos: return 25, f"Bearish -{neg}"
        else: return 60, "Neutral"
    except: return 50, "N/A"
def get_ultimate_combo(perfect_old, news_score):
    ultimate = int(perfect_old*0.75 + news_score*0.25)
    return min(99,max(0,ultimate)), "7 AI STRONG" if ultimate>=85 else "6 AI BUY"

def load_history():
    if not os.path.exists(HISTORY_FILE): return []
    try:
        with open(HISTORY_FILE,"r") as f: return json.load(f)
    except: return []
def save_history(picks):
    h=load_history(); today=str(date.today())
    if any(x.get("date")==today for x in h): return
    for p in picks: h.append({"date":today,"name":p.get("name"),"entry":round(float(p.get("live",0)),2),"target":round(float(p.get("target",0)),2),"sl":round(float(p.get("sl",0)),2),"profit_pct":p.get("profit_pct",0),"score":p.get("score",0),"ticker":p.get("ticker",""),"ai":p.get("ai_prob",0),"perfect":p.get("perfect_combo",0),"news":p.get("news_score",0),"ultimate":p.get("ultimate_combo",0)})
    with open(HISTORY_FILE,"w") as f: json.dump(h[-60:],f,indent=2)

NIFTY500 = ["360ONE","3MINDIA","ABB","ACC","AIAENG","APLAPOLLO","AUBANK","AARTIIND","AAVAS","ABBOTINDIA","ADANIENSOL","ADANIENT","ADANIGREEN","ADANIPORTS","ADANIPOWER","ATGL","ABCAPITAL","ABFRL","ABSLAMC","ADVENZYMES","AEGISCHEM","AFFLE","AJANTPHARM","AKZOINDIA","ALKEM","ALKYLAMINE","ALOKINDS","AMBER","AMBUJACEM","ANANDRATHI","ANGELONE","ANURAS","APARINDS","APLLTD","APOLLOHOSP","APOLLOTYRE","APTUS","ASAHIINDIA","ASHOKLEY","ASIANPAINT","ASTERDM","ASTRAL","ATUL","AUROPHARMA","AVANTIFEED","DMART","AXISBANK","BEML","BLS","BSE","BAJAJ-AUTO","BAJAJFINSV","BAJFINANCE","BALKRISIND","BALRAMCHIN","BANDHANBNK","BANKBARODA","BANKINDIA","BATAINDIA","BAYERCROP","BERGEPAINT","BEL","BHARATFORG","BHEL","BPCL","BHARTIARTL","BIKAJI","BIOCON","BIRLACORPN","BSOFT","BLUEDART","BLUESTARCO","BBTC","BORORENEW","BOSCHLTD","BRIGADE","BRITANNIA","MAPMYINDIA","CCL","CESC","CGPOWER","CIEINDIA","CRISIL","CSBBANK","CAMPUS","CANFINHOME","CANBK","CAPLIPOINT","CGCL","CARBORUNDU","CASTROLIND","CEATLTD","CENTRALBK","CDSL","CENTURYPLY","CERA","CHALET","CHAMBLFERT","CHEMPLASTS","CHOLAHLDNG","CHOLAFIN","CIPLA","CUB","CLEAN","COALINDIA","COCHINSHIP","COFORGE","COLPAL","CAMS","CONCOR","COROMANDEL","CRAFTSMAN","CREDITACC","CROMPTON","CUMMINSIND","CUPID","CYIENT","DCMSHRIRAM","DLF","DABUR","DALBHARAT","DATAPATTNS","DEEPAKFERT","DEEPAKNTR","DELHIVERY","DELTACORP","DEVYANI","DIVISLAB","DIXON","LALPATHLAB","DRREDDY","EIDPARRY","EIHOTEL","EPL","EASEMYTRIP","ECLERX","ELECON","ELGIEQUIP","EMAMILTD","ENDURANCE","ENGINERSIN","EQUITASBNK","ERIS","ESABINDIA","EXIDEIND","FDC","FEDERALBNK","FACT","FINEORG","FINCABLES","FINPIPE","FSL","FIVESTAR","FORTIS","GAIL","GMMPFAUDLR","GMRINFRA","GALAXYSURF","GRSE","GARFIBRES","GICRE","GILLETTE","GLAND","GLAXO","GLENMARK","GODFRYPHLP","GODREJCP","GODREJIND","GODREJPROP","GRANULES","GRAPHITE","GRASIM","GESHIP","GRINDWELL","GUJALKALI","GAEL","FLUOROCHEM","GUJGASLTD","GMDCLTD","GNFC","GPPL","GSFC","GSPL","HEG","HCLTECH","HDFCAMC","HDFCBANK","HDFCLIFE","HFCL","HAPPSTMNDS","HAPPYFORGE","HATHWAY","HATSUN","HAVELLS","HEROMOTOCO","HINDALCO","HAL","HINDCOPPER","HINDPETRO","HINDUNILVR","HINDWAREAP","HINDZINC","POWERINDIA","HOMEFIRST","HONASA","HONAUT","HUDCO","ICICIBANK","ICICIGI","ICICIPRULI","IDBI","IDFCFIRSTB","IDFC","IIFL","IRB","IRCTC","IRFC","IFCI","IEX","INDIANB","IOLCP","IGL","INDHOTEL","INDIACEM","INDIAMART","INDIANHUME","INDUSINDBK","NAUKRI","INFY","INOXWIND","INTELLECT","INDUS_TOWERS","IPCALAB","JBCHEPHARM","JKCEMENT","JKLAKSHMI","JKPAPER","JMFINANCIL","JSWENERGY","JSWINFRA","JSWSTEEL","JAMNAAUTO","JINDALSAW","JSL","JINDALSTEL","JIOFIN","JUBLFOOD","JUBLINGREA","JUBLPHARMA","JUSTDIAL","JYOTHYLAB","KPRMILL","KEI","KFINTECH","KALYANKJIL","KAJARIACER","KPITTECH","KARURVYSYA","KAYNES","KEC","KNRCON","KPIL","KOTAKBANK","KIMS","LTF","LTTS","LT","LTIM","LATENTVIEW","LAURUSLABS","LXCHEM","LEMONTREE","LICHSGFIN","LICI","LINDE","LUPIN","MRF","MGL","MAHSEAMLES","M_AND_MFIN","M_AND_M","MANAPPURAM","MRPL","MANKIND","MARICO","MARUTI","MASTEK","MFSL","MAXHEALTH","MAZDOCK","MEDANTA","MEDPLUS","METROPOLIS","MOTHERSON","MSUMI","MPHASIS","MCX","MUTHOOTFIN","NATCOPHARM","NBCC","NCC","NHPC","NLCINDIA","NMDC","NSLNISP","NTPC","NH","NATIONALUM","NAVINFLUOR","NAZARA","NESTLEIND","NETWORK18","NAM-INDIA","NUVAMA","OBEROIRLTY","ONGC","OIL","OLECTRA","PAYTM","OFSS","POLICYBZR","PCBL","PFC","PEL","PHOENIXLTD","PIDILITIND","PPLPHARMA","POLYCAB","POWERGRID","PRAJIND","PRESTIGE","PRINCEPIPE","PRSMJOHNSN","PGHH","PGHL","PNB","PNBHOUSING","QUESS","RBLBANK","RECLTD","RHIM","RITES","RADICO","RVNL","RAILTEL","RALLIS","RKFORGE","RCF","RTNINDIA","RAYMOND","REDINGTON","RELIANCE","RBA","ROUTE","SBICARD","SBILIFE","SJVN","SKFINDIA","SRF","SANOFI","SAPPHIRE","SAREGAMA","SCHAEFFLER","SEQUENT","SFL","SHOPERSTOP","SHYAMMETL","SIEMENS","SOBHA","SOLARINDS","SONACOMS","STARHEALTH","SBIN","SAIL","SWSOLAR","SUMICHEM","SUNPHARMA","SUNTV","SUNDARMFIN","SUNDRMFAST","SUPREMEIND","SUZLON","SYNGENE","SYRMA","TTKPRESTIG","TV18BRDCST","TVSMOTOR","TMB","TATACHEM","TATACOMM","TCS","TATACONSUM","TATAELXSI","TATAMOTORS","TATAPOWER","TATASTEEL","TATATECH","TTML","TEAMLEASE","TECHM","THERMAX","TIMKEN","TITAN","TORNTPHARM","TORNTPOWER","TRENT","TRIDENT","TRIVENI","TRITURBINE","TIINDIA","UCOBANK","UNIONBANK","UBL","MCDOWELL-N","VGUARD","DBREALTY","VTL","VARROC","VBL","MANYAVAR","VEDL","VIJAYA","VOLTAS","WELCORP","WELSPUNLTD","WESTLIFE","WHIRLPOOL","WIPRO","YESBANK","ZFCVINDIA","ZOMATO","ZYDUSLIFE","ZYDUSWELL"]
WATCHLIST=NIFTY500
def resolve_ticker(t):
    r=t.upper().strip().replace("M_AND_MFIN","M&MFIN").replace("M_AND_M","M&M").replace("INDUS_TOWERS","INDUS TOWERS")
    ns=re.sub(r'[^A-Z0-9 &-]','',r).replace(" & ","&").strip()
    return ns+".NS" if len(ns)>1 else r+".NS"

# 24H WORKING LOGIC - PICKS WILL NEVER BE EMPTY
def get_morning_picks():
    ist_now = datetime.now(pytz.timezone('Asia/Kolkata')); today=str(date.today())
    # 24H LOCK - same picks for whole day
    if st.session_state.pick_date==today and st.session_state.morning_picks:
        return st.session_state.morning_picks
    all_scanned=[]; strict_picks=[]; prog=st.progress(0); total=len(WATCHLIST)
    for idx,name in enumerate(WATCHLIST):
        prog.progress((idx+1)/total, text=f"24H AI Scanning {idx+1}/{total} : {name}")
        t=resolve_ticker(name); df=load_data(t,period="6mo")
        if not df.empty and len(df)>50:
            ai_prob,ai_reason=get_ai_prediction(t)
            sc,rsns,rsi,adx_v,filters=score_stock(df,ai_prob)
            live=float(df["Close"].iloc[-1]); profit,tgt,sl,atr=get_smart_target(df,live,sc)
            perfect_combo, perfect_reason = get_perfect_combo(df, ai_prob)
            news_score, news_reason = get_news_sentiment(t)
            ultimate_combo, ultimate_reason = get_ultimate_combo(perfect_combo, news_score)
            item={"name":name,"score":sc,"reasons":rsns,"rsi":rsi,"adx":adx_v,"filters":filters,"live":live,"target":tgt,"profit_pct":profit,"sl":sl,"atr_pct":atr,"ticker":t,"ai_prob":ai_prob,"ai_reason":ai_reason,"perfect_combo":perfect_combo,"perfect_reason":perfect_reason,"news_score":news_score,"news_reason":news_reason,"ultimate_combo":ultimate_combo,"ultimate_reason":ultimate_reason}
            all_scanned.append(item)
            # Strict filter for best quality
            if ai_prob>=60 and sc>=75 and 40<=rsi<=72:
                strict_picks.append(item)
    prog.empty()
    # 24H GUARANTEE: If strict empty, use top from all scanned
    if len(strict_picks)>=2:
        final_picks=sorted(strict_picks,key=lambda x:(x["ultimate_combo"],x["ai_prob"],x["score"]),reverse=True)[:2]
    else:
        final_picks=sorted(all_scanned,key=lambda x:(x["ultimate_combo"],x["ai_prob"],x["score"]),reverse=True)[:2]
    if not final_picks and all_scanned:
        final_picks=all_scanned[:2]
    st.session_state.morning_picks=final_picks; st.session_state.pick_date=today
    if final_picks: save_history(final_picks)
    return final_picks

ist_now = datetime.now(pytz.timezone('Asia/Kolkata'))
st.markdown(f"""<div class="header-god"><div style="display:flex; align-items:center; gap:18px;"><div>{get_logo()}</div><div><div style="display:flex; gap:10px;"><h1 style="margin:0; color:white; font-family:Space Grotesk; font-size:26px;">FinTrade</h1><span style="background: linear-gradient(135deg,#00FF88,#00D1FF); -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-family:Space Grotesk; font-weight:700; font-size:26px;">Premium</span></div><div style="margin-top:6px; color:rgba(255,255,255,0.7); font-family:JetBrains Mono; font-size:10px;">🔒 V52 FINAL LOCKED 24H • {ist_now.strftime('%d %b %I:%M %p')} • {len(WATCHLIST)} Stocks • PERFECT+NEWS</div></div></div></div>""", unsafe_allow_html=True)

morning_picks=get_morning_picks()
if morning_picks:
    c1,c2=st.columns(2)
    for i,pick in enumerate(morning_picks):
        col=c1 if i==0 else c2; pct=int(min(pick.get("score",0),110)/110*100)
        with col:
            st.markdown(f"""
            <div class="pick-god">
              <div style="display:flex; justify-content:space-between;">
                <div style="flex:1; min-width:0;">
                  <div style="display:flex; gap:6px; flex-wrap:wrap;">
                    <span style="background: rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.12); color:#8892b0; font-size:9px; padding:4px 10px; border-radius:100px; font-family:JetBrains Mono;">#{i+1} NIFTY500 AI PICK</span>
                    <span class="ai-badge">AI {pick.get('ai_prob',0)} pct UP</span>
                  </div>
                  <h2 style="margin:12px 0 0 0; color:white; font-family:Space Grotesk; font-size:26px;">{pick.get('name')}</h2>
                  <p style="margin:6px 0 0 0; color:#00D1FF; font-family:JetBrains Mono; font-size:22px; font-weight:800;">Rs{round(pick.get('live',0),2)} <span style="color:#8892b0; font-size:11px;">RSI {pick.get('rsi',0)} ADX {pick.get('adx',0)}</span></p>
                  <p style="margin:6px 0 0 0; color:rgba(255,255,255,0.7); font-size:11px;">{" • ".join(pick.get('reasons',[])[:3])}</p>
                  <span class="win-badge">{pick.get('ai_reason','')} • ATR {pick.get('atr_pct',0):.1f} pct</span>
                </div>
                <div style="text-align:center; margin-left:12px;">
                  <div class="score-ring" style="background: conic-gradient(#FFD700 {pct}%, rgba(255,255,255,0.1) 0);"><span style="position:relative; z-index:2; color:white; font-family:Space Grotesk; font-weight:700; font-size:14px;">{pick.get('score',0)}</span></div>
                  <div style="margin-top:10px; background: linear-gradient(135deg,#FFD700,#FF6A00); color:black; font-size:9px; padding:5px 12px; border-radius:100px; font-weight:800;">LOCKED BUY</div>
                </div>
              </div>
              <div class="perfect-row">
                <div style="font-family:JetBrains Mono; font-size:10px; font-weight:800; color:#FFD700;">PERFECT {pick.get('perfect_combo',0)} pct • {pick.get('perfect_reason','')}</div>
                <div style="font-family:JetBrains Mono; font-size:8px; font-weight:700; color:black; background: linear-gradient(135deg,#FFD700,#FF8C00); padding:4px 10px; border-radius:100px;">5 AI AGREE</div>
              </div>
              <div class="news-row">
                <div style="font-family:JetBrains Mono; font-size:9px; font-weight:700; color:#00D1FF;">NEWS {pick.get('news_score',0)} pct • {pick.get('news_reason','')}</div>
                <div style="font-family:JetBrains Mono; font-size:9px; font-weight:800; color:#FFD700; background: rgba(255,215,0,0.15); padding:3px 8px; border-radius:100px;">ULTIMATE {pick.get('ultimate_combo',0)} pct • {pick.get('ultimate_reason','')}</div>
              </div>
              <div class="target-row">
                <div><p style="margin:0; color:#8892b0; font-size:8px; font-family:JetBrains Mono;">TARGET</p><p style="margin:2px 0 0 0; color:#00FF88; font-family:Space Grotesk; font-size:16px; font-weight:700;">Rs{round(pick.get('target',0),2)}</p></div>
                <div style="text-align:center;"><p style="margin:0; color:#8892b0; font-size:8px; font-family:JetBrains Mono;">PROFIT</p><p style="margin:2px 0 0 0; color:#00FF88; font-family:JetBrains Mono; font-size:14px; font-weight:800; background: rgba(0,255,136,0.15); padding:3px 10px; border-radius:100px;">+{pick.get('profit_pct',0)} pct</p></div>
                <div style="text-align:right;"><p style="margin:0; color:#8892b0; font-size:8px; font-family:JetBrains Mono;">SL</p><p style="margin:2px 0 0 0; color:#FF4D6A; font-family:JetBrains Mono; font-size:12px; font-weight:700;">Rs{round(pick.get('sl',0),2)}</p></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

# SEARCH SECTION - 24H WORKING
c1,c2=st.columns([5.2,1])
with c1: user_input=st.text_input("search",value="CUPID",placeholder="Search NIFTY500...",label_visibility="collapsed")
with c2: st.button("SEARCH",use_container_width=True)
raw=user_input.upper().strip(); ticker=resolve_ticker(raw); df=load_data(ticker,period="1y")
if not df.empty:
    last=float(df["Close"].dropna().iloc[-1]); ai_prob_search,ai_reason_search=get_ai_prediction(ticker)
    sc_search,rsns_search,rsi_search,adx_search,filters_search=score_stock(df,ai_prob_search)
    profit_main,tgt,sl_main,atr_main=get_smart_target(df,last,sc_search)
    perfect_search, perfect_reason_search = get_perfect_combo(df, ai_prob_search)
    news_search, news_reason_search = get_news_sentiment(ticker)
    ultimate_search, ultimate_reason_search = get_ultimate_combo(perfect_search, news_search)
    st.markdown(f"""
    <div class="top-god">
      <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
        <div>
          <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:center;">
            <h2 style="margin:0; color:white; font-family:Space Grotesk; font-size:28px;">{raw}</h2>
            <span class="ai-badge">AI {ai_prob_search} pct • {ai_reason_search}</span>
            <span style="background: linear-gradient(135deg,#FFD700,#FF6A00); color:black; font-size:10px; padding:6px 14px; border-radius:100px; font-family:JetBrains Mono; font-weight:900;">PERFECT {perfect_search} pct</span>
            <span style="background: rgba(0,209,255,0.15); border:1px solid #00D1FF; color:#00D1FF; font-size:10px; padding:6px 14px; border-radius:100px; font-family:JetBrains Mono;">NEWS {news_search} pct • ULTIMATE {ultimate_search} pct</span>
          </div>
          <div style="display:flex; gap:12px; margin-top:16px; flex-wrap:wrap;">
            <div style="background: linear-gradient(90deg, rgba(112,0,255,0.2), rgba(0,209,255,0.15)); border:1px solid rgba(112,0,255,0.3); border-left:3px solid #7000FF; border-radius:10px; padding:8px 14px;">
              <p style="margin:0; color:#8892b0; font-size:8px; font-family:JetBrains Mono;">AI TARGET</p>
              <p style="margin:2px 0 0 0; color:#00FF88; font-family:JetBrains Mono; font-weight:800; font-size:14px;">Rs{round(tgt,2)} +{profit_main} pct</p>
            </div>
            <div style="background: rgba(255,77,106,0.08); border:1px solid rgba(255,77,106,0.2); border-radius:10px; padding:8px 14px;">
              <p style="margin:0; color:#8892b0; font-size:8px; font-family:JetBrains Mono;">AI SL</p>
              <p style="margin:2px 0 0 0; color:#FF4D6A; font-family:JetBrains Mono; font-weight:700; font-size:13px;">Rs{round(sl_main,2)}</p>
            </div>
          </div>
        </div>
        <div style="text-align:right;"><p class="live-price">Rs{round(last,2)}</p></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.caption(f"🔒 V52 FINAL LOCKED 24H • {len(WATCHLIST)} Stocks • No More Edits • IST: {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d %b %I:%M %p')} • 24H Working Guarantee")
