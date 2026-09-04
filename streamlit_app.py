import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="V27 MEGA ALL", layout="wide")
st.markdown("<h1 style=color:#00D1FF>FinTrade V27 - MEGA ULTIMATE</h1>", unsafe_allow_html=True)
st.write("V1 to V26 All Features - BUY CUPID 25.4% Logic Locked")

# V1 - V6 Maps
TICKER_MAP = {"ZOMATO":"ETERNAL.NS","PAYTM":"PAYTM.NS","ZOM":"ETERNAL.NS","CUPID":"CUPID.NS","RELIANCE":"RELIANCE.NS","TCS":"TCS.NS","INFY":"INFY.NS"}
NAME_MAP = {"ETERNAL.NS":"ZOMATO","PAYTM.NS":"PAYTM","CUPID.NS":"CUPID"}

def load_data(tick):
    try:
        t = yf.Ticker(tick)
        df = t.history(period="1mo", interval="1d", auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        return df
    except:
        return pd.DataFrame()

def resolve_ticker(u):
    uu = u.upper().strip()
    if uu in TICKER_MAP: return TICKER_MAP[uu]
    if ".NS" in uu: return uu
    return uu + ".NS"

def get_display_name(tick):
    if tick in NAME_MAP: return NAME_MAP[tick]
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
    den = 1 + rs
    div = 100 / den
    rsi = 100 - div
    exp1 = close.ewm(span=12).mean()
    exp2 = close.ewm(span=26).mean()
    macd = exp1 - exp2
    sig = macd.ewm(span=9).mean()
    last_rsi = float(rsi.iloc[-1])
    last_close = float(close.iloc[-1])
    last_ema20 = float(ema20.iloc[-1])
    last_ema50 = float(ema50.iloc[-1])
    last_macd = float(macd.iloc[-1])
    last_sig = float(sig.iloc[-1])
    score = 0
    if last_ema20 > last_ema50: score = score + 1
    if last_ema20 < last_ema50: score = score - 1
    if last_close > last_ema20: score = score + 1
    if last_close < last_ema20: score = score - 1
    if last_rsi > 60: score = score + 1
    if last_rsi < 40: score = score - 1
    if last_macd > last_sig: score = score + 1
    if last_macd < last_sig: score = score - 1
    final = "HOLD"
    if score >= 2: final = "BUY"
    if score <= -2: final = "SELL"
    return final, last_rsi, score, last_ema20, last_ema50, last_macd, last_sig

def run_screener():
    watch = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","BHARTIARTL.NS","ITC.NS","SBIN.NS","CUPID.NS","ETERNAL.NS","PAYTM.NS"]
    rows = []
    for sym in watch:
        d = load_data(sym)
        if not d.empty and len(d) > 20:
            sig, rsi_v, sc, e20, e50, m, s = get_signal(d)
            lc = float(d["Close"].iloc[-1])
            sp = float(d["Low"].tail(20).min())
            rs_ = float(d["High"].tail(20).max())
            tg = rs_; sl = sp
            if sig == "BUY": tg = lc + (lc - sp) * 1.5; sl = sp
            if sig == "SELL": tg = sp; sl = rs_
            prof = ((tg - lc) / lc * 100) if sig!= "SELL" else ((lc - tg) / lc * 100)
            disp = get_display_name(sym)
            rows.append({"Stock":disp,"LTP":round(lc,2),"Signal":sig,"Target":round(tg,2),"Profit%":round(prof,1),"SL":round(sl,2),"Support":round(sp,2),"Resist":round(rs_,2),"Score":sc,"RSI":round(rsi_v,1),"EMA20":round(e20,2),"EMA50":round(e50,2)})
    df_out = pd.DataFrame(rows)
    if not df_out.empty:
        df_out = df_out.sort_values(by="Profit%", ascending=False)
        st.dataframe(df_out, use_container_width=True)
        csv = df_out.to_csv(index=False)
        st.download_button("Download V27 MEGA CSV", csv, "screener_v27.csv", "text/csv")
        best = df_out.iloc[0]
        st.success("Best Pick: " + str(best["Stock"]) + " " + str(best["Signal"]) + " Profit " + str(best["Profit%"]) + "% | Target " + str(best["Target"]))

# UI
st.sidebar.header("Settings - V1 to V27")
ticker_input = st.sidebar.text_input("Stock Name", value="Cupid")
timeframe = st.sidebar.selectbox("Timeframe", ["1mo","3mo","6mo","1y"], index=0)
st.sidebar.write("V27 Includes All")

ticker = resolve_ticker(ticker_input)
display_name = get_display_name(ticker)

st.write("Fetching: " + ticker + " | TF: " + timeframe)

df = load_data(ticker)

st.write("Rows:")
st.write(len(df) if not df.empty else 0)

if df.empty:
    st.error("No data - Internet check")
    st.stop()

last_close = float(df["Close"].iloc[-1])
support_level = float(df["Low"].tail(20).min())
resist_level = float(df["High"].tail(20).max())
signal, rsi_val, score, ema20_val, ema50_val, macd_val, sig_val = get_signal(df)

target_level = resist_level; stoploss_level = support_level
if signal == "BUY": diff = last_close - support_level; target_level = last_close + diff * 1.5; stoploss_level = support_level
if signal == "SELL": target_level = support_level; stoploss_level = resist_level

profit_pct = ((target_level - last_close) / last_close * 100) if signal!= "SELL" else ((last_close - target_level) / last_close * 100)

if signal == "BUY": st.success("BUY " + display_name + " | Profit " + str(round(profit_pct,1)) + "%")
if signal == "HOLD": st.warning("HOLD " + display_name + " | RSI " + str(round(rsi_val,1)))
if signal == "SELL": st.error("SELL " + display_name + " | Down " + str(round(profit_pct,1)) + "%")

# V1 to V26 All Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Ticker", ticker)
col2.metric("LTP", round(last_close,2))
col3.metric("Target", str(round(target_level,2)) + " (" + str(round(profit_pct,1)) + "%)")
col4.metric("SL", round(stoploss_level,2))

col5, col6, col7, col8 = st.columns(4)
col5.metric("Support", round(support_level,2))
col6.metric("Resist", round(resist_level,2))
col7.metric("RSI", round(rsi_val,1))
col8.metric("Score", score)

col9, col10, col11 = st.columns(3)
col9.metric("EMA20", round(ema20_val,2))
col10.metric("EMA50", round(ema50_val,2))
col11.metric("MACD", round(macd_val,2))

st.write("Price Chart - V27 Light")
st.line_chart(df["Close"])

st.subheader("V27 MEGA Screener - V1 to V26 All Features")
if st.button("Run MEGA Screener - Profit Sort + Best Pick"): run_screener()

st.write("V27 MEGA ULTIMATE OK - All Features from V1 to V26 Locked")
