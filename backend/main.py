from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import logging
import os

# Import our core services
from services.scraper import UniversalScraper
from services.embedder import CohereEmbedder
from services.chat import ClaudeChat
from services.weaviate_manager import WeaviateManager
from services.job_orchestrator import JobOrchestrator

app = FastAPI(title="Ulti Weavi Guy API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
scraper = UniversalScraper()
embedder = CohereEmbedder()
chat = ClaudeChat()
weaviate_manager = WeaviateManager()
job_orchestrator = JobOrchestrator(scraper, embedder, weaviate_manager)

# Pydantic models
class ScrapeRequest(BaseModel):
    prompt: str
    source_type: str = "auto"  # auto, firecrawl, apify, local

class ChatRequest(BaseModel):
    message: str
    context_collection: Optional[str] = None
    chat_type: str = "data"  # data, config

class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: float
    result: Optional[Dict[str, Any]] = None

@app.get("/")
async def root():
    return {"message": "Ulti Weavi Guy API is running!"}

@app.post("/scrape")
async def initiate_scrape(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """Initiate a scrape job based on natural language prompt"""
    try:
        job_id = await job_orchestrator.create_scrape_job(request.prompt, request.source_type)
        background_tasks.add_task(job_orchestrator.execute_job, job_id)
        return {"job_id": job_id, "status": "initiated", "message": "Scrape job started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get status of a running job"""
    try:
        status = await job_orchestrator.get_job_status(job_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

@app.post("/chat")
async def chat_with_data(request: ChatRequest):
    """Chat with your data or configure Weaviate"""
    try:
        if request.chat_type == "data":
            # Chat with scraped data
            response = await chat.chat_with_context(
                request.message, 
                request.context_collection,
                weaviate_manager
            )
        elif request.chat_type == "config":
            # Chat to configure Weaviate
            response = await chat.configure_weaviate(
                request.message,
                weaviate_manager
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid chat_type")
        
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collections")
async def list_collections():
    """List all Weaviate collections"""
    try:
        collections = await weaviate_manager.list_collections()
        return {"collections": collections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collections/{collection_name}/stats")
async def get_collection_stats(collection_name: str):
    """Get statistics for a specific collection"""
    try:
        stats = await weaviate_manager.get_collection_stats(collection_name)
        return stats
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Collection {collection_name} not found")

@app.post("/upload-local")
async def upload_local_files(files: List[str], background_tasks: BackgroundTasks):
    """Upload and process local files"""
    try:
        job_id = await job_orchestrator.create_local_upload_job(files)
        background_tasks.add_task(job_orchestrator.execute_job, job_id)
        return {"job_id": job_id, "status": "initiated", "message": "Local file processing started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint for Northflank monitoring"""
    try:
        # Basic health checks
        health_status = {
            "status": "healthy",
            "timestamp": asyncio.get_event_loop().time(),
            "services": {
                "weaviate": "unknown",
                "redis": "unknown"
            }
        }
        
        # Test Weaviate connection
        try:
            weaviate_manager = WeaviateManager()
            await weaviate_manager.list_collections()
            health_status["services"]["weaviate"] = "healthy"
        except Exception:
            health_status["services"]["weaviate"] = "unhealthy"
            health_status["status"] = "degraded"
        
        return health_status
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
