# 🚀 Deploy Ulti Weavi Guy to Northflank - Quick Start

## Your API Keys
```
UNSTRUCTURED_API_KEY=your_unstructured_api_key_here
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
APIFY_API_KEY=your_apify_api_key_here
COHERE_API_KEY=your_cohere_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## Quick Deployment Steps

### 1. Access Northflank Dashboard
- Go to: https://app.northflank.com
- You're already logged in from the CLI setup

### 2. Create Project
1. Click "Create New" → "Project"
2. Name: `ulti-weavi-guy`
3. Description: `Ultimate Weaviate Frontend Tool`
4. Click "Create Project"

### 3. Create Secret Group
1. In your project, go to "Secret Groups"
2. Click "Create Secret Group"
3. Name: `ulti-weavi-secrets`
4. Add these secrets:
   - `FIRECRAWL_API_KEY` = `your_firecrawl_api_key_here`
   - `APIFY_API_KEY` = `your_apify_api_key_here`
   - `UNSTRUCTURED_API_KEY` = `your_unstructured_api_key_here`
   - `COHERE_API_KEY` = `your_cohere_api_key_here`
   - `ANTHROPIC_API_KEY` = `your_anthropic_api_key_here`
   - `DEBUG` = `false`
   - `LOG_LEVEL` = `INFO`

### 4. Deploy Redis Addon
1. Go to "Addons" → "Create New"
2. Select "Redis"
3. Configuration:
   - Name: `ulti-weavi-redis`
   - Version: `7.0`
   - Plan: `nf-compute-10`
   - Storage: `1GB`
   - Persistence: ✅ Enabled
   - TLS: ❌ Disabled
   - Public Access: ❌ Disabled
4. Click "Create Addon"

### 5. Deploy Weaviate Service
1. Go to "Services" → "Create New" → "Deployment Service"
2. Configuration:
   - Name: `ulti-weavi-weaviate`
   - Image: `semitechnologies/weaviate:1.22.4`
   - Port: `8080` (HTTP, Public ✅)
   - CPU: `0.5 vCPU`
   - Memory: `2GB`
   - Storage: `10GB`
3. Environment Variables:
   ```
   QUERY_DEFAULTS_LIMIT=25
   AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true
   PERSISTENCE_DATA_PATH=/var/lib/weaviate
   DEFAULT_VECTORIZER_MODULE=none
   ENABLE_MODULES=text2vec-cohere,text2vec-openai,generative-openai,generative-cohere
   CLUSTER_HOSTNAME=node1
   ```
4. Click "Create & Deploy"

### 6. Deploy Backend API
1. Go to "Services" → "Create New" → "Combined Service"
2. Configuration:
   - Name: `ulti-weavi-backend`
   - Repository: Connect your GitHub repo (this one)
   - Branch: `main`
   - Build Context: `/backend`
   - Build Type: `Dockerfile`
   - Dockerfile Path: `/backend/Dockerfile`
   - Port: `8000` (HTTP, Public ✅)
   - CPU: `1 vCPU`
   - Memory: `2GB`
3. Environment Variables:
   ```
   PORT=8000
   PYTHONPATH=/app
   WEAVIATE_URL=${LINK.ulti-weavi-weaviate.HOST}:${LINK.ulti-weavi-weaviate.PORT}
   REDIS_URL=redis://${ADDON.ulti-weavi-redis.HOST}:${ADDON.ulti-weavi-redis.PORT}
   ```
4. Secret Groups: Link `ulti-weavi-secrets`
5. Click "Create & Deploy"

### 7. Deploy Frontend
1. Go to "Services" → "Create New" → "Combined Service"
2. Configuration:
   - Name: `ulti-weavi-frontend`
   - Repository: Same GitHub repo
   - Branch: `main`
   - Build Context: `/frontend`
   - Build Type: `Dockerfile`
   - Dockerfile Path: `/frontend/Dockerfile`
   - Port: `3000` (HTTP, Public ✅)
   - CPU: `0.5 vCPU`
   - Memory: `1GB`
3. Environment Variables:
   ```
   NODE_ENV=production
   NEXT_PUBLIC_API_URL=${LINK.ulti-weavi-backend.HOST}
   ```
4. Build Arguments:
   ```
   NODE_VERSION=18
   NEXT_PUBLIC_API_URL=${LINK.ulti-weavi-backend.HOST}
   ```
5. Click "Create & Deploy"

## 🎉 Your Deployment URLs

After deployment completes (5-10 minutes), your services will be available at:

- **Frontend**: `https://ulti-weavi-frontend--ulti-weavi-guy--[your-team].code.run`
- **Backend API**: `https://ulti-weavi-backend--ulti-weavi-guy--[your-team].code.run`
- **Weaviate**: `https://ulti-weavi-weaviate--ulti-weavi-guy--[your-team].code.run`

## 📊 Monitor Deployment

1. Watch build logs in each service
2. Check health endpoints:
   - Backend: `/health`
   - Frontend: `/api/health`
3. Monitor resource usage in the dashboard

## 🧪 Test Your MVP

1. Open the frontend URL
2. Try the "Scrape & Embed" tab with: `"Scrape articles from https://techcrunch.com"`
3. Monitor job progress in the "Job Status" tab
4. Once complete, chat with your data in the "Chat with Data" tab

## 🔧 Troubleshooting

- **Build Failures**: Check build logs and Dockerfile syntax
- **Service Crashes**: Verify environment variables and secret groups
- **Connection Issues**: Ensure service linking is configured correctly

Your Ulti Weavi Guy MVP is now live on Northflank! 🚀
