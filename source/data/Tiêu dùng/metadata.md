# Bộ dữ liệu Chỉ số giá tiêu dùng (CPI)

Dữ liệu này chứa thông tin chi tiết về chỉ số CPI của các nhóm hàng hóa và dịch vụ tiêu dùng tại Việt Nam theo thời gian.

### Các cột dữ liệu chính:
- **Năm**: Năm lấy dữ liệu (định dạng số nguyên).
- **Tháng**: Tháng lấy dữ liệu (từ 1 đến 12).
- **Nhóm hàng**: Tên loại hàng hóa hoặc dịch vụ (ví dụ: Thực phẩm, Đồ uống, Giao thông...).
- **Chỉ số tiêu dùng**: Giá trị chỉ số CPI tương ứng (số thập phân).

### Cách sử dụng:
Sử dụng DataFrame `df_tieu_dung` để thực hiện các phân tích về lạm phát, biến động giá cả theo nhóm hàng hoặc so sánh giữa các tháng/năm.