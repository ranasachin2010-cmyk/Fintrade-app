import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from fpdf import FPDF
import urllib.parse

st.set_page_config(page_title='FinTrade V14 PREMIUM INDIAN', layout='wide', page_icon='💎')

# ============ PREMIUM CSS - GLASSMORPHISM ============
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');
* { font-family: 'Poppins', sans-serif; }
.stApp { background: radial-gradient(circle at 20% 20%, #0a1628 0%, #050a14 40%, #000000 100%); }
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.05)!important;
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px!important;
    box-shadow: 0 8px 32px rgba(0,209,255,0.15);
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    background: linear-gradient(90deg, #00D1FF, #FFD700)!important;
    color: black!important;
    font-weight: 800!important;
    box-shadow: 0 0 20px rgba(0,209,255,0.5);
}
.stButton > button {
    background: linear-gradient(90deg, #00D1FF, #0080FF)!important;
    color: white!important;
    border-radius: 12px!important;
    font-weight: 700!important;
    border: none!important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="background: linear-gradient(90deg,#00D1FF,#FFD700);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:42px;">💎 FinTrade V14 PREMIUM INDIAN</h1>', unsafe_allow_html=True)
st.markdown('<p style="color:#888;letter-spacing:3px;margin-top:-15px">PREMIUM EDITION • BSE FREE + NSE REAL DATA • AYODHYA</p>', unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_data(tick, per='6mo', interval='1d'):
    df = yf.download(tick, period=per, interval=interval, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def rsi_calc(data, w=14):
    d = data['Close'].diff()
    g = d.where(d>0,0).rolling(w).mean()
    l = (-d.where(d<0,0)).rolling(w).mean()
    return 100 - (100/(1+g/l))

def make_pdf(ticker, ltp, sup, res, trend):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial','B',18)
    pdf.cell(0,10
