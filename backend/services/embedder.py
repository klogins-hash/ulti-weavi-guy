import os
import asyncio
from typing import List, Dict, Any
from langchain_cohere import CohereEmbeddings
from langchain.schema import Document
import logging

logger = logging.getLogger(__name__)

class CohereEmbedder:
    """Cohere v3 English embedding service"""
    
    def __init__(self):
        self.api_key = os.getenv("COHERE_API_KEY")
        if not self.api_key:
            raise ValueError("COHERE_API_KEY not set")
        
        self.embeddings = CohereEmbeddings(
            cohere_api_key=self.api_key,
            model="embed-english-v3.0"
        )
    
    async def embed_documents(self, documents: List[Document]) -> List[List[float]]:
        """
        Embed a list of documents using Cohere v3 English model
        
        Args:
            documents: List of LangChain Document objects
        
        Returns:
            List of embedding vectors
        """
        try:
            # Extract text content from documents
            texts = [doc.page_content for doc in documents]
            
            # Generate embeddings
            embeddings = await asyncio.to_thread(
                self.embeddings.embed_documents, texts
            )
            
            logger.info(f"Generated embeddings for {len(documents)} documents")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    async def embed_query(self, query: str) -> List[float]:
        """
        Embed a single query string
        
        Args:
            query: Query string to embed
        
        Returns:
            Embedding vector
        """
        try:
            embedding = await asyncio.to_thread(
                self.embeddings.embed_query, query
            )
            
            logger.info(f"Generated embedding for query: {query[:50]}...")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors"""
        return 1024  # Cohere v3 English embeddings are 1024 dimensional
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the embedding model"""
        return {
            "provider": "cohere",
            "model": "embed-english-v3.0",
            "dimension": 1024,
            "language": "english",
            "max_tokens": 512
        }
