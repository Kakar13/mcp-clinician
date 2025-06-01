import json
import httpx
from mcp.server import Server
from mcp.types import TextContent, Tool
from typing import Dict, Any, Optional, List
import re

class ClinicalGuidelinesServer:
    def __init__(self):
        self.server = Server("clinical-guidelines")
        self.setup_tools()
    
    def _split_text_into_chunks(self, text: str, max_chunk_size: int = 1000) -> List[str]:
        """Split long text into smaller chunks for processing"""
        if len(text) <= max_chunk_size:
            return [text]
        
        # Split by sentences to maintain context
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_size = len(sentence)
            if current_size + sentence_size > max_chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_size = sentence_size
            else:
                current_chunk.append(sentence)
                current_size += sentence_size
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    async def query_nice_guidelines(self, condition: str) -> Optional[Dict[str, Any]]:
        """Query NICE guidelines API (free public API)"""
        base_url = "https://api.nice.org.uk/guidance"
        async with httpx.AsyncClient() as client:
            try:
                # Split condition into chunks if needed
                chunks = self._split_text_into_chunks(condition)
                all_results = []
                
                for chunk in chunks:
                    response = await client.get(
                        f"{base_url}?search={chunk}"
                    )
                    if response.status_code == 200:
                        result = response.json()
                        if result and "results" in result:
                            all_results.extend(result["results"])
                
                return {"results": all_results} if all_results else None
            except Exception as e:
                return {"error": str(e)}
    
    async def query_guidelines_central(self, condition: str) -> Optional[Dict[str, Any]]:
        """Query Guidelines Central API (free public API)"""
        base_url = "https://www.guidelinescentral.com/api/v1"
        async with httpx.AsyncClient() as client:
            try:
                # Split condition into chunks if needed
                chunks = self._split_text_into_chunks(condition)
                all_results = []
                
                for chunk in chunks:
                    response = await client.get(
                        f"{base_url}/guidelines/search",
                        params={"query": chunk}
                    )
                    if response.status_code == 200:
                        result = response.json()
                        if result and "guidelines" in result:
                            all_results.extend(result["guidelines"])
                
                return {"results": all_results} if all_results else None
            except Exception as e:
                return {"error": str(e)}
    
    async def query_health_gov(self, condition: str) -> Optional[Dict[str, Any]]:
        """Query Health.gov guidelines API (free public API)"""
        base_url = "https://health.gov/api/guidelines"
        async with httpx.AsyncClient() as client:
            try:
                # Split condition into chunks if needed
                chunks = self._split_text_into_chunks(condition)
                all_results = []
                
                for chunk in chunks:
                    response = await client.get(
                        f"{base_url}?query={chunk}"
                    )
                    if response.status_code == 200:
                        result = response.json()
                        if result and "results" in result:
                            all_results.extend(result["results"])
                
                return {"results": all_results} if all_results else None
            except Exception as e:
                return {"error": str(e)}
    
    async def get_guidelines(self, condition: str) -> Dict[str, Any]:
        """Get comprehensive guidelines from multiple sources"""
        nice_guidelines = await self.query_nice_guidelines(condition)
        guidelines_central = await self.query_guidelines_central(condition)
        health_gov = await self.query_health_gov(condition)
        
        return {
            "condition": condition,
            "sources": {
                "nice": nice_guidelines,
                "guidelines_central": guidelines_central,
                "health_gov": health_gov
            },
            "timestamp": httpx.get_event_loop().time()
        }
    
    def setup_tools(self):
        @self.server.list_tools()
        async def list_tools():
            return [
                Tool(
                    name="get_treatment_guidelines",
                    description="Get comprehensive clinical treatment guidelines from multiple sources",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "condition": {"type": "string"}
                        },
                        "required": ["condition"]
                    }
                ),
                Tool(
                    name="get_guideline_sources",
                    description="Get available guideline sources and their status",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            if name == "get_treatment_guidelines":
                condition = arguments.get("condition", "")
                guidelines = await self.get_guidelines(condition)
                return [TextContent(type="text", text=json.dumps(guidelines))]
            
            elif name == "get_guideline_sources":
                sources = {
                    "nice": True,
                    "guidelines_central": True,
                    "health_gov": True
                }
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "available_sources": sources,
                        "total_sources": len(sources),
                        "active_sources": len(sources)
                    })
                )]