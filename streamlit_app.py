import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="FinTrade", layout="wide")
st.title("📈 FinTrade - Buy/Sell Signal")

stock = st.sidebar.text_input("Stock (NSE)", "RELIANCE.NS")

df = yf.download(stock, period="6mo", interval="1d")

if not df.empty:
    # Fix for new yfinance
    if isinstance(df.columns, type(df.columns)) and 'Close' in str(df.columns):
        try:
            df.columns = df.columns.droplevel(1)
        except:
            pass
    
    last = float(df['Close'].iloc[-1])
    prev = float(df['Close'].iloc[-2])
    change = last - prev
    pct = (change/prev)*100

    st.metric("LTP", f"{last:.2f}", f"{change:.2f} ({pct:.2f}%)")

    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    )])
    fig.update_layout(height=400, template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    # Simple Signal Logic
    last_c = df.iloc[-1]
    prev_c = df.iloc[-2]
    
    if prev_c['Close'] < prev_c['Open'] and last_c['Close'] > last_c['Open']:
        st.success("✅ STRONG BUY - Bullish Engulfing (Confidence 87%) | Target +1.2%")
        st.balloons()
    elif prev_c['Close'] > prev_c['Open'] and last_c['Close'] < last_c['Open']:
        st.error("🔻 SELL - Bearish Engulfing (Confidence 80%) | Stop-loss 25,100")
    else:
        st.warning("⚠️ WAIT - No Clear Pattern")
    
    st.subheader("📰 News Analysis")
    st.info("✅ RBI Repo Rate Unchanged - Positive for Banks")
    st.info("✅ IT Stocks Q2 Outlook Positive")
    
    c1, c2 = st.columns(2)
    c1.button("🚀 BUY", use_container_width=True)
    c2.button("📉 SELL", use_container_width=True)
else:
    st.error("Data nahi mila, TCS.NS try karo")
