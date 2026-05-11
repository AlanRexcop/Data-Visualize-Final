Dữ liệu biến `df_cpi` là ma trận (Pivot Table) MultiIndex Pandas DataFrame của chỉ số CPI (MoM).
- **Trục 1 (Index - Cấp 1):** Năm (Year)
- **Trục 2 (Index - Cấp 2):** Tháng (Month)
- **Trục 3 (Columns):** Danh mục nhóm hàng (Category)

**Mục đích:**
Bức tranh toàn cảnh của một tháng cụ thể (tất cả các nhóm hàng) hoặc theo dõi biến động của một nhóm hàng xuyên suốt các năm.

**Lưu ý về giá trị:**
Mọi giá trị tại các ô giao nhau là chỉ số CPI so với tháng trước. 
Ví dụ: `df_cpi.loc[(2024, 1), 'Lương thực']` sẽ trả về chỉ số của mặt hàng Lương thực vào tháng 1 năm 2024.