import pandas as pd
import os

def load_data():
    """
    Nạp dữ liệu Khách du lịch từ file CSV.
    Trả về một dictionary chứa biến DataFrame cho sandbox.
    """
    # Lấy đường dẫn tuyệt đối đến file CSV cùng thư mục
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, "KhachDuLich.csv")
    
    try:
        # Đọc dữ liệu với encoding utf-8
        df = pd.read_csv(csv_path, encoding='utf-8')
        
        # Xử lý làm sạch cơ bản: ép kiểu số cho cột Lượng khách
        # Các ô trống (như giai đoạn dịch COVID-19) sẽ tự động biến thành NaN
        df['Lượng khách'] = pd.to_numeric(df['Lượng khách'], errors='coerce')
        
        # Trả về biến df_khach_du_lich để AI sử dụng
        return {
            "df_khach_du_lich": df
        }
    except Exception as e:
        print(f"Lỗi khi nạp dữ liệu khách du lịch: {e}")
        return {}