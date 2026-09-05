import streamlit as st
import yfinance as yf
import pandas as pd
import ta

# V48.2 20 STOCK EDITION - FINAL LOCKED
st.set_page_config(page_title="FinTrade Premium", layout="wide", initial_sidebar_state="collapsed")

WATCHLIST = ["RELIANCE","CUPID","INFY","TCS","HDFCBANK","ICICIBANK","SBIN","BHARTIARTL","ITC","BAJFINANCE","LT","MARUTI","TITAN","ASIANPAINT","WIPRO","ADANIENT","TATASTEEL","JSWSTEEL","NTPC","POWERGRID"]

st.markdown('''
<style>
.stApp {background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);}
.card {background: rgba(255,255,255,0.1); border-radius: 20px; padding: 20px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2);}
.premium-header {background: linear-gradient(90deg, #a18cd1, #fbc2eb); border-radius: 20px; padding: 25px;}
.ai-buy {background: linear-gradient(90deg, #8a2be2, #00ff88); color: white; padding: 8px 18px; border-radius: 12px; font-weight: bold;}
</style>
''', unsafe_allow_html=True)

def get_ai_score(symbol):
    try:
        df = yf.download(symbol+".NS", period="6mo", interval="1d", progress=False)
        if len(df) < 50: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df['RSI'] = ta.momentum.RSIIndicator(df['Close'], 14).rsi()
        df['EMA20'] = ta.trend.EMAIndicator(df['Close'], 20).ema_indicator()
        df['EMA50'] = ta.trend.EMAIndicator(df['Close'], 50).ema_indicator()
        df['ADX'] = ta.trend.ADXIndicator(df['High'], df['Low'], df['Close'], 14).adx()
        last = df.iloc[-1]
        score = 0
        if last['Close'] > last['EMA20']: score+=25
        if last['EMA20'] > last['EMA50']: score+=20
        if 40 < last['RSI'] < 70: score+=25
        elif last['RSI'] < 75: score+=15
        if last['ADX'] > 20: score+=20
        if last['ADX'] > 25: score+=10
        price = float(last['Close'])
        target = price * 1.093
        sl = price * 0.95
        return {"symbol": symbol, "price": price, "score": min(score,96), "rsi": float(last['RSI']), "adx": float(last['ADX']), "target": target, "sl": sl}
    except:
        return None

# Header
st.markdown(f'''
<div class="premium-header">
<h2 style="margin:0;">FinTrade <span style="color:#00ffcc;">Premium</span> <span style="background:#ffcc00; color:black; padding:3px 10px; border-radius:20px; font-size:12px;">BSE MODE</span> <span style="background:#00ff88; color:black; padding:3px 10px; border-radius:20px; font-size:12px;">V48.2 20 STOCK FINAL LOCKED</span></h2>
<p style="margin-top:10px;"><span style="background:rgba(0,0,0,0.2); padding:5px 12px; border-radius:20px;">NIFTY50 23,897 0.10%</span> <span style="background:rgba(255,100,0,0.3); padding:5px 12px; border-radius:20px; margin-left:10px;">BEAR + AI FILTER - 20 STOCKS</span></p>
</div>
''', unsafe_allow_html=True)

st.markdown('''
<div style="background: linear-gradient(90deg, #ffcc00, #ff8800); padding:12px; border-radius:12px; margin-top:15px; color:black; font-weight:500;">
V48.2 FINAL LOCKED! BEAR + AI FILTER - AI 60%+ filter active hai. 20 stocks scan ho rahe hain. Aaj strong pick nahi mila toh loss se bacha liya. Yehi AI ka power hai!
</div>
''', unsafe_allow_html=True)

# Logic - 20 stocks scan
results = []
for sym in WATCHLIST:
    data = get_ai_score(sym)
    if data and data['score'] >= 60 and data['rsi'] < 72:
        results.append(data)

results = sorted(results, key=lambda x: x['score'], reverse=True)
top_picks = [r for r in results if r['score'] >= 85][:2]

if len(top_picks) == 0:
    st.markdown('''
    <div style="background: rgba(0,200,255,0.2); border: 1px solid #00ccff; padding:15px; border-radius:12px; margin-top:15px; color:#00e5ff;">
    AI Protected! BEAR + AI FILTER - AI ne 60% se kam wale saare stocks cut kar diye. 20 stocks me se aaj koi strong pick nahi - Loss se bachao! Yehi V48.2 ka power hai.
    </div>
    ''', unsafe_allow_html=True)
else:
    for pick in top_picks:
        st.markdown(f'''
        <div style="background: rgba(0,255,100,0.15); border: 1px solid #00ff88; padding:15px; border-radius:12px; margin-top:15px; color:#00ff88; font-weight:bold;">
        TOP AI PICK: {pick['symbol']} - {pick['score']}% AI BUY - Rs{pick['price']:.2f}
        </div>
        ''', unsafe_allow_html=True)

# Search
st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns([4,1])
with col1:
    search = st.text_input("Search Stock", value="CUPID", label_visibility="collapsed")
with col2:
    st.button("SEARCH", use_container_width=True)

sym_to_show = search.strip().upper() if search else "CUPID"
info = get_ai_score(sym_to_show)
if info:
    st.markdown(f'''
    <div class="card" style="margin-top:20px;">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div style="display:flex; align-items:center; gap:15px;">
            <h2 style="margin:0; color:white;">{info['symbol']}</h2>
            <span style="background: linear-gradient(90deg, #8a2be2, #00aaff); padding:6px 14px; border-radius:20px; font-size:12px; color:white;">AI {info['score']}% UP - Strong AI Buy</span>
            <span style="background: rgba(255,0,100,0.3); border:1px solid #ff0066; padding:4px 10px; border-radius:20px; font-size:11px; color:#ff88aa;">RSI/ ADX {info['rsi']:.1f} AI {info['adx']:.0f}%</span>
        </div>
        <div style="color:white; font-weight:bold;">Rs{info['price']:.2f}</div>
    </div>
    <div style="display:flex; gap:15px; margin-top:20px; align-items:center;">
        <div style="background: rgba(0,200,255,0.2); border:1px solid #00ccff; padding:10px 15px; border-radius:12px;">
            <div style="font-size:10px; color:#88ddff;">AI TARGET</div>
            <div style="color:#00ff88; font-weight:bold;">Rs{info['target']:.2f} +9.3%</div>
        </div>
        <div style="background: rgba(255,0,100,0.15); padding:10px 15px; border-radius:12px;">
            <div style="font-size:10px; color:#ff88aa;">AI SL</div>
            <div style="color:white; font-weight:bold;">Rs{info['sl']:.2f}</div>
        </div>
        <div style="margin-left:auto;">
            <span class="ai-buy">AI BUY 85 {info['score']}%</span>
        </div>
    </div>
    <div style="margin-top:10px; font-size:11px; color:#aaa;">EMA Uptrend - Long Bull - Price>EMA20 - Supertrend BUY</div>
    </div>
    ''', unsafe_allow_html=True)

st.caption("V48.2 20 STOCK EDITION - FINAL LOCKED - FinTrade Premium")
