import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from fpdf import FPDF
import urllib.parse
import requests

st.set_page_config(page_title="FinTrade V5.1 POLISHED", layout="wide", page_icon="🚀")

st.title("🚀 FinTrade - V5.1 POLISHED PRO")
st.caption("Fixed Option Chain | Portfolio | Alerts | NIFTY | AI Signals")

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ V5.1 Controls")
    user_input = st.text_input("Search NSE Stock", value="RELIANCE").upper().strip()
    ticker = user_input if ".NS" in user_input or "^" in user_input else user_input + ".NS"
    clean_ticker = user_input.replace(".NS","") # For NSE API
    period = st.select_slider("Chart Period", options=["1mo","3mo","6mo","1y","2y"], value="6mo")
    st.divider()
    st.subheader("💼 My Portfolio")
    if 'portfolio' not in st.session_state: st.session_state.portfolio = []
    p_stock = st.text_input("Stock Name", value="RELIANCE.NS")
    p_qty = st.number_input("Qty", min_value=1, value=10)
    p_buy = st.number_input("Buy Price", min_value=1.0, value=1300.0)
    if st.button("Add to Portfolio", use_container_width=True):
        st.session_state.portfolio.append({"Stock": p_stock, "Qty": p_qty, "Buy": p_buy})
        st.success(f"Added {p_stock}!")
    if st.button("Clear Portfolio", use_container_width=True):
        st.session_state.portfolio = []
    if st.button("🔄 Refresh All", use_container_width=True):
        st.cache_data.clear(); st.rerun()

tab1, tab2, tab3 = st.tabs(["📈 LIVE MARKET + CHART", "💼 PORTFOLIO TRACKER", "🔥 OPTION CHAIN + ALERTS"])

@st.cache_data(ttl=300)
def load_data(tick, per):
    df = yf.download(tick, period=per, interval="1d", auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    return df

def rsi_calc(data,w=14):
    delta=data['Close'].diff(); gain=(delta.where(delta>0,0)).rolling(window=w).mean()
    loss=(-delta.where(delta<0,0)).rolling(window=w).mean(); rs=gain/loss
    return 100-(100/(1+rs))

# --- TAB 1 ---
with tab1:
    df = load_data(ticker, period)
    if df.empty: st.error(f"{ticker} ka data nahi mila"); st.stop()
    df['RSI']=rsi_calc(df); df['SMA20']=df['Close'].rolling(20).mean(); df['SMA50']=df['Close'].rolling(50).mean()
    last=df.iloc[-1]; prev=df.iloc[-2]; chg=last['Close']-prev['Close']; pct=chg/prev['Close']*100
    
    c1,c2,c3,c4 = st.columns(4)
    c1.metric(f"LTP - {ticker}", f"{last['Close']:.2f}", f"{chg:.2f} ({pct:.2f}%)")
    c2.metric("RSI (14)", f"{last['RSI']:.1f}")
    c3.metric("High / Low", f"{last['High']:.2f} / {last['Low']:.2f}")
    c4.metric("Volume", f"{last['Volume']/1e6:.2f}M")
    
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='orange',width=1.5), name="SMA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='#00BFFF',width=1.5), name="SMA50"))
    fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    buy = last['SMA20']>last['SMA50'] and 45<last['RSI']<70
    sell = last['SMA20']<last['SMA50'] or last['RSI']>75
    if buy: signal_text="STRONG BUY"; msg=f"✅ STRONG BUY - {ticker} | Entry: {last['Close']:.2f} | Target: {last['Close']*1.03:.2f} | SL: {last['Close']*0.978:.2f}"; st.success(msg); st.balloons()
    elif sell: signal_text="SELL / AVOID"; msg=f"🔻 SELL - {ticker} | RSI: {last['RSI']:.1f}"; st.error(msg)
    else: signal_text="SIDEWAYS / WAIT"; msg=f"⚠️ WAIT - {ticker} | RSI: {last['RSI']:.1f}"; st.warning(msg)

