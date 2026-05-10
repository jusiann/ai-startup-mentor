from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from src.routes import auth_router, idea_router, ai_router
from src.lib.db.database import engine, Base

from src.lib.db.models.user import User

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database connected and tables created.")
    yield
    await engine.dispose()

app = FastAPI(
    title="AI Startup Mentor API",
    description="Backend for AI Platform.",
    version="1.0.0",
    lifespan=lifespan
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"success": False, "error": "Validation error", "details": exc.errors()}
    )

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
