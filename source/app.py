# source/app.py
import streamlit as st
import json
from config import GEMINI_MODEL
from services.ai_logic import AIAnalystAgent
from services.data_registry import DataRegistry
from services.execution import execute_code
from services.logger import log_session
import os
from config import LOG_DIR
from streamlit_ace import st_ace

log_dir = LOG_DIR
if not os.path.exists(log_dir):
    os.makedirs(log_dir)


# --- Page Configuration ---
st.set_page_config(page_title="Local AI Analyst", layout="wide")

# --- Initialization ---
if "agent" not in st.session_state:
    st.session_state.agent = AIAnalystAgent()
if "messages" not in st.session_state:
    st.session_state.messages =[]
if "data_registry" not in st.session_state:
    st.session_state.data_registry = DataRegistry()
if "pending_code" not in st.session_state:
    st.session_state.pending_code = None
# ADD THESE TWO LINES:
if "last_execution_error" not in st.session_state:
    st.session_state.last_execution_error = None
if "auto_prompt" not in st.session_state:
    st.session_state.auto_prompt = None

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
                        st.rerun()
        except Exception as e:
            st.error("Could not load history.")
    else:
        st.info("No history yet.")

#  --- Main Chat Interface ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        # THÊM MỚI: Hiển thị lại Chain of Thought từ lịch sử nếu có
        if "thought" in msg and msg["thought"] and enable_cot:
            with st.expander("🧠 Suy luận của AI (Chain of Thought)"):
                st.write(msg["thought"])
                
        st.write(msg["content"])
        
        if "fig" in msg and msg["fig"]:
            st.plotly_chart(json.loads(msg["fig"]), use_container_width=True)
        if "result" in msg and msg["result"]:
            st.info(f"Numerical Result: {msg['result']}")

# --- Chat Input ---
prompt = st.chat_input("Hỏi tôi về dữ liệu hoặc yêu cầu phân tích...")

# Override prompt if triggered by the "Ask AI" button
if st.session_state.auto_prompt:
    prompt = st.session_state.auto_prompt
    st.session_state.auto_prompt = None

if prompt:
    # Clear pending code and errors if a new request comes in
    st.session_state.pending_code = None
    st.session_state.last_execution_error = None
    
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
            
            # QUAN TRỌNG: Lưu ngay response (bao gồm cả thought) vào history chat
            st.session_state.messages.append({
                "role": "assistant",
                "content": response["text"],
                "thought": response.get("thought", "")
            })
            
            # Hiển thị cho lượt chạy hiện tại
            if enable_cot and "thought" in response and response["thought"]:
                with st.expander("🧠 Suy luận của AI (Chain of Thought)"):
                    st.write(response["thought"])
            
            # Display Text response
            st.write(response["text"])
            
            # Store usage
            st.session_state.last_usage = response["usage"]
            
            # Detect if code was generated
            if "```python" in response["text"]:
                raw_code = response["text"].split("```python")[1].split("```")[0].strip()
                st.session_state.pending_code = raw_code
                st.rerun() # Bây giờ gọi rerun thì thought vẫn sẽ hiện vì đã được lưu ở trên

# --- Human-in-the-Loop Code Review Area ---
# --- Human-in-the-Loop Code Review Area ---
if st.session_state.pending_code:
    st.divider()
    st.subheader("📝 Code Review (Phê duyệt thực thi)")
    
    # 1. Display persistent error if it exists
    if st.session_state.last_execution_error:
        st.error(f"⚠️ Lỗi thực thi lần trước:\n{st.session_state.last_execution_error}")
    
    # Editable code area with Syntax Highlighting
    st.write("**AI đề xuất code sau (Bạn có thể chỉnh sửa):**")
    edited_code = st_ace(
        value=st.session_state.pending_code,
        language="python",
        theme="vscode",        # Bạn có thể đổi sang 'monokai', 'github', 'twilight'...
        keybinding="vscode",   # Hỗ trợ phím tắt như VS Code
        font_size=14,
        min_lines=15,          # Độ cao tối thiểu
        key="ace_editor"
    )
    
    # Added col_fix for the new button
    col_run, col_fix, col_cancel = st.columns([1.5, 1.5, 4])
    
    if col_run.button("✅ Approve & Run", type="primary"):
        # Load the actual dataframes for execution
        data_vars = st.session_state.data_registry.load_active_datasets(active_datasets)
        
        # Execute
        result = execute_code(edited_code, data_vars)
        
        # Log the session
        log_session({
            "prompt": st.session_state.messages[-1]["content"] if st.session_state.messages else "",
            "raw_code": st.session_state.pending_code,
            "final_code": edited_code,
            "success": result["error"] is None,
            "error": result["error"]
        })
        
        if result["error"]:
            # SAVE the error and keep the user's edited code in the text box
            st.session_state.last_execution_error = result["error"]
            st.session_state.pending_code = edited_code 
            st.rerun()
        else:
            # SUCCESS handling
            st.session_state.last_execution_error = None
            
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

    if col_fix.button("🪄 Ask AI to fix/review"):
        if st.session_state.last_execution_error:
            st.session_state.auto_prompt = f"Đoạn mã này bị lỗi:\n```\n{st.session_state.last_execution_error}\n```\n\nVui lòng sửa nó. Code hiện tại:\n```python\n{edited_code}\n```"
        else:
            st.session_state.auto_prompt = f"Vui lòng xem xét, tiếp tục hoặc tối ưu đoạn code hiện tại của tôi:\n```python\n{edited_code}\n```"
        st.rerun()

    if col_cancel.button("❌ Cancel"):
        st.session_state.pending_code = None
        st.session_state.last_execution_error = None
        st.rerun()

