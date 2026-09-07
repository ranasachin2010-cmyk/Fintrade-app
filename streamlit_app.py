# FinTrade V48.1 + 2X SCAN + NEWS + GPT SUMMARY - 07 SEP 2026
import streamlit as st, yfinance as yf, pandas as pd, re, json, os, requests
from datetime import date, datetime
import pytz, numpy as np
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="FinTrade V48.1 GPT NEWS", layout="wide", page_icon="🔒")
st.markdown("""<style>
.stApp{background:#020208;}
.header-god{background: linear-gradient(135deg, #6A5AE0 0%, #7B6EF0 100%)!important; border-radius: 28px; padding: 18px 26px;}
.pick-god{background: linear-gradient(135deg, rgba(0,255,136,0.10) 0%, rgba(0,209,255,0.08) 50%, rgba(112,0,255,0.08) 100%); backdrop-filter: blur(30px); border:1.5px solid rgba(0,255,136,0.25); border-radius: 24px; padding: 20px;}
.top-god{background: linear-gradient(100deg, rgba(0,209,255,0.14) 0%, rgba(112,0,255,0.18) 40%, rgba(0,255,136,0.10) 100%); border: 1px solid rgba(255,255,255,0.12); border-radius: 28px; padding: 24px;}
.live-price{font-family: Space Grotesk; font-weight: 700; font-size: 38px; background: linear-gradient(90deg, #fff 0%, #a5b4fc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
.ai-badge{background: linear-gradient(135deg, #7000FF, #00D1FF); color:white; font-size:10px; padding:6px 14px; border-radius:100px; font-weight:800; margin-left:6px;}
.news-badge{background: rgba(255,215,0,0.15); border:1px solid #FFD700; color:#FFD700; font-size:11px; padding:10px 12px; border-radius:10px; margin-top:10px; line-height:1.5; max-width:700px;}
.gpt-badge{background: rgba(0,255,136,0.15); border:1px solid #00FF88; color:#00FF88; font-size:11px; padding:10px 12px; border-radius:10px; margin-top:8px; line-height:1.5; max-width:700px;}
.target-row{display:flex; justify-content:space-between; margin-top:14px; padding:10px 12px; background: rgba(0,255,136,0.12); border:1px solid rgba(0,255,136,0.25); border-left:3px solid #00FF88; border-radius:12px;}
</style>""", unsafe_allow_html=True)

HISTORY_FILE="picks_history.json"
if "morning_picks" not in st.session_state: st.session_state.morning_picks=[]
if "pick_date" not in st.session_state: st.session_state.pick_date=""
if "pick_slot" not in st.session_state: st.session_state.pick_slot=""

@st.cache_data(ttl=1800, show_spinner=False)
def get_news_with_gpt(ticker, stock_name):
    # Step 1: Get yfinance news
    titles = []
    try:
        tk = yf.Ticker(ticker)
        news_list = tk.news if hasattr(tk,'news') else []
        titles = [n.get('title','') for n in news_list[:4] if n.get('title')]
    except:
        titles = []

    news_text = " | ".join(titles[:3]) if titles else "No recent major news"

    # Step 2: Try GPT summary if key available
    try:
        api_key = st.secrets.get("OPENAI_API_KEY", "")
        if api_key and titles:
            prompt = f"Stock {stock_name} ({ticker}) news: {news_text}. In 1 line Hindi+English mix, tell why this stock is bullish or bearish for short term trader. Max 20 words. Example: 'Q1 profit 25% up, new order win se bullish momentum'"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            data = {
                "model": "gpt-4o-mini",
                "messages": [{"role":"user","content":prompt}],
                "max_tokens": 60
            }
            r = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=15)
            if r.status_code == 200:
                gpt_summary = r.json()['choices'][0]['message']['content'].strip()
                return news_text, gpt_summary, "GPT"
    except Exception as e:
        pass

    # Fallback - Rule based summary
    text_lower = news_text.lower()
    if any(w in text_lower for w in ["profit","growth","beat","record","order","deal","upgrade"]):
        gpt_fallback = f"{stock_name} me positive news flow - {titles[0][:70]}... se buying interest"
    elif any(w in text_lower for w in ["loss","downgrade","fall"]):
        gpt_fallback = f"{stock_name} me thoda caution - {titles[0][:70]}... par technical strong"
    else:
        gpt_fallback = f"{stock_name} - Technical breakout + volume surge, news support se BUY momentum"

    return news_text, gpt_fallback, "RULE"

