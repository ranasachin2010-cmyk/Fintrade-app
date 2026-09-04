import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="FinTrade V7 ULTIMATE", layout="wide", page_icon="🚀")

st.markdown("""
<style>
.main-title{font-size:40px;font-weight:900;background:linear-gradient(90deg,#00D1FF,#FF8C00);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.stMetric{background:#11131a;padding:12px;border-radius:12px;border:1px solid #2a2d3e}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🚀 FinTrade V7 ULTIMATE - A+B+C</div>', unsafe_allow_html=True)
st.caption("✅ A) Option Chain LIVE | B) AI 7-Day Prediction | C) Screener + News | Ayodhya")

with st.sidebar:
    st.title("V7 Controls")
    user_input = st.text_input("NSE Stock", value="RELIANCE").upper().strip()
    ticker = user_input if ".NS" in user_input or "^" in user_input else user_input + ".NS"
    clean = user_input.replace(".NS","")
    period = st.select_slider("Period", ["3mo","6mo","1y","2y"], value="6mo")
    st.divider()
    if st.button("🔄 Refresh All"): st.cache_data.clear(); st.rerun()

@st.cache_data(ttl=300)
def load_data(tick, per):
    df = yf.download(tick, period=per, interval="1d", auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    return df

def rsi(data,w=14):
    d=data['Close'].diff(); g=(d.where(d>0,0)).rolling(w).mean(); l=(-d.where(d<0,0)).rolling(w).mean(); return 100-(100/(1+g/l))

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 CHART + AI", "🔥 OPTION CHAIN (A)", "🤖 AI PREDICTION (B)", "🔍 SCREENER (C)", "📰 NEWS (C)"])

# COMMON DATA
df = load_data(ticker, period)
if df.empty: st.error(f"{ticker} not found"); st.stop()
df['RSI']=rsi(df); df['SMA20']=df['Close'].rolling(20).mean(); df['SMA50']=df['Close'].rolling(50).mean()
last=df.iloc[-1]

# TAB 1 - CHART
with tab1:
    c1,c2,c3,c4=st.columns(4)
    chg=last['Close']-df.iloc[-2]['Close']; pct=chg/df.iloc[-2]['Close']*100
    c1.metric(f"LTP {ticker}", f"{last['Close']:.2f}", f"{chg:.2f} ({pct:.2f}%)")
    c2.metric("RSI", f"{last['RSI']:.1f}")
    c3.metric("SMA20/50", f"{last['SMA20']:.1f}/{last['SMA50']:.1f}")
    c4.metric("Volume", f"{last['Volume']/1e6:.2f}M")
    fig=go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='orange'), name="SMA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='#00BFFF'), name="SMA50"))
    fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)
    if last['SMA20']>last['SMA50'] and 45<last['RSI']<70: st.success(f"✅ STRONG BUY - Target {last['Close']*1.03:.2f} | SL {last['Close']*0.98:.2f}"); st.balloons()
    else: st.warning(f"⚠️ WAIT - RSI {last['RSI']:.1f}")

# TAB 2 - A) OPTION CHAIN
with tab2:
    st.subheader(f"🔥 A) Live Option Chain - {clean} - PCR + Max Pain")
    try:
        tk=yf.Ticker(ticker)
        exps=tk.options
        if exps:
            sel=st.selectbox("Expiry", exps[:6])
            oc=tk.option_chain(sel)
            calls=oc.calls; puts=oc.puts
            # PCR
            pcr = puts['openInterest'].sum() / calls['openInterest'].sum() if calls['openInterest'].sum()!=0 else 0
            # Max Pain logic
            all_strikes = pd.concat([calls[['strike','openInterest']], puts[['strike','openInterest']]]).groupby('strike')['openInterest'].sum()
            max_pain = all_strikes.idxmax() if not all_strikes.empty else last['Close']
            
            m1,m2,m3 = st.columns(3)
            m1.metric("PCR", f"{pcr:.2f}", "Bullish" if pcr>1 else "Bearish" if pcr<0.7 else "Neutral")
            m2.metric("Max Pain", f"{max_pain}")
            m3.metric("Spot vs Max Pain", f"{last['Close']-max_pain:.2f}")
            
            c1,c2 = st.columns(2)
            with c1: st.write("**CALLS (Top 10)**"); st.dataframe(calls[['strike','lastPrice','bid','ask','volume','openInterest','impliedVolatility']].head(10), use_container_width=True)
            with c2: st.write("**PUTS (Top 10)**"); st.dataframe(puts[['strike','lastPrice','bid','ask','volume','openInterest','impliedVolatility']].head(10), use_container_width=True)
        else:
            st.warning("yfinance expiry nahi de raha. NSE official link use karo.")
            st.link_button("NSE Option Chain", f"https://www.nseindia.com/option-chain")
    except Exception as e:
        st.error(f"Option Chain error: {e}")
        st.link_button("Open NSE Official", f"https://www.nseindia.com/option-chain")

# TAB 3 - B) AI PREDICTION
with tab3:
    st.subheader(f"🤖 B) AI Price Prediction - {ticker} - Next 7 Days")
    # Prepare data for Linear Regression
    df_pred = df[['Close']].copy
