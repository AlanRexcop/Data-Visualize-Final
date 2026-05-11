# source/app.py
import streamlit as st
import json
from config import GEMINI_MODEL
from services.ai_logic import AIAnalystAgent
from services.data_registry import DataRegistry
from services.execution import execute_code
from services.logger import log_session

# --- Page Configuration ---
st.set_page_config(page_title="Local AI Analyst", layout="wide")

# --- Initialization ---
if "agent" not in st.session_state:
    st.session_state.agent = AIAnalystAgent()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "data_registry" not in st.session_state:
    st.session_state.data_registry = DataRegistry()
if "pending_code" not in st.session_state:
    st.session_state.pending_code = None

# --- Custom CSS for AI Studio feel ---
st.markdown("""
    <style>
    .token-usage { color: #888; font-size: 0.8rem; text-align: right; }
    .stCodeBlock { border: 1px solid #444; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- Top Header: Token Usage ---
col_title, col_usage = st.columns([3, 1])
with col_title:
    st.title("🤖 Local AI Analyst")
with col_usage:
    if st.session_state.get("last_usage"):
        u = st.session_state.last_usage
        st.markdown(f"<div class='token-usage'>Tokens: In {u['input_tokens']} | Out {u['output_tokens']}</div>", unsafe_allow_html=True)

# --- Right Sidebar: Plug-and-Play Manager ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # 1. Model Settings
    thought_level = st.select_slider("Thinking Level (Temperature)", options=[0.1, 0.7, 1.0], value=0.7)
    enable_cot = st.toggle("Show Chain of Thought", value=True)
    
    st.divider()
    
    # 2. Data Registry (Plug-and-Play)
    st.subheader("📁 Datasets")
    available_data = st.session_state.data_registry.get_available_datasets()
    active_datasets = []
    for ds in available_data:
        if st.checkbox(ds, key=f"ds_{ds}", help="Activate this dataset for AI context"):
            active_datasets.append(ds)
            
    # View metadata button
    if active_datasets:
        with st.expander("📄 Data Metadata"):
            st.markdown(st.session_state.data_registry.get_metadata_context(active_datasets))

    st.divider()

    # 3. Tool Registry (Plug-and-Play)
    st.subheader("🛠️ Tools")
    # Dynamically get available tools from the agent's discovery
    available_tools = [t.__name__ for t in st.session_state.agent.tools]
    enabled_tools = []
    for tool_name in available_tools:
        if st.checkbox(tool_name, value=True, key=f"tool_{tool_name}"):
            enabled_tools.append(tool_name)

# --- Main Chat Interface ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "fig" in msg and msg["fig"]:
            st.plotly_chart(json.loads(msg["fig"]), use_container_width=True)
        if "result" in msg and msg["result"]:
            st.info(f"Numerical Result: {msg['result']}")

# --- Chat Input ---
if prompt := st.chat_input("Hỏi tôi về dữ liệu hoặc yêu cầu phân tích..."):
    # Clear pending code if new request comes in
    st.session_state.pending_code = None
    
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Call AI
    with st.chat_message("assistant"):
        with st.spinner("Đang suy nghĩ..."):
            # Update agent with current enabled tools/datasets
            response = st.session_state.agent.generate_response(
                prompt, 
                active_datasets, 
                temperature=thought_level
            )
            
            # Show Chain of Thought if requested
            if enable_cot and "thought" in response:
                with st.expander("🧠 Suy luận của AI (Chain of Thought)"):
                    st.write(response["thought"])
            
            # Display Text response
            st.write(response["text"])
            
            # Store usage
            st.session_state.last_usage = response["usage"]
            
            # Detect if code was generated (simplified regex or block detection)
            if "```python" in response["text"]:
                raw_code = response["text"].split("```python")[1].split("```")[0].strip()
                st.session_state.pending_code = raw_code
                st.rerun()

# --- Human-in-the-Loop Code Review Area ---
if st.session_state.pending_code:
    st.divider()
    st.subheader("📝 Code Review (Phê duyệt thực thi)")
    
    # Editable code area
    edited_code = st.text_area(
        "AI đề xuất code sau (Bạn có thể chỉnh sửa):",
        value=st.session_state.pending_code,
        height=250
    )
    
    col_run, col_cancel = st.columns([1, 5])
    if col_run.button("✅ Approve & Run", type="primary"):
        # Load the actual dataframes for execution
        data_vars = st.session_state.data_registry.load_active_datasets(active_datasets)
        
        # Execute
        result = execute_code(edited_code, data_vars)
        
        # Log the session
        log_session({
            "prompt": st.session_state.messages[-1]["content"],
            "raw_code": st.session_state.pending_code,
            "final_code": edited_code,
            "success": result["error"] is None,
            "error": result["error"]
        })
        
        # Display Results
        if result["error"]:
            st.error(f"Lỗi thực thi: {result['error']}")
        else:
            if result["fig_json"]:
                st.plotly_chart(json.loads(result["fig_json"]), use_container_width=True)
            if result["result_data"]:
                st.success(f"Kết quả: {result['result_data']}")
            if result["stdout"]:
                with st.expander("Console Output"):
                    st.code(result["stdout"])
                    
            # Update history with results
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "Đã thực thi mã thành công.",
                "fig": result["fig_json"],
                "result": result["result_data"]
            })
            
            # Feed result back to LLM for final analysis
            st.session_state.agent.feed_execution_result(result)
            
        st.session_state.pending_code = None
        st.rerun()

    if col_cancel.button("❌ Cancel"):
        st.session_state.pending_code = None
        st.rerun()