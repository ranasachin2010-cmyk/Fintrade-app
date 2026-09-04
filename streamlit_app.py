import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="V15.1 FIXED", layout="wide")

st.markdown("""
<style>
.stApp {background: #0a0e1a;}
h1 {background: linear-gradient(90deg, #00D1FF, #7000FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight:900; font-size:42px!important;}
div[data-testid="metric-container"] {background: linear-gradient(135deg, #1a1f35, #12162a); border:1px solid #2a3a5c; border-radius:15px; padding:15px;}
.stButton>button {background: linear-gradient(90deg, #00D1FF, #7000FF); color:white; border:none; border-radius:12px; padding:12px 25px; font-weight:700; width:100%;}
.premium-card {background: linear-gradient(135deg, #1a1f35, #12162a); border:1px solid #2a3a5c; border-radius:15px; padding:20px; margin:10px 0;}
.buy-card {border-left:5px solid #00ff88;}
.hold-card {border-left:5px solid #ffaa00;}
.sell-card {border-left:5px solid #ff0040;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>FinTrade V15.1 - FIXED NIFTY500 💎</h1>", unsafe_allow_html=True)

TICKER_MAP = {
"ZOMATO":"ETERNAL.NS",
"PAYTM":"PAYTM.NS",
"RELIANCE":"RELIANCE.NS",
"CUPID":"CUPID.NS",
"GAIL":"GAIL.NS"
}
NAME_MAP = {
"ETERNAL.NS":"ZOMATO",
"RELIANCE.NS":"RELIANCE"
}

# FIXED - Har stock alag line pe - WhatsApp kabhi nahi todega
NIFTY50 = [
"RELIANCE.NS",
"TCS.NS",
"INFY.NS",
"HDFCBANK.NS",
"ICICIBANK.NS",
"BHARTIARTL.NS",
"ITC.NS",
"SBIN.NS",
"LT.NS",
"KOTAKBANK.NS",
"AXISBANK.NS",
"BAJFINANCE.NS",
"MARUTI.NS",
"TITAN.NS",
"SUNPHARMA.NS",
"NTPC.NS",
"ONGC.NS",
"WIPRO.NS",
"GAIL.NS",
"CUPID.NS",
"ETERNAL.NS",
"PAYTM.NS"
]

NIFTY100 = [
"RELIANCE.NS",
"TCS.NS",
"INFY.NS",
"HDFCBANK.NS",
"ICICIBANK.NS",
"BHARTIARTL.NS",
"ITC.NS",
"SBIN.NS",
"LT.NS",
"KOTAKBANK.NS",
"AXISBANK.NS",
"BAJFINANCE.NS",
"MARUTI.NS",
"TITAN.NS",
"SUNPHARMA.NS",
"NTPC.NS",
"ONGC.NS",
"WIPRO.NS",
"GAIL.NS",
"CUPID.NS",
"ETERNAL.NS",
"PAYTM.NS",
"INDUSINDBK.NS",
"BANKBARODA.NS",
"PNB.NS",
"DLF.NS",
"GODREJPROP.NS",
"IRCTC.NS",
"TATAMOTORS.NS",
"JSWSTEEL.NS",
"TATASTEEL.NS",
"ADANIENT.NS",
"ADANIPORTS.NS"
]

NIFTY500 = [
"RELIANCE.NS",
"TCS.NS",
"INFY.NS",
"HDFCBANK.NS",
"ICICIBANK.NS",
"BHARTIARTL.NS",
"ITC.NS",
"SBIN.NS",
"LT.NS",
"KOTAKBANK.NS",
"CUPID.NS",
"GAIL.NS",
"ETERNAL.NS",
"PAYTM.NS",
"ABB.NS",
"AARTIIND.NS",
"ABCAPITAL.NS",
"ADANIGREEN.NS",
"ADANIPOWER.NS",
"ALKEM.NS",
"APOLLOHOSP.NS",
"ASHOKLEY.NS",
"ASTRAL.NS",
"AUBANK.NS",
"BATAINDIA.NS",
"BEL.NS",
"BHEL.NS",
"CAMS.NS",
"CDSL.NS",
"CESC.NS",
"CHOLAFIN.NS",
"COFORGE.NS",
"CONCOR.NS",
"CUMMINSIND.NS",
"DMART.NS",
"HAL.NS",
"HDFCAMC.NS",
"INDIGO.NS",
"IOC.NS",
"IRFC.NS",
"JINDALSTEL.NS",
"JSWENERGY.NS",
"LTIM.NS",
"MOTHERSON.NS",
"NHPC.NS",
"NMDC.NS",
"PAGEIND.NS",
"PERSISTENT.NS",
"PETRONET.NS",
"PFC.NS",
"POWERGRID.NS",
"RECLTD.NS",
"SAIL.NS",
"SRF.NS",
"TATAPOWER.NS",
"TRENT.NS",
"TVSMOTOR.NS",
"VEDL.NS",
"VOLTAS.NS",
"WIPRO.NS",
"ZEEL.NS"
]

def load_data(tick):
    try:
        t = yf.Ticker(tick)
        df = t.history(period="1mo", interval="1d", auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return pd.DataFrame()

def resolve_ticker(u):
    uu = u.upper().strip()
    if uu in TICKER_MAP:
        return TICKER_MAP[uu]
    if ".NS" in uu:
        return uu
    return uu + ".NS"

def get_display_name(tick):
    if tick in NAME_MAP:
        return NAME_MAP[tick]
    return tick.replace(".NS","")

def get_signal(df):
    close = df["Close"]
    ema20 = close.ewm(span=20).mean()
    ema50 = close.ewm(span=50).mean()
    delta = close.diff()
    up = delta.clip(lower=0)
    down = delta.clip(upper=0)
    down = down * -1
    gain = up.rolling(14).mean()
    loss = down.rolling(14).mean()
    loss = loss.replace(0, 0.001)
    rs = gain / loss
    rsi = 100 - 100 / (1 + rs)
    last_rsi = float(rsi.iloc[-1])
    last_close = float(close.iloc[-1])
    last_ema20 = float(ema20.iloc[-1])
    last_ema50 = float(ema50.iloc[-1])
    score = 0
    if last_ema20 > last_ema50:
        score = score + 1
    else:
        score = score - 1
    if last_close > last_ema20:
        score = score + 1
    else:
        score = score - 1
    if last_rsi > 60:
        score = score + 1
    if last_rsi < 40:
        score = score - 1
    final = "HOLD"
    if score >= 2:
        final = "BUY"
    if score <= -2:
        final = "SELL"
    return final, last_rsi, score

def run_scanner(watch_list, title):
    rows = []
    prog = st.progress(0)
    total = len(watch_list)
    for i, sym in enumerate(watch_list):
        prog.progress((i + 1) / total)
        d = load_data(sym)
        if not d.empty and len(d) > 20:
            sig, rsi_v, sc = get_signal(d)
            lc = float(d["Close"].iloc[-1])
            sp = float(d["Low"].tail(20).min())
            rs_ = float(d["High"].tail(20).max())
            tg = rs_
            sl = sp
            if sig == "BUY":
                tg = lc + (lc - sp) * 1.5
                sl = sp
            if sig == "SELL":
                tg = sp
                sl = rs_
            prof = 0
            if sig!= "SELL":
                prof = (tg - lc) / lc * 100
            else:
                prof = (lc - tg) / lc * 100
            disp = get_display_name(sym)
            rows.append({"Stock":disp,"LTP":round(lc,2),"Signal":sig,"Target":round(tg,2),"Profit%":round(prof,1),"SL":round(sl,2),"RSI":round(rsi_v,1)})
    df_out = pd.DataFrame(rows)
    if not df_out.empty:
        df_out = df_out.sort_values(by="Profit%", ascending=False)
        st.dataframe(df_out, use_container_width=True)
        best = df_out.iloc[0]
        st.success(f"Best: {best['Stock']} {best['Signal']} {best['Profit%']}%")
        csv = df_out.to_csv(index=False)
        st.download_button("Download CSV", csv, title + ".csv", "text/csv")

st.sidebar.markdown("<h2 style=color:#00D1FF>💎 V15.1 FIXED</h2>", unsafe_allow_html=True)
ticker_input = st.sidebar.text_input("Stock", value="Reliance")

ticker = resolve_ticker(ticker_input)
display_name = get_display_name(ticker)

df = load_data(ticker)
if df.empty:
    st.error("No Data")
    st.stop()

last_close = float(df["Close"].iloc[-1])
support_level = float(df["Low"].tail(20).min())
resist_level = float(df["High"].tail(20).max())
signal, rsi_val, score = get_signal(df)

target_level = resist_level
stoploss_level = support_level
if signal == "BUY":
    target_level = last_close + (last_close - support_level) * 1.5
    stoploss_level = support_level
if signal == "SELL":
    target_level = support_level
    stoploss_level = resist_level

profit_pct = 0
if signal!= "SELL":
    profit_pct = (target_level - last_close) / last_close * 100
else:
    profit_pct = (last_close - target_level) / last_close * 100

if signal == "BUY":
    st.markdown(f"<div class='premium-card buy-card'><h2 style=color:#00ff88>BUY {display_name} {round(profit_pct,1)}%</h2></div>", unsafe_allow_html=True)
if signal == "HOLD":
    st.markdown(f"<div class='premium-card hold-card'><h2 style=color:#ffaa00>HOLD {display_name}</h2></div>", unsafe_allow_html=True)
if signal == "SELL":
    st.markdown(f"<div class='premium-card sell-card'><h2 style=color:#ff0040>SELL {display_name}</h2></div>", unsafe_allow_html=True)

st.metric("LTP", round(last_close,2))
st.metric("Target", str(round(target_level,2)) + f" ({round(profit_pct,1)}%)")
st.line_chart(df["Close"])

c1, c2, c3 = st.columns(3)
with c1:
    if st.button("NIFTY 50"):
        run_scanner(NIFTY50, "NIFTY50")
with c2:
    if st.button("NIFTY 100"):
        run_scanner(NIFTY100, "NIFTY100")
with c3:
    if st.button("NIFTY 500"):
        run_scanner(NIFTY500, "NIFTY500")

st.write("V15.1 FIXED OK - No unterminated string error")