@st.cache_data(ttl=600, show_spinner=False)
def load_data(tick, period="6mo"):
    try:
        tk=yf.Ticker(tick); df=tk.history(period=period,interval="1d",auto_adjust=False)
        if isinstance(df.columns,pd.MultiIndex): df.columns=df.columns.get_level_values(0)
        return df.dropna()
    except: return pd.DataFrame()

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
        score=0; reasons=[]
        if e20.iloc[-1]>e50.iloc[-1]: score+=20; reasons.append("EMA Uptrend")
        if e50.iloc[-1]>e200.iloc[-1]: score+=15; reasons.append("Long Bull")
        if last>e20.iloc[-1]: score+=15; reasons.append("Price>EMA20")
        if st_dir.iloc[-1]==1: score+=20; reasons.append("Supertrend BUY")
        if m.iloc[-1]>s.iloc[-1]: score+=10; reasons.append("MACD Bull")
        r=float(rsi.iloc[-1])
        if 50<=r<=66: score+=10; reasons.append(f"RSI {round(r,1)}")
        else: score-=15
        if adx_val>=22: score+=15; reasons.append(f"ADX {round(adx_val,1)}")
        else: score-=10
        if vol>vol_avg*1.3: score+=10
        if ai_prob>=70: score+=15; reasons.append(f"AI {ai_prob}% UP")
        elif ai_prob>=60: score+=5
        else: score-=10
        return score,reasons,round(r,1),round(adx_val,1)
    except: return 0,[],50,0

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

