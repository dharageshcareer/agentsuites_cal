# Agent Suite

This project is a full-stack application showcasing a modular suite of AI-powered agents. It features a Python/FastAPI backend that provides the core agent logic and a vanilla HTML/CSS/JavaScript frontend for user interaction.

## Features

*   **Full-Stack Architecture**: A decoupled frontend and backend for modularity and scalability.
*   **Dynamic Agent Hub**: The frontend dynamically displays available agents by fetching a list from the backend.
*   **Job Placement Agent**: A chat interface powered by a hybrid RAG agent that can query both a SQL database (for student/placement data) and a vector store (for job descriptions) to answer complex questions.
*   **Instructor Assistant**: A document analysis tool that accepts a file (e.g., student feedback) and returns an LLM-powered summary, sentiment analysis, and actionable suggestions in a clean report format.
*   **Extensible Backend**: Built with FastAPI, designed to be easily extended with new agents and capabilities.

## Architecture Overview

The application consists of two main components that work together:

1.  **Frontend (`agent_suite_frontend/`)**: A static web application built with HTML, CSS, and JavaScript. It provides the user interfaces for listing agents, chatting, and uploading documents. It communicates with the backend via REST API calls.
2.  **Backend (`agent_suite_backend/`)**: A Python application built with FastAPI. It hosts the AI agents, manages connections to data sources (PostgreSQL, ChromaDB), and exposes the agent functionalities through a series of API endpoints.

## Backend Project Structure

## Frontend-Backend Communication

The frontend and backend operate as separate applications that communicate over the network using HTTP requests. This is a standard client-server architecture.

*   **Client (Frontend)**: The frontend is a collection of static files (HTML, CSS, JavaScript) served from a simple web server (e.g., on `http://localhost:9000`). User interactions in the browser trigger JavaScript functions.


*   **API Calls**: The JavaScript files (e.g., `app.js`, `jobplacement_chat.js`) use the browser's built-in `fetch` API to send requests to the backend. The backend API URLs are hardcoded in these files, for example:
    ```javascript
    const API_URL = 'http://127.0.0.1:8000/api/jobplacement_rag/chat';
    ```

*   **Server (Backend)**: The backend is a FastAPI application running on `http://127.0.0.1:8000`. It listens for incoming API requests, processes them, interacts with databases or other services, and sends back a JSON response.

*   **CORS (Cross-Origin Resource Sharing)**: Since the frontend and backend are served from different origins (`localhost:9000` and `localhost:8000`), the backend must be configured to allow cross-origin requests. This is typically handled in FastAPI using `CORSMiddleware` to specify which frontend origins are permitted to access the API. Without this configuration, web browsers will block the frontend's requests for security reasons.

## Project Structure

```
agent-suite/
├── agent_suite_backend/
│   ├── app/                  # Main application source code
│   ├── scripts/              # Standalone scripts (e.g., populate_vector_db.py)
│   ├── .env                  # (Local) Environment variables
│   ├── requirements.txt      # Python dependencies
│   └── ...
└── agent_suite_frontend/
    ├── app.js                # Main script for the agent hub
    ├── index.html            # The main agent selection page
    ├── instructor_assistant/ # Files for the Instructor Assistant agent
    │   ├── instructor_assistant.html
    │   ├── instructor_assistant.js
    │   └── instructor_assistant.css
    └── jobplacement/         # Files for the Job Placement agent
        ├── jobplacement_chat.html
        ├── jobplacement_chat.js
        └── style.css
```


## Setup and Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd agent-suite/
```

### 2. Create and Activate a Virtual Environment

```bash
cd agent_suite_backend/
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```


### 4. Set up PostgreSQL Database

1.  Ensure you have PostgreSQL installed and running.
2.  Create a new database for the project (e.g., `agentsuite`).
3.  Execute the `database_setup.sql` script (provided in your project) to create the necessary schemas and tables.

### 5. Configure Environment Variables

Create a `.env` file in the project backendcdirectory. This file will store your sensitive credentials and configuration, and it should not be committed to version control.

```env
GOOGLE_API_KEY="your_google_api_key_here"
DATABASE_URL="postgresql://user:password@host:port/agentsuite"
```

### 6. Populate the Vector Database

Run the provided script to fetch job descriptions from your PostgreSQL database, generate embeddings, and store them in the local ChromaDB vector store.

```bash
python3 scripts/populate_vector_db.py
```

This command will create the `chroma_db/` directory. This directory is included in `.gitignore` as it contains generated data that can be reproduced by running the script.

## Running the backend Application

Once the setup is complete, you can run the FastAPI server using Uvicorn.

```bash
# Assuming your FastAPI app instance is in `app/main.py`
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## Runnin the frontend application

you should run frontend as a webserver to avoid cors issue, for MVP run as simple python http server

```bash
cd agent_suite_frontend/
python3 -m http.server 9000
```


## Usage Examples

You can interact with the agent by sending requests to the `/api` endpoints.

#### Example 1: Factual, SQL-based question

```bash
curl -X POST "http://127.0.0.1:8000/api/jobplacement_rag/chat" \
-H "Content-Type: application/json" \
-d '{"user_prompt": "What is the average offered salary for jobs at Tech Solutions Inc.?"}'
```

#### Example 2: Conceptual, Semantic Search-based question

```bash
curl -X POST "http://127.0.0.1:8000/agent/query" \
-H "Content-Type: application/json" \
-d '{"prompt": "Find me jobs suitable for a data scientist with Python experience"}'
```
