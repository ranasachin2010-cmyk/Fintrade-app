import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from fpdf import FPDF
import urllib.parse

st.set_page_config(page_title="FinTrade V5 ULTIMATE PRO", layout="wide", page_icon="🚀")
st.markdown("<style>.stMetric{background:#11131a;padding:15px;border-radius:12px;border:1px solid #2a2d3e}</style>", unsafe_allow_html=True)

st.title("🚀 FinTrade - V5 ULTIMATE PRO")
st.caption("Portfolio | Option Chain | Alerts | NIFTY | AI Signals | PDF + WhatsApp")

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ V5 Controls")
    user_input = st.text_input("Search NSE Stock", value="RELIANCE").upper().strip()
    ticker = user_input if ".NS" in user_input or "^" in user_input else user_input + ".NS"
    period = st.select_slider("Chart Period", options=["1mo","3mo","6mo","1y","2y"], value="6mo")
    st.divider()
    st.subheader("💼 My Portfolio (Demo)")
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = []
    p_stock = st.text_input("Stock Name", value="RELIANCE.NS")
    p_qty = st.number_input("Qty", min_value=1, value=10)
    p_buy = st.number_input("Buy Price", min_value=1.0, value=1300.0)
    if st.button("Add to Portfolio"):
        st.session_state.portfolio.append({"Stock": p_stock, "Qty": p_qty, "Buy": p_buy})
        st.success("Added!")
    if st.button("Clear Portfolio"):
        st.session_state.portfolio = []
    st.divider()
    if st.button("🔄 Refresh All", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📈 LIVE MARKET + CHART", "💼 PORTFOLIO TRACKER", "🔥 OPTION CHAIN + ALERTS"])

# --- Helper functions ---
@st.cache_data(ttl=300)
def get_market_data():
    nifty = yf.download("^NSEI", period="1d", interval="1m", auto_adjust=True, progress=False)
    bank = yf.download("^NSEBANK", period="1d", interval="1m", auto_adjust=True, progress=False)
    if isinstance(nifty.columns, pd.MultiIndex): nifty.columns = nifty.columns.get_level_values(0)
    if isinstance(bank.columns, pd.MultiIndex): bank.columns = bank.columns.get_level_values(0)
    return nifty, bank

@st.cache_data(ttl=600)
def get_gainers_losers():
    nifty_stocks = ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","SBIN.NS","TATAMOTORS.NS","BAJFINANCE.NS","BHARTIARTL.NS","ITC.NS"]
    data=[]
    for s in nifty_stocks:
        try:
            df = yf.download(s, period="2d", interval="1d", auto_adjust=True, progress=False)
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            if len(df)>=2:
                chg = ((df['Close'].iloc[-1]-df['Close'].iloc[-2])/df['Close'].iloc[-2])*100
                data.append({"Stock": s.replace(".NS",""), "LTP": round(df['Close'].iloc[-1],2), "Change%": round(chg,2)})
        except: pass
    df_all = pd.DataFrame(data).sort_values("Change%", ascending=False)
    return df_all.head(5), df_all.tail(5).sort_values("Change%")

@st.cache_data(ttl=300)
def load_data(tick, per):
    df = yf.download(tick, period=per, interval="1d", auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    return df

def rsi_calc(data,w=14):
    delta=data['Close'].diff()
    gain=(delta.where(delta>0,0)).rolling(window=w).mean()
    loss=(-delta.where(delta<0,0)).rolling(window=w).mean()
    rs=gain/loss
    return 100-(100/(1+rs))

# --- TAB 1: MARKET ---
with tab1:
    st.subheader("🌍 Market Overview - LIVE")
    m1,m2,m3 = st.columns([2,2,3])
    try:
        nifty_live, bank_live = get_market_data()
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
        m1.metric("NIFTY 50","Live..."); m2.metric("BANKNIFTY","Live...")
    top_gainers, top_losers = get_gainers_losers()
    with m3:
        c_g,c_l = st.columns(2)
        c_g.write("🔥 **Top Gainers**"); c_g.dataframe(top_gainers, hide_index=True, use_container_width=True)
        c_l.write("💔 **Top Losers**"); c_l.dataframe(top_losers, hide_index=True, use_container_width=True)
    st.divider()
    df = load_data(ticker, period)
    if df.empty:
        st.error(f"{ticker} ka data nahi mila"); st.stop()
    df['RSI']=rsi_calc(df); df['SMA20']=df['Close'].rolling(20).mean(); df['SMA50']=df['Close'].rolling(50).mean()
    last=df.iloc[-1]; prev=df.iloc[-2]
    c1,c2,c3,c4 = st.columns(4)
    chg=last['Close']-prev['Close']; pct=chg/prev['Close']*100
    c1.metric(f"LTP - {ticker}", f"{last['Close']:.2f}", f"{chg:.2f} ({pct:.2f}%)")
    c2.metric("RSI (14)", f"{last['RSI']:.1f}", "Overbought" if last['RSI']>70 else "Oversold" if last['RSI']<30 else "Neutral")
    c3.metric("High / Low", f"{last['High']:.2f} / {last['Low']:.2f}")
    c4.metric("Volume", f"{last['Volume']/1e6:.2f}M")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], line=dict(color='orange',width=1.5), name="SMA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA50'], line=dict(color='#00BFFF',width=1.5), name="SMA50"))
    fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)
    fig2 = go.Figure(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='violet'), name="RSI"))
    fig2.add_hline(y=70,line_dash="dash",line_color="red"); fig2.add_hline(y=30,line_dash="dash",line_color="green")
    fig2.update_layout(height=220, template="plotly_dark", title="RSI (14)", margin=dict(l=0,r=0,t=30,b=0))
    st.plotly_chart(fig2, use_container_width=True)
    buy = last['SMA20']>last['SMA50'] and 45<last['RSI']<70 and last['Close']>last['SMA20']
    sell = last['SMA20']<last['SMA50'] or last['RSI']>75
    if buy:
        signal_text="STRONG BUY"; msg=f"✅ STRONG BUY - {ticker} | Entry: {last['Close']:.2f} | Target: {last['Close']*1.03:.2f} | SL: {last['Close']*0.978:.2f}"; st.success(msg); st.balloons()
    elif sell:
        signal_text="SELL / AVOID"; msg=f"🔻 SELL / AVOID - {ticker} | Weak Trend | RSI: {last['RSI']:.1f}"; st.error(msg)
    else:
        signal_text="SIDEWAYS / WAIT"; msg=f"⚠️ SIDEWAYS / WAIT - {ticker} | RSI Neutral: {last['RSI']:.1f}"; st.warning(msg)
    st.subheader("📰 Live News")
    try:
        news=yf.Ticker(ticker).news
        if news:
            for n in news[:5]:
                title=n.get('title') or n.get('content',{}).get('title','News')
                link=n.get('link') or n.get('content',{}).get('clickThroughUrl',{}).get('url','#')
                st.markdown(f"- [{title}]({link})")
        else: st.write("News abhi available nahi hai.")
    except: st.write("News load nahi ho paya.")
    st.divider()
    def create_pdf():
        pdf=FPDF(); pdf.add_page(); pdf.set_font("Arial",'B',16)
        pdf.cell(200,10,f"FinTrade V5 PRO - {ticker}",ln=True,align='C')
        pdf.set_font("Arial",'',12); pdf.ln(10)
        pdf.cell(200,10,f"LTP: {last['Close']:.2f} | Change: {chg:.2f} ({pct:.2f}%)",ln=True)
        pdf.cell(200,10,f"RSI: {last['RSI']:.1f} | SMA20: {last['SMA20']:.2f} | SMA50: {last['SMA50']:.2f}",ln=True)
        pdf.cell(200,10,f"Signal: {signal_text}",ln=True)
        out=pdf.output(dest='S')
        return out.encode('latin-1') if isinstance(out,str) else bytes(out)
    pdf_data=create_pdf()
    col_pdf,col_wa = st.columns(2)
    with col_pdf: st.download_button("📄 Download PDF Report", data=pdf_data, file_name=f"{ticker}_report.pdf", mime="application/pdf", use_container_width=True)
    with col_wa:
        wa_text=urllib.parse.quote(f"{msg}\n\nFull Report: https://fintrade-app-nvfrcmhxdqux3qtqsfsd67.streamlit.app\n\nBy FinTrade V5")
        wa_link=f"https://wa.me/?text={wa_text}"
        st.link_button("💬 Share on WhatsApp", wa_link, use_container_width=True)

