import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from fpdf import FPDF

st.set_page_config(page_title="FinTrade Pro V3", layout="wide", page_icon="📈")

st.title("📈 FinTrade - Pro V3")
st.caption("Search Any NSE Stock | Live News | AI Signal | PDF Report")

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Search")
    user_input = st.text_input("Stock Symbol likho", value="RELIANCE").upper().strip()
    # Auto add .NS if not there
    ticker = user_input if ".NS" in user_input or "^" in user_input else user_input + ".NS"
    
    period = st.select_slider("Period", options=["1mo", "3mo", "6mo", "1y", "2y"], value="6mo")
    st.info("Example: RELIANCE, TCS, INFY, HDFCBANK, SBIN, TATAMOTORS")
    st.success("App Auto-Updates every 5 mins")

# --- Data ---
@st.cache_data(ttl=300)
def load_data(tick, per):
    df = yf.download(tick, period=per, interval="1d", auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

df = load_data(ticker, period)

if df.empty:
    st.error(f"❌ {ticker} ka data nahi mila. Symbol sahi likho jaise RELIANCE, TCS")
    st.stop()

# --- Indicators ---
def rsi_calc(data, w=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=w).mean()
            )
    loss = (-delta.where(delta < 0, 0)).rolling(window=w).mean())
    rs = gain / loss
    return 100 - (100 / (1 + rs))

df['RSI'] = rsi_calc(df)
df['SMA20'] = df['Close'].rolling(20).mean()
df['SMA50'] = df['Close'].rolling(50).mean()
last = df.iloc[-1]
prev = df.iloc[-2]

# --- Metrics ---
c1,c2,c3,c4 = st.columns(4)
chg = last['Close']-prev['Close']
pct = chg/prev['Close']*100
c1.metric("LTP - "+ticker, f"{last['Close']:.2f}", f"{chg:.2f} ({pct:.2f}%)")
c2.metric("RSI (14)", f"{last['RSI']:.1f}", "Overbought" if last['RSI']>70 else "Oversold" if last['RSI']<30 else "Neutral")
c3.metric("High", f"{last['High']:.2f}")
c4.metric("Volume", f"{last['Volume']/1e6:.2f}M")

# --- Chart ---
fig = go.Figure()
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='orange', width=1.5), name="SMA20"))
fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='#00BFFF', width=1.5), name="SMA50"))
fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=10,b=0))
st.plotly_chart(fig, use_container_width=True)

# RSI
fig2 = go.Figure(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='violet'), name="RSI"))
fig2.add_hline(y=70, line_dash="dash", line_color="red")
fig2.add_hline(y=30, line_dash="dash", line_color="green")
fig2.update_layout(height=220, template="plotly_dark", title="RSI (14)", margin=dict(l=0,r=0,t=30,b=0))
st.plotly_chart(fig2, use_container_width=True)

# --- SIGNAL ---
st.divider()
buy = last['SMA20'] > last['SMA50'] and 45 < last['RSI'] < 70 and last['Close'] > last['SMA20']
sell = last['SMA20'] < last['SMA50'] or last['RSI'] > 75

if buy:
    signal_text = "STRONG BUY"
    st.success(f"✅ {signal_text} - {ticker} | Entry: {last['Close']:.2f} | Target: {last['Close']*1.03:.2f} | SL: {last['Close']*0.978:.2f}")
    st.balloons()
elif sell:
    signal_text = "SELL / AVOID"
    st.error(f"🔻 {signal_text} - {ticker} | Weak Trend | RSI: {last['RSI']:.1f}")
else:
    signal_text = "SIDEWAYS / WAIT"
    st.warning(f"⚠️ {signal_text} - {ticker} | RSI Neutral: {last['RSI']:.1f}")

# --- NEWS ---
st.subheader("📰 Live News")
try:
    news = yf.Ticker(ticker).news
    if news and len(news)>0:
        for n in news[:5]:
            title = n.get('title') or n.get('content',{}).get('title','News')
            link = n.get('link') or n.get('content',{}).get('clickThroughUrl',{}).get('url','#')
            st.markdown(f"- [{title}]({link})")
    else:
        st.write("News abhi available nahi hai is stock ke liye.")
except:
    st.write("News load nahi ho paya.")
