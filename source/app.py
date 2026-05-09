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

# --- HELPER: EXTRACT METADATA ---
@st.cache_data
def load_data(path):
    return pd.read_csv(path)

def get_df_metadata(df: pd.DataFrame) -> str:
    res = [f"Tập dữ liệu (dataframe `df`) chứa {df.shape[1]} cột và {len(df)} dòng."]
    for col in df.columns:
        col_dtype = df[col].dtype
        res.append(f"\nCột: '{col}' (Kiểu dữ liệu: {col_dtype})")
        if col_dtype == 'object' or str(col_dtype) == 'bool':
            res.append(f"--- Tỷ lệ NaNs: {df[col].isna().sum() / len(df[col]) * 100:.2f}%")
            uniques = df[col].dropna().unique()
            # Giới hạn số lượng unique values để không làm tràn token của AI
            if len(uniques) <= 30:
                res.append(f"--- Các giá trị Unique:\n {uniques}")
            else:
                res.append(f"--- Các giá trị Unique (Lấy mẫu 20 giá trị đầu):\n {uniques[:20]} ... (và còn nữa)")
        else:
            desc = df[col].describe()
            res.append(f"--- Thống kê cơ bản: min={desc.get('min')}, max={desc.get('max')}, mean={desc.get('mean'):.2f}")
    return "\n".join(res)

# Khởi tạo Data và Metadata ngay từ đầu
df = load_data(DATA_PATH)
metadata_str = get_df_metadata(df)

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
tab_analyst, tab_history = st.tabs(["🤖 AI Analyst (Auto-Routing)", "📋 Audit & History"])

