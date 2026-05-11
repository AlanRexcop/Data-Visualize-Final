import pandas as pd
import os

def load_data() -> dict:
    """
    Nạp CSV, chuyển đổi sang cấu trúc MultiIndex DataFrame 3D
    và trả về dict để đưa vào Execution Sandbox cho LLM.
    """
    # Lấy đường dẫn thư mục hiện tại của file loader.py này
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'CPI_final_for_powerbi.csv')
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Không tìm thấy dữ liệu tại: {file_path}")

    # Đọc dữ liệu
    df = pd.read_csv(file_path)

    # Chuyển đổi sang dạng 3 chiều: 
    data_3d = df.pivot_table(
        index=['Year', 'Month'],
        columns='Category',
        values='Index_Value',
        aggfunc='first'
    )
    
    # Sắp xếp lại index
    data_3d = data_3d.sort_index(level=['Year', 'Month'])
    
    # Trả về biến df_cpi để LLM có thể gọi tên chính xác
    return {
        "df_cpi": data_3d
    }