import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="V24 ULTIMATE", layout="wide")
st.markdown("<h1 style=color:#00D1FF>FinTrade V24 - ULTIMATE</h1>", unsafe_allow_html=True)
st.write("V23 BUY CUPID 25.4% Success - Now V24 Ultimate")

TICKER_MAP = {"ZOMATO":"ETERNAL.NS","PAYTM":"PAYTM.NS","ZOM":"ETERNAL.NS","CUPID":"CUPID.NS"}
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
    return final, last_rsi, score

def run_screener():
    watch = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","BHARTIARTL.NS","ITC.NS","CUPID.NS","ETERNAL.NS","PAYTM.NS","SBIN.NS"]
    rows = []
    for sym in watch:
        d = load_data(sym)
        if not d.empty and len(d) > 20:
            sig, rsi_v, sc = get_signal(d)
            lc = float(d["Close"].iloc[-1])
            sp = float(d["Low"].tail(20).min())
            rs_ = float(d["High"].tail(20).max())
            tg = rs_; sl = sp
            if sig == "BUY": tg = lc + (lc - sp) * 1.5; sl = sp
            if sig == "SELL": tg = sp; sl = rs_
            prof = ((tg - lc) / lc * 100) if sig!= "SELL" else ((lc - tg) / lc * 100)
            disp = get_display_name(sym)
            rows.append({"Stock":disp,"LTP":round(lc,2),"Signal":sig,"Target":round(tg,2),"Profit%":round(prof,1),"SL":round(sl,2),"Score":sc,"RSI":round(rsi_v,1)})
    df_out = pd.DataFrame(rows)
    if not df_out.empty:
        df_out = df_out.sort_values(by="Profit%", ascending=False)
    st.dataframe(df_out, use_container_width=True)
    csv
