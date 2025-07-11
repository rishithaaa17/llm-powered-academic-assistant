from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import generate, evaluate

app = FastAPI(
    title="Question Paper Generator & Evaluator API",
    description="AI-powered question paper generation and answer evaluation system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],  # Streamlit default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(generate.router, prefix="/api/v1", tags=["generation"])
app.include_router(evaluate.router, prefix="/api/v1", tags=["evaluation"])

@app.get("/")
async def root():
    return {"message": "Question Paper Generator & Evaluator API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 