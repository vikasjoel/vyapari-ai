"""FastAPI backend for Vyapari.ai — connects React frontend to the agent system."""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv()

from api.routes import chat, upload, voice, catalog, health, simulate, template, demo, intelligence  # noqa: E402

app = FastAPI(title="Vyapari.ai API", version="1.0.0")

# CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(health.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(voice.router, prefix="/api")
app.include_router(catalog.router, prefix="/api")
app.include_router(simulate.router, prefix="/api")
app.include_router(template.router, prefix="/api")
app.include_router(demo.router, prefix="/api")
app.include_router(intelligence.router, prefix="/api")

# Serve React frontend static files (production mode)
FRONTEND_DIR = Path(__file__).parent.parent / "frontend" / "dist"
if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="assets")

    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        """Serve React app for all non-API routes (SPA fallback)."""
        file_path = FRONTEND_DIR / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(FRONTEND_DIR / "index.html"))
