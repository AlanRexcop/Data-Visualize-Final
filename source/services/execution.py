import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def execute_analysis(final_code, df):
    exec_globals = {'pd': pd, 'px': px, 'go': go, 'df': df}
    exec(final_code, exec_globals)
    return exec_globals.get('fig')
