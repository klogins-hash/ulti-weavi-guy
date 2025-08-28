#!/bin/bash

# Northflank Deployment Script for Ulti Weavi Guy
echo "🚀 Deploying Ulti Weavi Guy to Northflank..."

# Check if Northflank CLI is installed
if ! npx @northflank/cli --version &> /dev/null; then
    echo "❌ Northflank CLI not found. Installing..."
    npm install -g @northflank/cli
fi

# Check if user is logged in
if ! npx @northflank/cli whoami &> /dev/null; then
    echo "🔐 Please log in to Northflank:"
    npx @northflank/cli login
fi

# Validate required environment variables
echo "📋 Validating API keys..."
required_vars=("FIRECRAWL_API_KEY" "APIFY_API_KEY" "UNSTRUCTURED_API_KEY" "COHERE_API_KEY" "ANTHROPIC_API_KEY")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Missing required environment variables:"
    printf '%s\n' "${missing_vars[@]}"
    echo "Please set these variables before deploying."
    exit 1
fi

# Create project
echo "📁 Creating Northflank project..."
npx @northflank/cli create project ulti-weavi-guy --description "Ultimate Weaviate Frontend Tool"

# Create secret group
echo "🔐 Creating secret group..."
npx @northflank/cli create secret-group ulti-weavi-secrets --project ulti-weavi-guy

# Add secrets
echo "🔑 Adding API keys to secret group..."
npx @northflank/cli create secret FIRECRAWL_API_KEY "$FIRECRAWL_API_KEY" --secret-group ulti-weavi-secrets --project ulti-weavi-guy
npx @northflank/cli create secret APIFY_API_KEY "$APIFY_API_KEY" --secret-group ulti-weavi-secrets --project ulti-weavi-guy
npx @northflank/cli create secret UNSTRUCTURED_API_KEY "$UNSTRUCTURED_API_KEY" --secret-group ulti-weavi-secrets --project ulti-weavi-guy
npx @northflank/cli create secret COHERE_API_KEY "$COHERE_API_KEY" --secret-group ulti-weavi-secrets --project ulti-weavi-guy
npx @northflank/cli create secret ANTHROPIC_API_KEY "$ANTHROPIC_API_KEY" --secret-group ulti-weavi-secrets --project ulti-weavi-guy

# Optional secrets
if [ -n "$WEAVIATE_API_KEY" ]; then
    npx @northflank/cli create secret WEAVIATE_API_KEY "$WEAVIATE_API_KEY" --secret-group ulti-weavi-secrets --project ulti-weavi-guy
fi

# Generate random secrets
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 64)
npx @northflank/cli create secret SECRET_KEY "$SECRET_KEY" --secret-group ulti-weavi-secrets --project ulti-weavi-guy
npx @northflank/cli create secret JWT_SECRET "$JWT_SECRET" --secret-group ulti-weavi-secrets --project ulti-weavi-guy
npx @northflank/cli create secret DEBUG "false" --secret-group ulti-weavi-secrets --project ulti-weavi-guy
npx @northflank/cli create secret LOG_LEVEL "INFO" --secret-group ulti-weavi-secrets --project ulti-weavi-guy

# Deploy Redis addon
echo "🗄️ Deploying Redis addon..."
npx @northflank/cli create addon redis ulti-weavi-redis \
    --project ulti-weavi-guy \
    --plan nf-compute-10 \
    --version 7.0 \
    --storage 1Gi

# Deploy PostgreSQL addon (optional)
echo "🗄️ Deploying PostgreSQL addon..."
npx @northflank/cli create addon postgresql ulti-weavi-postgres \
    --project ulti-weavi-guy \
    --plan nf-compute-10 \
    --version 15 \
    --storage 10Gi

# Wait for addons to be ready
echo "⏳ Waiting for addons to be ready..."
sleep 30

# Deploy Weaviate service
echo "🧠 Deploying Weaviate service..."
npx @northflank/cli create service deployment ulti-weavi-weaviate \
    --project ulti-weavi-guy \
    --image semitechnologies/weaviate:1.22.4 \
    --port 8080 \
    --cpu 0.5 \
    --memory 2Gi \
    --storage 10Gi \
    --env QUERY_DEFAULTS_LIMIT=25 \
    --env AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
    --env PERSISTENCE_DATA_PATH=/var/lib/weaviate \
    --env DEFAULT_VECTORIZER_MODULE=none \
    --env ENABLE_MODULES=text2vec-cohere,text2vec-openai,generative-openai,generative-cohere \
    --env CLUSTER_HOSTNAME=node1

# Deploy backend API
echo "🔧 Deploying backend API..."
npx @northflank/cli create service combined ulti-weavi-backend \
    --project ulti-weavi-guy \
    --repo-url $(git config --get remote.origin.url) \
    --branch main \
    --build-context /backend \
    --dockerfile /backend/Dockerfile \
    --port 8000 \
    --cpu 1 \
    --memory 2Gi \
    --secret-group ulti-weavi-secrets \
    --env PORT=8000 \
    --env PYTHONPATH=/app

# Deploy frontend
echo "🎨 Deploying frontend..."
npx @northflank/cli create service combined ulti-weavi-frontend \
    --project ulti-weavi-guy \
    --repo-url $(git config --get remote.origin.url) \
    --branch main \
    --build-context /frontend \
    --dockerfile /frontend/Dockerfile \
    --port 3000 \
    --cpu 0.5 \
    --memory 1Gi \
    --env NODE_ENV=production

echo "✅ Deployment initiated!"
echo ""
echo "🌐 Your services will be available at:"
echo "Frontend: https://ulti-weavi-frontend--ulti-weavi-guy--<your-team>.code.run"
echo "Backend API: https://ulti-weavi-backend--ulti-weavi-guy--<your-team>.code.run"
echo "Weaviate: https://ulti-weavi-weaviate--ulti-weavi-guy--<your-team>.code.run"
echo ""
echo "📊 Monitor deployment progress in the Northflank dashboard:"
echo "https://app.northflank.com/projects/ulti-weavi-guy"
echo ""
echo "⚡ Deployment complete! Your Ulti Weavi Guy MVP is now live on Northflank!"
