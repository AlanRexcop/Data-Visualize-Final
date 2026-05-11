# source/services/data_registry.py
import os
import importlib.util
import pandas as pd
from config import DATA_DIR

class DataRegistry:
    def __init__(self):
        self.data_dir = DATA_DIR
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def get_available_datasets(self) -> list:
        """Returns a list of valid dataset folder names in source/data/"""
        datasets =[]
        for d in os.listdir(self.data_dir):
            if os.path.isdir(os.path.join(self.data_dir, d)):
                datasets.append(d)
        return datasets

    def get_metadata_context(self, active_datasets: list) -> str:
        """Reads metadata.md from selected datasets to inject into the LLM system prompt."""
        if not active_datasets:
            return "No datasets currently active."
            
        context = "### Available Data Context ###\n"
        context += "You have access to the following pre-loaded variables in your Python environment:\n"
        
        for ds in active_datasets:
            md_path = os.path.join(self.data_dir, ds, "metadata.md")
            if os.path.exists(md_path):
                with open(md_path, "r", encoding="utf-8") as f:
                    context += f"\n--- Dataset: {ds} ---\n{f.read()}\n"
        return context

    def load_active_datasets(self, active_datasets: list) -> dict:
        """
        Executes loader.py for each active dataset. 
        Returns a combined dictionary of variables for the execution sandbox.
        """
        sandbox_vars = {}
        for ds in active_datasets:
            ds_path = os.path.join(self.data_dir, ds)
            loader_path = os.path.join(ds_path, "loader.py")
            
            # Prefer custom loader.py
            if os.path.exists(loader_path):
                try:
                    spec = importlib.util.spec_from_file_location(f"loader_{ds}", loader_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    if hasattr(module, "load_data"):
                        # Execute load_data() with no arguments
                        dataset_vars = module.load_data()
                        if isinstance(dataset_vars, dict):
                            sandbox_vars.update(dataset_vars)
                except Exception as e:
                    print(f"Error loading {ds} via loader.py: {e}")
            else:
                # Fallback: Auto-load the first CSV found
                for file in os.listdir(ds_path):
                    if file.endswith(".csv"):
                        try:
                            df = pd.read_csv(os.path.join(ds_path, file))
                            # Fallback naming convention: df_filename
                            var_name = f"df_{file.replace('.csv', '').lower()}"
                            sandbox_vars[var_name] = df
                            break # Only load one fallback CSV per folder
                        except Exception as e:
                            print(f"Error auto-loading CSV in {ds}: {e}")
                            
        return sandbox_vars