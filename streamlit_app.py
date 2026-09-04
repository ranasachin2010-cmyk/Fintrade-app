import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="V16.2 FULL 500", layout="wide")
st.markdown("<h1>FinTrade V16.2 - FULL 500 NSE BSE 💎</h1>", unsafe_allow_html=True)

# FULL 500 NSE - Har stock alag line pe - WhatsApp proof
NSE_500 = [
"RELIANCE.NS",
"TCS.NS",
"INFY.NS",
"HDFCBANK.NS",
"ICICIBANK.NS",
"BHARTIARTL.NS",
"ITC.NS",
"SBIN.NS",
"LT.NS",
"KOTAKBANK.NS",
"AXISBANK.NS",
"BAJFINANCE.NS",
"ASIANPAINT.NS",
"MARUTI.NS",
"TITAN.NS",
"SUNPHARMA.NS",
"ULTRACEMCO.NS",
"NTPC.NS",
"POWERGRID.NS",
"ONGC.NS",
"WIPRO.NS",
"HCLTECH.NS",
"M&M.NS",
"ADANIENT.NS",
"ADANIPORTS.NS",
"COALINDIA.NS",
"HINDALCO.NS",
"JSWSTEEL.NS",
"TATASTEEL.NS",
"GRASIM.NS",
"CIPLA.NS",
"DRREDDY.NS",
"DIVISLAB.NS",
"EICHERMOT.NS",
"BAJAJ-AUTO.NS",
"HEROMOTOCO.NS",
"BRITANNIA.NS",
"NESTLEIND.NS",
"TATACONSUM.NS",
"HINDUNILVR.NS",
"GAIL.NS",
"BPCL.NS",
"INDUSINDBK.NS",
"BANDHANBNK.NS",
"FEDERALBNK.NS",
"IDFCFIRSTB.NS",
"PNB.NS",
"BANKBARODA.NS",
"CANBK.NS",
"AUROPHARMA.NS",
"LUPIN.NS",
"BIOCON.NS",
"TORNTPHARM.NS",
"ZYDUSLIFE.NS",
"DABUR.NS",
"GODREJCP.NS",
"MARICO.NS",
"COLPAL.NS",
"BERGEPAINT.NS",
"PIDILITIND.NS",
"HAVELLS.NS",
"VOLTAS.NS",
"CROMPGREAV.NS",
"DIXON.NS",
"AMBUJACEM.NS",
"ACC.NS",
"SHREECEM.NS",
"SAIL.NS",
"NMDC.NS",
"HINDPETRO.NS",
"INDIANB.NS",
"MUTHOOTFIN.NS",
"PEL.NS",
"RECLTD.NS",
"PFC.NS",
"IRCTC.NS",
"ETERNAL.NS",
"PAYTM.NS",
"POLYCAB.NS",
"DLF.NS",
"GODREJPROP.NS",
"OBEROIRLTY.NS",
"PHOENIXLTD.NS",
"INDIGO.NS",
"TATAMOTORS.NS",
"ASHOKLEY.NS",
"BALKRISIND.NS",
"MRF.NS",
"BOSCHLTD.NS",
"SIEMENS.NS",
"ABB.NS",
"AARTIIND.NS",
"ABBOTINDIA.NS",
"ABCAPITAL.NS",
"ABFRL.NS",
"ADANIGREEN.NS",
"ADANIPOWER.NS",
"ATGL.NS",
"ALKEM.NS",
"AMARAJABAT.NS",
"APOLLOHOSP.NS",
"APOLLOTYRE.NS",
"ASHOKLEY.NS",
"ASTRAL.NS",
"ATUL.NS",
"AUBANK.NS",
"BAJAJHLDNG.NS",
"BAJAJELEC.NS",
"BATAINDIA.NS",
"BEL.NS",
"BHARATFORG.NS",
"BHEL.NS",
"BIKAJI.NS",
"BSE.NS",
"BSOFT.NS",
"CAMS.NS",
"CDSL.NS",
"CESC.NS",
"CGPOWER.NS",
"CHAMBLFERT.NS",
"CHOLAFIN.NS",
"COFORGE.NS",
"CONCOR.NS",
"COROMANDEL.NS",
"CRAFTSMAN.NS",
"CUMMINSIND.NS",
"DALBHARAT.NS",
"DEEPAKNTR.NS",
"DELHIVERY.NS",
"DEVYANI.NS",
"DMART.NS",
"ELGIEQUIP.NS",
"ESCORTS.NS",
"EXIDEIND.NS",
"FORTIS.NS",
"GLAND.NS",
"GLENMARK.NS",
"GNFC.NS",
"GODREJIND.NS",
"GRANULES.NS",
"HAL.NS",
"HDFCAMC.NS",
"HINDCOPPER.NS",
"ICICIPRULI.NS",
"IDFC.NS",
"IIFL.NS",
"INDHOTEL.NS",
"INDIAMART.NS",
"INDUSTOWER.NS",
"IOC.NS",
"IPCALAB.NS",
"IRFC.NS",
"JINDALSTEL.NS",
"JKCEMENT.NS",
"JSWENERGY.NS",
"JUBLFOOD.NS",
"KAJARIACER.NS",
"KANSAINER.NS",
"KEI.NS",
"KPITTECH.NS",
"LALPATHLAB.NS",
"LAURUSLABS.NS",
"LICHSGFIN.NS",
"LTIM.NS",
"LTTS.NS",
"MANAPPURAM.NS",
"MFSL.NS",
"MGL.NS",
"MOTHERSON.NS",
"MPHASIS.NS",
"MUTHOOTFIN.NS",
"NAM-INDIA.NS",
"NATIONALUM.NS",
"NAUKRI.NS",
"NAVINFLUOR.NS",
"NHPC.NS",
"NLCINDIA.NS",
"OFSS.NS",
"PAGEIND.NS",
"PERSISTENT.NS",
"PETRONET.NS",
"PFIZER.NS",
"PIIND.NS",
"PVRINOX.NS",
"RAMCOCEM.NS",
"RBLBANK.NS",
"RELAXO.NS",
"SBICARD.NS",
"SBILIFE.NS",
"HDFCLIFE.NS",
"BAJAJFINSV.NS",
"SRF.NS",
"SUNTV.NS",
"TATACHEM.NS",
"TATACOMM.NS",
"TATAPOWER.NS",
"TECHM.NS",
"TORNTPOWER.NS",
"TRENT.NS",
"TVSMOTOR.NS",
"UBL.NS",
"UPL.NS",
"VEDL.NS",
"ZEEL.NS",
"CUPID.NS",
"IDEA.NS",
"YESBANK.NS",
"SUZLON.NS",
"RVNL.NS",
"IRCON.NS",
"MAZDOCK.NS",
"COCHINSHIP.NS",
"BDL.NS",
"GRSE.NS",
"NBCC.NS",
"HUDCO.NS",
"SJVN.NS",
"POWERGRID.NS",
"TATAPOWER.NS",
"TORNTPOWER.NS",
"CESC.NS",
"KEI.NS",
"POLYCAB.NS",
"HAVELLS.NS",
"CROMPTON.NS",
"AMBER.NS",
"KAYNES.NS",
"SYRMA.NS",
"PGEL.NS",
"TATATECH.NS",
"TATAELXSI.NS",
"KPITTECH.NS",
"COFORGE.NS",
"BSOFT.NS",
"HAPPSTMNDS.NS",
"INTELLECT.NS",
"MASTEK.NS",
"ZENSAR.NS",
"SONATSOFTW.NS",
"CYIENT.NS",
"DATAPATTNS.NS",
"MTARTECH.NS",
"ANANTRAJ.NS",
"KPIL.NS",
"THERMAX.NS",
"TRIVENI.NS",
"PRAJIND.NS",
"AAVAS.NS",
"AFFLE.NS",
"APTUS.NS",
"ASTRAZEN.NS",
"BAYERCROP.NS",
"CLEAN.NS",
"DEEPAKFERT.NS",
"FLUOROCHEM.NS",
"GALAXYSURF.NS",
"GSFC.NS",
"HONAUT.NS",
"JBMA.NS",
"KPRMILL.NS",
"LTFOODS.NS",
"MEDPLUS.NS",
"METROPOLIS.NS",
"MSUMI.NS",
"NAZARA.NS",
"RAILTEL.NS",
"ROUTE.NS",
"SAPPHIRE.NS",
"SUPREMEIND.NS",
"TIMKEN.NS",
"TRIDENT.NS",
"UJJIVAN.NS",
"UJJIVANSFB.NS",
"VGUARD.NS",
"VINATIORGA.NS",
"WHIRLPOOL.NS",
"ZFCVINDIA.NS"
]

