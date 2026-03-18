import streamlit as st
import pandas as pd
import plotly.express as px
from core.DataIngestor import FinancialDataIngestor
from services.InferenceWorker import InferenceWorker
from services.ServiceRegistry import ServiceRegistry

st.set_page_config(page_title="Vanguard Nexus Hub", layout="wide")

def apply_ui_theme():
    st.markdown("""
    <style>
    .stApp { background: #0f172a; }
    [data-testid="stMetric"], .stMarkdown, .plot-container {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    apply_ui_theme()
    st.title("🚀 Vanguard Nexus Intelligence")
    
    ingestor = FinancialDataIngestor(api_key="demo")
    worker = InferenceWorker()
    ticker = st.sidebar.text_input("Asset Ticker", "BTC")
    
    if st.sidebar.button("Run Intel Cycle"):
        with st.status("Vanguard Nexus Active...") as s:
            raw = ingestor.fetch_latest_news(ticker)
            intel = worker.process_pending_data(raw)
            s.update(label="Sync Complete", state="complete")

        if intel:
            c1, c2, c3 = st.columns(3)
            c1.metric("Sentiment", intel['aggregate_score'])
            c2.metric("Stance", intel['sentiment_label'])
            c3.metric("Samples", intel['sample_size'])
            
            df = pd.DataFrame(raw)
            fig = px.histogram(df, x='relevance_score', title="Data Relevance Pulse", color_discrete_sequence=['#3b82f6'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
