import google.generativeai as genai
from sqlalchemy import create_engine, text
import chromadb
from chromadb.utils import embedding_functions

from app.core.config import GOOGLE_API_KEY, DATABASE_URL

# --- 1. Configure the Gemini Model ---
genai.configure(api_key=GOOGLE_API_KEY)


# --- 2. Define the Tools ---

# Tool 1: SQL Query Executor (Existing Tool)
def execute_sql_query(query: str) -> str:
    """
    Executes a SQL query against the 'jobplacement_RAG' schema for structured data
    and returns the result as a string. Use this for specific, factual questions
    about students, employers, salaries, counts, or averages.
    """
    print(f"--- Executing SQL Query: {query} ---")
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            trans = connection.begin()
            result = connection.execute(text(query))
            rows = result.fetchall()
            trans.commit()
            if not rows:
                return "Query executed successfully, but returned no results."
            column_names = result.keys()
            result_string = ", ".join(column_names) + "\n"
            for row in rows:
                result_string += ", ".join(map(str, row)) + "\n"
            return result_string
    except Exception as e:
        return f"Error executing query: {str(e)}"

# Tool 2: Semantic Job Search (New Tool)
def search_job_descriptions(search_query: str) -> str:
    """
    Performs a semantic search on job descriptions in the vector database.
    Use this for open-ended or conceptual questions about job roles, skills, or responsibilities,
    like 'find jobs related to python and machine learning' or 'what roles require strong communication skills?'.
    Do NOT use this tool for questions about salaries, counts, or other specific data points;
    use the `execute_sql_query` tool for those instead.
    """
    print(f"--- Performing Semantic Search for: '{search_query}' ---")
    try:
        client = chromadb.PersistentClient(path="chroma_db")
        sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        collection = client.get_collection(
            name="job_descriptions",
            embedding_function=sentence_transformer_ef
        )
        results = collection.query(
            query_texts=[search_query],
            n_results=3 # Return the top 3 most similar results
        )

        if not results or not results.get('documents') or not results['documents'][0]:
            return "No relevant job descriptions found for your query."

        # Format the results for the LLM
        response_str = "Found the following relevant job listings:\n\n"
        for i, doc in enumerate(results['documents'][0]):
            metadata = results['metadatas'][0][i]
            response_str += f"Result {i+1}:\n"
            response_str += f"Job ID: {metadata.get('job_id')}\n"
            response_str += f"{doc}\n\n"
        return response_str
    except Exception as e:
        return f"Error during semantic search: {e}"


# --- 3. Create the Hybrid Agent ---
SYSTEM_PROMPT = """
You are an expert assistant for a job placement agency. Your goal is to answer user questions using the tools provided.

Here is the database schema you can query. ALL tables are in the `jobplacement_RAG` schema:
- `students` (columns: student_id, first_name, last_name, email, major, graduation_year, resume_url)
- `employers` (columns: employer_id, company_name, industry, website, contact_email)
- `job_listings` (columns: job_id, employer_id, job_title, job_description, min_salary, max_salary, location, posted_date, is_active)
- `placements` (columns: placement_id, student_id, job_id, placement_date, offered_salary)

You have two tools at your disposal:

1.  `execute_sql_query`: For questions about structured data.
    - Use this for queries involving counts, averages, specific names, salaries, or filtering on columns like `graduation_year` or `company_name`.
    - **IMPORTANT**: All tables are in the `jobplacement_RAG` schema. You MUST prefix table names with `jobplacement_RAG.`. For example: `SELECT count(*) FROM jobplacement_RAG.students;`.

2.  `search_job_descriptions`: For questions about the content of job descriptions.
    - Use this for semantic or conceptual questions like "find jobs for a Medical advisor".
    - This tool finds jobs based on the *meaning* of the user's query, not exact keywords.

Decision-Making Process:
- First, analyze the user's question.
- If it's a factual, specific question that can be answered with SQL, use `execute_sql_query`.
- If the question is about the role, skills, or nature of a job described in free text, use `search_job_descriptions`.
- After getting results from a tool, formulate a clear, conversational answer. Do not just return the raw tool output.
- You can use a tool's output to inform a call to another tool. For example, use `search_job_descriptions` to find a job ID, then use `execute_sql_query` to find its salary details.
"""

agent_model = genai.GenerativeModel(
    model_name="gemini-2.5-pro",
    system_instruction=SYSTEM_PROMPT,
    # Provide BOTH tools to the model
    tools=[execute_sql_query, search_job_descriptions]
)

chat_session = agent_model.start_chat(
    enable_automatic_function_calling=True
)

def query_agent_adk(user_prompt: str) -> str:
    """
    Sends a prompt to the hybrid agent.
    The agent will decide which tool to use (SQL or Vector Search).
    """
    try:
        response = chat_session.send_message(user_prompt)
        return response.text
    except Exception as e:
        return f"An error occurred while communicating with the agent: {e}"
