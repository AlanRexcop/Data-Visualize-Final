Dữ liệu biến `df_market` là ma trận MultiIndex Pandas DataFrame chứa thông tin giao dịch tài chính và giá cả hàng hóa.

**Cấu trúc dữ liệu:**
- **Trục Dòng (Row Index - 3 cấp):** `Năm` (Year), `Tháng` (Month), `Ngày` (Day) - Tạo thành chuỗi thời gian liên tục.
- **Trục Cột (Column Index - 2 cấp):** 
  - **Cấp 1 (Nhóm hàng - Category):** Phân loại thành 4 nhóm chính là `Gold`, `VNI`, `USD`, và `Xăng dầu`.
  - **Cấp 2 (Chỉ số - Metric):** Chi tiết các thông số của nhóm hàng đó (Giá mở phiên, Giá kết phiên, Volume, % Thay đổi, hoặc tên các loại xăng/dầu cụ thể).

**Lưu ý về giá trị:**
- Tất cả các giá trị số (Giá, Volume) đã được làm sạch thành định dạng số thực (float). 
- Đơn vị `Volume` đã được quy đổi (ví dụ: `M` -> triệu, `B` -> tỷ, `K` -> nghìn).
- Đơn vị `% Thay đổi` đã được chuyển về số thập phân (ví dụ: `1.00%` -> `0.01`).
- Các ô không có dữ liệu giao dịch hoặc chưa cập nhật giá sẽ là `NaN`.

**Ví dụ trích xuất:**
- `df_market.loc[(2025, 12, 31), ('Gold', 'Giá kết phiên')]` sẽ trả về giá kết phiên của vàng vào ngày 31/12/2025.
- `df_market['VNI']` sẽ trả về toàn bộ dữ liệu (Open, High, Low, Close, Volume, % Change) của nhóm VN-Index.