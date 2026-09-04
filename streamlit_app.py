import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="FinTrade V9 MEGA", layout="wide", page_icon="🚀")
st.markdown('<h1 style="background: linear-gradient(90deg,#00D1FF,#FF8C00);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:900;">🚀 FinTrade V9 MEGA - All Free Features</h1>', unsafe_allow_html=True)
st.caption("Market Dashboard + Support/Resistance + Compare + Intraday 5min + Watchlist + 52W Alert")

@st.cache_data(ttl=300)
def load_data(tick, per="6mo", interval="1d"):
    df = yf.download(tick, period=per, interval=interval, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    return df
def rsi(data,w=14):
    d=data['Close'].diff(); g=(d.where(d>0,0)).rolling(w).mean(); l=(-d.where(d<0,0)).rolling(w).mean(); return 100-(100/(1+g/l))

# Watchlist in session
if 'watchlist' not in st.session_state: st.session_state.watchlist = ["RELIANCE.NS","TCS.NS","INFY.NS"]

with st.sidebar:
    st.title("V9 MEGA")
    user_input = st.text_input("NSE Stock", value="RELIANCE").upper().strip()
    ticker = user_input if ".NS" in user_input or "^" in user_input else user_input + ".NS"
    clean = user_input.replace(".NS","")
    st.divider()
    st.subheader("⭐ My Watchlist")
    new_w = st.text_input("Add to Watchlist (e.g. SBIN.NS)")
    if st.button("Add"):
        if new_w: st.session_state.watchlist.append(new_w.upper()); st.success("Added!")
    st.write(st.session_state.watchlist)
    if st.button("Clear Watchlist"): st.session_state.watchlist = []
    st.divider()
    if st.button("🔄 Refresh"): st.cache_data.clear(); st.rerun()

# NEW FEATURE 1 - MARKET DASHBOARD
st.subheader("📊 Market Dashboard LIVE")
m1,m2,m3,m4 = st.columns(4)
for idx, sym, name in [(0,"^NSEI","NIFTY"), (1,"^NSEBANK","BANKNIFTY"), (2,"^BSESN","SENSEX"), (3,"INR=X","USD/INR")]:
    try:
        d=load_data(sym, per="2d"); l=d.iloc[-1]['Close']; p=d.iloc[-2]['Close']; ch=(l-p)/p*100
        [m1,m2,m3,m4][idx].metric(name, f"{l:.2f}", f"{ch:.2f}%")
    except: [m1,m2,m3,m4][idx].metric(name, "Loading...")

st.divider()
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📈 CHART + S/R", "⏱️ INTRADAY 5MIN", "⚖️ COMPARE", "🔥 OPTION CHAIN", "🤖 AI FORECAST", "⭐ WATCHLIST + 52W"])

df = load_data(ticker, "6mo", "1d")
if df.empty: st.error(f"{ticker} not found"); st.stop()
df['RSI']=rsi(df); df['SMA20']=df['Close'].rolling(20).mean(); df['SMA50']=df['Close'].rolling(50).mean()
last=df.iloc[-1]

# TAB1 - CHART + SUPPORT RESISTANCE
with tab1:
    st.subheader(f"Chart + Auto Support/Resistance - {ticker}")
    # Support Resistance Logic - Last 20 days High/Low
    sup = df['Low'].tail(20).min(); res = df['High'].tail(20).max()
    c1,c2,c3=st.columns(3)
    c1.metric(f"LTP {ticker}", f"{last['Close']:.2f}")
    c2.metric("Support (20D Low)", f"{sup:.2f}", f"{last['Close']-sup:.2f} away")
    c3.metric("Resistance (20D High)", f"{res:.2f}", f"{res-last['Close']:.2f} away")

    fig=go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
    fig.add_hline(y=sup, line_dash="dash", line_color="green", annotation_text=f"Support {sup:.2f}")
    fig.add_hline(y=res, line_dash="dash", line_color="red", annotation_text=f"Resistance {res:.2f}")
    fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
    if abs(last['Close']-res)/last['Close'] < 0.02: st.warning(f"⚠️ {ticker} Resistance ke paas hai! Breakout ho sakta hai!")
    if abs(last['Close']-sup)/last['Close'] < 0.02: st.success(f"✅ {ticker} Support pe hai! Buying chance!")

# TAB2 - INTRADAY 5MIN
with tab2:
    st.subheader(f"Intraday 5min Chart - {ticker}")
    df_intra = load_data(ticker, per="1d", interval="5m")
    if not df_intra.empty:
        fig2=go.Figure(); fig2.add_trace(go.Candlestick(x=df_intra.index, open=df_intra['Open'], high=df_intra['High'], low=df_intra['Low'], close=df_intra['Close']))
        fig2.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig2, use_container_width=True)
    else: st.info("Intraday data market hours me hi milta hai (9:15-3:30)")

