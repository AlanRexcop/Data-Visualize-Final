import json
from google import genai

def get_ai_analysis(api_key, prompt, context=None):
    client = genai.Client(api_key=api_key)
    context_str = f"\nContext from previous steps:\n{context}\n" if context else ""
    
    system_prompt = f"""
    You are an expert Data Scientist analyzing Vietnam's CPI data using Plotly.
    Context:
    - Year (int), Month (int), Category (str), Index_Value (float), Hierarchy_Level (str), Economic_Period (str), Category_Group (str), Is_Tet_Month (bool).
    {context_str}
    
    Request: {prompt}
    
    MANDATORY OUTPUT FORMAT:
    Respond ONLY with a JSON object containing:
    1. "explanation": A natural language description of what the code does.
    2. "code": Clean, executable Python code. 
    
    CODE RULES:
    - Use 'df' as the primary DataFrame variable.
    - Always assign your interactive Plotly figure to a variable named 'fig'.
    - Use 'plotly.express' or 'plotly.graph_objects'.
    - Enable tooltips, markers, and gridlines.
    - Do NOT include any display command like 'fig.show()'.
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=system_prompt
    )
    
    try:
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        return {"explanation": "Error", "code": f"# Error: {str(e)}"}
