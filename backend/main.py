from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api import upload, dashboard, copilot, insights, ws, debug
from core.database import verify_db_connection
from core.logger import logger
import models.database  # Import models

# Removed Base.metadata.create_all to rely on Alembic

app = FastAPI(title="Revenue Command Center API")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Revenue Command Center API")
    if verify_db_connection():
        from core.database import DATABASE_URL
        host = "unknown"
        if "@" in DATABASE_URL:
            host = DATABASE_URL.split("@")[1].split(":")[0]
        logger.info("Connected to PostgreSQL database successfully.")
        logger.info(f"Database Host: {host}")
    else:
        logger.error("Failed to connect to the database. Check your DATABASE_URL.")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred. Please try again later.", "details": str(exc)},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api/v1/upload", tags=["upload"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(copilot.router, prefix="/api/v1/copilot", tags=["copilot"])
app.include_router(ws.router, prefix="/api/v1/ws", tags=["websocket"])
app.include_router(insights.router, prefix="/api/v1/insights", tags=["insights"])
app.include_router(debug.router, prefix="/api/v1/debug", tags=["debug"])

@app.get("/")
def root():
    return {"message": "Welcome to Revenue Command Center API"}