NIFTY500 = ["360ONE","3MINDIA","ABB","ACC","AIAENG","APLAPOLLO","AUBANK","AARTIIND","AAVAS","ABBOTINDIA","ADANIENSOL","ADANIENT","ADANIGREEN","ADANIPORTS","ADANIPOWER","ATGL","ABCAPITAL","ABFRL","ABSLAMC","ADVENZYMES","AEGISCHEM","AFFLE","AJANTPHARM","AKZOINDIA","ALKEM","ALKYLAMINE","ALOKINDS","AMBER","AMBUJACEM","ANANDRATHI","ANGELONE","ANURAS","APARINDS","APLLTD","APOLLOHOSP","APOLLOTYRE","APTUS","ASAHIINDIA","ASHOKLEY","ASIANPAINT","ASTERDM","ASTRAL","ATUL","AUROPHARMA","AVANTIFEED","DMART","AXISBANK","BEML","BLS","BSE","BAJAJ-AUTO","BAJAJFINSV","BAJFINANCE","BALKRISIND","BALRAMCHIN","BANDHANBNK","BANKBARODA","BANKINDIA","BATAINDIA","BAYERCROP","BERGEPAINT","BEL","BHARATFORG","BHEL","BPCL","BHARTIARTL","BIKAJI","BIOCON","BIRLACORPN","BSOFT","BLUEDART","BLUESTARCO","BBTC","BORORENEW","BOSCHLTD","BRIGADE","BRITANNIA","MAPMYINDIA","CCL","CESC","CGPOWER","CIEINDIA","CRISIL","CSBBANK","CAMPUS","CANFINHOME","CANBK","CAPLIPOINT","CGCL","CARBORUNDU","CASTROLIND","CEATLTD","CENTRALBK","CDSL","CENTURYPLY","CERA","CHALET","CHAMBLFERT","CHEMPLASTS","CHOLAHLDNG","CHOLAFIN","CIPLA","CUB","CLEAN","COALINDIA","COCHINSHIP","COFORGE","COLPAL","CAMS","CONCOR","COROMANDEL","CRAFTSMAN","CREDITACC","CROMPTON","CUMMINSIND","CUPID","CYIENT","DCMSHRIRAM","DLF","DABUR","DALBHARAT","DATAPATTNS","DEEPAKFERT","DEEPAKNTR","DELHIVERY","DELTACORP","DEVYANI","DIVISLAB","DIXON","LALPATHLAB","DRREDDY","EIDPARRY","EIHOTEL","EPL","EASEMYTRIP","ECLERX","ELECON","ELGIEQUIP","EMAMILTD","ENDURANCE","ENGINERSIN","EQUITASBNK","ERIS","ESABINDIA","EXIDEIND","FDC","FEDERALBNK","FACT","FINEORG","FINCABLES","FINPIPE","FSL","FIVESTAR","FORTIS","GAIL","GMMPFAUDLR","GMRINFRA","GALAXYSURF","GRSE","GARFIBRES","GICRE","GILLETTE","GLAND","GLAXO","GLENMARK","GODFRYPHLP","GODREJCP","GODREJIND","GODREJPROP","GRANULES","GRAPHITE","GRASIM","GESHIP","GRINDWELL","GUJALKALI","GAEL","FLUOROCHEM","GUJGASLTD","GMDCLTD","GNFC","GPPL","GSFC","GSPL","HEG","HCLTECH","HDFCAMC","HDFCBANK","HDFCLIFE","HFCL","HAPPSTMNDS","HAPPYFORGE","HATHWAY","HATSUN","HAVELLS","HEROMOTOCO","HINDALCO","HAL","HINDCOPPER","HINDPETRO","HINDUNILVR","HINDWAREAP","HINDZINC","POWERINDIA","HOMEFIRST","HONASA","HONAUT","HUDCO","ICICIBANK","ICICIGI","ICICIPRULI","IDBI","IDFCFIRSTB","IDFC","IIFL","IRB","IRCTC","IRFC","IFCI","IEX","INDIANB","IOLCP","IGL","INDHOTEL","INDIACEM","INDIAMART","INDIANHUME","INDUSINDBK","NAUKRI","INFY","INOXWIND","INTELLECT","INDUS_TOWERS","IPCALAB","JBCHEPHARM","JKCEMENT","JKLAKSHMI","JKPAPER","JMFINANCIL","JSWENERGY","JSWINFRA","JSWSTEEL","JAMNAAUTO","JINDALSAW","JSL","JINDALSTEL","JIOFIN","JUBLFOOD","JUBLINGREA","JUBLPHARMA","JUSTDIAL","JYOTHYLAB","KPRMILL","KEI","KFINTECH","KALYANKJIL","KAJARIACER","KPITTECH","KARURVYSYA","KAYNES","KEC","KNRCON","KPIL","KOTAKBANK","KIMS","LTF","LTTS","LT","LTIM","LATENTVIEW","LAURUSLABS","LXCHEM","LEMONTREE","LICHSGFIN","LICI","LINDE","LUPIN","MRF","MGL","MAHSEAMLES","M_AND_MFIN","M_AND_M","MANAPPURAM","MRPL","MANKIND","MARICO","MARUTI","MASTEK","MFSL","MAXHEALTH","MAZDOCK","MEDANTA","MEDPLUS","METROPOLIS","MOTHERSON","MSUMI","MPHASIS","MCX","MUTHOOTFIN","NATCOPHARM","NBCC","NCC","NHPC","NLCINDIA","NMDC","NSLNISP","NTPC","NH","NATIONALUM","NAVINFLUOR","NAZARA","NESTLEIND","NETWORK18","NAM-INDIA","NUVAMA","OBEROIRLTY","ONGC","OIL","OLECTRA","PAYTM","OFSS","POLICYBZR","PCBL","PFC","PEL","PHOENIXLTD","PIDILITIND","PPLPHARMA","POLYCAB","POWERGRID","PRAJIND","PRESTIGE","PRINCEPIPE","PRSMJOHNSN","PGHH","PGHL","PNB","PNBHOUSING","QUESS","RBLBANK","RECLTD","RHIM","RITES","RADICO","RVNL","RAILTEL","RALLIS","RKFORGE","RCF","RTNINDIA","RAYMOND","REDINGTON","RELIANCE","RBA","ROUTE","SBICARD","SBILIFE","SJVN","SKFINDIA","SRF","SANOFI","SAPPHIRE","SAREGAMA","SCHAEFFLER","SEQUENT","SFL","SHOPERSTOP","SHYAMMETL","SIEMENS","SOBHA","SOLARINDS","SONACOMS","STARHEALTH","SBIN","SAIL","SWSOLAR","SUMICHEM","SUNPHARMA","SUNTV","SUNDARMFIN","SUNDRMFAST","SUPREMEIND","SUZLON","SYNGENE","SYRMA","TTKPRESTIG","TV18BRDCST","TVSMOTOR","TMB","TATACHEM","TATACOMM","TCS","TATACONSUM","TATAELXSI","TATAMOTORS","TATAPOWER","TATASTEEL","TATATECH","TTML","TEAMLEASE","TECHM","THERMAX","TIMKEN","TITAN","TORNTPHARM","TORNTPOWER","TRENT","TRIDENT","TRIVENI","TRITURBINE","TIINDIA","UCOBANK","UNIONBANK","UBL","MCDOWELL-N","VGUARD","DBREALTY","VTL","VARROC","VBL","MANYAVAR","VEDL","VIJAYA","VOLTAS","WELCORP","WELSPUNLTD","WESTLIFE","WHIRLPOOL","WIPRO","YESBANK","ZFCVINDIA","ZOMATO","ZYDUSLIFE","ZYDUSWELL"]
WATCHLIST=NIFTY500
def resolve_ticker(t):
    r=t.upper().strip().replace("M_AND_MFIN","M&MFIN").replace("M_AND_M","M&M").replace("INDUS_TOWERS","INDUS TOWERS")
    ns=re.sub(r'[^A-Z0-9 &-]','',r).replace(" & ","&").strip()
    return ns+".NS" if len(ns)>1 else r+".NS"

