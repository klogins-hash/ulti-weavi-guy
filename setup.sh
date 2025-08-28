#!/bin/bash

# Ulti Weavi Guy - Setup Script
echo "🚀 Setting up Ulti Weavi Guy MVP..."

# Create environment files from examples
echo "📝 Creating environment files..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from .env.example"
    echo "⚠️  Please edit .env and add your API keys!"
fi

if [ ! -f frontend/.env.local ]; then
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local
    echo "Created frontend/.env.local"
fi

# Install backend dependencies
echo "🐍 Installing Python backend dependencies..."
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "📦 Installing Node.js frontend dependencies..."
cd frontend
npm install
cd ..

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys (Firecrawl, Apify, Unstructured, Cohere, Anthropic)"
echo "2. Start the services:"
echo "   docker-compose up -d weaviate redis"
echo "   cd backend && source venv/bin/activate && uvicorn main:app --reload"
echo "   cd frontend && npm run dev"
echo "3. Open http://localhost:3000 in your browser"
