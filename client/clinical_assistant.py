import asyncio
from anthropic import Anthropic
import json
import re
import os
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

class ClinicalDecisionSupport:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        # Initialize local knowledge bases for testing
        self.symptoms_db = self._load_symptoms_db()
        self.conditions_db = self._load_conditions_db()
        self.guidelines_db = self._load_guidelines_db()
        
    def _load_symptoms_db(self) -> Dict[str, List[str]]:
        """Load symptom mapping database"""
        return {
            "fever": ["fever", "high temperature", "pyrexia", "febrile", "hot", "burning up"],
            "headache": ["headache", "head pain", "cephalgia", "migraine", "head hurts"],
            "cough": ["cough", "coughing", "persistent cough", "dry cough", "wet cough"],
            "fatigue": ["tired", "fatigue", "exhaustion", "weakness", "worn out", "drained"],
            "sore_throat": ["sore throat", "throat pain", "scratchy throat", "throat hurts"],
            "runny_nose": ["runny nose", "nasal congestion", "stuffy nose", "blocked nose"],
            "body_aches": ["body aches", "muscle pain", "joint pain", "aches", "soreness"]
        }
    
    def _load_conditions_db(self) -> Dict[tuple, Dict[str, Any]]:
        """Load condition mapping database"""
        return {
            ("fever", "cough"): {
                "conditions": ["Upper Respiratory Infection", "Pneumonia", "Bronchitis"],
                "urgency": "moderate",
                "likelihood": [0.6, 0.2, 0.2]
            },
            ("fever", "headache"): {
                "conditions": ["Viral Infection", "Sinusitis", "Meningitis"],
                "urgency": "moderate",
                "likelihood": [0.7, 0.2, 0.1]
            },
            ("fever", "cough", "fatigue"): {
                "conditions": ["Influenza", "COVID-19", "Pneumonia", "Bronchitis"],
                "urgency": "moderate",
                "likelihood": [0.4, 0.3, 0.2, 0.1]
            },
            ("cough", "fatigue"): {
                "conditions": ["Upper Respiratory Infection", "Bronchitis", "Allergies"],
                "urgency": "low",
                "likelihood": [0.5, 0.3, 0.2]
            }
        }
    
    def _load_guidelines_db(self) -> Dict[str, Dict[str, Any]]:
        """Load treatment guidelines database"""
        return {
            "Upper Respiratory Infection": {
                "first_line_treatment": ["Rest", "Hydration", "Supportive care"],
                "medications": ["Acetaminophen for fever", "Throat lozenges", "Decongestants if needed"],
                "red_flags": ["High fever >101.5°F for >3 days", "Difficulty breathing", "Severe throat pain"],
                "follow_up": "If symptoms worsen or persist beyond 7-10 days",
                "duration": "7-10 days typically"
            },
            "Influenza": {
                "first_line_treatment": ["Rest", "Hydration", "Antiviral medications if within 48 hours"],
                "medications": ["Oseltamivir (Tamiflu)", "Acetaminophen/Ibuprofen for fever"],
                "red_flags": ["Difficulty breathing", "Chest pain", "Severe dehydration"],
                "follow_up": "Monitor closely, seek care if breathing difficulties",
                "duration": "7-14 days typically"
            },
            "COVID-19": {
                "first_line_treatment": ["Isolation", "Rest", "Hydration", "Monitor oxygen levels"],
                "medications": ["Acetaminophen for fever", "Consider Paxlovid if high risk"],
                "red_flags": ["Difficulty breathing", "Chest pain", "Confusion", "Bluish lips"],
                "follow_up": "Isolate for 5-10 days, seek immediate care for severe symptoms",
                "duration": "5-14 days typically"
            }
        }
    
    async def normalize_symptoms(self, symptoms_text: str) -> Dict[str, Any]:
        """Normalize user input to standard medical terminology"""
        normalized = []
        symptoms_lower = symptoms_text.lower()
        
        for standard_term, variations in self.symptoms_db.items():
            for variation in variations:
                if variation in symptoms_lower:
                    normalized.append(standard_term)
                    break
        
        return {
            "original_input": symptoms_text,
            "normalized_symptoms": list(set(normalized)),
            "symptom_count": len(set(normalized))
        }
    
    async def get_differential_diagnosis(self, symptoms: List[str]) -> Dict[str, Any]:
        """Get potential conditions based on symptoms"""
        # Try different combinations of symptoms
        symptoms_set = set(symptoms)
        best_match = None
        best_score = 0
        
        for symptom_combo, condition_info in self.conditions_db.items():
            combo_set = set(symptom_combo)
            # Calculate match score (intersection over union)
            intersection = len(symptoms_set.intersection(combo_set))
            union = len(symptoms_set.union(combo_set))
            score = intersection / union if union > 0 else 0
            
            if score > best_score:
                best_score = score
                best_match = condition_info
        
        if best_match:
            return best_match
        else:
            return {
                "conditions": ["Consult healthcare provider for evaluation"],
                "urgency": "unknown",
                "likelihood": [1.0]
            }
    
    async def get_treatment_guidelines(self, condition: str) -> Dict[str, Any]:
        """Get treatment guidelines for a condition"""
        return self.guidelines_db.get(condition, {
            "message": f"No specific guidelines found for {condition}",
            "recommendation": "Consult healthcare provider for appropriate treatment"
        })
        
    async def analyze_patient_case(self, symptoms_description: str):
        """Main function to analyze patient symptoms and provide recommendations"""
        
        # Step 1: Analyze symptoms
        normalized_symptoms = await self.normalize_symptoms(symptoms_description)
        
        # Step 2: Get differential diagnosis
        differential = await self.get_differential_diagnosis(
            normalized_symptoms["normalized_symptoms"]
        )
        
        # Step 3: Get treatment guidelines for the most likely condition
        guidelines = None
        if differential.get("conditions") and len(differential["conditions"]) > 0:
            primary_condition = differential["conditions"][0]
            guidelines = await self.get_treatment_guidelines(primary_condition)
        
        # Step 4: Generate comprehensive response using Claude
        prompt = f"""
        Based on the following medical analysis, provide educational information:
        
        Patient Symptoms: {symptoms_description}
        Normalized Symptoms: {normalized_symptoms['normalized_symptoms']}
        Potential Conditions: {differential.get('conditions', [])}
        Urgency Level: {differential.get('urgency', 'unknown')}
        Treatment Guidelines: {guidelines}
        
        Please provide a clear, educational response that includes:
        1. A summary of what the symptoms might indicate
        2. General self-care recommendations
        3. Clear guidance on when to seek professional medical care
        4. Important medical disclaimers
        
        Format your response in a helpful, easy-to-understand manner while emphasizing that this is educational information only.
        """
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "analysis": {
                "symptoms": normalized_symptoms,
                "differential": differential,
                "guidelines": guidelines
            },
            "clinical_response": response.content[0].text
        }

