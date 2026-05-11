# Bộ dữ liệu Lượng khách du lịch quốc tế đến Việt Nam

Bộ dữ liệu chứa thông tin thống kê về số lượng khách du lịch quốc tế đến Việt Nam, được phân loại theo tháng, năm và theo từng quốc gia hoặc khu vực lãnh thổ (từ năm 2018 đến 2026).

### Các cột dữ liệu:
- **Năm**: Năm quan sát (2018 - 2026).
- **Tháng**: Tháng quan sát (1 - 12).
- **Quốc gia/Khu vực**: Tên châu lục, vùng lãnh thổ hoặc quốc gia (ví dụ: Châu Á, Châu Âu, Hàn Quốc, Hoa Kỳ...). 
  *Lưu ý phân tích: Cột này chứa cả số liệu tổng của Châu lục (VD: "Châu Á") và số liệu chi tiết của từng quốc gia (VD: "Hàn Quốc"). Khi tính tổng, cần cẩn thận để không cộng gộp trùng lặp cả châu lục và quốc gia.*
- **Lượng khách**: Số lượng khách du lịch (người). 

### Đặc điểm dữ liệu cần lưu ý (Context):
- **Tác động của COVID-19**: Dữ liệu lượng khách trống (NaN) hoặc sụt giảm cực mạnh từ tháng 4/2020 đến hết năm 2021 do Việt Nam đóng cửa biên giới phòng chống dịch bệnh.

### Biến môi trường:
Dữ liệu được nạp vào biến `df_khach_du_lich`.