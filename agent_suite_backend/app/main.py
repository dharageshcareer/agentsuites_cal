from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router

app = FastAPI(
    title="Agent Suite Backend",
    description="Backend API for a suite of AI agents.",
    version="1.0.0"
)

# --- CORS Configuration ---
# This is crucial for allowing the frontend to communicate with the backend.
origins = [
    "http://localhost:5173",  # Default Vite dev server port
    "http://localhost:3000",  # Default Create React App dev server port
    "http://localhost:8000",  # As seen in the error message
    "http://localhost:9000",  # As seen in the error message
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Include the API router
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Agent Suite Backend API"}
