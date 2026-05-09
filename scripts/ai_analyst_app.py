import streamlit as st
import pandas as pd
from google import genai
import os
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import contextlib
import io
from dotenv import load_dotenv

# --- CONFIGURATION & PATHS ---
DATA_PATH = "analysis/CPI_final_for_powerbi.csv"
LOG_PATH = "output/audit_log.json"

# --- PAGE SETUP ---
st.set_page_config(page_title="VN-CPI AI Analyst", layout="wide", page_icon="🇻🇳")
st.title("🇻🇳 Vietnam CPI AI Analyst Module")
st.markdown("""
*Interactive AI Module using Plotly. Follows the 'Human-in-the-Loop' standard.*
""")

# --- AUTHENTICATION ---
load_dotenv()
with st.sidebar:
    st.header("🔑 Authentication")
    env_key = os.getenv("GEMINI_API_KEY", "")
    api_key = st.text_input("Enter Gemini API Key", 
                           value=env_key, 
                           type="password",
                           help="Get a free key at aistudio.google.com")
    
    if api_key:
        client = genai.Client(api_key=api_key)
        st.success("API Key Loaded!")
    else:
        st.warning("Please provide an API Key.")

# --- SESSION STATE INITIALIZATION ---
if "history" not in st.session_state:
    if os.path.exists(LOG_PATH):
        try:
            with open(LOG_PATH, "r", encoding="utf-8") as f:
                st.session_state.history = json.load(f)
        except:
            st.session_state.history = []
    else:
        st.session_state.history = []

# --- HELPER FUNCTIONS ---
def log_interaction(prompt, ai_explanation, ai_code, final_code, was_edited, result_log, plot_json):
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "prompt": prompt,
        "ai_explanation": ai_explanation,
        "ai_code": ai_code,
        "final_code": final_code,
        "was_edited": was_edited,
        "result_log": result_log,
        "plot_json": plot_json
    }
    st.session_state.history.append(entry)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(st.session_state.history, f, indent=4, ensure_ascii=False)

def get_ai_analysis(prompt):
    system_prompt = f"""
    You are an expert Data Scientist analyzing Vietnam's CPI data using Plotly.
    Context:
    - Year (int), Month (int), Category (str), Index_Value (float), Hierarchy_Level (str), Economic_Period (str), Category_Group (str), Is_Tet_Month (bool).
    
    Request: {prompt}
    
    MANDATORY OUTPUT FORMAT:
    Respond ONLY with a JSON object containing:
    1. "explanation": A natural language description of what the code does.
    2. "code": Clean, executable Python code. 
    
    CODE RULES:
    - Use 'df' as the primary DataFrame variable.
    - Always assign your interactive Plotly figure to a variable named 'fig'.
    - Use 'plotly.express' or 'plotly.graph_objects'.
    - Enable tooltips, markers, and gridlines.
    - Do NOT include any display command like 'fig.show()'.
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=system_prompt
    )
    
    try:
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        return {"explanation": "Error", "code": f"# Error: {str(e)}"}

# --- MAIN TABS ---
tab_analyst, tab_history = st.tabs(["🤖 AI Analyst", "📋 Audit & History"])

with tab_analyst:
    query = st.text_input("What would you like to analyze?")
    if st.button("Generate Code"):
        if query:
            st.session_state.current_ai_response = get_ai_analysis(query)
            st.session_state.last_query = query

    if "current_ai_response" in st.session_state and st.session_state.current_ai_response:
        final_code = st.text_area("Python Code Editor", value=st.session_state.current_ai_response['code'], height=300)
        
        if st.button("🚀 Approve & Execute"):
            df = pd.read_csv(DATA_PATH)
            exec_globals = {'pd': pd, 'px': px, 'go': go, 'df': df}
            try:
                exec(final_code, exec_globals)
                fig = exec_globals['fig']
                st.plotly_chart(fig, use_container_width=True)
                
                log_interaction(
                    st.session_state.last_query,
                    st.session_state.current_ai_response['explanation'],
                    st.session_state.current_ai_response['code'],
                    final_code,
                    final_code != st.session_state.current_ai_response['code'],
                    "",
                    fig.to_json()
                )
            except Exception as e:
                st.error(str(e))

with tab_history:
    if st.session_state.history:
        for entry in reversed(st.session_state.history):
            with st.expander(f"📍 {entry['timestamp']}"):
                st.write(f"**Prompt:** {entry['prompt']}")
                
                # Render interactive plot if it exists
                if entry.get('plot_json'):
                    st.plotly_chart(go.Figure(json.loads(entry['plot_json'])), use_container_width=True)
                # Fallback to legacy plot_path if it exists
                elif entry.get('plot_path') and os.path.exists(entry['plot_path']):
                    st.image(entry['plot_path'])
                
                st.code(entry['final_code'])
