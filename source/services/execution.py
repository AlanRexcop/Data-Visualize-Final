import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import io
import contextlib

def execute_analysis(final_code, df):
    exec_globals = {'pd': pd, 'px': px, 'go': go, 'df': df}
    
    # Tạo bộ đệm để hứng kết quả từ các lệnh print() của AI
    output_buffer = io.StringIO()
    
    try:
        # Chạy code và chuyển hướng toàn bộ print() vào bộ đệm
        with contextlib.redirect_stdout(output_buffer):
            exec(final_code, exec_globals)
            
        stdout_result = output_buffer.getvalue()
        fig = exec_globals.get('fig')
        
        return {
            "status": "success", 
            "text_output": stdout_result.strip(), 
            "fig": fig
        }
    except Exception as e:
        return {
            "status": "error", 
            "text_output": f"Lỗi thực thi (Execution Error): {str(e)}", 
            "fig": None
        }