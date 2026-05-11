import pandas as pd
import os
import numpy as np

def clean_financial_value(val):
    """
    Hàm xử lý các định dạng đặc biệt: "1,784.49", "592.84M", "1.00%"
    """
    if pd.isna(val) or val == "":
        return np.nan
    
    # Nếu đã là số thì trả về luôn
    if isinstance(val, (int, float)):
        return val
    
    # Chuyển về string và làm sạch khoảng trắng, dấu ngoặc kép
    s = str(val).replace('"', '').replace("'", "").strip()
    
    try:
        # 1. Xử lý phần trăm
        if '%' in s:
            return float(s.replace('%', ''))
        
        # 2. Xử lý hậu tố Volume (M = Triệu, K = Nghìn)
        if 'M' in s:
            return float(s.replace('M', '').replace(',', '')) * 1_000_000
        if 'K' in s:
            return float(s.replace('K', '').replace(',', '')) * 1_000
        
        # 3. Xử lý dấu phẩy phân cách phần ngàn (VD: 1,784.49)
        return float(s.replace(',', ''))
    except:
        return np.nan

def load_data():
    """
    Nạp và làm sạch dữ liệu tài chính.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, "TiGiaHoiDoai.csv")
    
    try:
        # Đọc file CSV
        df = pd.read_csv(csv_path, encoding='utf-8')
        
        # Tạo cột Ngày_Full để phân tích chuỗi thời gian
        # Errors='coerce' để xử lý các ngày không hợp lệ nếu có
        df['Ngày_Full'] = pd.to_datetime(
            df[['Năm', 'Tháng', 'Ngày']].rename(columns={'Năm': 'year', 'Tháng': 'month', 'Ngày': 'day'}),
            errors='coerce'
        )
        
        # Danh sách các cột cần làm sạch (tất cả trừ các cột thời gian)
        exclude_cols = ['Năm', 'Tháng', 'Ngày', 'Ngày_Full']
        cols_to_clean = [c for s in [df.columns] for c in s if c not in exclude_cols]
        
        for col in cols_to_clean:
            df[col] = df[col].apply(clean_financial_value)
            
        # Sắp xếp theo ngày tăng dần
        df = df.sort_values('Ngày_Full').reset_index(drop=True)
        
        return {
            "df_tai_chinh": df
        }
    except Exception as e:
        print(f"Lỗi Loader Tài chính: {e}")
        return {}