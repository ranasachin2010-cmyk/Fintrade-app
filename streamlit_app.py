# ===== V15 WATCHLIST UPGRADE - Is code ko tab7 me replace karo =====
with tab7:
    st.markdown('##### ⭐ NIFTY 50 WATCHLIST KING')
    
    # Nifty 50 full list
    nifty50 = ['RELIANCE.NS','TCS.NS','INFY.NS','HDFCBANK.NS','ICICIBANK.NS','SBIN.NS','BHARTIARTL.NS','ITC.NS','LT.NS','KOTAKBANK.NS','AXISBANK.NS','ASIANPAINT.NS','MARUTI.NS','WIPRO.NS','HCLTECH.NS','TITAN.NS','BAJFINANCE.NS','SUNPHARMA.NS','ONGC.NS','NTPC.NS','TATAMOTORS.NS','TATASTEEL.NS','ADANIENT.NS','POWERGRID.NS','ULTRACEMCO.NS','JSWSTEEL.NS','M&M.NS','HINDUNILVR.NS','NESTLEIND.NS','GRASIM.NS']
    
    col1,col2 = st.columns([3,1])
    with col1:
        new_stock = st.text_input('Add NSE Stock (e.g. PAYTM, ZOMATO, IRCTC)', placeholder='STOCK NAME').upper().strip()
    with col2:
        st.write('')
        st.write('')
        if st.button('➕ Add to Watchlist', use_container_width=True):
            if new_stock:
                full = new_stock if '.NS' in new_stock else new_stock + '.NS'
                if full not in st.session_state.watchlist:
                    st.session_state.watchlist.append(full)
                    st.success(f'{full} added!')
                    st.rerun()
    
    # Quick Add Buttons
    st.write('**Quick Add Nifty 50:**')
    q1,q2,q3,q4,q5 = st.columns(5)
    for i, stk in enumerate(nifty50[:25]):
        if [q1,q2,q3,q4,q5][i%5].button(stk.replace('.NS',''), key=f'q_{stk}'):
            if stk not in st.session_state.watchlist:
                st.session_state.watchlist.append(stk)
                st.rerun()
    
    if st.button('📊 Load Full Watchlist 52W Data', use_container_width=True):
        rows=[]
        prog = st.progress(0)
        for idx, s in enumerate(st.session_state.watchlist):
            d = load_data(s, per='1y')
            if not d.empty:
                ltp = float(d['Close'].iloc[-1])
                high = float(d['High'].max())
                low = float(d['Low'].min())
                near = '🔥 Near High' if (high-ltp)/high < 0.05 else '💎 Near Low' if (ltp-low)/low < 0.05 else ''
                rows.append({'Stock':s, 'LTP':round(ltp,2), '52W High':round(high,2), '52W Low':round(low,2), 'Signal':near})
            prog.progress((idx+1)/len(st.session_state.watchlist))
        df_watch = pd.DataFrame(rows)
        st.dataframe(df
