import json
from google import genai

def get_ai_plan(api_key, user_request, metadata_str):
    # Lưu ý: Bạn đề cập Gemini 3.1 Flash Lite, nếu ý bạn là 1.5 Flash hoặc bản mới nhất
    # hãy đảm bảo tên model chính xác. Ở đây tôi dùng gemini-1.5-flash để ổn định.
    client = genai.Client(api_key=api_key)
    
    system_prompt = f"""
    Bạn là Chuyên gia Lập kế hoạch (Orchestrator). 
    Nhiệm vụ của bạn là chia yêu cầu của người dùng thành một quy trình gồm NHIỀU BƯỚC, sử dụng các đặc vụ chuyên biệt.

    DỮ LIỆU CỦA BẠN:
    {metadata_str}

    DANH SÁCH ĐẶC VỤ:
    1. "Explorer": CHỈ dùng để tính toán số liệu, lọc dữ liệu, nhóm (aggregation) và in kết quả (print). KHÔNG VẼ BIỂU ĐỒ.
    2. "Visualizer": CHỈ dùng để vẽ biểu đồ (Plotly) dựa trên các tính toán từ Explorer.
    3. "Analyst": CHỈ dùng để viết báo cáo giải thích kết quả cuối cùng. KHÔNG VIẾT CODE.

    QUY TẮC CHIA BƯỚC (BẮT BUỘC):
    - Nếu người dùng yêu cầu "khám phá/tính toán" -> Phải có bước của Explorer.
    - Nếu người dùng yêu cầu "vẽ/plot/biểu đồ" -> BẮT BUỘC phải tách riêng một bước cho Visualizer.
    - Nếu người dùng yêu cầu "giải thích/phân tích/báo cáo" -> BẮT BUỘC phải có bước cuối cho Analyst.
    - TUYỆT ĐỐI KHÔNG gộp chung việc tính toán và vẽ biểu đồ vào một bước.

    ĐỊNH DẠNG TRẢ VỀ: CHỈ trả về mảng JSON.
    Mẫu: [
        {{"step": 1, "agent": "Explorer", "task": "Tính tổng hợp CPI theo tháng..."}},
        {{"step": 2, "agent": "Visualizer", "task": "Vẽ biểu đồ đường..."}},
        {{"step": 3, "agent": "Analyst", "task": "Giải thích xu hướng..."}}
    ]
    """
    
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite", # Hoặc model bạn đang dùng
        contents=f"{system_prompt}\n\nYêu cầu khách hàng: {user_request}"
    )
    
    try:
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        raw_plan = json.loads(clean_text)
        
        # Hậu xử lý chuẩn hóa key
        final_plan = []
        for i, p in enumerate(raw_plan):
            final_plan.append({
                "step": i + 1,
                "agent": p.get("agent", "Explorer"),
                "task": p.get("task", "Thực hiện phân tích")
            })
        
        # Kiểm tra nếu AI quá lười (chỉ trả về 1 bước trong khi yêu cầu có "plot" hoặc "giải thích")
        # Đây là logic dự phòng (fallback)
        keywords_plot = ['vẽ', 'plot', 'biểu đồ', 'graph', 'chart']
        keywords_analyze = ['giải thích', 'phân tích', 'báo cáo', 'tại sao']
        
        has_plot = any(k in user_request.lower() for k in keywords_plot)
        has_analyze = any(k in user_request.lower() for k in keywords_analyze)
        
        # Nếu AI chỉ trả về 1 bước nhưng yêu cầu phức tạp, ta chèn thêm bước thủ công (nếu cần)
        if len(final_plan) == 1:
            if has_plot:
                final_plan.append({"step": 2, "agent": "Visualizer", "task": "Trực quan hóa kết quả đã tìm thấy."})
            if has_analyze:
                final_plan.append({"step": len(final_plan)+1, "agent": "Analyst", "task": "Phân tích và giải thích ý nghĩa số liệu."})

        return final_plan
    except:
        return [{"step": 1, "agent": "Explorer", "task": "Khám phá dữ liệu tổng quát"}]


def get_ai_analysis(api_key, prompt, mode="Explorer", context=None, observation=None, metadata_str=""):
    client = genai.Client(api_key=api_key)
    
    context_str = f"\nBối cảnh các bước trước:\n{context}\n" if context else ""
    react_context = f"\nKết quả thu được từ lệnh in trước đó (Observation):\n{observation}\n" if observation else "" 
    
    # LUẬT THÉP BẮT BUỘC DÀNH CHO AI
    vn_enforcement = """
    CÁC LUẬT THÉP BẮT BUỘC (NẾU VI PHẠM SẼ BỊ PHẠT):
    1. TIẾNG VIỆT 100%: Dòng suy nghĩ (thought), báo cáo (report), và TẤT CẢ các chú thích/comment trong code Python (bắt đầu bằng #) PHẢI được viết bằng TIẾNG VIỆT.
    2. CẤM MOCK DATA: Biến dataframe `df` ĐÃ ĐƯỢC KHỞI TẠO SẴN TRONG MÔI TRƯỜNG. Tuyệt đối KHÔNG tạo dummy data. KHÔNG gọi `pd.DataFrame(...)` hoặc `pd.read_csv(...)`.
    3. MÔI TRƯỜNG ĐỘC LẬP: Các biến tạo ra ở bước trước (VD: `df_time_series`) SẼ BỊ XÓA SẠCH ở bước sau. Do đó, Visualizer HÃY ĐỌC PHẦN "Code đã chạy" của Explorer trong Observation để COPY/VIẾT LẠI logic xử lý dữ liệu (groupby, filter...) từ `df` gốc.
    4. CẤM CẮT XÉN DỮ LIỆU TỔNG HỢP: Khi Explorer in các bảng thống kê hoặc dữ liệu đã được nhóm (groupby), TUYỆT ĐỐI KHÔNG DÙNG `.head()`. Hãy in bằng `print(df_grouped.to_string())` để hiển thị toàn bộ kết quả, nhằm đảm bảo Visualizer và Analyst có đầy đủ số liệu của tất cả các tháng/năm.
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
        model="gemini-3.1-flash-lite",
        contents=f"{system_prompt}\n\nYêu cầu hiện tại: {prompt}"
    )
    
    try:
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        return {"thought": "Lỗi định dạng", "code": f"# Lỗi: {str(e)}", "report": f"Lỗi: {str(e)}"}