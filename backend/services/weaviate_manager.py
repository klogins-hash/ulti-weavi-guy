import os
import asyncio
from typing import List, Dict, Any, Optional
import weaviate
from weaviate.auth import Auth
from weaviate.classes.config import Configure, Property, DataType
from langchain.schema import Document
import logging

logger = logging.getLogger(__name__)

class WeaviateManager:
    """Weaviate database manager for collections and data operations"""
    
    def __init__(self):
        self.url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        self.api_key = os.getenv("WEAVIATE_API_KEY")
        
        # Initialize Weaviate client
        if self.api_key:
            self.client = weaviate.connect_to_weaviate_cloud(
                cluster_url=self.url,
                auth_credentials=Auth.api_key(self.api_key)
            )
        else:
            self.client = weaviate.connect_to_local(host=self.url.replace("http://", "").replace("https://", ""))
    
    async def create_collection(
        self, 
        name: str, 
        description: str = "",
        properties: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Create a new Weaviate collection
        
        Args:
            name: Collection name
            description: Collection description
            properties: List of property definitions
        
        Returns:
            True if successful
        """
        try:
            # Default properties for scraped content
            default_properties = [
                Property(name="content", data_type=DataType.TEXT, description="Main content of the document"),
                Property(name="title", data_type=DataType.TEXT, description="Title of the document"),
                Property(name="url", data_type=DataType.TEXT, description="Source URL if applicable"),
                Property(name="source", data_type=DataType.TEXT, description="Source type (firecrawl, apify, local)"),
                Property(name="timestamp", data_type=DataType.DATE, description="When the document was scraped/processed"),
                Property(name="metadata", data_type=DataType.OBJECT, description="Additional metadata")
            ]
            
            # Use provided properties or defaults
            collection_properties = properties or default_properties
            
            # Create collection with Cohere vectorizer
            await asyncio.to_thread(
                self.client.collections.create,
                name=name,
                description=description,
                vectorizer_config=Configure.Vectorizer.text2vec_cohere(
                    model="embed-english-v3.0"
                ),
                properties=collection_properties
            )
            
            logger.info(f"Created collection: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating collection {name}: {str(e)}")
            raise
    
    async def add_documents(
        self, 
        collection_name: str, 
        documents: List[Document], 
        embeddings: List[List[float]]
    ) -> bool:
        """
        Add documents with embeddings to a collection
        
        Args:
            collection_name: Target collection name
            documents: List of LangChain documents
            embeddings: Corresponding embedding vectors
        
        Returns:
            True if successful
        """
        try:
            collection = self.client.collections.get(collection_name)
            
            # Batch insert documents
            with collection.batch.dynamic() as batch:
                for doc, embedding in zip(documents, embeddings):
                    properties = {
                        "content": doc.page_content,
                        "title": doc.metadata.get("title", ""),
                        "url": doc.metadata.get("url", ""),
                        "source": doc.metadata.get("source", "unknown"),
                        "timestamp": doc.metadata.get("timestamp"),
                        "metadata": doc.metadata
                    }
                    
                    batch.add_object(
                        properties=properties,
                        vector=embedding
                    )
            
            logger.info(f"Added {len(documents)} documents to {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents to {collection_name}: {str(e)}")
            raise
    
    async def search_similar(
        self, 
        collection_name: str, 
        query: str, 
        limit: int = 5,
        embedding_service=None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using vector similarity
        
        Args:
            collection_name: Collection to search
            query: Search query
            limit: Number of results to return
            embedding_service: Service to generate query embedding
        
        Returns:
            List of similar documents
        """
        try:
            collection = self.client.collections.get(collection_name)
            
            # Perform vector search
            response = await asyncio.to_thread(
                collection.query.near_text,
                query=query,
                limit=limit,
                return_metadata=["score"]
            )
            
            results = []
            for obj in response.objects:
                results.append({
                    "id": str(obj.uuid),
                    "content": obj.properties.get("content", ""),
                    "title": obj.properties.get("title", ""),
                    "url": obj.properties.get("url", ""),
                    "source": obj.properties.get("source", ""),
                    "score": obj.metadata.score if obj.metadata else None,
                    "metadata": obj.properties.get("metadata", {})
                })
            
            logger.info(f"Found {len(results)} similar documents for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Error searching {collection_name}: {str(e)}")
            raise
    
    async def list_collections(self) -> List[Dict[str, Any]]:
        """
        List all collections in Weaviate
        
        Returns:
            List of collection information
        """
        try:
            collections = []
            for collection in self.client.collections.list_all():
                # Get collection stats
                stats = await asyncio.to_thread(
                    collection.aggregate.over_all,
                    total_count=True
                )
                
                collections.append({
                    "name": collection.name,
                    "description": collection.description or "",
                    "count": stats.total_count if stats else 0,
                    "vectorizer": collection.config.vectorizer_config.vectorizer.value if collection.config.vectorizer_config else None
                })
            
            return collections
            
        except Exception as e:
            logger.error(f"Error listing collections: {str(e)}")
            raise
    
    async def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        Get statistics for a specific collection
        
        Args:
            collection_name: Name of the collection
        
        Returns:
            Collection statistics
        """
        try:
            collection = self.client.collections.get(collection_name)
            
            # Get basic stats
            stats = await asyncio.to_thread(
                collection.aggregate.over_all,
                total_count=True
            )
            
            # Get recent documents
            recent_docs = await asyncio.to_thread(
                collection.query.fetch_objects,
                limit=5,
                sort=collection.query.Sort.by_property("timestamp", ascending=False)
            )
            
            return {
                "name": collection_name,
                "total_count": stats.total_count if stats else 0,
                "recent_documents": len(recent_docs.objects) if recent_docs else 0,
                "last_updated": recent_docs.objects[0].properties.get("timestamp") if recent_docs and recent_docs.objects else None
            }
            
        except Exception as e:
            logger.error(f"Error getting stats for {collection_name}: {str(e)}")
            raise
    
    async def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection
        
        Args:
            collection_name: Name of collection to delete
        
        Returns:
            True if successful
        """
        try:
            await asyncio.to_thread(
                self.client.collections.delete,
                collection_name
            )
            
            logger.info(f"Deleted collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting collection {collection_name}: {str(e)}")
            raise
    
    async def collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection exists
        
        Args:
            collection_name: Name of collection to check
        
        Returns:
            True if exists
        """
        try:
            return await asyncio.to_thread(
                self.client.collections.exists,
                collection_name
            )
        except Exception as e:
            logger.error(f"Error checking if collection {collection_name} exists: {str(e)}")
            return False
    
    def close(self):
        """Close the Weaviate client connection"""
        if hasattr(self.client, 'close'):
            self.client.close()
