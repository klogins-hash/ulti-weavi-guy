import os
import asyncio
from typing import List, Dict, Any, Optional
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage
import logging

logger = logging.getLogger(__name__)

class ClaudeChat:
    """Claude Sonnet 3.5 chat service for data interaction and Weaviate configuration"""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        
        self.llm = ChatAnthropic(
            anthropic_api_key=self.api_key,
            model_name="claude-3-5-sonnet-20241022",
            temperature=0.1,
            max_tokens=4000
        )
    
    async def chat_with_context(
        self, 
        message: str, 
        context_collection: Optional[str],
        weaviate_manager
    ) -> str:
        """
        Chat with scraped data using context from Weaviate
        
        Args:
            message: User's question/message
            context_collection: Weaviate collection to search for context
            weaviate_manager: WeaviateManager instance
        
        Returns:
            Claude's response based on the context
        """
        try:
            # Get relevant context from Weaviate
            context_docs = []
            if context_collection:
                context_docs = await weaviate_manager.search_similar(
                    collection_name=context_collection,
                    query=message,
                    limit=5
                )
            
            # Build context string
            context_text = ""
            if context_docs:
                context_text = "\n\n".join([
                    f"Document {i+1}:\n{doc.get('content', '')}"
                    for i, doc in enumerate(context_docs)
                ])
            
            # Create system prompt
            system_prompt = """You are an AI assistant helping users interact with their scraped data stored in Weaviate. 
            
Your role is to:
1. Answer questions based on the provided context from their data
2. Be helpful, accurate, and concise
3. If you don't have enough context to answer, say so clearly
4. Cite which documents you're referencing when possible

Context from user's data:
{context}
""".format(context=context_text if context_text else "No specific context provided.")
            
            # Generate response
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=message)
            ]
            
            response = await asyncio.to_thread(self.llm.invoke, messages)
            
            logger.info(f"Generated chat response for: {message[:50]}...")
            return response.content
            
        except Exception as e:
            logger.error(f"Error in chat_with_context: {str(e)}")
            raise
    
    async def configure_weaviate(self, message: str, weaviate_manager) -> str:
        """
        Chat interface for configuring Weaviate collections and schema
        
        Args:
            message: User's configuration request
            weaviate_manager: WeaviateManager instance
        
        Returns:
            Response about the configuration action taken
        """
        try:
            # Get current Weaviate state
            collections = await weaviate_manager.list_collections()
            
            system_prompt = f"""You are an AI assistant helping users configure their Weaviate database through natural language.

Current Weaviate collections: {collections}

Your role is to:
1. Understand configuration requests (create collections, modify schema, etc.)
2. Generate appropriate Weaviate operations
3. Explain what changes will be made
4. Ask for confirmation for destructive operations

You can help with:
- Creating new collections
- Modifying collection properties
- Setting up vectorizers
- Configuring indexes
- Managing data organization

Respond with both an explanation and any necessary configuration steps.
"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=message)
            ]
            
            response = await asyncio.to_thread(self.llm.invoke, messages)
            
            # TODO: Parse response to extract actual Weaviate operations
            # For MVP, just return the explanation
            
            logger.info(f"Generated config response for: {message[:50]}...")
            return response.content
            
        except Exception as e:
            logger.error(f"Error in configure_weaviate: {str(e)}")
            raise
    
    async def parse_scrape_intent(self, prompt: str) -> Dict[str, Any]:
        """
        Use Claude to parse scraping intent from natural language
        
        Args:
            prompt: Natural language scraping request
        
        Returns:
            Structured scraping configuration
        """
        try:
            system_prompt = """You are an AI assistant that parses natural language requests into structured scraping configurations.

Extract the following information from the user's request:
1. URLs to scrape (if any)
2. File paths to process (if any)
3. Scraping method preference (firecrawl, apify, local)
4. Any specific requirements or constraints

Respond with a JSON object containing:
{
    "type": "firecrawl|apify|local",
    "urls": ["list", "of", "urls"],
    "paths": ["list", "of", "file", "paths"],
    "requirements": "any specific requirements",
    "collection_name": "suggested collection name"
}
"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Parse this scraping request: {prompt}")
            ]
            
            response = await asyncio.to_thread(self.llm.invoke, messages)
            
            # TODO: Parse JSON response properly
            # For MVP, return a simple structure
            
            logger.info(f"Parsed scrape intent for: {prompt[:50]}...")
            return {
                "type": "auto",
                "urls": [],
                "paths": [],
                "requirements": response.content,
                "collection_name": "scraped_data"
            }
            
        except Exception as e:
            logger.error(f"Error parsing scrape intent: {str(e)}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the chat model"""
        return {
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4000,
            "temperature": 0.1
        }
