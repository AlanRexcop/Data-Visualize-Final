import pandas as pd
import os

def load_data():
    """
    Nạp dữ liệu Chỉ số tiêu dùng từ file CSV.
    Trả về một dictionary chứa các biến DataFrame cho sandbox.
    """
    # Lấy đường dẫn tuyệt đối đến file CSV cùng thư mục
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, "TieuDung.csv")
    
    # Ánh xạ từ các mã/tên chuẩn (CPI_product) sang tiêu đề cột tiếng Việt trong CSV
    column_mapping = {
        "year": "Năm",
        "month": "Tháng",
        "product_item": "Nhóm hàng",
        "cpi_value": "Chỉ số tiêu dùng",
        "region": "Khu vực/Vùng miền"
    }
    
    try:
        # Đọc dữ liệu với encoding utf-8 để hỗ trợ tiếng Việt
        df = pd.read_csv(csv_path, encoding='utf-8')
        
        # Kiểm tra và nạp đúng cột dựa trên mapping
        # Nếu file có các cột tiếng Anh, chúng ta sẽ đổi tên sang tiếng Việt để thống nhất
        inv_map = {v: v for k, v in column_mapping.items()} # Giữ nguyên nếu đã là tiếng Việt
        
        # Đảm bảo cột quan trọng nhất 'Chỉ số tiêu dùng' được ép kiểu số
        target_col = column_mapping["cpi_value"]
        if target_col in df.columns:
            df[target_col] = pd.to_numeric(df[target_col], errors='coerce')
        
        # Loại bỏ các dòng hoàn toàn trống (nếu có)
        df = df.dropna(how='all')
        
        # Trả về biến df_tieu_dung để AI sử dụng
        return {
            "df_tieu_dung": df
        }
    except Exception as e:
        print(f"Lỗi khi nạp dữ liệu tiêu dùng: {e}")
        return {}