from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from database.connection import engine
from models.document import Base


app = FastAPI(
    title="AISoC - AI-Powered Research Assistant",
    description="Backend API for the AISoC research assistant",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "Welcome to AISoC",
        "status": "API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }