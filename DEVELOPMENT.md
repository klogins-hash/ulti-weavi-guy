# Development Guide

## Quick Start

1. **Run setup script:**
   ```bash
   ./setup.sh
   ```

2. **Configure environment:**
   Edit `.env` and add your API keys:
   ```bash
   # Required API Keys
   FIRECRAWL_API_KEY=your_firecrawl_key
   APIFY_API_KEY=your_apify_key  
   UNSTRUCTURED_API_KEY=your_unstructured_key
   COHERE_API_KEY=your_cohere_key
   ANTHROPIC_API_KEY=your_anthropic_key
   ```

3. **Start services:**
   ```bash
   # Terminal 1: Start Weaviate and Redis
   docker-compose up -d weaviate redis
   
   # Terminal 2: Start backend
   cd backend
   source venv/bin/activate
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   
   # Terminal 3: Start frontend
   cd frontend
   npm run dev
   ```

4. **Access the app:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Weaviate: http://localhost:8080

## API Endpoints

### Scraping & Jobs
- `POST /scrape` - Start scraping job
- `POST /upload-local` - Upload local files
- `GET /jobs/{job_id}` - Get job status

### Chat
- `POST /chat` - Chat with data or configure DB

### Collections
- `GET /collections` - List all collections
- `DELETE /collections/{name}` - Delete collection

## Frontend Components

### ScrapeForm
- Prompt-based scraping initiation
- Auto-detection of scraping method
- Support for Firecrawl, Apify, and local files

### ChatInterface  
- Two modes: data chat and config chat
- Collection selection for targeted queries
- Real-time message streaming

### JobStatus
- Real-time job progress tracking
- Auto-polling for running jobs
- Error handling and results display

### CollectionsList
- Visual collection browser
- Document counts and metadata
- Collection deletion

## Testing

### Manual Testing Flow
1. Start a scraping job with a simple URL
2. Monitor job progress in Job Status tab
3. Once complete, chat with the data
4. Try configuration commands
5. View collections overview

### Example Prompts
**Scraping:**
- "Scrape articles from https://techcrunch.com"
- "Process PDF files in my Documents folder"

**Data Chat:**
- "What are the main topics in my data?"
- "Summarize the latest articles"

**Config Chat:**
- "Create a collection for news articles"
- "Show me my current collections"

## Troubleshooting

### Common Issues
1. **API Keys**: Ensure all required keys are set in `.env`
2. **Weaviate Connection**: Check if Weaviate is running on port 8080
3. **CORS Issues**: Backend includes CORS middleware for localhost
4. **Job Failures**: Check backend logs for detailed error messages

### Logs
- Backend: `uvicorn main:app --reload --log-level debug`
- Frontend: Check browser console
- Weaviate: `docker-compose logs weaviate`

## Architecture

```
Frontend (Next.js) → Backend (FastAPI) → Weaviate
                  ↓
              Job Queue (Redis)
                  ↓
            External APIs (Firecrawl, Apify, etc.)
```

## Next Steps
- Add authentication/authorization
- Implement advanced job scheduling
- Add data visualization
- Support for more embedding providers
- Multi-user collections
