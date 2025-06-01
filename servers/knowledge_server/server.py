import asyncio
import httpx
from mcp.server import Server
from mcp.types import TextContent, Tool
import json
from typing import Optional, Dict, Any, List
import re

class MedicalKnowledgeServer:
    def __init__(self):
        self.server = Server("medical-knowledge")
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
    
    async def query_openfda(self, condition: str) -> Optional[Dict[str, Any]]:
        """Query OpenFDA for drug information (free public API)"""
        base_url = "https://api.fda.gov/drug/label.json"
        async with httpx.AsyncClient() as client:
            try:
                # Split condition into chunks if needed
                chunks = self._split_text_into_chunks(condition)
                all_results = []
                
                for chunk in chunks:
                    response = await client.get(
                        f"{base_url}?search=indications_and_usage:{chunk}&limit=5"
                    )
                    if response.status_code == 200:
                        result = response.json()
                        if result and "results" in result:
                            all_results.extend(result["results"])
                
                return {"results": all_results} if all_results else None
            except Exception as e:
                return {"error": str(e)}

    async def query_rxnorm(self, drug_name: str) -> Optional[Dict[str, Any]]:
        """Query RxNorm API (free public API)"""
        base_url = "https://rxnav.nlm.nih.gov/REST"
        async with httpx.AsyncClient() as client:
            try:
                # Split drug name into chunks if needed
                chunks = self._split_text_into_chunks(drug_name)
                all_results = []
                
                for chunk in chunks:
                    response = await client.get(
                        f"{base_url}/drugs.json?name={chunk}"
                    )
                    if response.status_code == 200:
                        result = response.json()
                        if result and "drugGroup" in result:
                            all_results.extend(result["drugGroup"].get("conceptGroup", []))
                
                return {"results": all_results} if all_results else None
            except Exception as e:
                return {"error": str(e)}

    async def query_medline(self, condition: str) -> Optional[Dict[str, Any]]:
        """Query MedlinePlus Connect API (free public API)"""
        base_url = "https://connect.medlineplus.gov/service"
        async with httpx.AsyncClient() as client:
            try:
                # Split condition into chunks if needed
                chunks = self._split_text_into_chunks(condition)
                all_results = []
                
                for chunk in chunks:
                    response = await client.get(
                        f"{base_url}?mainSearchCriteria.v.cs=2.16.840.1.113883.6.177&mainSearchCriteria.v.dn={chunk}&knowledgeResponseType=application/json"
                    )
                    if response.status_code == 200:
                        result = response.json()
                        if result and "feed" in result:
                            all_results.extend(result["feed"].get("entry", []))
                
                return {"results": all_results} if all_results else None
            except Exception as e:
                return {"error": str(e)}
    
    async def get_condition_info(self, symptoms: list) -> Dict[str, Any]:
        """Get comprehensive condition information from multiple sources"""
        conditions = []
        for symptom in symptoms:
            medline_info = await self.query_medline(symptom)
            if medline_info and "error" not in medline_info:
                conditions.append(medline_info)
        
        return {
            "conditions": conditions,
            "sources": ["MedlinePlus", "OpenFDA"],
            "timestamp": asyncio.get_event_loop().time()
        }
    
    def setup_tools(self):
        @self.server.list_tools()
        async def list_tools():
            return [
                Tool(
                    name="get_differential_diagnosis",
                    description="Get potential conditions based on symptoms",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symptoms": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["symptoms"]
                    }
                ),
                Tool(
                    name="get_drug_information",
                    description="Get comprehensive drug information from multiple sources",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "drug_name": {"type": "string"}
                        },
                        "required": ["drug_name"]
                    }
                ),
                Tool(
                    name="get_condition_details",
                    description="Get detailed information about a medical condition",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "condition": {"type": "string"}
                        },
                        "required": ["condition"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            if name == "get_differential_diagnosis":
                symptoms = arguments.get("symptoms", [])
                condition_info = await self.get_condition_info(symptoms)
                return [TextContent(type="text", text=json.dumps(condition_info))]
            
            elif name == "get_drug_information":
                drug_name = arguments.get("drug_name", "")
                fda_info = await self.query_openfda(drug_name)
                rxnorm_info = await self.query_rxnorm(drug_name)
                
                combined_info = {
                    "fda_data": fda_info,
                    "rxnorm_data": rxnorm_info,
                    "timestamp": asyncio.get_event_loop().time()
                }
                return [TextContent(type="text", text=json.dumps(combined_info))]
            
            elif name == "get_condition_details":
                condition = arguments.get("condition", "")
                medline_info = await self.query_medline(condition)
                return [TextContent(type="text", text=json.dumps(medline_info))]