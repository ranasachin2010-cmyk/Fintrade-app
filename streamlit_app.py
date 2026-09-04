import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from fpdf import FPDF
import urllib.parse

st.set_page_config(page_title="FinTrade Ultimate V4", layout="wide", page_icon="🚀")

# --- CSS ---
st.markdown("""
<style>
.stMetric {background-color: #11131a; padding: 15px; border-radius: 12px; border: 1px solid #2a2d3e;}
</style>
""", unsafe_allow_html=True)

st.title("🚀 FinTrade - ULTIMATE V4")
st.caption("India's Most Advanced Trading Dashboard | NIFTY | BANKNIFTY | Gainers/Losers | AI Signal")

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Ultimate Controls")
    user_input = st.text_input("Search Any NSE Stock", value="RELIANCE").upper().strip()
    ticker = user_input if ".NS" in user_input or "^" in user_input else user_input + ".NS"
    period = st.select_slider("Chart Period", options=["1mo", "3mo", "6mo", "1y", "2y"], value="6mo")
    st.divider()
    st.info("💡 Tips: Try NIFTYBEES, TATAMOTORS, BAJFINANCE, PAYTM")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# --- Market Overview Function ---
@st.cache_data(ttl=300)
def get_market_overview():
    nifty = yf.download("^NSEI", period="1d", interval="1m", auto_adjust=True)
    bank = yf.download("^NSEBANK", period="1d", interval="1m", auto_adjust=True)
    if isinstance(nifty.columns, pd.MultiIndex): nifty.columns = nifty.columns.get_level_values(0)
    if isinstance(bank.columns, pd.MultiIndex): bank.columns = bank.columns.get_level_values(0)
    return nifty, bank

@st.cache_data(ttl=600)
def get_gainers_losers():
    nifty_stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "TATAMOTORS.NS", "BAJFINANCE.NS", "BHARTIARTL.NS", "ITC.NS", "LT.NS", "KOTAKBANK.NS"]
    data = []
    for s in nifty_stocks:
        try:
            df = yf.download(s, period="2d", interval="1d", auto_adjust=True, progress=False)
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            if len(df) >= 2:
                chg = ((df['Close'].iloc[-1] - df['Close'].iloc[-2])/df['Close'].iloc[-2])*100
                data.append({"Stock": s.replace(".NS",""), "LTP": df['Close'].iloc[-1], "Change%": chg})
        except:
            pass
    df_all = pd.DataFrame(data).sort_values("Change%", ascending=False)
    return df_all.head(5), df_all.tail(5).sort_values("Change%")

# --- Display Market Overview ---
st.subheader("🌍 Market Overview - LIVE")
m1, m2, m3 = st.columns([2,2,3])
try:
    nifty_live, bank_live = get_market_overview()
    if not nifty_live.empty:
        n_ltp = nifty_live['Close'].iloc[-1]
        n_chg = n_ltp - nifty_live['Open'].iloc[0]
        n_pct = (n_chg/nifty_live['Open'].iloc[0])*100
        m1.metric("NIFTY 50", f"{n_ltp:.2f}", f"{n_chg:.2f} ({n_pct:.2f}%)")
    if not bank_live.empty:
        b_ltp = bank_live['Close'].iloc[-1]
        b_chg = b_ltp - bank_live['Open'].iloc[0]
        b_pct = (b_chg/bank_live['Open'].iloc[0])*100
        m2.metric("BANKNIFTY", f"{b_ltp:.2f}", f"{b_chg:.2f} ({b_pct:.2f}%)")
except:
    m1.metric("NIFTY 50", "Live...")
    m2.metric("BANKNIFTY", "Live...")

# Gainers / Losers
top_gainers, top_losers = get_gainers_losers()
with m3:
    c_g, c_l = st.columns(2)
    c_g.write("🔥 **Top Gainers**")
    c_g.dataframe(top_gainers, hide_index=True, use_container_width=True)
    c_l.write("💔 **Top Losers**")
    c_l.dataframe(top_losers, hide_index=True, use_container_width=True)

st.divider()

# --- Main Stock Analysis ---
@st.cache_data(ttl=300)
def load_data(tick, per):
    df = yf.download(tick, period=per, interval="1d", auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

df = load_data(ticker, period)

if df.empty:
    st.error(f"{ticker} ka data nahi mila.")
    st.stop()

def rsi_calc(data, w=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=w).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=w).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

