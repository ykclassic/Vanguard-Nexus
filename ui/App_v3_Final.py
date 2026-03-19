# Inside ui/App_v3_Final.py -> render_zenith_chart function
def render_zenith_chart(ticker, intel):
    cp = intel.get('current_price', 0)
    if cp == 0:
        st.warning("⚠️ Waiting for live price feed from Alpha Vantage...")
        return

    # Create a small artificial range around the price for visual context
    prices = [cp * (1 + (i * 0.0005)) for i in range(-10, 11)]
    
    fig = go.Figure(data=[go.Scatter(x=list(range(len(prices))), y=prices, name="Spot Price")])
    
    zones = intel['zones']
    fig.add_hline(y=zones['entry'], line_dash="dot", line_color="cyan", annotation_text="ENTRY")
    fig.add_hline(y=zones['tp'], line_dash="dash", line_color="green", annotation_text="TP")
    fig.add_hline(y=zones['sl'], line_dash="dash", line_color="red", annotation_text="SL")

    fig.update_layout(template="plotly_dark", height=400, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)
