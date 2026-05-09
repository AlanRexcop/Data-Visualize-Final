# Project Environment & Workflow Standards

## Environment Management
- All Python code execution MUST be performed through the project-specific Conda environment.
- **Environment Name:** `Data_Lab1`
- **Execution Prefix:** Every command must be prefixed with `conda run -n Data_Lab1 ...`.
  - Example: `conda run -n Data_Lab1 python source/app.py`
  - Example: `conda run -n Data_Lab1 python -m unittest discover tests`

## Testing Standards
- All tests are located in the `tests/` directory.
- Tests MUST be executed within the `Data_Lab1` environment to ensure necessary dependencies (like `google-genai`, `streamlit`, `pandas`, `plotly`) are available.
- **Command:** `conda run -n Data_Lab1 python -m unittest discover tests`

## Dependency Handling
- The environment includes core data science and application libraries. Never attempt to run code with the system Python; always use the environment wrapper.
- If a new dependency is required, request its addition to `docs/CONDA_ENV_CONFIG.md` before updating the environment.
