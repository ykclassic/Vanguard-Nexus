import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import os
from datetime import datetime

# --- PATH INJECTOR: Root access for core/services ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.DataIngestor import FinancialDataIngestor
from services.InferenceWorker import InferenceWorker

st.set_page_config(page_title="Vanguard Nexus: Zenith Command", layout="wide", page_icon="🛡️")

def apply_zenith_theme():
    """Advanced UI Styling for the Zenith Edition."""
    st.markdown("""
    <style>
    .stApp { background-color: #050b18; color: #e2e8f0; }
    [data-testid="stMetricValue"] { font-size: 28px !important; color: #38bdf8 !important; }
    .stStatus { background: rgba(59, 130, 246, 0.1); border: 1px solid #3b82f6; border-radius: 10px; }
    .signal-box { 
        padding: 20px; border-radius: 15px; border: 2px solid #3b82f6; 
        background: rgba(59, 130, 246, 0.05); text-align: center; margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

def render_zenith_chart(ticker, intel):
    """Plots interactive Candlesticks with overlaid Entry, SL, and TP zones."""
    # Note: Real apps would pull 100+ candles; this uses the 20-candle buffer from our worker
    prices = [intel['current_price'] * (1 + (i * 0.001)) for i in range(-10, 11)] # Simulated for visual path
    
    fig = go.Figure(data=[go.Candlestick(
        x=list(range(len(prices))),
        open=[p*0.999 for p in prices], high=[p*1.002 for p in prices],
        low=[p*0.997 for p in prices], close=prices,
        name="Price Action"
    )])

    # Overlay Trade Zones
    zones = intel['zones']
    fig.add_hline(y=zones['entry'], line_dash="dot", line_color="blue", annotation_text="ENTRY")
    fig.add_hline(y=zones['tp'], line_dash="dash", line_color="green", annotation_text="TAKE PROFIT")
    fig.add_hline(y=zones['sl'], line_dash="dash", line_color="red", annotation_text="STOP LOSS")

    fig.update_layout(
        title=f"Zenith Tactical Chart: {ticker}",
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        xaxis_rangeslider_visible=False, height=500
    )
    st.plotly_chart(fig, use_container_width=True)

def main():
    apply_zenith_theme()
    st.title("🛡️ Vanguard Nexus: Zenith Command")
    st.caption(f"System Online | Confluence Engine v2.0 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Sidebar Configuration
    with st.sidebar:
        st.header("Nexus Control")
        api_key = st.text_input("Alpha Vantage API", type="password", value=os.getenv("ALPHAVANTAGE_API_KEY", ""))
        target_asset = st.selectbox("Sentry Target", ["BTC", "ETH", "SOL", "AAPL", "TSLA"])
        run_cycle = st.button("🚀 INITIATE ZENITH CYCLE", use_container_width=True)

    if run_cycle:
        if not api_key:
            st.error("Access Denied: API Key Missing.")
            return

        ingestor = FinancialDataIngestor(api_key)
        worker = InferenceWorker()

        with st.status(f"Scanning {target_asset} via Multi-Channel Logic...") as status:
            # 1. Gather Intelligence (Sentiment)
            raw_news = ingestor.fetch_latest_news(target_asset)
            # 2. Process Zenith Cycle (Technicals + Sentiment + Signals)
            intel = worker.process_pending_data(raw_news, ticker=target_asset)
            status.update(label="Zenith Confluence Established", state="complete")

        if intel:
            # Signal Header
            st.markdown(f"""<div class='signal-box'><h2>{intel['confluence_signal']}</h2></div>""", unsafe_allow_html=True)

            # Core Metrics
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Current Price", f"${intel['current_price']}")
            m2.metric("RSI (14)", intel['rsi'], delta="Oversold" if intel['rsi'] < 30 else "Overbought" if intel['rsi'] > 70 else "Neutral")
            m3.metric("Sentiment Score", intel['aggregate_score'], delta=intel['sentiment_label'])
            m4.metric("Volatility", f"{round(intel['volatility']*100, 2)}%")

            # Tactical Visualization
            render_zenith_chart(target_asset, intel)
            
            # Actionable Trade Ticket
            st.subheader("⚡ Tactical Execution Ticket")
            t1, t2, t3 = st.columns(3)
            t1.metric("ENTRY", f"${intel['zones']['entry']}")
            t2.metric("TAKE PROFIT", f"${intel['zones']['tp']}", delta="Target", delta_color="normal")
            t3.metric("STOP LOSS", f"${intel['zones']['sl']}", delta="Risk", delta_color="inverse")
            
        else:
            st.warning("Nexus could not establish a clean signal. Check API limits or data availability.")

if __name__ == "__main__":
    main()
