import asyncio
from mcp.server import Server
from mcp.types import TextContent, Tool
import json
import re
import httpx
from typing import List, Dict, Any, Optional

class SymptomAnalysisServer:
    def __init__(self):
        self.server = Server("symptom-analysis")
        self.symptoms_db = self.load_symptoms_database()
        
    def load_symptoms_database(self) -> Dict[str, List[str]]:
        """Load standardized symptom terminology"""
        return {
            "fever": ["fever", "high temperature", "pyrexia", "febrile", "hot", "chills", "running a temperature"],
            "headache": ["headache", "head pain", "cephalgia", "migraine", "head ache", "throbbing head", "pressure in head"],
            "cough": ["cough", "coughing", "persistent cough", "dry cough", "wet cough", "hacking cough", "productive cough"],
            "fatigue": ["tired", "fatigue", "exhaustion", "weakness", "lethargy", "low energy", "feeling drained"],
            "nausea": ["nausea", "queasy", "sick to stomach", "vomiting", "throwing up", "upset stomach", "feeling sick"],
            "dizziness": ["dizzy", "lightheaded", "vertigo", "unsteady", "woozy", "spinning sensation", "balance problems"],
            "chest_pain": ["chest pain", "chest discomfort", "chest tightness", "heart pain", "pressure in chest", "chest ache"],
            "shortness_of_breath": ["shortness of breath", "difficulty breathing", "breathlessness", "dyspnea", "can't catch breath", "breathing problems"],
            "abdominal_pain": ["stomach pain", "abdominal pain", "belly ache", "cramps", "stomach cramps", "tummy ache", "gut pain"],
            "joint_pain": ["joint pain", "arthritis", "joint stiffness", "joint swelling", "achy joints", "joint discomfort", "joint inflammation"],
            "muscle_pain": ["muscle pain", "muscle ache", "muscle soreness", "muscle cramps", "muscle stiffness", "muscle tenderness"],
            "back_pain": ["back pain", "backache", "lower back pain", "upper back pain", "spinal pain", "back stiffness"],
            "throat_pain": ["sore throat", "throat pain", "throat irritation", "scratchy throat", "throat discomfort", "difficulty swallowing"],
            "ear_pain": ["ear pain", "earache", "ear discomfort", "ear pressure", "ear fullness", "ear infection"],
            "eye_problems": ["eye pain", "eye irritation", "red eyes", "watery eyes", "blurred vision", "eye strain"],
            "skin_problems": ["rash", "skin rash", "hives", "itching", "skin irritation", "skin redness", "skin lesions"],
            "sleep_problems": ["insomnia", "difficulty sleeping", "trouble falling asleep", "waking up frequently", "poor sleep quality"],
            "anxiety": ["anxiety", "nervousness", "worry", "panic", "stress", "feeling anxious", "restlessness"],
            "depression": ["depression", "sadness", "low mood", "hopelessness", "lack of interest", "emotional numbness"],
            "cognitive_problems": ["memory problems", "difficulty concentrating", "brain fog", "confusion", "forgetfulness", "mental fatigue"]
        }
    
    async def query_quickumls(self, text: str) -> Optional[Dict[str, Any]]:
        """Query QuickUMLS API (free medical concept extraction)"""
        base_url = "https://quickumls.nlm.nih.gov/api"
        async with httpx.AsyncClient() as client:
            try:
                # Split text into chunks if needed for processing
                chunks = self._split_text_into_chunks(text)
                all_entities = []
                
                for chunk in chunks:
                    response = await client.post(
                        f"{base_url}/process",
                        json={"text": chunk}
                    )
                    if response.status_code == 200:
                        result = response.json()
                        if result and "entities" in result:
                            all_entities.extend(result["entities"])
                
                return {"entities": all_entities} if all_entities else None
            except Exception as e:
                return {"error": str(e)}
    
    async def query_scispacy(self, text: str) -> Optional[Dict[str, Any]]:
        """Query scispaCy API (free medical entity recognition)"""
        base_url = "https://scispacy.apps.allenai.org/api/process"
        async with httpx.AsyncClient() as client:
            try:
                # Split text into chunks if needed for processing
                chunks = self._split_text_into_chunks(text)
                all_entities = []
                
                for chunk in chunks:
                    response = await client.post(
                        base_url,
                        json={"text": chunk}
                    )
                    if response.status_code == 200:
                        result = response.json()
                        if result and "entities" in result:
                            all_entities.extend(result["entities"])
                
                return {"entities": all_entities} if all_entities else None
            except Exception as e:
                return {"error": str(e)}
    
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
    
    async def normalize_symptoms(self, symptoms_text: str) -> Dict[str, Any]:
        """Normalize user input to standard medical terminology using multiple sources"""
        normalized = []
        symptoms_lower = symptoms_text.lower()
        
        # Local database matching
        for standard_term, variations in self.symptoms_db.items():
            for variation in variations:
                if variation in symptoms_lower:
                    normalized.append(standard_term)
                    break
        
        # Query medical NLP APIs
        quickumls_results = await self.query_quickumls(symptoms_text)
        scispacy_results = await self.query_scispacy(symptoms_text)
        
        # Combine results
        result = {
            "original_input": symptoms_text,
            "normalized_symptoms": list(set(normalized)),  # Remove duplicates
            "quickumls_entities": quickumls_results.get("entities", []) if quickumls_results else [],
            "scispacy_entities": scispacy_results.get("entities", []) if scispacy_results else [],
            "confidence_scores": {
                "local_matching": len(normalized) / len(self.symptoms_db),
                "quickumls_confidence": quickumls_results.get("confidence", 0) if quickumls_results else 0,
                "scispacy_confidence": scispacy_results.get("confidence", 0) if scispacy_results else 0
            },
            "timestamp": asyncio.get_event_loop().time()
        }
        
        return result
    
    def setup_tools(self):
        @self.server.list_tools()
        async def list_tools():
            return [
                Tool(
                    name="analyze_symptoms",
                    description="Analyze and normalize symptom descriptions using multiple medical NLP services",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symptoms": {"type": "string", "description": "Patient symptoms description"}
                        },
                        "required": ["symptoms"]
                    }
                ),
                Tool(
                    name="get_symptom_variations",
                    description="Get all known variations of a specific symptom",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symptom": {"type": "string", "description": "Standard symptom term"}
                        },
                        "required": ["symptom"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            if name == "analyze_symptoms":
                symptoms = arguments.get("symptoms", "")
                analysis = await self.normalize_symptoms(symptoms)
                return [TextContent(type="text", text=json.dumps(analysis))]
            
            elif name == "get_symptom_variations":
                symptom = arguments.get("symptom", "").lower()
                variations = self.symptoms_db.get(symptom, [])
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "symptom": symptom,
                        "variations": variations,
                        "count": len(variations)
                    })
                )]