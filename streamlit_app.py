import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from fpdf import FPDF
import urllib.parse

st.set_page_config(page_title="FinTrade V12.3 FINAL", layout="wide", page_icon="💎")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');
* { font-family: 'Poppins', sans-serif; }
.stApp { background: radial-gradient(circle at 20% 20%, #0a1628 0%, #000000 100%); }
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.05)!important;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px!important;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="background: linear-gradient(90deg,#00D1FF,#FFD700);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:38px;">💎 FinTrade V12.3 - FINAL FIXED</h1>', unsafe_allow_html=True)

@st.cache_data(ttl=300)
def load_data(tick, per="6mo", interval="1d"):
    df = yf.download(tick, period=per, interval=interval, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def rsi(data, w=14):
    d = data['Close'].diff()
    g = d.where(d > 0, 0).rolling(w).mean()
    l = (-d.where(d < 0, 0)).rolling(w).mean()
    rs = g / l
    return 100 - (100 / (1 + rs))

def create_pdf(ticker, ltp, sup, res, trend):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial
