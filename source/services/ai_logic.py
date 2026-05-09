import json
from google import genai

def get_ai_plan(api_key, user_request, metadata_str):
    client = genai.Client(api_key=api_key)
    
    system_prompt = f"""
    Bạn là một AI Quản lý dự án (Orchestrator) phân tích dữ liệu CPI tại Việt Nam.
    Hãy chia yêu cầu của người dùng thành một kế hoạch gồm các bước logic.
    
    THÔNG TIN DỮ LIỆU HIỆN CÓ (Đã được load sẵn vào biến dataframe `df`):
    {metadata_str}
    
    Bạn có 3 Agents (Đặc vụ) để sử dụng:
    1. "Explorer": Dùng pandas và lệnh print() để khám phá, lọc dữ liệu (Không vẽ biểu đồ).
    2. "Visualizer": Dùng Plotly để vẽ biểu đồ từ dữ liệu (Chỉ vẽ, gán vào biến `fig`).
    3. "Analyst": Đọc các kết quả phía trên và viết báo cáo bằng chữ (Không viết code).
    
    YÊU CẦU BẮT BUỘC: 
    - Các mô tả 'task' PHẢI viết hoàn toàn bằng TIẾNG VIỆT, giải thích rõ sẽ làm gì với các cột nào.
    - Output CHỈ LÀ mảng JSON.
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{system_prompt}\n\nYêu cầu của người dùng: {user_request}"
    )
    
    try:
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        return[{"step": 1, "agent": "Explorer", "task": f"Lỗi tạo kế hoạch, chuyển về khám phá. Yêu cầu: {user_request}"}]


def get_ai_analysis(api_key, prompt, mode="Explorer", context=None, observation=None, metadata_str=""):
    client = genai.Client(api_key=api_key)
    
    context_str = f"\nBối cảnh các bước trước:\n{context}\n" if context else ""
    react_context = f"\nKết quả thu được từ lệnh in trước đó (Observation):\n{observation}\n" if observation else ""
    
    # LUẬT THÉP BẮT BUỘC DÀNH CHO AI
    vn_enforcement = """
    CÁC LUẬT THÉP BẮT BUỘC (NẾU VI PHẠM SẼ BỊ PHẠT):
    1. TIẾNG VIỆT 100%: Dòng suy nghĩ (thought), báo cáo (report), và TẤT CẢ các chú thích/comment trong code Python (bắt đầu bằng #) PHẢI được viết bằng TIẾNG VIỆT.
    2. CẤM MOCK DATA: Biến dataframe `df` ĐÃ ĐƯỢC KHỞI TẠO SẴN TRONG MÔI TRƯỜNG. Tuyệt đối KHÔNG tạo dummy data. KHÔNG gọi `pd.DataFrame(...)` hoặc `pd.read_csv(...)`.
    3. MÔI TRƯỜNG ĐỘC LẬP BỊ XÓA SAU MỖI BƯỚC: Code của bạn chạy trong môi trường độc lập. Các biến tạo ra ở bước trước (VD: `df_filtered`) SẼ BỊ XÓA SẠCH ở bước sau. Do đó:
       - Nếu bạn là Visualizer, bạn PHẢI TỰ VIẾT LẠI đoạn code lọc/xử lý dữ liệu từ `df` gốc. Không được gọi lại tên biến của Explorer.
       - LUÔN TẠO BẢN SAO nếu cần biến đổi dữ liệu (ví dụ: `df_plot = df.copy()`), tuyệt đối KHÔNG chỉnh sửa đè trực tiếp lên `df` (không dùng `inplace=True`).
    """
    
    if mode == "Explorer":
        system_prompt = f"""
        Bạn là Chuyên gia Khám phá Dữ liệu (Data Explorer).
        Nhiệm vụ: Viết code Python (pandas) sử dụng hàm `print()` để in ra các chỉ số. Không vẽ biểu đồ.
        
        {vn_enforcement}
        
        THÔNG TIN VỀ BIẾN `df` HIỆN CÓ:
        {metadata_str}
        
        {context_str}
        {react_context}
        
        MẪU OUTPUT JSON:
        {{
            "thought": "Tôi sẽ dùng pandas để lọc các tháng Tết và tính trung bình...",
            "code": "# Lọc các tháng Tết để kiểm tra\\ntet_data = df[df['Is_Tet_Month'] == True]\\nprint(tet_data.describe())"
        }}
        """
    elif mode == "Visualizer":
        system_prompt = f"""
        Bạn là Chuyên gia Trực quan hóa (Visualizer). 
        Nhiệm vụ: Đọc số liệu từ Explorer, viết code Plotly để vẽ biểu đồ có tính tương tác.
        Luôn gán biểu đồ vào biến tên là `fig`. KHÔNG sử dụng `fig.show()`.
        
        {vn_enforcement}
        
        THÔNG TIN VỀ BIẾN `df` HIỆN CÓ:
        {metadata_str}
        
        {context_str}
        {react_context}
        
        MẪU OUTPUT JSON:
        {{
            "thought": "Dựa vào số liệu trên, tôi sẽ vẽ biểu đồ đường...",
            "code": "# Khởi tạo biểu đồ đường thể hiện lạm phát\\nfig = px.line(df, x='Year', y='Index_Value', title='Biểu đồ CPI')"
        }}
        """
    elif mode == "Analyst":
        system_prompt = f"""
        Bạn là Chuyên gia Phân tích (Lead Analyst). Bạn KHÔNG viết code.
        Nhiệm vụ: Đọc số liệu từ Explorer và hình ảnh từ Visualizer để viết báo cáo.
        
        {vn_enforcement}
        
        {context_str}
        {react_context}
        
        MẪU OUTPUT JSON:
        {{
            "thought": "Xâu chuỗi các dữ liệu để tìm ra Insight...",
            "report": "### Báo cáo Phân tích\\nTừ dữ liệu ta có thể thấy..."
        }}
        """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{system_prompt}\n\nYêu cầu hiện tại: {prompt}"
    )
    
    try:
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        return {"thought": "Lỗi định dạng", "code": f"# Lỗi: {str(e)}", "report": f"Lỗi: {str(e)}"}