def get_morning_picks():
    ist_now = datetime.now(pytz.timezone('Asia/Kolkata'))
    today = str(date.today())
    current_slot = "AM" if ist_now.hour < 13 else "PM"
    if st.session_state.pick_date==today and st.session_state.pick_slot==current_slot and st.session_state.morning_picks:
        return st.session_state.morning_picks
    temp=[]; prog=st.progress(0); total=len(WATCHLIST)
    slot_name = "Morning 9:30 AM" if current_slot=="AM" else "Afternoon 1:30 PM"
    for idx,name in enumerate(WATCHLIST):
        prog.progress((idx+1)/total, text=f"AI {slot_name} Scanning {idx+1}/{total} : {name}")
        t=resolve_ticker(name); df=load_data(t,period="6mo")
        if not df.empty and len(df)>50:
            ai_prob,ai_reason=get_ai_prediction(t)
            if ai_prob<60: continue
            sc,rsns,rsi,adx_v=score_stock(df,ai_prob)
            if sc<85: continue
            if rsi>70 or rsi<45: continue
            live=float(df["Close"].iloc[-1]); profit,tgt,sl,atr=get_smart_target(df,live,sc)
            news_raw, gpt_summary, mode = get_news_with_gpt(t, name)
            temp.append({"name":name,"score":sc,"reasons":rsns,"rsi":rsi,"adx":adx_v,"live":live,"target":tgt,"profit_pct":profit,"sl":sl,"atr_pct":atr,"ticker":t,"ai_prob":ai_prob,"ai_reason":ai_reason,"news_raw":news_raw,"gpt_summary":gpt_summary,"mode":mode})
    prog.empty()
    temp=sorted(temp,key=lambda x:(x["ai_prob"],x["score"]),reverse=True)[:2]
    st.session_state.morning_picks=temp; st.session_state.pick_date=today; st.session_state.pick_slot=current_slot
    save_history(temp)
    return temp

ist_now = datetime.now(pytz.timezone('Asia/Kolkata'))
slot_display = "Morning Session (9:30 AM)" if ist_now.hour < 13 else "Afternoon Session (1:30 PM)"

st.markdown(f"""<div class="header-god"><h1 style="margin:0; color:white; font-size:22px;">🔒 FinTrade Premium GPT NEWS • {slot_display} • {ist_now.strftime('%I:%M %p')}</h1></div>""", unsafe_allow_html=True)

morning_picks=get_morning_picks()

if morning_picks:
    c1,c2=st.columns(2)
    for i,pick in enumerate(morning_picks):
        col=c1 if i==0 else c2
        with col:
            st.markdown(f"""
            <div class="pick-god">
              <h2 style="margin:0; color:white; font-size:24px;">{pick.get('name')} <span class="ai-badge">AI {pick.get('ai_prob',0)}%</span></h2>
              <p style="color:#00D1FF; font-size:20px; font-weight:800;">Rs{round(pick.get('live',0),2)}</p>
              <p style="color:#8892b0; font-size:11px;">{" • ".join(pick.get('reasons',[])[:3])}</p>
              <div class="news-badge">📰 Raw: {pick.get('news_raw','')[:120]}</div>
              <div class="gpt-badge">🤖 {pick.get('mode','')} Summary: {pick.get('gpt_summary','')}</div>
              <div class="target-row">
                <div><p style="margin:0; color:#8892b0; font-size:8px;">TARGET</p><p style="margin:0; color:#00FF88; font-weight:700;">Rs{round(pick.get('target',0),2)} +{pick.get('profit_pct',0)}%</p></div>
                <div><p style="margin:0; color:#8892b0; font-size:8px;">SL</p><p style="margin:0; color:#FF4D6A; font-weight:700;">Rs{round(pick.get('sl',0),2)}</p></div>
              </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.warning("No strong BUY today")

st.caption("Add OPENAI_API_KEY in Secrets for GPT summary, else rule-based summary will show")
