# Ulti Weavi Guy 🚀

The ultimate Weaviate frontend tool for intelligent data scraping, embedding, and chat-based interaction.

## Vision

A comprehensive platform that can scrape using any tool, embed with any API, chat using any LLM, and organize data through natural language prompts - all with automated job orchestration.

## MVP Features

### Core Functionality
- **Prompt-based scraping**: Initiate scrapes through natural language
- **Auto-embed pipeline**: Scraped data automatically uploaded and embedded into Weaviate
- **Data chat**: Chat directly with your scraped data
- **Configuration chat**: Manage Weaviate structure through conversation

### MVP Tech Stack
- **Scraping**: Firecrawl, Apify, Local files (Unstructured.io)
- **Embedding**: Cohere v3 English
- **LLM**: Claude Sonnet 3.5
- **Vector DB**: Weaviate
- **Backend**: FastAPI + LangChain
- **Frontend**: Next.js + TypeScript

## Project Structure

```
ulti-weavi-guy/
├── backend/           # FastAPI + LangChain backend
├── frontend/          # Next.js frontend
├── docker/           # Docker configurations
├── docs/             # Documentation
└── scripts/          # Utility scripts
```

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Weaviate instance (local or cloud)

### Environment Variables
```bash
# API Keys
FIRECRAWL_API_KEY=your_firecrawl_key
APIFY_API_KEY=your_apify_key
UNSTRUCTURED_API_KEY=your_unstructured_key
COHERE_API_KEY=your_cohere_key
ANTHROPIC_API_KEY=your_anthropic_key

# Weaviate
WEAVIATE_URL=your_weaviate_url
WEAVIATE_API_KEY=your_weaviate_key
```

### Quick Start
```bash
# Clone and setup
git clone <repo-url>
cd ulti-weavi-guy

# Start with Docker Compose
docker-compose up -d

# Or run locally
cd backend && pip install -r requirements.txt && uvicorn main:app --reload
cd frontend && npm install && npm run dev
```

## Roadmap

### Phase 1: MVP (Current)
- [x] Project setup
- [ ] Basic scraping (Firecrawl, Apify, local files)
- [ ] Cohere embedding integration
- [ ] Claude chat integration
- [ ] Weaviate auto-upload
- [ ] Basic frontend

### Phase 2: Enhanced Features
- [ ] Multiple embedding providers
- [ ] Multiple LLM providers
- [ ] Advanced job orchestration
- [ ] Parallel processing

### Phase 3: Full Vision
- [ ] 50+ scraping tools
- [ ] 50+ embedding providers
- [ ] 100+ LLM models
- [ ] Advanced UI/UX
- [ ] Enterprise features

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details.