# --- TAB 2: PORTFOLIO ---
with tab2:
    st.subheader("💼 My Portfolio Tracker - Real P&L")
    if not st.session_state.portfolio:
        st.info("Left sidebar se stock add karo. Eg: RELIANCE.NS, 10 Qty, Buy 1300")
    else:
        total_pnl=0; rows=[]
        for item in st.session_state.portfolio:
            try:
                live_df = yf.download(item['Stock'], period="1d", auto_adjust=True, progress=False)
                if isinstance(live_df.columns, pd.MultiIndex): live_df.columns = live_df.columns.get_level_values(0)
                ltp = live_df['Close'].iloc[-1] if not live_df.empty else item['Buy']
                pnl = (ltp - item['Buy'])*item['Qty']
                pnl_pct = ((ltp-item['Buy'])/item['Buy'])*100
                total_pnl+=pnl
                rows.append({"Stock": item['Stock'], "Qty": item['Qty'], "Buy": item['Buy'], "LTP": round(float(ltp),2), "P&L": round(pnl,2), "P&L %": round(pnl_pct,2)})
            except: rows.append({"Stock": item['Stock'], "Qty": item['Qty'], "Buy": item['Buy'], "LTP": item['Buy'], "P&L": 0, "P&L %": 0})
        df_port = pd.DataFrame(rows)
        st.dataframe(df_port, use_container_width=True, hide_index=True)
        st.metric("Total Portfolio P&L", f"₹ {total_pnl:.2f}", f"{'Profit' if total_pnl>0 else 'Loss'}")