# Usage example
async def main():
    # Get API key from environment or replace with your key
    api_key = os.getenv("ANTHROPIC_API_KEY", "your-anthropic-api-key-here")
    
    if api_key == "your-anthropic-api-key-here":
        print("Please set your ANTHROPIC_API_KEY environment variable or update the code with your API key")
        return
    
    assistant = ClinicalDecisionSupport(api_key)
    
    print("🏥 Clinical Decision Support System")
    print("=" * 50)
    print("Please describe your symptoms in detail (e.g., 'I have been feeling tired with a fever and cough')")
    symptoms = input("Enter your symptoms: ")
    
    print("-" * 50)
    print(f"Analyzing symptoms: {symptoms}")
    print("-" * 50)
    
    try:
        result = await assistant.analyze_patient_case(symptoms)
        
        print("📊 ANALYSIS SUMMARY:")
        print(f"Original symptoms: {result['analysis']['symptoms']['original_input']}")
        print(f"Normalized symptoms: {result['analysis']['symptoms']['normalized_symptoms']}")
        print(f"Potential conditions: {result['analysis']['differential']['conditions']}")
        print(f"Urgency level: {result['analysis']['differential']['urgency']}")
        
        print("\n🩺 CLINICAL RECOMMENDATIONS:")
        print(result['clinical_response'])
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have set your ANTHROPIC_API_KEY correctly")

if __name__ == "__main__":
    asyncio.run(main())