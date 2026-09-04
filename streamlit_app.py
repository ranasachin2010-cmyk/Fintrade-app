import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="V13.2 BUY SELL HOLD", layout="wide")
st.markdown("<h1 style=color:#00D1FF>FinTrade V13.2 - 100% INDIAN + BUY SELL HOLD</h1>", unsafe_allow_html=True)
st.write("V13.1 Fix: TradingView NSE block karta hai Apple dikhata hai, isliye BSE + Yahoo NSE Data")

TICKER_MAP = {"ZOMATO":"ETERNAL.NS","PAYTM":"PAYTM.NS","RELIANCE":"RELIANCE.NS","CUPID":"CUPID.NS","GAIL":"GAIL.NS","TCS":"TCS.NS"}
NAME_MAP = {"ETERNAL.NS":"ZOMATO","RELIANCE.NS":"RELIANCE"}

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
    return final, last_rsi, score, last_ema20, last_ema50

st.sidebar.header("Settings")
ticker_input = st.sidebar.text_input("Stock", value="Reliance")
st.sidebar.write("100% INDIAN NSE/BSE FIXED")

ticker = resolve_ticker(ticker_input)
display_name = get_display_name(ticker)

st.write("Fetching: " + ticker + " - 100% NSE Data from Yahoo")

df = load_data(ticker)

if df.empty:
    st.error("No Data - Internet Check")
    st.stop()

st.write("Rows: " + str(len(df)))

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

# BUY SELL HOLD FEATURE
st.markdown("### " + ticker + " - LTP " + str(round(last_close,2)) + " - 100% NSE Data from Yahoo")
st.write("TradingView (BSE Free Data - BSE:" + display_name + ") - NSE/BSE price same hota hai")

if signal == "BUY":
    st.success("BUY " + display_name + " | Profit " + str(round(profit_pct,1)) + "% | Target " + str(round(target_level,2)))
if signal == "HOLD":
    st.warning("HOLD " + display_name + " | RSI " + str(round(rsi_val,1)) + " | Wait for BUY/SELL")
if signal == "SELL":
    st.error("SELL " + display_name + " | Down " + str(round(profit_pct,1)) + "% | SL " + str(round(stoploss_level,2)))

col1, col2, col3, col4 = st.columns(4)
col1.metric("Signal", signal)
col2.metric("LTP", round(last_close,2))
col3.metric("Target", str(round(target_level,2)) + " (" + str(round(profit_pct,1)) + "%)")
col4.metric("SL", round(stoploss_level,2))

col5, col6, col7, col8 = st.columns(4)
col5.metric("Support", round(support_level,2))
col6.metric("Resist", round(resist_level,2))
col7.metric("RSI", round(rsi_val,1))
col8.metric("Score", score)

st.write("Indian Chart - LTP " + str(round(last_close,2)))
st.line_chart(df["Close"])

# BSE TradingView - No Apple Bug
bse_ticker = ticker.replace(".NS","")
tradingview_url = "https://s.tradingview.com/widgetembed/?symbol=BSE%3A" + bse_ticker + "&interval=D&hidesidetoolbar=0"
st.components.v1.iframe(tradingview_url, height=400)

st.write("V13.2 BUY SELL HOLD OK - 100% INDIAN FIXED")
