# Bộ dữ liệu Tổng hợp Tài chính và Giá Xăng dầu (2018 - 2025)

Bộ dữ liệu cung cấp cái nhìn toàn cảnh về thị trường tài chính và năng lượng tại Việt Nam theo từng ngày.

### Các nhóm dữ liệu chính:
1. **Nhóm Vàng thế giới [gold]**: 
   - Giá mở phiên, cao nhất, thấp nhất, kết phiên và khối lượng giao dịch (Volume).
2. **Nhóm Chỉ số VN-Index [VNI]**: 
   - Chỉ số chứng khoán Việt Nam. Bao gồm giá mở phiên trước, mở phiên, cao/thấp nhất và % thay đổi.
3. **Nhóm Tỉ giá USD [USD]**: 
   - Tỉ giá đô la Mỹ so với Việt Nam Đồng (VND).
4. **Nhóm Xăng dầu**: 
   - Giá các loại dầu DO, FO, KO và các loại xăng (E5 RON 92, RON 95-III, RON 95-IV).

### Các cột thời gian:
- **Năm, Tháng, Ngày**: Thời điểm ghi nhận dữ liệu.
- **Ngày_Full**: Cột được tạo thêm theo định dạng YYYY-MM-DD để vẽ biểu đồ thời gian.

### Biến môi trường:
Dữ liệu được nạp vào biến `df_tai_chinh`.

### Lưu ý khi phân tích:
- Một số ngày nghỉ lễ sẽ không có giá Vàng hoặc Chứng khoán (để trống).
- Giá xăng dầu thường cập nhật theo chu kỳ điều hành, không phải thay đổi hàng ngày.