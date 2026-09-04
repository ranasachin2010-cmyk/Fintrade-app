import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="V23 UNIVERSAL", layout="wide")

st.markdown("""
<style>
.stApp {background: #0a0e1a;}
.top-pin {background: linear-gradient(90deg, #1a1f35, #2a3a5c); border:2px solid #00D1FF; border-radius:15px; padding:20px; margin:15px 0;}
.stTextInput>div>div>input {background: #1a1f35; color:white; font-size:22px; font-weight:900; border:2px solid #00D1FF; border-radius:12px; height:60px;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>FinTrade V23 - KOI BHI STOCK MILEGA 💎</h1>", unsafe_allow_html=True)
st.success("IOCL, CUPID, GAIL, ZOMATO, SUZLON, YESBANK - Koi bhi likho - Aap pr milega + Upar pin hoga!")

# 150+ SMART MAP - Koi bhi stock ka asli Yahoo naam
SMART_MAP = {
"IOCL":"IOC.NS","IOC":"IOC.NS","RELIANCE":"RELIANCE.NS","TCS":"TCS.NS","INFY":"INFY.NS","INFOSYS":"INFY.NS",
"HDFCBANK":"HDFCBANK.NS","HDFC BANK":"HDFCBANK.NS","ICICIBANK":"ICICIBANK.NS","ICICI":"ICICIBANK.NS",
"SBIN":"SBIN.NS","SBI":"SBIN.NS","ITC":"ITC.NS","LT":"LT.NS","LARSEN":"LT.NS",
"CUPID":"CUPID.NS","GAIL":"GAIL.NS","ONGC":"ONGC.NS","NTPC":"NTPC.NS","COALINDIA":"COALINDIA.NS","COAL INDIA":"COALINDIA.NS",
"BHEL":"BHEL.NS","BEL":"BEL.NS","HAL":"HAL.NS","BDL":"BDL.NS","MAZDOCK":"MAZDOCK.NS","MAZAGON":"MAZDOCK.NS",
"RVNL":"RVNL.NS","IRFC":"IRFC.NS","IRCTC":"IRCTC.NS","SUZLON":"SUZLON.NS","YESBANK":"YESBANK.NS","YES BANK":"YESBANK.NS",
"IDEA":"IDEA.NS","VODAFONE":"IDEA.NS","VI":"IDEA.NS","ZOMATO":"ETERNAL.NS","ETERNAL":"ETERNAL.NS",
"PAYTM":"PAYTM.NS","TATAMOTORS":"TATAMOTORS.NS","TATA MOTORS":"TATAMOTORS.NS","TATAPOWER":"TATAPOWER.NS","TATA POWER":"TATAPOWER.NS",
"ADANIENT":"ADANIENT.NS","ADANI ENT":"ADANIENT.NS","ADANIPORTS":"ADANIPORTS.NS","ADANI PORTS":"ADANIPORTS.NS",
"BAJFINANCE":"BAJFINANCE.NS","BAJAJ FINANCE":"BAJFINANCE.NS","MARUTI":"MARUTI.NS","TITAN":"TITAN.NS","SUNPHARMA":"SUNPHARMA.NS",
"VEDL":"VEDL.NS","VEDANTA":"VEDL.NS","SAIL":"SAIL.NS","TATASTEEL":"TATASTEEL.NS","TATA STEEL":"TATASTEEL.NS",
"JSWSTEEL":"JSWSTEEL.NS","JSW STEEL":"JSWSTEEL.NS","DLF":"DLF.NS","GODREJPROP":"GODREJPROP.NS","POLYCAB":"POLYCAB.NS",
"DMART":"DMART.NS","TRENT":"TRENT.NS","INDIGO":"INDIGO.NS","HINDALCO":"HINDALCO.NS","POWERGRID":"POWERGRID.NS",
"WIPRO":"WIPRO.NS","AXISBANK":"AXISBANK.NS","AXIS BANK":"AXISBANK.NS","KOTAKBANK":"KOTAKBANK.NS","KOTAK BANK":"KOTAKBANK.NS",
"BANKBARODA":"BANKBARODA.NS","BOB":"BANKBARODA.NS","PNB":"PNB.NS","HDFCLIFE":"HDFCLIFE.NS","SBILIFE":"SBILIFE.NS",
"BPCL":"BPCL.NS","HINDPETRO":"HINDPETRO.NS","HPCL":"HINDPETRO.NS","M&M":"M&M.NS","M AND M":"M&M.NS","EICHERMOT":"EICHERMOT.NS",
"BAJAJ-AUTO":"BAJAJ-AUTO.NS","BAJAJ AUTO":"BAJAJ-AUTO.NS","HEROMOTOCO":"HEROMOTOCO.NS","HERO":"HEROMOTOCO.NS","TVSMOTOR":"TVSMOTOR.NS","TVS":"TVSMOTOR.NS"
}

def load_data(tick):
    try:
        t = yf.Ticker(tick)
        df = t.history(period="1mo", interval="1d", auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return pd.DataFrame()

def resolve_ticker(user_text):
    txt = user_text.upper().strip()
    # 1. Direct map
    if txt in SMART_MAP:
        return SMART_MAP[txt], f"Map: {txt} -> {SMART_MAP[txt]}"
    # 2. Try.NS
    for suffix in [".NS",".BO"]:
        try_ticker = txt.replace(" ","").replace("-","") + suffix if suffix not in txt else txt
        # Handle if user already added.NS/.BO
        if ".NS" in txt or ".BO" in txt:
            try_ticker = txt
        df_test = load_data(try_ticker)
        if not df_test.empty:
            return try_ticker, f"Found: {try_ticker}"
    # 3. Fallback.NS
    return txt + ".NS", f"Trying: {txt}.NS"

# === UNIVERSAL SEARCH BAR ===
st.markdown("### 🔍 Koi bhi Stock Likho - Upar Pin Hoga")
user_input = st.text_input("", value="IOCL", placeholder="IOCL, RELIANCE, CUPID, GAIL, SUZLON, ZOMATO, koi bhi...", label_visibility="collapsed")

ticker_in, status = resolve_ticker(user_input)

col1, col2 = st.columns([3,1])
with col1:
    st.write(f"**{status}**")
with col2:
    st.write(f"Searching: {user_input.upper()}")

df = load_data(ticker_in)
# Agar NSE fail to BSE try
if df.empty:
    bse_ticker = ticker_in.replace(".NS",".BO")
    df = load_data(bse_ticker)
    if not df.empty:
        ticker_in = bse_ticker
        st.warning(f"NSE pe nahi mila, BSE pe mila: {ticker_in}")

if df.empty:
    st.error(f"❌ {user_input.upper()} ({ticker_in}) ka data Yahoo pe nahi mila. Sahi naam likho: jaise IOCL, IOC, RELIANCE, TCS, CUPID")
    st.info("Tip: NSE ka sahi symbol likho - jaise TATA MOTORS ke liye TATAMOTORS, YES BANK ke liye YESBANK")
    st.stop()

last = float(df["Close"].iloc[-1])
sup = float(df["Low"].tail(20).min())
res = float(df["High"].tail(20).max())
tgt = last + (last-sup)*1.5
profit = (tgt-last)/last*100

# Signal
close = df["Close"]
ema20 = close.ewm(span=20).mean()
ema50 = close.ewm(span=50).mean()
sig = "HOLD"
if ema20.iloc[-1] > ema50.iloc[-1] and close.iloc[-1] > ema20.iloc[-1]: sig="BUY"
elif ema20.iloc[-1] < ema50.iloc[-1]: sig="SELL"

# === TOP PIN - Koi bhi stock search karoge to yaha upar show hoga ===
st.markdown(f"""
<div class="top-pin">
<h2 style="color:#00D1FF; margin:0;">📈 {user_input.upper()} ({ticker_in}) - LTP ₹{round(last,2)} - {sig} - {round(profit,1)}%</h2>
<p style="color:white; margin:5px 0;">Target ₹{round(tgt,2)} | SL ₹{round(sup,2)} | Support ₹{round(sup,2)} | Resistance ₹{round(res,2)}</p>
<p style="color:#00ff88;">✅ Aap pr mil gaya - Koi bhi stock search karo to yaha upar ayega!</p>
</div>
""", unsafe_allow_html=True)

# Chart
fig = go.Figure(data=[go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"])])
fig.update_layout(template="plotly_dark", height=500)
st.plotly_chart(fig, use_container_width=True)

bse_sym = ticker_in.replace(".NS","").replace(".BO","")
st.components.v1.iframe(f"https://s.tradingview.com/widgetembed/?symbol=BSE%3A{bse_sym}&interval=D&theme=dark", height=400)

st.success(f"✅ V23 - {user_input.upper()} aap pr mil gaya! Ab koi bhi stock likho - IOCL, CUPID, GAIL, PAYTM sab upar pin hoga!")