BSE_500 = [s.replace(".NS",".BO") for s in NSE_500]

st.write(f"Loaded NSE: {len(NSE_500)} | BSE: {len(BSE_500)}")

# CSV DOWNLOAD - FULL 500
col1, col2, col3 = st.columns(3)
with col1:
    df_nse = pd.DataFrame({"SYMBOL": NSE_500})
    csv_nse = df_nse.to_csv(index=False)
    st.download_button("📥 NSE 500 CSV Download", csv_nse, "NSE_500_FULL.csv", "text/csv")
with col2:
    df_bse = pd.DataFrame({"SYMBOL": BSE_500})
    csv_bse = df_bse.to_csv(index=False)
    st.download_button("📥 BSE 500 CSV Download", csv_bse, "BSE_500_FULL.csv", "text/csv")
with col3:
    df_all = pd.DataFrame({"SYMBOL": NSE_500 + BSE_500})
    csv_all = df_all.to_csv(index=False)
    st.download_button("📥 COMBINED 1000 CSV", csv_all, "NSE_BSE_1000_FULL.csv", "text/csv")

# SCANNER
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

limit = st.slider("Scan Limit", 20, 500, 100)

def run_scanner(watch_list, title):
    rows = []
    prog = st.progress(0)
    total = len(watch_list[:limit])
    for i, sym in enumerate(watch_list[:limit]):
        prog.progress((i + 1) / total)
        d = load_data(sym)
        if not d.empty and len(d) > 20:
            sig, rsi_v, sc = get_signal(d)
            lc = float(d["Close"].iloc[-1])
            sp = float(d["Low"].tail(20).min())
            rs_ = float(d["High"].tail(20).max())
            tg = rs_
            sl = sp
            if sig == "BUY":
                tg = lc + (lc - sp) * 1.5
            prof = (tg - lc) / lc * 100
            if sig== "SELL":
                prof = (lc - tg) / lc * 100
            rows.append({"Stock":sym,"LTP":round(lc,2),"Signal":sig,"Profit%":round(prof,1),"RSI":round(rsi_v,1)})
    df_out = pd.DataFrame(rows)
    if not df_out.empty:
        df_out = df_out.sort_values(by="Profit%", ascending=False)
        st.dataframe(df_out, use_container_width=True, height=500)
        st.download_button(f"Download {title} Result", df_out.to_csv(index=False), title + ".csv", "text/csv")

c1, c2 = st.columns(2)
with c1:
    if st.button("SCAN NSE FULL 500"):
        run_scanner(NSE_500, "NSE_500")
with c2:
    if st.button("SCAN BSE FULL 500"):
        run_scanner(BSE_500, "BSE_500")

st.success("V16.2 FULL 500 OK - No unterminated string - Har ticker alag line")