# --- TAB 3: OPTION CHAIN + ALERTS ---
with tab3:
    c1,c2 = st.columns([2,1])
    with c1:
        st.subheader("🔥 Live Option Chain")
        st.caption(f"For {ticker} - Next Expiry")
        try:
            tk = yf.Ticker(ticker)
            exps = tk.options
            if exps:
                sel_exp = st.selectbox("Select Expiry", exps[:6])
                oc = tk.option_chain(sel_exp)
                st.write("**CALLS**"); st.dataframe(oc.calls[['strike','lastPrice','bid','ask','volume','openInterest']].head(10), use_container_width=True, hide_index=True)
                st.write("**PUTS**"); st.dataframe(oc.puts[['strike','lastPrice','bid','ask','volume','openInterest']].head(10), use_container_width=True, hide_index=True)
                # PCR
                pcr = oc.puts['openInterest'].sum() / oc.calls['openInterest'].sum() if oc.calls['openInterest'].sum()!=0 else 0
                st.metric("PCR (Put Call Ratio)", f"{pcr:.2f}", "Bullish" if pcr>1 else "Bearish")
            else:
                st.warning("Is stock ka Option Data NSE pe available nahi hai. Try RELIANCE.NS, TCS.NS, INFY.NS")
        except Exception as e:
            st.error(f"Option Chain load nahi hua: {e}. Try RELIANCE.NS / TCS.NS")
    with c2:
        st.subheader("🔔 Price Alert System")
        st.caption("Set your target")
        alert_price = st.number_input(f"Alert Price for {ticker}", value=float(last['Close']*1.02) if 'last' in locals() else 1000.0)
        alert_type = st.selectbox("Alert Type", ["Price > Target", "Price < Target"])
        if st.button("Set Alert 🚀", use_container_width=True):
            st.success(f"Alert Set! {ticker} {alert_type} {alert_price}")
            st.balloons()
            if 'last' in locals():
                if (alert_type=="Price > Target" and last['Close']>=alert_price) or (alert_type=="Price < Target" and last['Close']<=alert_price):
                    st.error(f"🔔 ALERT TRIGGERED! {ticker} is at {last['Close']:.2f}!")
                else:
                    st.info(f"Current: {last['Close']:.2f}. We will notify you when it hits {alert_price}. (V6 me WhatsApp pe aayega)")
        st.divider()
        st.write("**Future V6:** Telegram + WhatsApp Auto Alerts")
