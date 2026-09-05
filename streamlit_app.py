    # BOX SELECTION HATA DIYA - SIRF PINCH ZOOM RAHEGA
    fig.update_layout(
        template="plotly_dark", 
        height=850, 
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)", 
        xaxis_rangeslider_visible=False, 
        showlegend=True, 
        legend=dict(orientation="h", y=1.01, x=0, font=dict(size=9)), 
        margin=dict(l=0,r=0,t=35,b=0), 
        dragmode=False,  # <-- BOX WALA HATA DIYA
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True, config={
        'displayModeBar': False, 
        'scrollZoom': True, 
        'doubleClick': 'reset', 
        'displaylogo': False,
        'modeBarButtonsToRemove': ['zoom2d','select2d','lasso2d','zoomIn2d','zoomOut2d','autoScale2d','resetScale2d']
    })
