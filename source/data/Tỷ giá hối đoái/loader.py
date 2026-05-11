import pandas as pd
import os

def clean_numeric(val):
    """Hàm hỗ trợ làm sạch chuỗi số chứa dấu phẩy, ký hiệu %, và hậu tố M/B/K"""
    if pd.isna(val):
        return val
    if isinstance(val, str):
        val = val.strip().replace(',', '')
        if val.endswith('%'):
            return float(val[:-1]) / 100.0
        if val.endswith('B'):
            return float(val[:-1]) * 1e9
        if val.endswith('M'):
            return float(val[:-1]) * 1e6
        if val.endswith('K'):
            return float(val[:-1]) * 1e3
        try:
            return float(val)
        except ValueError:
            return val
    return float(val)

def load_data() -> dict:
    """
    Nạp CSV, chuyển đổi sang cấu trúc MultiIndex DataFrame cho cả dòng và cột
    và trả về dict để đưa vào Execution Sandbox cho LLM.
    """
    # Lấy đường dẫn thư mục hiện tại của file loader.py này
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'TiGiaHoiDoai.csv')
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Không tìm thấy dữ liệu tại: {file_path}")

    # Đọc dữ liệu
    df = pd.read_csv(file_path)

    # Đặt MultiIndex cho dòng (Năm, Tháng, Ngày)
    df = df.set_index(['Năm', 'Tháng', 'Ngày'])
    df = df.sort_index(level=['Năm', 'Tháng', 'Ngày'])

    # Tạo từ điển ánh xạ để build MultiIndex cho cột: (Cấp 1: Nhóm, Cấp 2: Chỉ số)
    col_mapping = {}
    for col in df.columns:
        if col.startswith('[gold]'):
            col_mapping[col] = ('Gold', col.replace('[gold] ', '').strip())
        elif col.startswith('[VNI]'):
            col_mapping[col] = ('VNI', col.replace('[VNI] ', '').strip())
        elif col.startswith('[USD]'):
            col_mapping[col] = ('USD', col.replace('[USD] ', '').strip())
        else:
            col_mapping[col] = ('Xăng dầu', col.strip())

    # Gán MultiIndex mới cho các cột
    df.columns = pd.MultiIndex.from_tuples([col_mapping[c] for c in df.columns], names=['Nhóm', 'Chỉ số'])

    # Làm sạch toàn bộ các giá trị string thành float
    for col in df.columns:
        df[col] = df[col].apply(clean_numeric)

    # Trả về biến df_market để LLM có thể gọi tên chính xác
    return {
        "df_market": df
    }