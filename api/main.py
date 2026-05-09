from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes import auth_router, idea_router, ai_router

app = FastAPI(
    title="AI Startup Mentor API",
    description="Backend for AI Platform.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/api/auth", tags=["Auth"])
app.include_router(idea_router.router, prefix="/api/idea", tags=["Idea"])
app.include_router(ai_router.router, prefix="/api/ai", tags=["AI"])

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Startup Mentor API"}
