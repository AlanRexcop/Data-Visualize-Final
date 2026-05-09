import streamlit as st
import pandas as pd
import os
import json
import plotly.graph_objects as go
from dotenv import load_dotenv
import sys

# Add source to path for service imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services import ai_logic, execution, logger

# --- CONFIGURATION & PATHS ---
DATA_PATH = "analysis/CPI_final_for_powerbi.csv"

# --- PAGE SETUP ---
st.set_page_config(page_title="VN-CPI AI Analyst", layout="wide", page_icon="🇻🇳")
st.title("🇻🇳 Vietnam CPI AI Analyst Module")

# --- AUTHENTICATION ---
load_dotenv()
with st.sidebar:
    st.header("🔑 Authentication")
    api_key = st.text_input("Enter Gemini API Key", type="password")

# --- INITIALIZATION ---
if "history" not in st.session_state:
    st.session_state.history = logger.load_history()

# --- TABS ---
tab_analyst, tab_history = st.tabs(["🤖 AI Analyst", "📋 Audit & History"])

with tab_analyst:
    mode = st.selectbox("Select Agent Mode", ["Explorer", "Visualizer", "Analyst"])
    
    history = logger.load_history()
    context_indices = st.multiselect("Select Context (History Items)", 
                                     options=range(len(history)), 
                                     format_func=lambda i: f"{history[i]['timestamp']} - {history[i]['prompt'][:30]}...")
    
    query = st.text_input("What would you like to analyze?")
    
    if st.button("Generate Code"):
        if query and api_key:
            context = "\n".join([f"Step {i}: {history[i]['explanation']}" for i in context_indices])
            st.session_state.current_ai_response = ai_logic.get_ai_analysis(api_key, query, mode, context)
            st.session_state.last_query = query
    
    if "current_ai_response" in st.session_state and st.session_state.current_ai_response:
        st.info(f"**Thinking Trail:** {st.session_state.current_ai_response['explanation']}")
        final_code = st.text_area("Python Code Editor", value=st.session_state.current_ai_response['code'], height=300)
        
        if st.button("🚀 Approve & Execute"):
            df = pd.read_csv(DATA_PATH)
            fig = execution.execute_analysis(final_code, df)
            st.plotly_chart(fig, use_container_width=True)
            
            st.session_state.history = logger.log_interaction(
                st.session_state.history,
                st.session_state.last_query,
                st.session_state.current_ai_response['explanation'],
                st.session_state.current_ai_response['code'],
                final_code,
                final_code != st.session_state.current_ai_response['code'],
                "",
                fig.to_json()
            )

with tab_history:
    if st.session_state.history:
        for i, entry in enumerate(reversed(st.session_state.history)):
            with st.expander(f"📍 {entry['timestamp']} (ID: {len(st.session_state.history)-1-i})"):
                st.write(f"**Prompt:** {entry['prompt']}")
                st.info(f"**Thinking:** {entry['explanation']}")
                if entry.get('plot_json'):
                    st.plotly_chart(go.Figure(json.loads(entry['plot_json'])), use_container_width=True)
                st.code(entry['final_code'])