df['RSI'] = rsi_calc(df)
df['SMA20'] = df['Close'].rolling(20).mean()
df['SMA50'] = df['Close'].rolling(50).mean()
last = df.iloc[-1]
prev = df.iloc[-2]

# Metrics
c1,c2,c3,c4 = st.columns(4)
chg = last['Close']-prev['Close']
pct = chg/prev['Close']*100
c1.metric(f"LTP - {ticker}", f"{last['Close']:.2f}", f"{chg:.2f} ({pct:.2f}%)")
c2.metric("RSI (14)", f"{last['RSI']:.1f}", "Overbought" if last['RSI']>70 else "Oversold" if last['RSI']<30 else "Neutral")
c3.metric("High / Low", f"{last['High']:.2f} / {last['Low']:.2f}")
c4.metric("Volume", f"{last['Volume']/1e6:.2f}M")

# Charts
fig = go.Figure()
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='orange', width=1.5), name="SMA20"))
fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='#00BFFF', width=1.5), name="SMA50"))
fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=10,b=0))
st.plotly_chart(fig, use_container_width=True)

fig2 = go.Figure(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='violet'), name="RSI"))
fig2.add_hline(y=70, line_dash="dash", line_color="red")
fig2.add_hline(y=30, line_dash="dash", line_color="green")
fig2.update_layout(height=220, template="plotly_dark", title="RSI (14)", margin=dict(l=0,r=0,t=30,b=0))
st.plotly_chart(fig2, use_container_width=True)

# --- Signal ---
st.divider()
buy = last['SMA20'] > last['SMA50'] and 45 < last['RSI'] < 70 and last['Close'] > last['SMA20']
sell = last['SMA20'] < last['SMA50'] or last['RSI'] > 75

if buy:
    signal_text = "STRONG BUY"
    msg = f"✅ STRONG BUY - {ticker} | Entry: {last['Close']:.2f} | Target: {last['Close']*1.03:.2f} | SL: {last['Close']*0.978:.2f}"
    st.success(msg)
    st.balloons()
elif sell:
    signal_text = "SELL / AVOID"
    msg = f"🔻 SELL / AVOID - {ticker} | Weak Trend | RSI: {last['RSI']:.1f}"
    st.error(msg)
else:
    signal_text = "SIDEWAYS / WAIT"
    msg = f"⚠️ SIDEWAYS / WAIT - {ticker} | RSI Neutral: {last['RSI']:.1f}"
    st.warning(msg)

# --- News ---
st.subheader("📰 Live News")
try:
    news = yf.Ticker(ticker).news
    if news:
        for n in news[:5]:
            title = n.get('title') or n.get('content',{}).get('title','News')
            link = n.get('link') or n.get('content',{}).get('clickThroughUrl',{}).get('url','#')
            st.markdown(f"- [{title}]({link})")
    else:
        st.write("News abhi available nahi hai.")
except:
    st.write("News load nahi ho paya.")

st.divider()

# --- PDF + WhatsApp ---
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, f"FinTrade Ultimate V4 - {ticker}", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.ln(10)
    pdf.cell(200, 10, f"LTP: {last['Close']:.2f} | Change: {chg:.2f} ({pct:.2f}%)", ln=True)
    pdf.cell(200, 10, f"RSI: {last['RSI']:.1f} | SMA20: {last['SMA20']:.2f} | SMA50: {last['SMA50']:.2f}", ln=True)
    pdf.cell(200, 10, f"Signal: {signal_text}", ln=True)
    pdf.cell(200, 10, f"High: {last['High']:.2f} | Low: {last['Low']:.2f} | Volume: {last['Volume']:.0f}", ln=True)
    pdf.ln(10)
    pdf.cell(200, 10, "Generated by FinTrade Ultimate V4", ln=True, align='C')
    out = pdf.output(dest='S')
    if isinstance(out, str):
        return out.encode('latin-1')
    return bytes(out)

pdf_data = create_pdf()

col_pdf, col_wa = st.columns(2)

with col_pdf:
    st.download_button("📄 Download PDF Report", data=pdf_data, file_name=f"{ticker}_report.pdf", mime="application/pdf", use_container_width=True)

with col_wa:
    wa_text = urllib.parse.quote(f"{msg}\n\nFull Report: https://fintrade-app-nvfrcmhxdqux3qtqsfsd67.streamlit.app\n\nBy FinTrade Ultimate V4")
    wa_link = f"https://wa.me/?text={wa_text}"
    st.link_button("💬 Share on WhatsApp", wa_link, use_container_width=True)

st.success("V4 Ultimate LIVE! 🚀")
