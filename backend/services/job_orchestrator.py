import uuid
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class JobOrchestrator:
    """Orchestrates scraping, embedding, and Weaviate upload jobs"""
    
    def __init__(self, scraper, embedder, weaviate_manager):
        self.scraper = scraper
        self.embedder = embedder
        self.weaviate_manager = weaviate_manager
        self.jobs: Dict[str, Dict[str, Any]] = {}
    
    async def create_scrape_job(self, prompt: str, source_type: str = "auto") -> str:
        """
        Create a new scrape job from a natural language prompt
        
        Args:
            prompt: Natural language description of what to scrape
            source_type: Preferred scraping method
        
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        
        self.jobs[job_id] = {
            "id": job_id,
            "type": "scrape",
            "status": JobStatus.PENDING.value,
            "prompt": prompt,
            "source_type": source_type,
            "progress": 0.0,
            "created_at": datetime.utcnow().isoformat(),
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None
        }
        
        logger.info(f"Created scrape job {job_id}: {prompt[:50]}...")
        return job_id
    
    async def create_local_upload_job(self, file_paths: List[str]) -> str:
        """
        Create a job to process local files
        
        Args:
            file_paths: List of file paths to process
        
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        
        self.jobs[job_id] = {
            "id": job_id,
            "type": "local_upload",
            "status": JobStatus.PENDING.value,
            "file_paths": file_paths,
            "progress": 0.0,
            "created_at": datetime.utcnow().isoformat(),
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None
        }
        
        logger.info(f"Created local upload job {job_id} for {len(file_paths)} files")
        return job_id
    
    async def execute_job(self, job_id: str):
        """
        Execute a job by ID
        
        Args:
            job_id: Job identifier
        """
        if job_id not in self.jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job = self.jobs[job_id]
        
        try:
            job["status"] = JobStatus.RUNNING.value
            job["started_at"] = datetime.utcnow().isoformat()
            job["progress"] = 0.1
            
            if job["type"] == "scrape":
                await self._execute_scrape_job(job)
            elif job["type"] == "local_upload":
                await self._execute_local_upload_job(job)
            else:
                raise ValueError(f"Unknown job type: {job['type']}")
            
            job["status"] = JobStatus.COMPLETED.value
            job["completed_at"] = datetime.utcnow().isoformat()
            job["progress"] = 1.0
            
            logger.info(f"Completed job {job_id}")
            
        except Exception as e:
            job["status"] = JobStatus.FAILED.value
            job["error"] = str(e)
            job["completed_at"] = datetime.utcnow().isoformat()
            logger.error(f"Job {job_id} failed: {str(e)}")
            raise
    
    async def _execute_scrape_job(self, job: Dict[str, Any]):
        """Execute a scraping job"""
        try:
            # Step 1: Scrape content
            job["progress"] = 0.2
            documents = await self.scraper.scrape_with_prompt(
                job["prompt"], 
                job["source_type"]
            )
            
            if not documents:
                raise ValueError("No documents scraped")
            
            # Step 2: Generate embeddings
            job["progress"] = 0.5
            embeddings = await self.embedder.embed_documents(documents)
            
            # Step 3: Determine collection name
            collection_name = self._generate_collection_name(job["prompt"])
            
            # Step 4: Create collection if it doesn't exist
            job["progress"] = 0.7
            if not await self.weaviate_manager.collection_exists(collection_name):
                await self.weaviate_manager.create_collection(
                    name=collection_name,
                    description=f"Scraped content from: {job['prompt'][:100]}"
                )
            
            # Step 5: Upload to Weaviate
            job["progress"] = 0.9
            await self.weaviate_manager.add_documents(
                collection_name=collection_name,
                documents=documents,
                embeddings=embeddings
            )
            
            job["result"] = {
                "collection_name": collection_name,
                "documents_processed": len(documents),
                "embeddings_generated": len(embeddings),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error in scrape job execution: {str(e)}")
            raise
    
    async def _execute_local_upload_job(self, job: Dict[str, Any]):
        """Execute a local file upload job"""
        try:
            # Step 1: Process local files
            job["progress"] = 0.2
            documents = await self.scraper.process_files_direct(job["file_paths"])
            
            if not documents:
                raise ValueError("No documents processed from local files")
            
            # Step 2: Generate embeddings
            job["progress"] = 0.5
            embeddings = await self.embedder.embed_documents(documents)
            
            # Step 3: Determine collection name
            collection_name = "local_files"  # Default collection for local files
            
            # Step 4: Create collection if it doesn't exist
            job["progress"] = 0.7
            if not await self.weaviate_manager.collection_exists(collection_name):
                await self.weaviate_manager.create_collection(
                    name=collection_name,
                    description="Local files processed and uploaded"
                )
            
            # Step 5: Upload to Weaviate
            job["progress"] = 0.9
            await self.weaviate_manager.add_documents(
                collection_name=collection_name,
                documents=documents,
                embeddings=embeddings
            )
            
            job["result"] = {
                "collection_name": collection_name,
                "documents_processed": len(documents),
                "files_processed": len(job["file_paths"]),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error in local upload job execution: {str(e)}")
            raise
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of a job
        
        Args:
            job_id: Job identifier
        
        Returns:
            Job status information
        """
        if job_id not in self.jobs:
            raise ValueError(f"Job {job_id} not found")
        
        return self.jobs[job_id].copy()
    
    async def list_jobs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List recent jobs
        
        Args:
            limit: Maximum number of jobs to return
        
        Returns:
            List of job information
        """
        jobs = list(self.jobs.values())
        jobs.sort(key=lambda x: x["created_at"], reverse=True)
        return jobs[:limit]
    
    def _generate_collection_name(self, prompt: str) -> str:
        """
        Generate a collection name from a prompt
        
        Args:
            prompt: Original scraping prompt
        
        Returns:
            Collection name
        """
        # Simple collection name generation
        # In production, use LLM to generate meaningful names
        
        import re
        
        # Extract domain or key terms
        if "http" in prompt:
            # Extract domain
            import urllib.parse
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', prompt)
            if urls:
                domain = urllib.parse.urlparse(urls[0]).netloc
                return f"scraped_{domain.replace('.', '_')}"
        
        # Generate from keywords
        words = re.findall(r'\b\w+\b', prompt.lower())
        meaningful_words = [w for w in words if len(w) > 3 and w not in ['scrape', 'crawl', 'get', 'from', 'with']]
        
        if meaningful_words:
            return f"scraped_{'_'.join(meaningful_words[:3])}"
        
        # Fallback
        return f"scraped_content_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
