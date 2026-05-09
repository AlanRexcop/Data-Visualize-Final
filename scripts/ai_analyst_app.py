import streamlit as st
import pandas as pd
from google import genai
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import contextlib
import io
from dotenv import load_dotenv

# --- CONFIGURATION & PATHS ---
DATA_PATH = "output/CPI_final_for_powerbi.csv"
LOG_PATH = "output/audit_log.json"
PLOT_DIR = "output/plots"
os.makedirs(PLOT_DIR, exist_ok=True)

# --- PAGE SETUP ---
st.set_page_config(page_title="VN-CPI AI Analyst", layout="wide", page_icon="🇻🇳")
st.title("🇻🇳 Vietnam CPI AI Analyst Module")
st.markdown("""
*Developed for the Data Visualization Final Project. This module follows the 'Human-in-the-Loop' and 'Non-Silent Execution' standards.*
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
        st.warning("Please provide an API Key to enable AI features.")

    st.divider()
    st.header("ℹ️ About this Module")
    st.info("""
    This AI Module follows **Standard 8: AI Integration**.
    It ensures:
    1. **Visibility:** Code is shown before running.
    2. **Approval:** User must click execute.
    3. **Audit:** Logs are saved for oral exam.
    """)

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

if "current_ai_response" not in st.session_state:
    st.session_state.current_ai_response = None

# --- HELPER FUNCTIONS ---
def log_interaction(prompt, ai_explanation, ai_code, final_code, was_edited, result_log, plot_name):
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "prompt": prompt,
        "ai_explanation": ai_explanation,
        "ai_code": ai_code,
        "final_code": final_code,
        "was_edited": was_edited,
        "result_log": result_log,
        "plot_path": f"output/plots/{plot_name}" if plot_name else None
    }
    st.session_state.history.append(entry)
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(st.session_state.history, f, indent=4, ensure_ascii=False)

def get_ai_analysis(prompt):
    schema_context = """
    Dataset Structure (df):
    - Year (int): 2002-2024
    - Month (int): 1-12
    - Category (str): Product/Group name
    - Index_Value (float): Month-over-month price change index
    - Hierarchy_Level (str): 'Total CPI', 'Main Category', 'Sub-category'
    - Economic_Period (str): Historical eras of VN economy
    - Category_Group (str): Broad sectors (Food, Transport, etc.)
    - Is_Tet_Month (bool): True if Lunar New Year season
    """
    
    system_prompt = f"""
    You are an expert Data Scientist analyzing Vietnam's CPI data.
    Context: {schema_context}
    
    Request: {prompt}
    
    MANDATORY OUTPUT FORMAT:
    Respond ONLY with a JSON object containing:
    1. "explanation": A natural language description of what the code does.
    2. "code": Clean, executable Python code. 
    
    CODE RULES:
    - Use 'df' as the primary DataFrame variable.
    - NEVER modify 'df' permanently; always use a copy or filtered view.
    - Always end the code by assigning your final visualization to a variable named 'fig'.
    - Use seaborn or matplotlib.
    - Include comments in the code explaining each step.
    - Do NOT include 'plt.show()'.
    """
    
    # Using the new google-genai client syntax
    response = client.models.generate_content(
        model="gemini-2.5-flash", # Using flash for speed/free tier
        contents=system_prompt
    )
    
    try:
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        return {
            "explanation": "Failed to parse AI response.",
            "code": f"# Error: {str(e)}\n# Raw output: {response.text}"
        }

# --- MAIN TABS ---
tab_analyst, tab_history = st.tabs(["🤖 AI Analyst", "📋 Audit & History"])

with tab_analyst:
    st.header("Step 1: Ask your Question")
    query = st.text_input("What would you like to analyze?", placeholder="e.g., Compare the volatility of Gold vs. Transport")
    
    if st.button("Generate Code"):
        if not api_key:
            st.error("Please enter an API Key in the sidebar.")
        elif query:
            with st.spinner("Gemini is analyzing and writing code..."):
                st.session_state.current_ai_response = get_ai_analysis(query)
                st.session_state.last_query = query
        else:
            st.warning("Please enter a question first.")

    if st.session_state.current_ai_response:
        st.divider()
        st.header("Step 2: Review & Approve")
        st.markdown(f"**AI Strategy:** {st.session_state.current_ai_response['explanation']}")
        
        final_code = st.text_area("Python Code Editor", 
                                  value=st.session_state.current_ai_response['code'], 
                                  height=300)
        
        if st.button("🚀 Approve & Execute"):
            with st.spinner("Running code on local data..."):
                df = pd.read_csv(DATA_PATH)
                exec_globals = {'pd': pd, 'sns': sns, 'plt': plt, 'df': df, 'os': os}
                output_buffer = io.StringIO()
                try:
                    with contextlib.redirect_stdout(output_buffer):
                        exec(final_code, exec_globals)
                    
                    st.success("Analysis Complete!")
                    if 'fig' in exec_globals:
                        st.pyplot(exec_globals['fig'])
                        p_name = f"plot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        exec_globals['fig'].savefig(f"{PLOT_DIR}/{p_name}")
                    else:
                        st.warning("Code ran successfully, but no 'fig' variable was found for display.")
                        p_name = None
                        
                    logs = output_buffer.getvalue()
                    if logs:
                        st.text_area("Console Logs", value=logs, height=100)
                    
                    was_edited = final_code != st.session_state.current_ai_response['code']
                    log_interaction(
                        st.session_state.last_query,
                        st.session_state.current_ai_response['explanation'],
                        st.session_state.current_ai_response['code'],
                        final_code,
                        was_edited,
                        logs,
                        p_name
                    )
                except Exception as e:
                    st.error(f"Execution Error: {str(e)}")
                    st.exception(e)

with tab_history:
    st.header("Project Audit Trail")
    if not st.session_state.history:
        st.info("No history yet.")
    else:
        for entry in reversed(st.session_state.history):
            with st.expander(f"📍 {entry['timestamp']} - {entry['prompt'][:60]}..."):
                st.write(f"**Question:** {entry['prompt']}")
                st.write(f"**AI Logic:** {entry['ai_explanation']}")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Original AI Code**")
                    st.code(entry['ai_code'], language='python')
                with c2:
                    st.markdown("**Executed Code**")
                    if entry['was_edited']: st.warning("Modified by Human")
                    st.code(entry['final_code'], language='python')
                if entry['plot_path'] and os.path.exists(entry['plot_path']):
                    st.image(entry['plot_path'])
                if entry['result_log']:
                    st.code(entry['result_log'])

st.divider()
st.caption("Vietnam CPI Analytics | Project Standard: Non-Silent AI Execution")
