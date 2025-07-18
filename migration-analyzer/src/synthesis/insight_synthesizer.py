import os
from typing import List, Dict
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

try:
    import google.generativeai as genai
    from google.generativeai import GenerativeModel
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from src.core.models import SemanticCodeMap
from src.core.utils import RateLimiter

if DOTENV_AVAILABLE:
    load_dotenv()

class InsightSynthesizer:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai not available. Install with: pip install google-generativeai")
            
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not provided")
            
        genai.configure(api_key=self.api_key)
        self.model = GenerativeModel('gemini-2.0-flash-exp')
        self.rate_limiter = RateLimiter(max_calls=14, period=60)
        
    @RateLimiter(max_calls=14, period=60)
    def generate_flow_narrative(self, semantic_maps: Dict[str, List[SemanticCodeMap]]) -> str:
        """Generate end-to-end flow narrative from semantic maps"""
        prompt = self._build_flow_prompt(semantic_maps)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating narrative: {str(e)}"
            
    def _build_flow_prompt(self, semantic_maps: Dict[str, List[SemanticCodeMap]]) -> str:
        """Build prompt for LLM"""
        prompt = """You are analyzing a microservices application. Based on the semantic code analysis below, 
provide a clear, technical narrative of how data flows through the system end-to-end.

Focus on:
1. User entry points
2. Service-to-service communication
3. Data transformations
4. Storage operations
5. Response flow back to user

Here's the semantic analysis of each component:

"""
        
        for component_name, maps in semantic_maps.items():
            prompt += f"\n## Component: {component_name}\n"
            
            for code_map in maps:
                prompt += f"\n### File: {code_map.file_path}\n"
                prompt += f"Language: {code_map.language}\n"
                
                if code_map.api_endpoints:
                    prompt += "\nAPI Endpoints:\n"
                    for endpoint in code_map.api_endpoints:
                        prompt += f"- {endpoint.methods} {endpoint.path}\n"
                        
                if code_map.database_interactions:
                    prompt += "\nDatabase Operations:\n"
                    for db_op in code_map.database_interactions:
                        prompt += f"- {db_op.operation} "
                        if db_op.raw_query:
                            prompt += f"(query: {db_op.raw_query[:50]}...)\n"
                        else:
                            prompt += "\n"
                            
                if code_map.outbound_http_calls:
                    prompt += "\nHTTP Calls:\n"
                    for call in code_map.outbound_http_calls:
                        prompt += f"- {call.method} {call.url}\n"
                        
        prompt += "\nProvide a cohesive narrative of the data flow, starting from user interaction to final response."
        
        return prompt