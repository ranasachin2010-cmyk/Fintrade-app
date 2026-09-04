import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="V21 FINAL", layout="wide")
st.markdown("<h1 style=color:#00D1FF>FinTrade V21 - FINAL PRO</h1>", unsafe_allow_html=True)
st.write("V20.2 success - Now final")

TICKER_MAP = {"ZOMATO":"ETERNAL.NS","PAYTM":"PAYTM.NS","ZOM":"ETERNAL.NS","RELIANCE":"RELIANCE.NS","TCS":"TCS.NS","INFY":"INFY.NS","SBIN":"SBIN.NS"}
NAME_MAP = {"ETERNAL.NS":"ZOMATO","PAYTM.NS":"PAYTM"}

def load_data(tick):
    t = yf.Ticker(tick)
    df = t.history(period="3mo", interval="1d", auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

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
    return final, last_rsi, score, last_ema20, last_ema50

st.sidebar.header("Settings")
ticker_input = st.sidebar.text_input("Stock", value="Zomato")
ticker = resolve_ticker(ticker_input)
display_name = get_display_name(ticker)

df = load_data(ticker)
if df.empty:
    st.error("No data")
    st.stop()

last_close = float(df["Close"].iloc[-1])
support_level = float(df["Low"].tail(20).min())
resist_level = float(df["High"].tail(20).max())
signal, rsi_val, score, ema20_val, ema50_val = get_signal(df)

target_level = resist_level
stoploss_level = support_level
if signal == "BUY":
    diff = last_close - support_level
    target_level = last_close + diff * 1.5
    stoploss_level = support_level
if signal == "SELL":
    target_level = support_level
    stoploss_level = resist_level

if signal == "BUY": st.success("BUY " + display_name)
if signal == "HOLD": st.warning("HOLD " + display_name)
if signal == "SELL": st.error("SELL " + display_name)

st.metric("Ticker", ticker)
st.metric("LTP", round(last_close,2))
st.metric("Target", round(target_level,2))
st.metric("SL", round(stoploss_level,2))
st.metric("Support", round(support_level,2))
st.metric("Resist", round(resist_level,2))
st.metric("RSI", round(rsi_val,1))
st.metric("EMA20", round(ema20_val,2))
st.metric("EMA50", round(ema50_val,2))
st.metric("Score", score)
st.metric("Rows", len(df))

st.write("Price Chart")
st.line_chart(df["Close"])

st.write("EMA Chart")
ema_df = pd.DataFrame()
ema_df["Close"] = df["Close"]
ema_df["EMA20"] = df["Close"].ewm(span=20).mean()
ema_df["EMA50"] = df["Close"].ewm(span=50).mean()
st.line_chart(ema_df)

st.markdown("---")
st.subheader("One Click Screener")
if st.button("Run Screener"):
