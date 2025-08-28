import os
import asyncio
from typing import List, Dict, Any, Optional
from langchain_community.document_loaders import FirecrawlLoader
from langchain_community.document_loaders import ApifyDatasetLoader
from langchain_community.document_loaders import UnstructuredFileLoader, DirectoryLoader
from langchain.schema import Document
import logging

logger = logging.getLogger(__name__)

class UniversalScraper:
    """Universal scraper supporting Firecrawl, Apify, and local files"""
    
    def __init__(self):
        self.firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
        self.apify_api_key = os.getenv("APIFY_API_KEY")
        self.unstructured_api_key = os.getenv("UNSTRUCTURED_API_KEY")
    
    async def scrape_with_prompt(self, prompt: str, source_type: str = "auto") -> List[Document]:
        """
        Scrape content based on natural language prompt
        
        Args:
            prompt: Natural language description of what to scrape
            source_type: "auto", "firecrawl", "apify", or "local"
        
        Returns:
            List of LangChain Document objects
        """
        try:
            # Parse the prompt to determine scraping strategy
            scrape_config = await self._parse_scrape_prompt(prompt, source_type)
            
            if scrape_config["type"] == "firecrawl":
                return await self._scrape_with_firecrawl(scrape_config)
            elif scrape_config["type"] == "apify":
                return await self._scrape_with_apify(scrape_config)
            elif scrape_config["type"] == "local":
                return await self._process_local_files(scrape_config)
            else:
                raise ValueError(f"Unsupported scrape type: {scrape_config['type']}")
                
        except Exception as e:
            logger.error(f"Error in scrape_with_prompt: {str(e)}")
            raise
    
    async def _parse_scrape_prompt(self, prompt: str, source_type: str) -> Dict[str, Any]:
        """Parse natural language prompt to determine scraping configuration"""
        
        # Simple prompt parsing - in production, use LLM for this
        config = {"type": source_type}
        
        if source_type == "auto":
            # Auto-detect based on prompt content
            if "http" in prompt or "www." in prompt or ".com" in prompt:
                if "crawl" in prompt.lower() or "sitemap" in prompt.lower():
                    config["type"] = "firecrawl"
                else:
                    config["type"] = "apify"
            elif "file" in prompt.lower() or "folder" in prompt.lower() or "local" in prompt.lower():
                config["type"] = "local"
            else:
                config["type"] = "firecrawl"  # Default to firecrawl
        
        # Extract URLs, file paths, etc.
        if "http" in prompt:
            import re
            urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', prompt)
            config["urls"] = urls
        
        # Extract file paths
        if config["type"] == "local":
            # Simple extraction - in production, use more sophisticated parsing
            config["paths"] = ["/path/to/files"]  # Placeholder
        
        return config
    
    async def _scrape_with_firecrawl(self, config: Dict[str, Any]) -> List[Document]:
        """Scrape using Firecrawl"""
        if not self.firecrawl_api_key:
            raise ValueError("FIRECRAWL_API_KEY not set")
        
        documents = []
        urls = config.get("urls", [])
        
        for url in urls:
            try:
                loader = FirecrawlLoader(
                    api_key=self.firecrawl_api_key,
                    url=url,
                    mode="scrape"  # or "crawl" for full site crawling
                )
                docs = await asyncio.to_thread(loader.load)
                documents.extend(docs)
                logger.info(f"Scraped {len(docs)} documents from {url}")
            except Exception as e:
                logger.error(f"Error scraping {url} with Firecrawl: {str(e)}")
        
        return documents
    
    async def _scrape_with_apify(self, config: Dict[str, Any]) -> List[Document]:
        """Scrape using Apify"""
        if not self.apify_api_key:
            raise ValueError("APIFY_API_KEY not set")
        
        # For MVP, use a simple web scraper actor
        # In production, intelligently select the best Apify actor based on the prompt
        
        try:
            from apify_client import ApifyClient
            
            client = ApifyClient(self.apify_api_key)
            
            # Example: Use Website Content Crawler
            run_input = {
                "startUrls": [{"url": url} for url in config.get("urls", [])],
                "maxCrawlPages": 10,
                "crawlerType": "playwright",
            }
            
            # Run the actor
            run = client.actor("apify/website-content-crawler").call(run_input=run_input)
            
            # Get results
            documents = []
            for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                doc = Document(
                    page_content=item.get("text", ""),
                    metadata={
                        "url": item.get("url", ""),
                        "title": item.get("title", ""),
                        "source": "apify"
                    }
                )
                documents.append(doc)
            
            logger.info(f"Scraped {len(documents)} documents with Apify")
            return documents
            
        except Exception as e:
            logger.error(f"Error scraping with Apify: {str(e)}")
            raise
    
    async def _process_local_files(self, config: Dict[str, Any]) -> List[Document]:
        """Process local files using Unstructured.io"""
        
        documents = []
        paths = config.get("paths", [])
        
        for path in paths:
            try:
                if os.path.isfile(path):
                    # Single file
                    loader = UnstructuredFileLoader(
                        path,
                        api_key=self.unstructured_api_key if self.unstructured_api_key else None
                    )
                    docs = await asyncio.to_thread(loader.load)
                    documents.extend(docs)
                elif os.path.isdir(path):
                    # Directory
                    loader = DirectoryLoader(
                        path,
                        loader_cls=UnstructuredFileLoader,
                        loader_kwargs={
                            "api_key": self.unstructured_api_key if self.unstructured_api_key else None
                        }
                    )
                    docs = await asyncio.to_thread(loader.load)
                    documents.extend(docs)
                
                logger.info(f"Processed {len(documents)} documents from {path}")
                
            except Exception as e:
                logger.error(f"Error processing {path}: {str(e)}")
        
        return documents
    
    async def scrape_url_direct(self, url: str, method: str = "firecrawl") -> List[Document]:
        """Direct URL scraping for testing"""
        config = {"type": method, "urls": [url]}
        
        if method == "firecrawl":
            return await self._scrape_with_firecrawl(config)
        elif method == "apify":
            return await self._scrape_with_apify(config)
        else:
            raise ValueError(f"Unsupported method: {method}")
    
    async def process_files_direct(self, file_paths: List[str]) -> List[Document]:
        """Direct file processing for testing"""
        config = {"type": "local", "paths": file_paths}
        return await self._process_local_files(config)
