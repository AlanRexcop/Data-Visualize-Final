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
    
    try:
        # Đọc dữ liệu với encoding utf-8 để hỗ trợ tiếng Việt
        df = pd.read_csv(csv_path, encoding='utf-8')
        
        # Xử lý làm sạch cơ bản: ép kiểu số cho cột chỉ số, các ô trống sẽ là NaN
        df['Chỉ số tiêu dùng'] = pd.to_numeric(df['Chỉ số tiêu dùng'], errors='coerce')
        
        # Trả về biến df_tieu_dung để AI sử dụng
        return {
            "df_tieu_dung": df
        }
    except Exception as e:
        print(f"Lỗi khi nạp dữ liệu tiêu dùng: {e}")
        return {}