with tab_analyst:
    st.markdown("### 🎯 Phân tích Dữ liệu Tự động (Autonomous Analytics)")
    query = st.text_input("Bạn muốn phân tích gì? (VD: 'Kiểm tra xem CPI có tăng vào tháng Tết không, vẽ biểu đồ và phân tích')")
    
    if st.button("Lên kế hoạch & Thực hiện (Generate Plan)") and query and api_key:
        with st.spinner("Đang lập kế hoạch..."):
            # Truyền metadata_str vào Planner
            st.session_state.plan = ai_logic.get_ai_plan(api_key, query, metadata_str)
            st.session_state.current_step = 0
            st.session_state.observations =[]
            st.session_state.current_response = None
            st.session_state.last_query = query
            st.session_state.generated_for_step = -1
            st.rerun()

    if "plan" in st.session_state and st.session_state.current_step < len(st.session_state.plan):
        plan = st.session_state.plan
        current_step_idx = st.session_state.current_step
        current_task = plan[current_step_idx]
        
        st.markdown("---")
        st.write(f"### 🗺️ Kế hoạch hiện tại: Bước {current_step_idx + 1} / {len(plan)}")
        for i, p in enumerate(plan):
            # Sử dụng p.get('step') và i+1 làm phương án dự phòng
            p_step = p.get('step', i + 1)
            p_agent = p.get('agent', 'Unknown')
            p_task = p.get('task', 'N/A')
            
            icon = "✅" if p_step <= current_step_idx else "⏳"
            
            if p_step == current_step_idx + 1:
                st.markdown(f"**{icon} Bước {p_step} ({p_agent}): {p_task}** 👈 *(Đang xử lý)*")
            else:
                st.write(f"{icon} Bước {p_step} ({p_agent}): {p_task}")
            
        st.markdown("---")
        st.subheader(f"🤖 Đang chờ Đặc vụ: {current_task['agent']}")
        
        if st.session_state.get('generated_for_step') != current_step_idx:
            with st.spinner(f"Đặc vụ {current_task['agent']} đang suy nghĩ..."):
                context_obs = "\n".join(st.session_state.observations)
                # Truyền metadata_str vào Agent
                st.session_state.current_response = ai_logic.get_ai_analysis(
                    api_key, 
                    prompt=current_task['task'], 
                    mode=current_task['agent'], 
                    observation=context_obs,
                    metadata_str=metadata_str
                )
                st.session_state.generated_for_step = current_step_idx
                st.rerun()
                
        resp = st.session_state.current_response
        st.info(f"**Dòng suy nghĩ (Thought):** {resp.get('thought', 'Không có suy nghĩ')}")
        
        if current_task['agent'] in ["Explorer", "Visualizer"]:
            final_code = st.text_area("Review & Edit Code (Trình biên tập)", value=resp.get('code', ''), height=250)
            
            if st.button(f"🚀 Phê duyệt & Chạy Bước {current_step_idx + 1}"):
                result = execution.execute_analysis(final_code, df)
                
                obs_text = ""
                plot_json_str = ""
                
                # SỬA LẠI LOGIC LƯU OBSERVATION: LƯU CẢ CODE VÀ KẾT QUẢ
                if current_task['agent'] == "Explorer":
                    st.markdown("**Kết quả xuất ra từ Terminal:**")
                    st.code(result.get("text_output", "Không có dữ liệu in ra."))
                    
                    # Truyền cả đoạn code Explorer đã viết vào cho Agent sau đọc
                    obs_text = f"--- BƯỚC {current_step_idx + 1} (EXPLORER) ---\nCode đã chạy:\n```python\n{final_code}\n```\nKết quả Terminal:\n{result.get('text_output')}"
                    
                elif current_task['agent'] == "Visualizer":
                    if result.get("fig"):
                        st.plotly_chart(result["fig"], use_container_width=True)
                        plot_json_str = result["fig"].to_json()
                        
                        # Truyền code vẽ biểu đồ cho Analyst đọc để biết nó đang nhìn biểu đồ gì
                        obs_text = f"--- BƯỚC {current_step_idx + 1} (VISUALIZER) ---\nCode vẽ biểu đồ đã chạy:\n```python\n{final_code}\n```\n(Trạng thái: Đã vẽ biểu đồ thành công)."
                    else:
                        st.error(f"Lỗi: Không thể tạo biểu đồ. {result.get('text_output')}")
                        obs_text = "Visualizer thất bại trong việc vẽ biểu đồ."
                
                st.session_state.history = logger.log_interaction(...) # Giữ nguyên như cũ
                
                # Đưa toàn bộ context cực giàu này vào bộ nhớ
                st.session_state.observations.append(obs_text)
                st.session_state.current_step += 1
                st.rerun()

        elif current_task['agent'] == "Analyst":
            final_report = st.text_area("Review & Edit Report (Báo cáo)", value=resp.get('report', ''), height=300)
            
            if st.button("✅ Phê duyệt & Hoàn tất"):
                st.markdown("### Báo Cáo Phân Tích Cuối Cùng")
                st.markdown(final_report)
                
                st.session_state.history = logger.log_interaction(
                    st.session_state.history,
                    prompt=current_task['task'],
                    ai_explanation=resp.get('thought', ''),
                    ai_code="",
                    final_code=final_report,
                    was_edited=(final_report != resp.get('report', '')),
                    result_log="Report Generated",
                    plot_json=""
                )
                
                st.session_state.current_step += 1
                st.success("🎉 Hoàn thành xuất sắc kế hoạch phân tích!")
                st.balloons()

with tab_history:
    if st.session_state.history:
        for i, entry in enumerate(reversed(st.session_state.history)):
            with st.expander(f"📍 {entry['timestamp']} - {entry['prompt'][:50]}..."):
                st.write(f"**Task:** {entry['prompt']}")
                st.info(f"**Suy nghĩ (Thought):** {entry.get('explanation', 'N/A')}")
                if entry.get('result_log') and entry['result_log'] != "Report Generated":
                    st.write("**Terminal Output:**")
                    st.code(entry['result_log'])
                if entry.get('plot_json'):
                    st.plotly_chart(go.Figure(json.loads(entry['plot_json'])), use_container_width=True)
                st.write("**Code / Báo cáo:**")
                st.code(entry['final_code'])