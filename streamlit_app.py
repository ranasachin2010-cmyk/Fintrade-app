import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="V14 PREMIUM", layout="wide")

# PREMIUM UI CSS
st.markdown("""
<style>
.stApp {background: #0a0e1a;}
h1 {background: linear-gradient(90deg, #00D1FF, #7000FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight:900; font-size:42px!important;}
div[data-testid="metric-container"] {background: linear-gradient(135deg, #1a1f35, #12162a); border:1px solid #2a3a5c; border-radius:15px; padding:15px; box-shadow:0 4px 20px rgba(0,209,255,0.15);}
div[data-testid="stDataFrame"] {border-radius:15px; overflow:hidden; border:1px solid #2a3a5c;}
.stButton>button {background: linear-gradient(90deg, #00D1FF, #7000FF); color:white; border:none; border-radius:12px; padding:12px 25px; font-weight:700; font-size:16px; width:100%;}
.stButton>button:hover {transform:scale(1.02); box-shadow:0 5px 25px rgba(0,209,255,0.4);}
.premium-card {background: linear-gradient(135deg, #1a1f35, #12162a); border:1px solid #2a3a5c; border-radius:15px; padding:20px; margin:10px 0; box-shadow:0 4px 20px rgba(0,0,0,0.3);}
.buy-card {border-left:5px solid #00ff88; background: linear-gradient(135deg, #0a2a1a, #12162a);}
.sell-card {border-left:5px solid #ff0040; background: linear-gradient(135deg, #2a0a15, #12162a);}
.hold-card {border-left:5px solid #ffaa00; background: linear-gradient(135deg, #2a2210, #12162a);}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>FinTrade V14 - PREMIUM EDITION 💎</h1>", unsafe_allow_html=True)
st.markdown("<p style=color:#8892b0;font-size:18px>V13.1 INDIAN FIX + BUY SELL HOLD + NIFTY50 SCANNER - PREMIUM UI</p>", unsafe_allow_html=True)

TICKER_MAP = {"ZOMATO":"ETERNAL.NS","PAYTM":"PAYTM.NS","RELIANCE":"RELIANCE.NS","CUPID":"CUPID.NS","GAIL":"GAIL.NS"}
NAME_MAP = {"ETERNAL.NS":"ZOMATO","RELIANCE.NS":"RELIANCE"}

NIFTY50 = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","BHARTIARTL.NS","ITC.NS","SBIN.NS","LT.NS","KOTAKBANK.NS","CUPID.NS","ETERNAL.NS","GAIL.NS","PAYTM.NS"]

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
    exp1 = close.ewm(span=12).mean()
    exp2 = close.ewm(span=26).mean()
    macd = exp1 - exp2
    sig = macd.ewm(span=9).mean()
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
    return final, last_rsi, score, last_ema20, last_ema50

def run_scanner(watch_list, title):
    rows = []
    prog = st.progress(0)
    total = len(watch_list)
    for i, sym in enumerate(watch_list):
        prog.progress((i + 1) / total)
        d = load_data(sym)
        if not d.empty and len(d) > 20:
            sig, rsi_v, sc, e20, e50 = get_signal(d)
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
        st.markdown(f"<div class=premium-card><h3 style=color:#00D1FF>🏆 Best Pick: {best['Stock']} - {best['Signal']} - {best['Profit%']}% Profit</h3></div>", unsafe_allow_html=True)
        csv = df_out.to_csv(index=False)
        st.download_button("📥 Download " + title + " CSV", csv, title + ".csv", "text/csv")

# SIDEBAR PREMIUM
st.sidebar.markdown("<h2 style=color:#00D1FF>💎 PREMIUM V14</h2>", unsafe_allow_html=True)
ticker_input = st.sidebar.text_input("🔍 Stock Name", value="Reliance")
st.sidebar.markdown("<p style=color:#8892b0>100% INDIAN NSE/BSE - No Apple Bug</p>", unsafe_allow_html=True)

ticker = resolve_ticker(ticker_input)
display_name = get_display_name(ticker)

st.markdown(f"<div class=premium-card><p style=color:#8892b0>📡 Fetching: <b style=color:white>{ticker}</b> | 100% NSE Data from Yahoo | LTP Live</p></div>", unsafe_allow_html=True)

df = load_data(ticker)

if df.empty:
    st.error("No Data")
    st.stop()

last_close = float(df["Close"].iloc[-1])
support_level = float(df["Low"].tail(20).min())
resist_level = float(df["High"].tail(20).max())
signal, rsi_val, score, ema20_val, ema50_val = get_signal(df)

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

# PREMIUM BUY SELL HOLD CARD
if signal == "BUY":
    st.markdown(f"<div class='premium-card buy-card'><h2 style=color:#00ff88>🚀 BUY {display_name}</h2><p style=color:white;font-size:20px>LTP ₹{round(last_close,2)} | Target ₹{round(target_level,2)} | <b style=color:#00ff88>{round(profit_pct,1)}% Profit</b></p><p style=color:#8892b0>RSI {round(rsi_val,1)} | Score {score} | SL ₹{round(stoploss_level,2)}</p></div>", unsafe_allow_html=True)
if signal == "HOLD":
    st.markdown(f"<div class='premium-card hold-card'><h2 style=color:#ffaa00>⏸️ HOLD {display_name}</h2><p style=color:white;font-size:20px>LTP ₹{round(last_close,2)} | RSI {round(rsi_val,1)} | Wait for Breakout</p><p style=color:#8892b0>Support ₹{round(support_level,2)} | Resist ₹{round(resist_level,2)}</p></div>", unsafe_allow_html=True)
if signal == "SELL":
    st.markdown(f"<div class='premium-card sell-card'><h2 style=color:#ff0040>🔻 SELL {display_name}</h2><p style=color:white;font-size:20px>LTP ₹{round(last_close,2)} | Down {round(profit_pct,1)}% | SL ₹{round(stoploss_level,2)}</p></div>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("📊 Signal", signal)
col2.metric("💰 LTP", round(last_close,2))
col3.metric("🎯 Target", str(round(target_level,2)) + " (" + str(round(profit_pct,1)) + "%)")
col4.metric("🛑 SL", round(stoploss_level,2))

col5, col6, col7, col8 = st.columns(4)
col5.metric("Support", round(support_level,2))
col6.metric("Resist", round(resist_level,2))
col7.metric("RSI", round(rsi_val,1))
col8.metric("EMA20/50", str(round(ema20_val,2)) + "/" + str(round(ema50_val,2)))

st.markdown("<div class=premium-card><h3 style=color:#00D1FF>📈 Premium Indian Chart - 100% NSE</h3></div>", unsafe_allow_html=True)
st.line_chart(df["Close"])

bse_ticker = ticker.replace(".NS","")
tradingview_url = "https://s.tradingview.com/widgetembed/?symbol=BSE%3A" + bse_ticker + "&interval=D&hidesidetoolbar=0&theme=dark"
st.components.v1.iframe(tradingview_url, height=400)

st.divider()
st.markdown("<h2 style=color:#00D1FF>🔍 PREMIUM SCANNER - NIFTY50</h2>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    if st.button("⚡ Quick Scanner 10"):
        run_scanner(NIFTY50[:10], "Quick Scanner")
with c2:
    if st.button("🚀 NIFTY 50 FULL Scanner"):
        run_scanner(NIFTY50, "NIFTY50 Scanner")

st.markdown("<div class=premium-card><p style=color:#8892b0;text-align:center>💎 V14 PREMIUM EDITION - 100% INDIAN FIXED - BUY SELL HOLD + SCANNER</p></div>", unsafe_allow_html=True)
