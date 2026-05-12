# source/app.py
import streamlit as st
import json
from config import GEMINI_MODEL
from services.ai_logic import AIAnalystAgent
from services.data_registry import DataRegistry
from services.execution import execute_code
import os
from config import LOG_DIR
from streamlit_ace import st_ace

from datetime import datetime
from services.logger import save_conversation, list_conversations, load_conversation

log_dir = LOG_DIR
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# --- Page Configuration ---
st.set_page_config(page_title="Local AI Analyst", layout="wide")

# --- REPLACE INITIALIZATION BLOCK ---
if "agent" not in st.session_state:
    st.session_state.agent = AIAnalystAgent()
if "data_registry" not in st.session_state:
    st.session_state.data_registry = DataRegistry()

# NEW: Track Conversation ID and Turns (replacing "messages")
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
if "turns" not in st.session_state:
    st.session_state.turns = []

# Helper to save state automatically
def trigger_save():
    save_conversation(st.session_state.conversation_id, {
        "conversation_id": st.session_state.conversation_id,
        "system_prompt": st.session_state.agent.system_instruction,
        "active_datasets": active_datasets, # Ensure this is defined by your sidebar checkboxes
        "turns": st.session_state.turns
    })

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
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        st.session_state.conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        st.session_state.turns = []
        st.session_state.pending_code = None
        st.session_state.agent = AIAnalystAgent() # Resets AI memory
        st.rerun()

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

    st.divider()
    # 4. History Archive (Option A)
    st.subheader("📜 History Archive")
    
    log_file = os.path.join(LOG_DIR, "session_history.json")
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                history_data = json.load(f)
            
            # Show the last 10 sessions, most recent first
            for idx, entry in enumerate(reversed(history_data[-10:])):
                timestamp = entry.get("timestamp", "").split("T")[0]
                prompt_preview = entry.get("prompt", "No prompt")[:30] + "..."
                
                # Use an expander for each history item to keep sidebar clean
                with st.expander(f"{timestamp}: {prompt_preview}"):
                    st.write(f"**Prompt:** {entry.get('prompt')}")
                    st.code(entry.get('final_code'), language="python")
                    if entry.get("success"):
                        st.success("Status: Success")
                    else:
                        st.error(f"Error: {entry.get('error')}")
                    
                    # Button to restore this code to the editor
                    if st.button("Restore Code", key=f"restore_{idx}"):
                        st.session_state.pending_code = entry.get('final_code')
                        st.session_state.editor_key += 1 # <-- THÊM DÒNG NÀY
                        st.rerun()
        except Exception as e:
            st.error("Could not load history.")
    else:
        st.info("No history yet.")

tab_chat, tab_history = st.tabs(["💬 Active Chat", "📜 History Archive"])

