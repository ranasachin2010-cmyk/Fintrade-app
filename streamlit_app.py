    fig.update_layout(template="plotly_dark", height=850, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis_rangeslider_visible=False, showlegend=True, legend=dict(orientation="h", y=1.01, x=0, font=dict(size=9)), margin=dict(l=0,r=0,t=35,b=0), dragmode=False, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'scrollZoom': True, 'doubleClick': 'reset', 'displaylogo': False})
    
    # TRADINGVIEW WAPAS ADD - YE LINE ADD KARO
    bse_sym = ticker.replace(".NS","").replace(".BO","")
    st.markdown("### 📊 TradingView Live")
    st.components.v1.iframe(f"https://s.tradingview.com/widgetembed/?symbol=BSE%3A{bse_sym}&interval=D&theme=dark&studies=Supertrend%40tv-basicstudies%2CMACD%40tv-basicstudies%2CRSI%40tv-basicstudies", height=500)

    st.success("✅ Green toolbar + Grey box hata diye - TradingView wapas aa gaya!")
