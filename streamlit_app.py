with tab_chart:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import numpy as np

    df_c = df.tail(100).copy()
    close = df_c["Close"]

    # INDICATORS
    ema20 = close.ewm(span=20).mean()
    ema50 = close.ewm(span=50).mean()
    ema200 = close.ewm(span=200).mean() if len(close)>50 else ema50

    # RSI for momentum
    delta = close.diff()
    gain = (delta.where(delta>0, 0)).rolling(14).mean()
    loss = (-delta.where(delta<0, 0)).rolling(14).mean()
    rs = gain / loss.replace(0, 0.001)
    rsi = 100 - (100 / (1 + rs))

    # Support / Resistance
    sup = float(df_c["Low"].tail(20).min())
    res = float(df_c["High"].tail(20).max())

    # Trend detection
    trend = "UPTREND" if ema20.iloc[-1] > ema50.iloc[-1] and close.iloc[-1] > ema20.iloc[-1] else "DOWNTREND" if ema20.iloc[-1] < ema50.iloc[-1] else "SIDEWAYS"
    trend_color = "#00FF88" if "UP" in trend else "#FF4D6A" if "DOWN" in trend else "#FFAA00"

    # Price Range
    price_range = res - sup
    range_mid = (res + sup)/2

    # FIGURE with 2 rows - Chart + RSI
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06, row_heights=[0.75, 0.25],
                        subplot_titles=(f"{raw} - {trend} | Range Rs {round(sup,2)} - {round(res,2)}", "MOMENTUM RSI"))

    # Candles
    fig.add_trace(go.Candlestick(x=df_c.index, open=df_c["Open"], high=df_c["High"], low=df_c["Low"], close=df_c["Close"],
                                 name="Price", increasing_line_color="#00FF88", decreasing_line_color="#FF4D6A",
                                 increasing_fillcolor="#00FF88", decreasing_fillcolor="#FF4D6A"), row=1, col=1)

    # EMA Lines - Bullish Bearish
    fig.add_trace(go.Scatter(x=df_c.index, y=ema20, line=dict(color="#00D1FF", width=2), name="EMA20 Bullish Line"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=ema50, line=dict(color="#FFAA00", width=2, dash="dash"), name="EMA50 Bearish Line"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df_c.index, y=ema200, line=dict(color="#7000FF", width=1, dash="dot"), name="EMA200 Long Trend"), row=1, col=1)

    # Support / Resistance + Price Range
    fig.add_hline(y=sup, line=dict(color="#00FF88", width=1, dash="dot"), annotation_text=f"SL/Support {round(sup,2)}", row=1, col=1)
    fig.add_hline(y=res, line=dict(color="#FF4D6A", width=1, dash="dot"), annotation_text=f"Target/Resistance {round(res,2)}", row=1, col=1)
    fig.add_hrect(y0=sup, y1=res, fillcolor="rgba(0,209,255,0.06)", line_width=0, row=1, col=1)

    # Uptrend / Downtrend Line
    x0, x1 = df_c.index[0], df_c.index[-1]
    if "UP" in trend:
        fig.add_trace(go.Scatter(x=[x0, x1], y=[sup, close.iloc[-1]], mode="lines", line=dict(color="#00FF88", width=2, dash="dash"), name="Uptrend Line"), row=1, col=1)
    elif "DOWN" in trend:
        fig.add_trace(go.Scatter(x=[x0, x1], y=[res, close.iloc[-1]], mode="lines", line=dict(color="#FF4D6A", width=2, dash="dash"), name="Downtrend Line"), row=1, col=1)

    # RSI Momentum
    fig.add_trace(go.Scatter(x=df_c.index, y=rsi, line=dict(color="#C084FC", width=2), name="RSI Momentum"), row=2, col=1)
    fig.add_hline(y=70, line=dict(color="#FF4D6A", dash="dash"), row=2, col=1)
    fig.add_hline(y=30, line=dict(color="#00FF88", dash="dash"), row=2, col=1)
    fig.add_hline(y=50, line=dict(color="#8892b0", dash="dot"), row=2, col=1)

    # Bullish/Bearish background for RSI
    fig.add_hrect(y0=70, y1=100, fillcolor="rgba(255,77,106,0.15)", line_width=0, row=2, col=1)
    fig.add_hrect(y0=0, y1=30, fillcolor="rgba(0,255,136,0.15)", line_width=0, row=2, col=1)

    fig.update_layout(
        template="plotly_dark",
        height=650,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_rangeslider_visible=False,
        showlegend=True,
        legend=dict(orientation="h", y=1.02, x=0, font=dict(size=10)),
        margin=dict(l=0,r=0,t=30,b=0),
        dragmode="zoom", # Two finger zoom enable
        hovermode="x unified"
    )

    # Two finger zoom + pan enable
    config = {
        'scrollZoom': True,
        'doubleClick': 'reset',
        'modeBarButtonsToAdd': ['drawline','drawrect','eraseshape'],
        'displaylogo': False
    }

    st.plotly_chart(fig, use_container_width=True, config=config)

    # INFO CARDS
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.metric("📈 TREND", trend, delta=f"EMA20 {round(ema20.iloc[-1],1)}")
    with c2:
        st.metric("💪 MOMENTUM", f"RSI {round(rsi.iloc[-1],1)}", delta="Bullish" if rsi.iloc[-1]>50 else "Bearish")
    with c3:
        st.metric("📦 PRICE RANGE", f"Rs {round(price_range,2)}", delta=f"{round(sup,2)} - {round(res,2)}")
    with c4:
        st.metric("🎯 BULL/BEAR", "BULLISH" if close.iloc[-1]>ema20.iloc[-1] else "BEARISH", delta=f"LTP {round(close.iloc[-1],2)}")

    st.caption("👆 Two finger se zoom karo, drag karke pan karo, double tap pe reset - Mobile/Tablet pe full touch support!")

    # TradingView with same features
    bse_sym = ticker.replace(".NS","").replace(".BO","")
    st.markdown(f"#### TradingView Pro - {raw}")
    st.components.v1.iframe(f"https://s.tradingview.com/widgetembed/?symbol=BSE%3A{bse_sym}&interval=D&theme=dark&hide_top_toolbar=0&withdateranges=1&studies=EMA%2CMACD%2CRSI", height=500)
