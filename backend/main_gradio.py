"""
KubeGenie Backend with Integrated Gradio UI

A FastAPI-based backend with integrated Gradio UI for the KubeGenie 
Kubernetes and Crossplane automation agent.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
from contextlib import asynccontextmanager
import gradio as gr
import asyncio
from threading import Thread

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.api.v1 import api_router
from app.core.database import engine, Base
from app.core.kubernetes import k8s_client
from app.core.websocket_manager import websocket_manager

# Import Gradio UI
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ui'))
from gradio_app import create_kubegenie_ui

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting KubeGenie Backend with Gradio UI...")
    
    # Create database tables
    # Base.metadata.create_all(bind=engine)
    
    # Initialize Kubernetes client
    await k8s_client.initialize()
    
    # Start Gradio UI in a separate thread
    gradio_app = create_kubegenie_ui()
    
    def run_gradio():
        gradio_app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            show_error=True,
            show_tips=True,
            enable_queue=True,
            prevent_thread_lock=True
        )
    
    gradio_thread = Thread(target=run_gradio, daemon=True)
    gradio_thread.start()
    
    logger.info("KubeGenie Backend and Gradio UI started successfully")
    logger.info("FastAPI Backend: http://localhost:8000")
    logger.info("Gradio UI: http://localhost:7860")
    
    yield
    
    logger.info("Shutting down KubeGenie Backend...")


# Create FastAPI app
app = FastAPI(
    title="KubeGenie API",
    description="Smart Kubernetes and Crossplane automation agent with integrated Gradio UI",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Add middleware
if settings.ENABLE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS + ["http://localhost:7860"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*"]
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint with UI redirect"""
    return {
        "message": "Welcome to KubeGenie API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "ui": "http://localhost:7860",
        "description": "Visit http://localhost:7860 for the interactive Gradio UI"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "kubegenie-backend", "version": "1.0.0"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket_manager.broadcast(f"Echo: {data}")
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)


if __name__ == "__main__":
    uvicorn.run(
        "main_gradio:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )