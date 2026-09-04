import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title='V18.9', layout='wide')
st.markdown('<h1 style="color:#00D1FF">FinTrade V18.9 - STABLE</h1>', unsafe_allow_html=True)
st.write('App started OK - No Glitch')

TICKER_MAP = {'ZOMATO':'ETERNAL.NS','PAYTM':'PAYTM.NS'}
NAME_MAP = {'ETERNAL.NS':'ZOMATO','PAYTM.NS':'PAYTM'}

def load_data(tick):
    t = yf.Ticker(tick)
    df = t.history(period='3mo', interval='1d', auto_adjust=True)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def resolve_ticker(u):
    uu = u.upper().strip()
    if uu in TICKER_MAP:
        return TICKER_MAP[uu]
    if '.NS' in uu:
        return uu
    return uu + '.NS'

def get_display_name(tick):
    if tick in NAME_MAP:
        return NAME_MAP[tick]
    return tick.replace('.NS','')

def get_signal(df):
    close = df['Close']
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
    den = 1 + rs
    div = 100 / den
    rsi = 100 - div
    exp1 = close.ewm(span=12).mean()
    exp2 = close.ewm(span=26).mean()
    macd = exp1 - exp2
    sig = macd.ewm(span=9).mean()
    last_rsi = float(rsi.iloc[-1])
    last_close = float(close.iloc[-1])
    last_ema20 = float(ema20.iloc[-1])
    last_ema50 = float(ema50.iloc[-1])
    last_macd = float(macd.iloc[-1])
    last_sig = float(sig.iloc[-1])
    score = 0
    if last_ema20 > last_ema50:
        score = score + 1
    if last_ema20 < last_ema50:
        score = score - 1
    if last_close > last_ema20:
        score = score + 1
    if last_close < last_ema20:
        score = score - 1
    if last_rsi > 60:
        score = score + 1
    if last_rsi < 40:
        score = score - 1
    if last_macd > last_sig:
        score = score + 1
    if last_macd < last_sig:
        score = score - 1
    final = 'HOLD'
    if score >= 2:
        final = 'BUY'
    if score <= -2:
        final = 'SELL'
    return final, last_rsi, score

st.sidebar.header('Settings')
ticker_input = st.sidebar.text_input('Stock', value='Zomato')
ticker = resolve_ticker(ticker_input)
display_name = get_display_name(ticker)
st.write('Ticker')
st.write(ticker)

df = load_data(ticker)
if df.empty:
    st.error('No data')
    st.stop()

last_close = float(df['Close'].iloc[-1])
support_level = float(df['Low'].tail(20).min())
resist_level = float(df['High'].tail(20).max())
signal, rsi_val, score = get_signal(df)

target_level = resist_level
stoploss_level = support_level
if signal == 'BUY':
    diff = last_close - support_level
    target_level = last_close + diff * 1.5
    stoploss_level = support_level
if signal == 'SELL':
    target_level = support_level
    stoploss_level = resist_level

ltp_r = round(last_close, 2)
tgt_r = round(target_level, 2)
sl_r = round(stoploss_level, 2)
rsi_r = round(rsi_val, 1)
sup_r = round(support_level, 2)
res_r = round(resist_level, 2)

# BIG CARD - NO HTML GLITCH
if signal == 'BUY':
    st.success(signal + ' ' + display_name)
if signal == 'HOLD':
    st.warning(signal + ' ' + display_name)
if signal == 'SELL':
    st.error(signal + ' ' + display_name)

col1 = st.columns(3)
col1[0].metric('LTP', ltp_r)
col1[1].metric('Target', tgt_r)
col1[2].metric('SL', sl_r)

col2 = st.columns(3)
col2[0].metric('Support', sup_r)
col2[1].metric('Resist', res_r)
col2[2].metric('RSI', rsi_r)

st.write('Score')
st.write(score)

# LIGHT CHART - NO PLOTLY = NO GLITCH
st.write('Price Chart - 3 Month')
st.line_chart(df['Close'])

st.write('Support Resist Levels')
line_df = pd.DataFrame()
line_df['Close'] = df['Close']
line_df['Support'] = support_level
line_df['Resist'] = resist_level
line_df['Target'] = target_level
line_df['SL'] = stoploss_level
st.line_chart(line_df)

st.write('V18.9 Loaded OK - No Glitch')
