import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="V13.3 SCANNER", layout="wide")
st.markdown("<h1 style=color:#00D1FF>FinTrade V13.3 - INDIAN + BUY SELL HOLD + SCANNER</h1>", unsafe_allow_html=True)
st.write("V13.1 Fix: BSE + Yahoo NSE - Apple Bug Fixed - 100% Indian")

TICKER_MAP = {"ZOMATO":"ETERNAL.NS","PAYTM":"PAYTM.NS","RELIANCE":"RELIANCE.NS","CUPID":"CUPID.NS","GAIL":"GAIL.NS","TCS":"TCS.NS","INFY":"INFY.NS"}
NAME_MAP = {"ETERNAL.NS":"ZOMATO","RELIANCE.NS":"RELIANCE"}

NIFTY50 = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","BHARTIARTL.NS","ITC.NS","SBIN.NS","LT.NS","KOTAKBANK.NS","AXISBANK.NS","BAJFINANCE.NS","ASIANPAINT.NS","MARUTI.NS","TITAN.NS","SUNPHARMA.NS","ULTRACEMCO.NS","NTPC.NS","POWERGRID.NS","ONGC.NS","WIPRO.NS","HCLTECH.NS","M&M.NS","ADANIENT.NS","GAIL.NS","CUPID.NS","ETERNAL.NS","PAYTM.NS"]

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
    last_macd = float(macd.iloc[-1])
    last_sig = float(sig.iloc[-1])
    score = 0
    if last_ema20 > last_ema50:
        score = score + 1
    if last_ema20 < last_ema50:
        score = score - 1
    if last_close > last_ema20:
        score = score + 1
    if last_close < last_ema20:
        score = score - 1
    if last_rsi > 60:
        score = score + 1
    if last_rsi < 40:
        score = score - 1
    if last_macd > last_sig:
        score = score + 1
    if last_macd < last_sig:
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
            rows.append({"Stock":disp,"LTP":round(lc,2),"Signal":sig,"Target":round(tg,2),"Profit%":round(prof,1),"SL":round(sl,2),"RSI":round(rsi_v,1),"Score":sc})
    df_out = pd.DataFrame(rows)
    if not df_out.empty:
        df_out = df_out.sort_values(by="Profit%", ascending=False)
        st.subheader(title)
        st.dataframe(df_out, use_container_width=True)
        best = df_out.iloc[0]
        st.success("Best: " + str(best["Stock"]) + " " + str(best["Signal"]) + " " + str(best["Profit%"]) + "%")
        buys = df_out[df_out["Signal"]=="BUY"]
        if not buys.empty:
            st.info("BUY Count: " + str(len(buys)) + " | Top: " + ", ".join(buys.head(3)["Stock"].tolist()))
        csv = df_out.to_csv(index=False)
        st.download_button("Download " + title + " CSV", csv, title + ".csv", "text/csv")
    else:
        st.error("No Data")

st.sidebar.header("V13.3 SCANNER")
ticker_input = st.sidebar.text_input("Stock", value="Reliance")

ticker = resolve_ticker(ticker_input)
display_name = get_display_name(ticker)

st.write("Fetching: " + ticker + " - 100% NSE Yahoo")

df = load_data(ticker)

if df.empty:
    st.error("No Data")
    st.stop()

st.write("Rows: " + str(len(df)))

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

st.markdown("### " + ticker + " - LTP " + str(round(last_close,2)) + " - 100% NSE")
st.write("BSE:" + display_name + " - NSE/BSE same price")

if signal == "BUY":
    st.success("BUY " + display_name + " | Profit " + str(round(profit_pct,1)) + "%")
if signal == "HOLD":
    st.warning("HOLD " + display_name + " | RSI " + str(round(rsi_val,1)))
if signal == "SELL":
    st.error("SELL " + display_name + " | Down " + str(round(profit_pct,1)) + "%")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Signal", signal)
col2.metric("LTP", round(last_close,2))
col3.metric("Target", str(round(target_level,2)) + " (" + str(round(profit_pct,1)) + "%)")
col4.metric("SL", round(stoploss_level,2))

st.line_chart(df["Close"])

bse_ticker = ticker.replace(".NS","")
tradingview_url = "https://s.tradingview.com/widgetembed/?symbol=BSE%3A" + bse_ticker + "&interval=D&hidesidetoolbar=0"
st.components.v1.iframe(tradingview_url, height=350)

st.divider()
st.subheader("SCANNER - V13.3 NEW")

c1, c2 = st.columns(2)
with c1:
    if st.button("Run Quick Scanner 10 Stocks"):
        run_scanner(NIFTY50[:10], "Quick Scanner")
with c2:
    if st.button("Run NIFTY 50 FULL Scanner"):
        run_scanner(NIFTY50, "NIFTY50 Scanner")

st.write("V13.3 SCANNER OK - INDIAN FIXED")
