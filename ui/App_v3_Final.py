import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import os
from datetime import datetime

# --- PATH INJECTOR: Fixes ModuleNotFoundError on Streamlit Cloud ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.DataIngestor import FinancialDataIngestor
from services.InferenceWorker import InferenceWorker

# --- Page Configuration ---
st.set_page_config(
    page_title="Vanguard Nexus: Zenith Command",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

def apply_zenith_theme():
    """Applies high-fidelity 'War Room' styling."""
    st.markdown("""
    <style>
    .stApp { background-color: #050b18; color: #e2e8f0; }
    [data-testid="stMetricValue"] { font-size: 32px !important; color: #38bdf8 !important; font-weight: 700; }
    .stStatus { background: rgba(59, 130, 246, 0.05); border: 1px solid #1e40af; border-radius: 10px; }
    
    /* Signal Box Styling */
    .signal-card {
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #3b82f6;
        background: rgba(59, 130, 246, 0.1);
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .signal-text { font-size: 24px; font-weight: 800; letter-spacing: 1.5px; }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] { background-color: #0f172a !important; }
    </style>
    """, unsafe_allow_html=True)

def render_tactical_chart(ticker, intel):
    """Plots interactive price lines with overlaid SL, Entry, and TP zones."""
    cp = intel.get('current_price', 0)
    zones = intel.get('zones', {"entry": 0, "sl": 0, "tp": 0})
    
    if cp == 0:
        st.warning("⚠️ Tactical Chart unavailable: Spot price is 0. Check API limits.")
        return

    # Create visual context around the spot price
    # We use a Scatter plot for a clean 'Zenith' look
    y_points = [cp * (1 + (i * 0.0002)) for i in range(-20, 21)]
    x_points = list(range(len(y_points)))

    fig = go.Figure()

    # Base Price Line
    fig.add_trace(go.Scatter(
        x=x_points, y=y_points,
        mode='lines',
        line=dict(color='#3b82f6', width=1),
        name="Market Flux",
        hoverinfo='skip'
    ))

    # Tactical Overlays
    fig.add_hline(y=zones['entry'], line_dash="dot", line_color="#0ea5e9", 
                  annotation_text="ENTRY", annotation_position="top left")
    
    fig.add_hline(y=zones['tp'], line_dash="dash", line_color="#22c55e", 
                  annotation_text="TAKE PROFIT (TARGET)", annotation_position="top right")
    
    fig.add_hline(y=zones['sl'], line_dash="dash", line_color="#ef4444", 
                  annotation_text="STOP LOSS (RISK)", annotation_position="bottom right")

    fig.update_layout(
        title=f"🛡️ Zenith Tactical Analysis: {ticker}",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(l=20, r=20, t=50, b=20),
        height=450,
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", zeroline=False)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def main():
    apply_zenith_theme()
    
    # --- Sidebar Control Center ---
    with st.sidebar:
        st.image("https://i.imgur.com/4M34hi2.png", width=80) # Placeholder for Nexus Logo
        st.title("Nexus Control")
        st.divider()
        
        # Priority 1: API Key Handling
        env_key = os.getenv("ALPHAVANTAGE_API_KEY", "")
        api_key = st.text_input("Alpha Vantage Key", type="password", value=env_key)
        
        # Asset Selection
        target_asset = st.selectbox("Sentry Target", ["BTC", "ETH", "SOL", "XAU", "AAPL"])
        
        # Operational Trigger
        initiate = st.button("🚀 INITIATE ZENITH CYCLE", use_container_width=True)
        
        st.divider()
        st.info(f"System Time: {datetime.now().strftime('%H:%M:%S UTC')}")

    # --- Main Dashboard ---
    st.title("🛡️ Vanguard Nexus: Zenith Command")
    st.caption("Advanced Confluence Engine • Sentiment + Technical Intelligence")

    if initiate:
        if not api_key:
            st.error("🚨 System Failure: API Key is required for data ingestion.")
            return

        # Initialize Services
        ingestor = FinancialDataIngestor(api_key)
        worker = InferenceWorker()

        with st.status(f"Synchronizing Zenith Channels for {target_asset}...") as status:
            # Step 1: Ingest News
            raw_news = ingestor.fetch_latest_news(target_asset)
            # Step 2: Execute Brain Logic (Price + RSI + Sentiment)
            intel = worker.process_pending_data(raw_news, ticker=target_asset)
            status.update(label="Zenith Confluence Established", state="complete")

        if intel and intel.get('current_price', 0) > 0:
            # 1. Main Signal Display
            signal_color = "#22c55e" if "BUY" in intel.get('confluence_signal', "") else "#ef4444" if "SELL" in intel.get('confluence_signal', "") else "#3b82f6"
            
            st.markdown(f"""
                <div class="signal-card" style="border-color: {signal_color}">
                    <div class="signal-text" style="color: {signal_color}">
                        {intel.get('confluence_signal', 'NEUTRAL').upper()}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # 2. Key Metric Grid
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Current Spot", f"${intel['current_price']:,.2f}")
            m2.metric("RSI (14)", intel['rsi'], delta="Oversold" if intel['rsi'] < 30 else "Overbought" if intel['rsi'] > 70 else "Neutral")
            m3.metric("Agg. Sentiment", f"{intel['aggregate_score']}", delta=intel['sentiment_label'])
            m4.metric("Market Volatility", f"{round(intel['volatility']*100, 2)}%")

            # 3. Visualization
            render_tactical_chart(target_asset, intel)

            # 4. Tactical Execution Ticket
            st.subheader("⚡ Tactical Execution Ticket")
            t1, t2, t3 = st.columns(3)
            with t1:
                st.metric("ENTRY ZONE", f"${intel['zones']['entry']:,.2f}")
            with t2:
                st.metric("TAKE PROFIT (TP)", f"${intel['zones']['tp']:,.2f}", delta="Expected Gain", delta_color="normal")
            with t3:
                st.metric("STOP LOSS (SL)", f"${intel['zones']['sl']:,.2f}", delta="Max Risk", delta_color="inverse")

        else:
            st.error("📡 Connection Interrupted: Alpha Vantage API is not returning price data.")
            st.info("Wait 60 seconds (Rate Limit) or check your API Key status in Alpha Vantage dashboard.")

if __name__ == "__main__":
    main()
