# source/skills/data_utils.py
import pandas as pd

def describe_df(df: pd.DataFrame):
    """
    Injected helper to provide a comprehensive summary of a DataFrame.
    Prints output to stdout (which is captured by execution.py).
    """
    print(f"--- Dataset Overview ---")
    print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")

    for col in df.columns:
        col_dtype = df[col].dtype
        print(f"\nColumn: {col} ({col_dtype})")
        
        # Check for nulls
        null_count = df[col].isna().sum()
        if null_count > 0:
            print(f"  - Percentage of NaNs: {(null_count / len(df)) * 100:.2f}%")
        
        # Logic for categorical vs numerical
        if col_dtype == 'object' or col_dtype == 'category':
            uniques = df[col].unique()
            if len(uniques) < 15:
                print(f"  - Unique values: {uniques}")
            else:
                print(f"  - Unique values: {len(uniques)} distinct values (too many to list)")
        else:
            # Summary stats for numbers
            desc = df[col].describe()
            print(f"  - Mean: {desc['mean']:.2f} | Min: {desc['min']} | Max: {desc['max']}")