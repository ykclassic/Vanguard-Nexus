import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# --- PATH INJECTOR: Fixes ModuleNotFoundError in Streamlit Cloud ---
# This ensures 'core' and 'services' are findable regardless of where the script is run.
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Now we can safely import our local modules
from core.DataIngestor import FinancialDataIngestor
from services.InferenceWorker import InferenceWorker
from services.ServiceRegistry import ServiceRegistry

st.set_page_config(page_title="Vanguard Nexus Hub", layout="wide", page_icon="🚀")

def apply_ui_theme():
    """Applies Glassmorphism styling to the Streamlit Dashboard."""
    st.markdown("""
    <style>
    .stApp { background: #0f172a; color: #f8fafc; }
    [data-testid="stMetric"], .stMarkdown, .plot-container {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
    }
    .stButton>button {
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        color: white; border: none; border-radius: 8px; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    apply_ui_theme()
    st.title("🚀 Vanguard Nexus Intelligence")
    st.caption("Advanced Sentiment Analysis & Market Data Ingestion")
    
    # Initialize Core Services (API Key handled via Streamlit Secrets or manual input)
    api_key = st.sidebar.text_input("Alpha Vantage API Key", type="password", value="demo")
    ingestor = FinancialDataIngestor(api_key=api_key)
    worker = InferenceWorker()
    
    ticker = st.sidebar.text_input("Asset Ticker", "BTC")
    
    if st.sidebar.button("Run Intel Cycle"):
        with st.status("Vanguard Nexus: Processing Market Data...") as s:
            # 1. Fetch Data
            raw = ingestor.fetch_latest_news(ticker)
            # 2. Process & Dispatch to Discord
            intel = worker.process_pending_data(raw, ticker=ticker)
            s.update(label="Cycle Complete!", state="complete")

        if intel:
            # Display Key Metrics
            c1, c2, c3 = st.columns(3)
            c1.metric("Sentiment Score", intel['aggregate_score'])
            c2.metric("Market Stance", intel['sentiment_label'])
            c3.metric("Data Volatility", intel['volatility'])
            
            # Interactive Visualization
            df = pd.DataFrame(raw)
            if not df.empty:
                fig = px.histogram(
                    df, 
                    x='relevance_score', 
                    title=f"Sentiment Distribution for {ticker}",
                    color_discrete_sequence=['#3b82f6']
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)', 
                    font_color="white"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No headline data found for this ticker.")
        else:
            st.error("Intelligence Cycle failed. Check API Key or Ticker.")

if __name__ == "__main__":
    main()
