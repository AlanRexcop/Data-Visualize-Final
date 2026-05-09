import json
from google import genai

def get_ai_analysis(api_key, prompt, mode="Explorer", context=None):
    client = genai.Client(api_key=api_key)
    context_str = f"\nContext from previous steps:\n{context}\n" if context else ""
    
    mode_instructions = {
        "Explorer": "You are a Data Explorer. Focus on identifying patterns, trends, and anomalies in the data.",
        "Visualizer": "You are a Visualizer. Focus on creating high-impact Plotly charts. Use professional color schemes.",
        "Analyst": "You are an Analyst. Interpret findings from previous agents. Provide statistical insights without writing new data processing code."
    }
    
    system_prompt = f"""
    {mode_instructions.get(mode, mode_instructions['Explorer'])}
    
    Dataset Context:
    - Year (int), Month (int), Category (str), Index_Value (float), Hierarchy_Level (str), Economic_Period (str), Category_Group (str), Is_Tet_Month (bool).
    {context_str}
    
    Request: {prompt}
    
    MANDATORY OUTPUT FORMAT:
    Respond ONLY with a JSON object containing:
    1. "explanation": A detailed 'Thinking Trail' explaining your logic.
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
