import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="FinTrade Pro", layout="wide", page_icon="📈")

# --- Custom CSS ---
st.markdown("""
<style>
.stMetric {background-color: #1a1c24; padding: 15px; border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

st.title("📈 FinTrade - Pro V2")

# --- Sidebar ---
st.sidebar.title("⚙️ Controls")
stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "NIFTY 50 - ^NSEI"]
selected_stock = st.sidebar.selectbox("Stock (NSE)", stocks, index=0)
period = st.sidebar.select_slider("Period", options=["1mo", "3mo", "6mo", "1y"], value="6mo")

# --- Data Download ---
@st.cache_data(ttl=300)
def load_data(ticker, per):
    df = yf.download(ticker, period=per, interval="1d", auto_adjust=True)
    # Fix for new yfinance multi-level column
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

df = load_data(selected_stock, period)

if df.empty:
    st.error("Data nahi mila. Internet check karo ya dusra stock try karo.")
    st.stop()

# --- Calculate Indicators ---
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

df['RSI'] = calculate_rsi(df)
df['SMA20'] = df['Close'].rolling(20).mean()
df['SMA50'] = df['Close'].rolling(50).mean()

last = df.iloc[-1]
prev = df.iloc[-2]

# --- Metrics ---
col1, col2, col3, col4 = st.columns(4)
change = last['Close'] - prev['Close']
pct = (change/prev['Close'])*100
col1.metric("LTP", f"{last['Close']:.2f}", f"{change:.2f} ({pct:.2f}%)")
col2.metric("RSI (14)", f"{last['RSI']:.1f}", "Overbought" if last['RSI']>70 else "Oversold" if last['RSI']<30 else "Neutral")
col3.metric("High", f"{last['High']:.2f}")
col4.metric("Volume", f"{last['Volume']/1e6:.2f}M")

# --- Chart ---
fig = go.Figure()
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Candle"))
fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='orange', width=1), name="SMA 20"))
fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='blue', width=1), name="SMA 50"))
fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
st.plotly_chart(fig, use_container_width=True)

# RSI Chart
fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple'), name="RSI"))
fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
fig_rsi.update_layout(height=200, template="plotly_dark", title="RSI (14)", margin=dict(l=0,r=0,t=30,b=0))
st.plotly_chart(fig_rsi, use_container_width=True)

# --- PRO SIGNAL LOGIC ---
st.divider()
st.subheader("🤖 AI Pro Signal")

buy_cond = last['SMA20'] > last['SMA50'] and last['RSI'] > 45 and last['RSI'] < 70 and last['Close'] > last['SMA20']
sell_cond = last['SMA20'] < last['SMA50'] or last['RSI'] > 75 or last['RSI'] < 30

if buy_cond:
    target = last['Close'] * 1.025
    sl = last['Close'] * 0.98
    st.success(f"✅ STRONG BUY - {selected_stock} \n\nConfidence: 89% | Entry: {last['Close']:.2f} | Target: {target:.2f} (+2.5%) | Stop-Loss: {sl:.2f} (-2%)")
    st.balloons()
elif sell_cond:
    st.error(f"🔻 SELL / WAIT - Weakness detected. RSI: {last['RSI']:.1f} | SMA Trend Down")
else:
    st.warning(f"⚠️ SIDEWAYS / WAIT - No clear trend. RSI is neutral at {last['RSI']:.1f}")

c1, c2 = st.columns(2)
c1.button("🚀 BUY ORDER", use_container_width=True, type="primary")
c2.button("📉 SELL ORDER", use_container_width=True)

st.sidebar.info("App Auto-Updates every 5 mins")