# TAB3 - COMPARE
with tab3:
    st.subheader("⚖️ Compare 2 Stocks")
    c1,c2=st.columns(2)
    s1=c1.text_input("Stock 1", value="RELIANCE.NS")
    s2=c2.text_input("Stock 2", value="TCS.NS")
    if st.button("Compare Now"):
        d1=load_data(s1, "6mo"); d2=load_data(s2, "6mo")
        if not d1.empty and not d2.empty:
            # Normalize to %
            d1['Norm'] = d1['Close']/d1['Close'].iloc[0]*100
            d2['Norm'] = d2['Close']/d2['Close'].iloc[0]*100
            fig3=go.Figure()
            fig3.add_trace(go.Scatter(x=d1.index, y=d1['Norm'], name=s1))
            fig3.add_trace(go.Scatter(x=d2.index, y=d2['Norm'], name=s2))
            fig3.update_layout(height=400, template="plotly_dark", title="% Return Comparison (Base 100)")
            st.plotly_chart(fig3, use_container_width=True)
            ret1=(d1['Close'].iloc[-1]/d1['Close'].iloc[0]-1)*100
            ret2=(d2['Close'].iloc[-1]/d2['Close'].iloc[0]-1)*100
            st.metric(f"{s1} 6M Return", f"{ret1:.2f}%")
            st.metric(f"{s2} 6M Return", f"{ret2:.2f}%")
            st.success(f"Winner: {s1 if ret1>ret2 else s2}")

# TAB4,5 - SAME AS BEFORE
with tab4:
    st.subheader(f"Option Chain - {clean}")
    try:
        tk=yf.Ticker(ticker); exps=tk.options
        if exps:
            sel=st.selectbox("Expiry", exps[:5]); oc=tk.option_chain(sel)
            pcr = oc.puts['openInterest'].sum() / oc.calls['openInterest'].sum() if oc.calls['openInterest'].sum()!=0 else 0
            st.metric("PCR", f"{pcr:.2f}", "Bullish" if pcr>1 else "Bearish")
            c1,c2=st.columns(2)
            with c1: st.dataframe(oc.calls[['strike','lastPrice','openInterest']].head(10), use_container_width=True)
            with c2: st.dataframe(oc.puts[['strike','lastPrice','openInterest']].head(10), use_container_width=True)
    except: st.link_button("NSE Option Chain", "https://www.nseindia.com/option-chain")

with tab5:
    st.subheader("AI 7-Day Forecast")
    y_vals = df['Close'].values; x_vals = np.arange(len(y_vals))
    slope, intercept = np.polyfit(x_vals, y_vals, 1)
    future_x = np.arange(len(y_vals), len(y_vals)+7); future_price = slope * future_x + intercept
    future_dates = pd.date_range(df.index[-1]+pd.Timedelta(days=1), periods=7, freq='B')
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=df.index, y=y_vals, name="Actual", line=dict(color='#00BFFF')))
    fig4.add_trace(go.Scatter(x=future_dates, y=future_price, name="AI Forecast", line=dict(color='orange', dash='dash', width=3)))
    fig4.update_layout(height=400, template="plotly_dark"); st.plotly_chart(fig4, use_container_width=True)

with tab6:
    st.subheader("⭐ Watchlist + 52W High/Low Alert")
    if st.button("Check Watchlist Now"):
        rows=[]
        for s in st.session_state.watchlist:
            try:
                d=load_data(s, per="1y")
                l=d['Close'].iloc[-1]; high52=d['High'].max(); low52=d['Low'].min()
                near_high = (high52-l)/high52*100; near_low = (l-low52)/low52*100
                alert = "Near 52W HIGH 🔥" if near_high < 3 else "Near 52W LOW 💎" if near_low < 5 else "Normal"
                rows.append({"Stock": s, "LTP": round(l,2), "52W High": round(high52,2), "52W Low": round(low52,2), "Alert": alert})
            except: pass
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.balloons()