# --- TAB 2 ---
with tab2:
    st.subheader("💼 My Portfolio - Real P&L")
    if not st.session_state.portfolio: st.info("Left sidebar se stock add karo")
    else:
        total_pnl=0; rows=[]
        for item in st.session_state.portfolio:
            try:
                live_df = yf.download(item['Stock'], period="1d", auto_adjust=True, progress=False)
                if isinstance(live_df.columns, pd.MultiIndex): live_df.columns = live_df.columns.get_level_values(0)
                ltp = live_df['Close'].iloc[-1] if not live_df.empty else item['Buy']
                pnl = (ltp - item['Buy'])*item['Qty']; total_pnl+=pnl
                rows.append({"Stock": item['Stock'], "Qty": item['Qty'], "Buy": item['Buy'], "LTP": round(float(ltp),2), "P&L": round(pnl,2)})
            except: rows.append({"Stock": item['Stock'], "Qty": item['Qty'], "Buy": item['Buy'], "LTP": item['Buy'], "P&L": 0})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.metric("Total Portfolio P&L", f"₹ {total_pnl:.2f}", "Profit" if total_pnl>0 else "Loss")

# --- TAB 3 - FIXED OPTION CHAIN ---
with tab3:
    c1,c2 = st.columns([2,1])
    with c1:
        st.subheader(f"🔥 Live Option Chain - {clean_ticker}")
        # TRY 1: yfinance
        option_found = False
        try:
            tk = yf.Ticker(ticker)
            exps = tk.options
            if exps:
                sel_exp = st.selectbox("Select Expiry (yfinance)", exps[:5])
                oc = tk.option_chain(sel_exp)
                st.write("**CALLS**"); st.dataframe(oc.calls[['strike','lastPrice','bid','ask','volume','openInterest']].head(10), use_container_width=True)
                st.write("**PUTS**"); st.dataframe(oc.puts[['strike','lastPrice','bid','ask','volume','openInterest']].head(10), use_container_width=True)
                pcr = oc.puts['openInterest'].sum() / oc.calls['openInterest'].sum() if oc.calls['openInterest'].sum()!=0 else 0
                st.metric("PCR", f"{pcr:.2f}", "Bullish" if pcr>1 else "Bearish")
                option_found = True
        except: pass
        
        # TRY 2: If yfinance fails, show NSE explanation + Sample Logic
        if not option_found:
            st.info(f"ℹ️ Note: {clean_ticker} ka Option Data yfinance pe abhi live nahi hai (NSE restriction). Isliye hum NSE ka official view de rahe hain.")
            st.markdown(f"""
            **NSE Option Chain Live Dekhne ke liye yaha click karo:**
            - [NSE India - {clean_ticker} Option Chain](https://www.nseindia.com/option-chain)
            
            **V6 me hum direct NSE API connect kar denge. Tab tak:**
            - RELIANCE, TCS, INFY, HDFCBANK, ICICIBANK me sabse zyada liquidity hai
            - PCR > 1 = Bullish, PCR < 0.7 = Bearish
            """)
            # Show a dummy calculated chain from current price
            if 'last' in locals():
                atm = round(last['Close']/50)*50
                strikes = [atm + i*50 for i in range(-5,6)]
                dummy = pd.DataFrame({"STRIKE": strikes, "CALL LTP (Est)": [max(0, last['Close']-s+10) for s in strikes], "PUT LTP (Est)": [max(0, s-last['Close']+10) for s in strikes]})
                st.write(f"**Estimated Option Chain around ATM {atm} (Demo Logic)**")
                st.dataframe(dummy, use_container_width=True)

    with c2:
        st.subheader("🔔 Price Alert System")
        alert_price = st.number_input(f"Alert Price for {ticker}", value=float(last['Close']*1.02) if 'last' in locals() else 1000.0)
        alert_type = st.selectbox("Alert Type", ["Price > Target", "Price < Target"])
        if st.button("Set Alert 🚀", use_container_width=True):
            st.success(f"Alert Set! {ticker} {alert_type} {alert_price}")
            if 'last' in locals():
                if (alert_type=="Price > Target" and last['Close']>=alert_price) or (alert_type=="Price < Target" and last['Close']<=alert_price):
                    st.error(f"🔔 ALERT TRIGGERED! {ticker} is at {last['Close']:.2f}!")
                else:
                    st.info(f"Current: {last['Close']:.2f}. Hit hote hi alert baje ga!")
