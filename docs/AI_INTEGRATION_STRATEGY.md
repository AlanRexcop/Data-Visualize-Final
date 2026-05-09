# Summary: AI Integration Requirements (ai-guide-v2.pdf)

This document summarizes the mandatory guidelines for integrating AI into the Data Visualization project, emphasizing human-in-the-loop control and local execution.

## 1. Core Philosophy: Human-in-the-Loop
The relationship between AI and the user must follow a strict hierarchy:
- **AI Role:** Advisor and coder. It suggests ideas, writes code, and presents results based *only* on provided data. It must never invent data or figures.
- **Human Role:** Director and Decision Maker. The human provides the direction, reviews the code, and is the **only one** authorized to execute it.

## 2. The "No Silent Execution" Rule
- AI is forbidden from silently changing original data or running algorithms in the background.
- **Mandatory Display:** All AI-generated code must be displayed clearly to the user.
- **Natural Language Explanation:** AI must explain its code using comments (e.g., "This code uses `dropna()` to remove 15 null rows").

## 3. The Approval Workflow (Mandatory)
1. **Pending State:** AI code is generated but sits in a "Waiting for Approval" state.
2. **Human Intervention:** The user has the right to edit, modify, or delete parts of the AI's code (e.g., changing a threshold from 3 to 2 standard deviations).
3. **Explicit Approval:** Code only runs and returns results/charts *after* the human clicks "Approve."

## 4. Technical Architecture
The system should ideally be split into:
- **Frontend:** A user interface (Streamlit, Gradio, React) with:
    - Chat/Form input for requests.
    - Code viewer/editor.
    - Approval button.
    - Results display area (Charts/Tables).
- **Backend/API:**
    - **API AI:** Connects to a model (Gemini/OpenAI) to get code + explanations.
    - **API Execution:** Runs approved code on the **local machine** and returns logs/images.
    - **API Logs:4** Stores every request, code snippet, and result for audit.

---

# Implementation Strategy: "Local AI Analyst"

To fulfill these requirements efficiently, we will build a **Streamlit-based AI Analyst Dashboard**.

### Step 1: Frontend & Interaction (Streamlit)
Streamlit is the best choice because it runs locally and handles Python execution natively.
- **UI Design:** A sidebar for data upload/preview and a main chat interface for interacting with the AI.
- **Code Editor:** Use `st.code` or a text area for the user to review and edit the generated Python code.
- **The "Big Red Button":** An explicit `st.button("Approve & Execute")` to fulfill Requirement 2.1.

### Step 2: AI Backend (API AI)
We will use a Python module that:
1. Takes the user's natural language request.
2. Provides the LLM (Gemini) with the **DataFrame Schema** (column names and types) as context.
3. Requests a response in a specific JSON format: `{ "explanation": "...", "code": "..." }`.

### Step 3: Local Execution & Logging (API Execution/Logs)
- **Safe Execution:** Use Python's `exec()` function in a controlled scope to run the approved code.
- **Result Capture:** Redirect `stdout` to capture logs and save generated plots (Matplotlib/Seaborn) to a temporary buffer to display in the UI.
- **Audit Trail:** Every interaction will be appended to a `logs/session_history.json` file to satisfy Requirement 2.2.

### Step 4: Final Handover
- We will provide a `README.md` explaining how the AI was used, documenting specific instances where the user "adjusted" the AI's code (to prove human control during the oral exam).