#  --- Main Chat Interface ---
with tab_chat:
    # 1. Render all previous Turns from the current conversation
    for i, turn in enumerate(st.session_state.turns):
        with st.chat_message("user"):
            st.write(turn["user_prompt"])
            
        if turn.get("agent_response") or turn.get("chain_of_thought"):
            with st.chat_message("assistant"):
                # Show Thought and Tools (if enabled)
                if enable_cot and (turn.get("chain_of_thought") or turn.get("tool_calls")):
                    with st.expander("🧠 Suy luận & Tools"):
                        if turn.get("chain_of_thought"):
                            st.write(turn["chain_of_thought"])
                        if turn.get("tool_calls"):
                            st.write("**Tools Executed:**")
                            st.json(turn["tool_calls"])
                
                # Show Text Response
                st.write(turn.get("agent_response", ""))
                
                # Show Execution Results if they exist in this turn
                if turn.get("fig_json"):
                    st.plotly_chart(
                        json.loads(turn["fig_json"]), 
                        use_container_width=True,
                        key=f"chart_active_{i}" # Thêm key duy nhất
                    )
                if turn.get("result_data"):
                    st.info(f"Kết quả: {turn['result_data']}")
                if turn.get("stdout"):
                    with st.expander("Console Output"):
                        st.code(turn["stdout"])
                if turn.get("error"):
                    st.error(f"Lỗi: {turn['error']}")

    # 2. Chat Input Logic
    prompt = st.chat_input("Hỏi tôi về dữ liệu...")
    if st.session_state.auto_prompt:
        prompt = st.session_state.auto_prompt
        st.session_state.auto_prompt = None

    if prompt:
        st.session_state.pending_code = None
        st.session_state.last_execution_error = None
        
        # Create a new Turn object and add to state
        new_turn = {
            "timestamp": datetime.now().isoformat(),
            "user_prompt": prompt,
            "agent_response": None,
            "chain_of_thought": None,
            "tool_calls": [],
            "raw_code": None,
            "final_code": None,
            "success": None,
            "error": None,
            "stdout": None,
            "fig_json": None,
            "result_data": None
        }
        st.session_state.turns.append(new_turn)

        with st.chat_message("assistant"):
            with st.spinner("Đang suy nghĩ..."):
                response = st.session_state.agent.generate_response(prompt, active_datasets)
                
                text_to_show = response["text"]
                raw_code = None
                
                # Extract code if present
                if "```python" in text_to_show:
                    parts = text_to_show.split("```python")
                    text_before = parts[0]
                    code_and_after = parts[1].split("```", 1)
                    raw_code = code_and_after[0].strip()
                    text_after = code_and_after[1] if len(code_and_after) > 1 else ""
                    text_to_show = f"{text_before.strip()}\n\n*(Đã trích xuất mã xuống khung Review)*\n\n{text_after.strip()}"
                    
                    st.session_state.pending_code = raw_code
                    st.session_state.editor_key += 1
                
                # UPDATE THE TURN with AI response data
                current_turn = st.session_state.turns[-1]
                current_turn["agent_response"] = text_to_show
                current_turn["chain_of_thought"] = response.get("thought", "")
                current_turn["tool_calls"] = response.get("tools", [])
                current_turn["raw_code"] = raw_code
                
                st.session_state.last_usage = response["usage"]
                trigger_save() # <--- Save turn to JSON file
                st.rerun()

    # 3. Code Review Area (Human-in-the-loop)
    if st.session_state.pending_code:
        st.divider()
        st.subheader("📝 Code Review")
        
        if st.session_state.last_execution_error:
            st.error(f"⚠️ Lỗi thực thi: {st.session_state.last_execution_error}")
        
        edited_code = st_ace(value=st.session_state.pending_code, language="python", theme="vscode", key=f"ace_{st.session_state.editor_key}")
        
        col_run, col_fix, col_cancel = st.columns([1.5, 1.5, 4])
        
        if col_run.button("✅ Approve & Run", type="primary"):
            data_vars = st.session_state.data_registry.load_active_datasets(active_datasets)
            result = execute_code(edited_code, data_vars)
            
            # UPDATE THE TURN with execution results
            current_turn = st.session_state.turns[-1]
            current_turn["final_code"] = edited_code
            current_turn["success"] = result["error"] is None
            current_turn["error"] = result["error"]
            current_turn["stdout"] = result["stdout"]
            current_turn["fig_json"] = result["fig_json"]
            current_turn["result_data"] = result["result_data"]
            
            trigger_save() # <--- Save results to JSON file
            
            if result["error"]:
                st.session_state.last_execution_error = result["error"]
                st.session_state.pending_code = edited_code 
            else:
                st.session_state.last_execution_error = None
                st.session_state.agent.feed_execution_result(result)
                st.session_state.pending_code = None
            st.rerun()

        if col_fix.button("🪄 Ask AI to fix"):
            st.session_state.auto_prompt = f"Sửa lỗi/Tối ưu code này: \n```python\n{edited_code}\n```"
            st.rerun()

        if col_cancel.button("❌ Cancel"):
            st.session_state.pending_code = None
            st.rerun()

with tab_history:
    st.subheader("📚 History Viewer")
    files = list_conversations()
    if files:
        selected_file = st.selectbox("Select Conversation:", files, format_func=lambda x: os.path.basename(x))
        hist_data = load_conversation(selected_file)
        
        for j, turn in enumerate(hist_data.get("turns", [])):
            with st.expander(f"Prompt: {turn['user_prompt'][:50]}..."):
                st.write(f"**Full Prompt:** {turn['user_prompt']}")
                st.divider()
                st.write("**AI Response:**", turn.get("agent_response"))
                if turn.get("fig_json"):
                    st.plotly_chart(
                        json.loads(turn["fig_json"]), 
                        use_container_width=True,
                        key=f"chart_hist_{j}" # Thêm key duy nhất
                    )
                if turn.get("final_code"):
                    st.code(turn["final_code"], language="python")
    else:
        st.info("No logs found.")
