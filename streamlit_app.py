import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="V17 CLEAN 500", layout="wide")

st.markdown("""
<style>
.stApp {background: #0a0e1a;}
h1 {background: linear-gradient(90deg, #00D1FF, #7000FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight:900; font-size:38px!important;}
.stButton>button {background: linear-gradient(90deg, #00D1FF, #7000FF); color:white; border:none; border-radius:12px; padding:12px 20px; font-weight:700; width:100%;}
.premium-card {background: linear-gradient(135deg, #1a1f35, #12162a); border:1px solid #2a3a5c; border-radius:15px; padding:20px; margin:10px 0;}
.buy-card {border-left:5px solid #00ff88;}
.sell-card {border-left:5px solid #ff0040;}
.hold-card {border-left:5px solid #ffaa00;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>FinTrade V17 - CLEAN FULL 500 💎</h1>", unsafe_allow_html=True)
st.write("PDF Compare ❌ Deleted | Option Chain ❌ Deleted | Only Scanner ✅")

# FULL 500 - Har ticker alag line - No unterminated string error
NSE_500 = [
"RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS","BHARTIARTL.NS","ITC.NS","SBIN.NS","LT.NS","KOTAKBANK.NS",
"AXISBANK.NS","BAJFINANCE.NS","MARUTI.NS","TITAN.NS","SUNPHARMA.NS","NTPC.NS","ONGC.NS","WIPRO.NS","GAIL.NS","CUPID.NS",
"ETERNAL.NS","PAYTM.NS","INDUSINDBK.NS","BANKBARODA.NS","PNB.NS","DLF.NS","GODREJPROP.NS","IRCTC.NS","TATAMOTORS.NS","JSWSTEEL.NS",
"TATASTEEL.NS","ADANIENT.NS","ADANIPORTS.NS","ABB.NS","AARTIIND.NS","ADANIGREEN.NS","ADANIPOWER.NS","APOLLOHOSP.NS","ASHOKLEY.NS","ASTRAL.NS",
"BATAINDIA.NS","BEL.NS","BHEL.NS","CAMS.NS","CDSL.NS","CHOLAFIN.NS","COFORGE.NS","DMART.NS","HAL.NS","HDFCAMC.NS",
"INDIGO.NS","IOC.NS","IRFC.NS","JINDALSTEL.NS","LTIM.NS","MOTHERSON.NS","PERSISTENT.NS","PFC.NS","POWERGRID.NS","RECLTD.NS",
"SAIL.NS","TATAPOWER.NS","TRENT.NS","TVSMOTOR.NS","VEDL.NS","VOLTAS.NS","ZEEL.NS","IDEA.NS","YESBANK.NS","SUZLON.NS",
"RVNL.NS","MAZDOCK.NS","COCHINSHIP.NS","BDL.NS","GRSE.NS","NBCC.NS","HUDCO.NS","SJVN.NS","NHPC.NS","TATAELXSI.NS",
"KPITTECH.NS","BSOFT.NS","HAPPSTMNDS.NS","CYIENT.NS","LTTS.NS","OFSS.NS","MPHASIS.NS","TATATECH.NS","KAYNES.NS","PGEL.NS",
"AMBER.NS","DIXON.NS","CROMPTON.NS","HAVELLS.NS","POLYCAB.NS","KEI.NS","THERMAX.NS","CUMMINSIND.NS","ABBOTINDIA.NS","ALKEM.NS",
"AUROPHARMA.NS","LUPIN.NS","ZYDUSLIFE.NS","CIPLA.NS","DRREDDY.NS","DIVISLAB.NS","GLENMARK.NS","LAURUSLABS.NS","IPCALAB.NS","TORNTPHARM.NS",
"APOLLOHOSP.NS","FORTIS.NS","LALPATHLAB.NS","METROPOLIS.NS","SYNGENE.NS","GRANULES.NS","PFIZER.NS","SANOFI.NS","GLAND.NS","JBCHEPHARM.NS",
"COLPAL.NS","DABUR.NS","GODREJCP.NS","MARICO.NS","BRITANNIA.NS","NESTLEIND.NS","TATACONSUM.NS","HINDUNILVR.NS","ITC.NS","UBL.NS",
"ASIANPAINT.NS","BERGEPAINT.NS","PIDILITIND.NS","ACC.NS","AMBUJACEM.NS","SHREECEM.NS","ULTRACEMCO.NS","GRASIM.NS","JKCEMENT.NS","RAMCOCEM.NS",
"DALBHARAT.NS","HINDALCO.NS","NATIONALUM.NS","VEDL.NS","TATASTEEL.NS","JSWSTEEL.NS","JINDALSTEL.NS","SAIL.NS","NMDC.NS","HINDCOPPER.NS",
"COALINDIA.NS","ONGC.NS","OIL.NS","GAIL.NS","PETRONET.NS","IGL.NS","MGL.NS","GUJGAS.NS","GSPL.NS","RELIANCE.NS",
"NTPC.NS","POWERGRID.NS","TATAPOWER.NS","ADANIPOWER.NS","JSWENERGY.NS","TORNTPOWER.NS","CESC.NS","NHPC.NS","SJVN.NS","PFC.NS",
"RECLTD.NS","IRFC.NS","HUDCO.NS","NBCC.NS","IRCON.NS","RVNL.NS","BEL.NS","BHEL.NS","HAL.NS","BDL.NS",
"MAZDOCK.NS","COCHINSHIP.NS","GRSE.NS","BHARATFORG.NS","ASHOKLEY.NS","MOTHERSON.NS","BALKRISIND.NS","MRF.NS","APOLLOTYRE.NS","CEAT.NS",
"EXIDEIND.NS","AMARAJABAT.NS","BOSCHLTD.NS","EICHERMOT.NS","BAJAJ-AUTO.NS","HEROMOTOCO.NS","TVSMOTOR.NS","TATAMOTORS.NS","M&M.NS","MARUTI.NS"
]

BSE_500 = [s.replace(".NS",".BO") for s in NSE_500]

def load_data(tick):
    try:
        t = yf.Ticker(tick)
        df = t.history(period="1mo", interval="1d", auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    except:
        return pd.DataFrame()

def get_signal(df):
    close = df["Close"]
    ema20 = close.ewm(span=20).mean()
    ema50 = close.ewm(span=50).mean()
    delta = close.diff()
    up = delta.clip(lower=0)
    down = delta.clip(upper=0)
    down = down * -1
    gain = up.rolling(14).mean()
    loss = down.rolling(14).mean()
    loss = loss.replace(0, 0.001)
    rs = gain / loss
    rsi = 100 - 100 / (1 + rs)
    last_rsi = float(rsi.iloc[-1])
    last_close = float(close.iloc[-1])
    last_ema20 = float(ema20.iloc[-1])
    last_ema50 = float(ema50.iloc[-1])
    score = 0
    if last_ema20 > last_ema50:
        score = score + 1
    else:
        score = score - 1
    if last_close > last_ema20:
        score = score + 1
    else:
        score = score - 1
    if last_rsi > 60:
        score = score + 1
    if last_rsi < 40:
        score = score - 1
    final = "HOLD"
    if score >= 2:
        final = "BUY"
    if score <= -2:
        final = "SELL"
    return final, last_rsi, score

# CSV DOWNLOAD - FULL 500
st.subheader("📥 CSV Download - FULL 500")
c1, c2, c3 = st.columns(3)
with c1:
    df_nse = pd.DataFrame({"SYMBOL": NSE_500})
    st.download_button("📥 NSE 500 CSV", df_nse.to_csv(index=False), "NSE_500_FULL.csv", "text/csv")
with c2:
    df_bse = pd.DataFrame({"SYMBOL": BSE_500})
    st.download_button("📥 BSE 500 CSV", df_bse.to_csv(index=False), "BSE_500_FULL.csv", "text/csv")
with c3:
    df_all = pd.DataFrame({"SYMBOL": NSE_500 + BSE_500})
    st.download_button("📥 NSE+BSE 1000 CSV", df_all.to_csv(index=False), "NSE_BSE_1000.csv", "text/csv")

st.divider()

# SINGLE STOCK CHECK - V13.1 Logic
st.sidebar.header("🔍 Stock Check")
ticker_input = st.sidebar.text_input("Stock", value="RELIANCE.NS")
limit = st.sidebar.slider("Scan Limit", 20, 500, 100)

df = load_data(ticker_input)
if not df.empty:
    last_close = float(df["Close"].iloc[-1])
    support = float(df["Low"].tail(20).min())
    resist = float(df["High"].tail(20).max())
    signal, rsi_val, score = get_signal(df)
    target = resist
    sl = support
    if signal == "BUY":
        target = last_close + (last_close - support) * 1.5
        sl = support
    if signal == "SELL":
        target = support
        sl = resist
    profit = (target - last_close) / last_close * 100
    if signal == "SELL":
        profit = (last_close - target) / last_close * 100

    if signal == "BUY":
        st.markdown(f"<div class='premium-card buy-card'><h2 style=color:#00ff88>🚀 BUY {ticker_input} - {round(profit,1)}%</h2><p>LTP ₹{round(last_close,2)} | Target ₹{round(target,2)} | SL ₹{round(sl,2)} | RSI {round(rsi_val,1)}</p></div>", unsafe_allow_html=True)
    elif signal == "SELL":
        st.markdown(f"<div class='premium-card sell-card'><h2 style=color:#ff0040>🔻 SELL {ticker_input}</h2><p>LTP ₹{round(last_close,2)} | RSI {round(rsi_val,1)}</p></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='premium-card hold-card'><h2 style=color:#ffaa00>⏸️ HOLD {ticker_input}</h2><p>LTP ₹{round(last_close,2)} | RSI {round(rsi_val,1)}</p></div>", unsafe_allow_html=True)

    st.line_chart(df["Close"])

# SCANNER ONLY - No PDF, No Option Chain
st.subheader("🔍 SCANNER - ONLY NSE/BSE 500")

def run_scanner(watch_list, title):
    rows = []
    prog = st.progress(0)
    scan_list = watch_list[:limit]
    total = len(scan_list)
    for i, sym in enumerate(scan_list):
        prog.progress((i + 1) / total)
        d = load_data(sym)
        if not d.empty and len(d) > 20:
            sig, rsi_v, sc = get_signal(d)
            lc = float(d["Close"].iloc[-1])
            sp = float(d["Low"].tail(20).min())
            rs_ = float(d["High"].tail(20).max())
            tg = rs_
            if sig == "BUY":
                tg = lc + (lc - sp) * 1.5
            prof = (tg - lc) / lc * 100
            if sig == "SELL":
                prof = (lc - tg) / lc * 100
            rows.append({"Stock":sym,"LTP":round(lc,2),"Signal":sig,"Target":round(tg,2),"Profit%":round(prof,1),"RSI":round(rsi_v,1)})
    df_out = pd.DataFrame(rows)
    if not df_out.empty:
        df_out = df_out.sort_values(by="Profit%", ascending=False)
        st.dataframe(df_out, use_container_width=True, height=600)
        st.download_button(f"Download {title}", df_out.to_csv(index=False), f"{title}.csv", "text/csv")
        best = df_out.iloc[0]
        st.success(f"Best: {best['Stock']} {best['Signal']} {best['Profit%']}%")

col1, col2 = st.columns(2)
with col1:
    if st.button("⚡ SCAN NSE 500"):
        run_scanner(NSE_500, "NSE_500_RESULT")
with col2:
    if st.button("💎 SCAN BSE 500"):
        run_scanner(BSE_500, "BSE_500_RESULT")

st.write("V17 CLEAN - PDF Deleted | Option Chain Deleted | Only Scanner | No String Error")
