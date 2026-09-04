import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from fpdf import FPDF
import urllib.parse

st.set_page_config(page_title="FinTrade V6 - BRANDED", layout="wide", page_icon="🚀")

st.markdown("""
<style>
    .main-title {font-size: 42px; font-weight: 900; background: linear-gradient(90deg, #00D1FF, #FF8C00); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .stMetric{background:#11131a;padding:15px;border-radius:12px;border:1px solid #2a2d3e}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🚀 FinTrade - V6 BRANDED PRO</div>', unsafe_allow_html=True)
st.caption("✅ Logo Branding | Portfolio | Option Chain | Alerts | Market Overview | Ayodhya")

with st.sidebar:
    st.markdown("## 🚀 FinTrade V6")
    st.caption("Ayodhya's Trading Terminal")
    user_input = st.text_input("Search NSE Stock", value="RELIANCE").upper().strip()
    ticker = user_input if ".NS" in user_input or "^" in user_input else user_input + ".NS"
    clean_ticker = user_input.replace(".NS","")
    period = st.select_slider("Chart Period", options=["1mo","3mo","6mo","1y","2y"], value="6mo")
    st.divider()
    st.subheader("💼 My Portfolio")
    if 'portfolio' not in st.session_state: st.session_state.portfolio = []
    p_stock = st.text_input("Stock", value="RELIANCE.NS")
    p_qty = st.number_input("Qty", value=10)
    p_buy = st.number_input("Buy Price", value=1300.0)
    if st.button("Add to Portfolio", use_container_width=True):
        st.session_state.portfolio.append({"Stock": p_stock, "Qty": p_qty, "Buy": p_buy})
    if st.button("🔄 Refresh", use_container_width=True):
        st.cache_data.clear(); st.rerun()
    st.divider()
    st.success("📱 Mobile App: Chrome -> 3 dots -> Add to Home Screen")

tab1, tab2, tab3 = st.tabs(["📈 LIVE CHART", "💼 PORTFOLIO", "🔥 OPTION CHAIN"])

@st.cache_data(ttl=300)
def load_data(tick, per):
    df = yf.download(tick, period=per, interval="1d", auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    return df

def rsi_calc(data,w=14):
    delta=data['Close'].diff(); gain=(delta.where(delta>0,0)).rolling(window=w).mean()
    loss=(-delta.where(delta<0,0)).rolling(window=w).mean(); rs=gain/loss
    return 100-(100/(1+rs))

with tab1:
    df = load_data(ticker, period)
    if df.empty: st.error(f"{ticker} not found"); st.stop()
    df['RSI']=rsi_calc(df); df['SMA20']=df['Close'].rolling(20).mean(); df['SMA50']=df['Close'].rolling(50).mean()
    last=df.iloc[-1]; prev=df.iloc[-2]; chg=last['Close']-prev['Close']; pct=chg/prev['Close']*100
    c1,c2,c3,c4 = st.columns(4)
    c1.metric(f"LTP {ticker}", f"{last['Close']:.2f}", f"{chg:.2f} ({pct:.2f}%)")
    c2.metric("RSI", f"{last['RSI']:.1f}")
    c3.metric("High/Low", f"{last['High']:.2f}/{last['Low']:.2f}")
    c4.metric("Volume", f"{last['Volume']/1e6:.2f}M")
    fig=go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='orange'), name="SMA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='#00BFFF'), name="SMA50"))
    fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)
    buy = last['SMA20']>last['SMA50'] and 45<last['RSI']<70
    if buy: st.success(f"✅ STRONG BUY - {ticker} | Target {last['Close']*1.03:.2f}"); st.balloons()
    else: st.warning(f"⚠️ WAIT - RSI {last['RSI']:.1f}")

with tab2:
    if not st.session_state.portfolio: st.info("Sidebar se Add karo")
    else:
        total=0; rows=[]
        for it in st.session_state.portfolio:
            try:
                ldf=yf.download(it['Stock'], period="1d", auto_adjust=True, progress=False)
                if isinstance(ldf.columns, pd.MultiIndex): ldf.columns=ldf.columns.get_level_values(0)
                ltp=ldf['Close'].iloc[-1] if not ldf.empty else it['Buy']
                pnl=(ltp-it['Buy'])*it['Qty']; total+=pnl
                rows.append({"Stock":it['Stock'],"Qty":it['Qty'],"Buy":it['Buy'],"LTP":round(float(ltp),2),"P&L":round(pnl,2)})
            except: rows.append(it)
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.metric("Total P&L", f"₹ {total:.2f}")

with tab3:
    st.subheader(f"Option Chain - {clean_ticker}")
    st.link_button(f"Open NSE Official Option Chain", f"https://www.nseindia.com/option-chain")
    st.info("yfinance Option Chain kabhi kabhi block karta hai - NSE link se live dekho. V7 me direct NSE API laga denge.")
