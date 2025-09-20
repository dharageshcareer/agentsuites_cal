import google.generativeai as genai
import pandas as pd
import io
import json
from app.core.config import GOOGLE_API_KEY

# Configure the Generative AI client with your API key
genai.configure(api_key=GOOGLE_API_KEY)

def analyze_feedback_file(file_content: bytes, filename: str) -> dict:
    """
    Parses a feedback file (CSV or JSON), sends the content to an LLM for analysis,
    and returns a structured summary, sentiment, and action items. This function is stateless
    and does not connect to a database.
    """
    try:
        # 1. Parse the uploaded file content using pandas
        if filename.lower().endswith('.csv'):
            # Use an in-memory byte stream to read the raw file content
            dataframe = pd.read_csv(io.BytesIO(file_content))
        elif filename.lower().endswith('.json'):
            dataframe = pd.read_json(io.BytesIO(file_content))
        else:
            raise ValueError("Unsupported file type. Please upload a CSV or JSON file.")

        # Convert the entire dataframe to a simple string format for the LLM
        feedback_text = dataframe.to_string()

        # 2. Engineer the prompt to guide the LLM
        # This detailed prompt is crucial for getting a reliable, structured JSON output.
        prompt = f"""
        You are an expert educational analyst. Your task is to analyze the following student feedback data for an instructor.

        **Feedback Data:**
        ```
        {feedback_text}
        ```

        **Your Instructions:**
        Based on the data, perform the following three tasks:
        1.  **Summarize:** Write a concise, one-paragraph summary of the key themes and points mentioned in the feedback.
        2.  **Sentiment Analysis:** Determine the overall sentiment. You must classify it as one of the following exact strings: "Positive", "Negative", or "Mixed".
        3.  **Action Suggestions:** Generate a list of exactly 2 or 3 clear, actionable, and constructive recommendations for the instructor.

        **Output Format:**
        You must return your analysis ONLY as a single, valid JSON object. Do not add any text before or after the JSON object. The object must have these exact keys: "summary", "sentiment", "action_suggestions". The "action_suggestions" value must be an array of strings.

        **Example of a perfect response:**
        {{
            "summary": "Students generally appreciate the instructor's enthusiasm but find the pace of the lectures too fast and the assignment instructions unclear.",
            "sentiment": "Mixed",
            "action_suggestions": [
                "Consider slowing down the pace during complex topics or providing supplementary videos.",
                "Review and clarify the instructions for all major assignments before releasing them.",
                "Hold an optional weekly Q&A session to address student questions."
            ]
        }}
        """

        # 3. Call the Gemini API for analysis
        model = genai.GenerativeModel('gemini-2.5-pro')
        response = model.generate_content(prompt)

        # 4. Clean and parse the JSON response from the LLM
        # LLMs sometimes wrap JSON in markdown backticks, so we robustly clean it.
        cleaned_response_text = response.text.strip().replace('```json', '').replace('```', '').strip()
        analysis_result = json.loads(cleaned_response_text)

        # 5. Validate the parsed result to ensure it has the expected structure
        if not all(k in analysis_result for k in ["summary", "sentiment", "action_suggestions"]):
             raise ValueError("LLM response did not contain the expected JSON keys.")

        return analysis_result

    except Exception as e:
        print(f"An error occurred during feedback analysis: {e}")
        # Return a structured error that matches the Pydantic model for consistency
        return {
            "summary": "Failed to process the feedback file.",
            "sentiment": "Error",
            "action_suggestions": [f"An error occurred: {str(e)}"]
        }