import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="FinTrade V7 ULTIMATE", layout="wide", page_icon="🚀")
st.markdown('<h1 style="background: linear-gradient(90deg,#00D1FF,#FF8C00);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:900;">🚀 FinTrade V7 ULTIMATE - FIXED</h1>', unsafe_allow_html=True)
st.caption("✅ A) Option Chain | B) AI 7D Prediction (No sklearn) | C) Screener + News")

with st.sidebar:
    st.title("V7 Controls")
    user_input = st.text_input("NSE Stock", value="RELIANCE").upper().strip()
    ticker = user_input if ".NS" in user_input or "^" in user_input else user_input + ".NS"
    clean = user_input.replace(".NS","")
    period = st.select_slider("Period", ["3mo","6mo","1y","2y"], value="6mo")
    if st.button("🔄 Refresh"): st.cache_data.clear(); st.rerun()

@st.cache_data(ttl=300)
def load_data(tick, per):
    df = yf.download(tick, period=per, interval="1d", auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    return df

def rsi(data,w=14):
    d=data['Close'].diff(); g=(d.where(d>0,0)).rolling(w).mean(); l=(-d.where(d<0,0)).rolling(w).mean(); return 100-(100/(1+g/l))

tab1, tab2, tab3, tab4 = st.tabs(["📈 CHART", "🔥 OPTION CHAIN (A)", "🤖 AI PREDICTION (B) - FIXED", "🔍 SCREENER + NEWS (C)"])

df = load_data(ticker, period)
if df.empty: st.error(f"{ticker} not found"); st.stop()
df['RSI']=rsi(df); df['SMA20']=df['Close'].rolling(20).mean(); df['SMA50']=df['Close'].rolling(50).mean()
last=df.iloc[-1]

with tab1:
    chg=last['Close']-df.iloc[-2]['Close']; pct=chg/df.iloc[-2]['Close']*100
    st.metric(f"LTP {ticker}", f"{last['Close']:.2f}", f"{chg:.2f} ({pct:.2f}%)")
    fig=go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='orange'), name="SMA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='#00BFFF'), name="SMA50"))
    fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
    if last['SMA20']>last['SMA50']: st.success("✅ STRONG BUY"); st.balloons()
    else: st.warning("⚠️ WAIT")

with tab2:
    st.subheader(f"A) Live Option Chain - {clean}")
    try:
        tk=yf.Ticker(ticker); exps=tk.options
        if exps:
            sel=st.selectbox("Expiry", exps[:5])
            oc=tk.option_chain(sel)
            pcr = oc.puts['openInterest'].sum() / oc.calls['openInterest'].sum() if oc.calls['openInterest'].sum()!=0 else 0
            st.metric("PCR", f"{pcr:.2f}", "Bullish" if pcr>1 else "Bearish")
            c1,c2=st.columns(2)
            with c1: st.write("CALLS"); st.dataframe(oc.calls[['strike','lastPrice','volume','openInterest']].head(10), use_container_width=True)
            with c2: st.write("PUTS"); st.dataframe(oc.puts[['strike','lastPrice','volume','openInterest']].head(10), use_container_width=True)
        else: st.link_button("NSE Option Chain", f"https://www.nseindia.com/option-chain")
    except: st.link_button("Open NSE Official", "https://www.nseindia.com/option-chain")

with tab3:
    st.subheader("B) AI Prediction - Next 7 Days (Fixed - Numpy Model)")
    # Numpy Polyfit - No sklearn needed
    y_vals = df['Close'].values
    x_vals = np.arange(len(y_vals))
    slope, intercept = np.polyfit(x_vals, y_vals, 1)
    future_x = np.arange(len(y_vals), len(y_vals)+7)
    future_price = slope * future_x + intercept
    future_dates = pd.date_range(df.index[-1]+pd.Timedelta(days=1), periods=7, freq='B')
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df.index, y=y_vals, name="Actual", line=dict(color='#00BFFF')))
    fig2.add_trace(go.Scatter(x=future_dates, y=future_price, name="AI Forecast 7D", line=dict(color='orange', dash='dash', width=3)))
    fig2.update_layout(height=400, template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)
    
    f_df = pd.DataFrame({"Date": future_dates.date, "Predicted": np.round(future_price,2)})
    st.dataframe(f_df, use_container_width=True, hide_index=True)
    trend = "BULLISH 🚀" if future_price[-1] > last['Close'] else "BEARISH 🔻"
    st.metric("AI Trend", trend)

with tab4:
    st.subheader("C) Screener + News")
    watchlist = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","SBIN.NS"]
    if st.button("Run Screener"):
        res=[]
        for s in watchlist:
            d=load_data(s, "6mo")
            if d.empty: continue
            d['RSI']=rsi(d); d['SMA20']=d['Close'].rolling(20).mean(); d['SMA50']=d['Close'].rolling(50).mean()
            l=d.iloc[-1]
            res.append({"Stock": s, "LTP": round(l['Close'],2), "RSI": round(l['RSI'],2), "Signal": "BUY" if l['SMA20']>l['SMA50'] and 50<l['RSI']<70 else "WAIT"})
        st.dataframe(pd.DataFrame(res), use_container_width=True, hide_index=True)
    st.divider()
    try:
        tk=yf.Ticker(ticker)
        for n in tk.news[:5]:
            st.markdown(f"**{n['title']}**"); st.markdown(f"[Read]({n['link']})"); st.divider()
    except: st.link_button(f"Google News {clean}", f"https://news.google.com/search?q={clean}")
