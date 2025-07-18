"""
Documentation analyzer with comprehensive logging for diagnosing LLM issues
"""
import os
import re
import json
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from src.core.utils import RateLimiter
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

@dataclass
class DocumentationInsights:
    """Insights extracted from documentation"""
    application_purpose: str
    business_criticality: str  # LOW, MEDIUM, HIGH, CRITICAL
    compliance_requirements: List[str]
    security_considerations: List[str]
    technology_stack: List[str]
    deployment_model: str
    user_types: List[str]
    integration_points: List[str]
    performance_requirements: List[str]
    business_context_keywords: List[str]
    architecture_patterns: List[str]

class DocumentationAnalyzerWithLogging:
    """Analyzer for extracting business context from documentation with comprehensive logging"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        if GENAI_AVAILABLE and api_key:
            genai.configure(api_key=api_key)
            model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash-lite-preview-06-17')
            self.model = genai.GenerativeModel(model_name)
        else:
            self.model = None
        
        # Common documentation file patterns
        self.doc_patterns = [
            'README.md', 'README.rst', 'README.txt',
            'ARCHITECTURE.md', 'DESIGN.md', 'OVERVIEW.md',
            'API.md', 'GETTING_STARTED.md', 'INSTALLATION.md',
            'DEPLOYMENT.md', 'CONFIGURATION.md', 'SECURITY.md'
        ]
    
    def analyze_documentation(self, repo_path: str) -> DocumentationInsights:
        """Analyze documentation files in repository"""
        print(f"🔍 [DOC-ANALYZER] Starting documentation analysis for: {repo_path}")
        
        documentation_content = self._collect_documentation(repo_path)
        
        if not documentation_content:
            print("⚠️  [DOC-ANALYZER] No documentation found, returning empty insights")
            return self._create_empty_insights()
        
        print(f"📄 [DOC-ANALYZER] Found {len(documentation_content)} documentation files")
        
        # Use LLM to extract insights
        insights = self._extract_insights_with_llm(documentation_content)
        
        # Enhance with pattern-based analysis
        self._enhance_with_patterns(insights, documentation_content)
        
        return insights
    
    def _collect_documentation(self, repo_path: str) -> Dict[str, str]:
        """Collect documentation files from repository"""
        documentation = {}
        
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden directories and common build directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and 
                      d not in ['node_modules', '__pycache__', 'target', 'build']]
            
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, repo_path)
                
                # Check if it's a documentation file
                if self._is_documentation_file(file, relative_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if content.strip():  # Only include non-empty files
                                documentation[relative_path] = content
                    except Exception as e:
                        print(f"❌ [DOC-ANALYZER] Error reading {file_path}: {e}")
        
        return documentation
    
    def _is_documentation_file(self, filename: str, relative_path: str) -> bool:
        """Check if file is likely documentation"""
        # Check exact filename matches
        if filename in self.doc_patterns:
            return True
        
        # Check if it's a markdown or text file in docs directory
        if any(part in relative_path.lower() for part in ['docs/', 'documentation/', 'wiki/']):
            if filename.endswith(('.md', '.rst', '.txt', '.adoc')):
                return True
        
        # Check for specific patterns
        filename_lower = filename.lower()
        doc_keywords = ['readme', 'changelog', 'contributing', 'license', 'install', 
                       'setup', 'guide', 'tutorial', 'manual', 'spec', 'design']
        
        if any(keyword in filename_lower for keyword in doc_keywords):
            if filename.endswith(('.md', '.rst', '.txt', '.adoc')):
                return True
        
        return False
    
    @RateLimiter(max_calls=14, period=60)
    def _extract_insights_with_llm(self, documentation: Dict[str, str]) -> DocumentationInsights:
        """Use LLM to extract insights from documentation with comprehensive logging"""
        
        print(f"🔍 [DOC-LLM] Starting LLM documentation analysis...")
        print(f"🔍 [DOC-LLM] GENAI_AVAILABLE: {GENAI_AVAILABLE}")
        print(f"🔍 [DOC-LLM] Model available: {self.model is not None}")
        print(f"🔍 [DOC-LLM] API key configured: {bool(self.api_key)}")
        
        # Check if LLM is available
        if not GENAI_AVAILABLE or not self.model:
            print("⚠️  [DOC-LLM] LLM not available, using fallback insights")
            if not GENAI_AVAILABLE:
                print("⚠️  [DOC-LLM] google.generativeai not available")
            if not self.model:
                print("⚠️  [DOC-LLM] Model not initialized")
            return self._create_empty_insights()
        
        # Prepare content for LLM
        combined_content = ""
        for file_path, content in documentation.items():
            combined_content += f"\n\n=== {file_path} ===\n{content}"
        
        print(f"🔍 [DOC-LLM] Documentation files: {list(documentation.keys())}")
        print(f"🔍 [DOC-LLM] Combined content length: {len(combined_content)} chars")
        
        # Limit content size to avoid token limits
        original_length = len(combined_content)
        if len(combined_content) > 50000:
            combined_content = combined_content[:50000] + "\n\n[Content truncated...]"
            print(f"⚠️  [DOC-LLM] Content truncated from {original_length} to 50000 chars")
        
        prompt = f"""
Analyze the following documentation and extract key insights about the application:

{combined_content}

Please provide a structured analysis with the following information:

1. APPLICATION_PURPOSE: What is the main purpose of this application? (1-2 sentences)

2. BUSINESS_CRITICALITY: How critical is this application to the business?
   - CRITICAL: Mission-critical, customer-facing, revenue-generating
   - HIGH: Important business function, core system
   - MEDIUM: Supporting system, internal tool
   - LOW: Development/testing tool, experimental

3. COMPLIANCE_REQUIREMENTS: List any compliance standards mentioned (PCI-DSS, HIPAA, SOX, GDPR, etc.)

4. SECURITY_CONSIDERATIONS: List security features, requirements, or concerns mentioned

5. TECHNOLOGY_STACK: List technologies, frameworks, databases, languages mentioned

6. DEPLOYMENT_MODEL: How is this application deployed? (container, cloud, on-premise, etc.)

7. USER_TYPES: Who are the users of this application?

8. INTEGRATION_POINTS: What external systems or services does this integrate with?

9. PERFORMANCE_REQUIREMENTS: Any performance, scalability, or SLA requirements mentioned

10. BUSINESS_CONTEXT_KEYWORDS: Key business domain terms (e.g., e-commerce, financial, healthcare)

11. ARCHITECTURE_PATTERNS: Any architectural patterns mentioned (microservices, SOA, event-driven, etc.)

Format your response as a JSON object with these fields. If information is not available, use empty arrays or "Unknown".
"""
        
        print(f"🔍 [DOC-LLM] Prompt length: {len(prompt)} chars")
        print(f"🔍 [DOC-LLM] Making LLM call...")
        
        try:
            response = self.model.generate_content(prompt)
            print(f"✅ [DOC-LLM] LLM call completed successfully")
            print(f"🔍 [DOC-LLM] Response object type: {type(response)}")
            print(f"🔍 [DOC-LLM] Response object attributes: {dir(response)}")
            
            # Check if response has text attribute
            if hasattr(response, 'text'):
                response_text = response.text
                print(f"🔍 [DOC-LLM] Response text type: {type(response_text)}")
                print(f"🔍 [DOC-LLM] Response text length: {len(response_text) if response_text else 0} chars")
                
                if response_text:
                    print(f"🔍 [DOC-LLM] Response text preview (first 300 chars): {response_text[:300]}...")
                    print(f"🔍 [DOC-LLM] Response text preview (last 300 chars): ...{response_text[-300:]}")
                else:
                    print("❌ [DOC-LLM] Response text is None or empty")
            else:
                print(f"❌ [DOC-LLM] Response has no 'text' attribute")
                print(f"🔍 [DOC-LLM] Available attributes: {[attr for attr in dir(response) if not attr.startswith('_')]}")
                return self._create_empty_insights()
            
            # Check for empty response
            if not response_text or response_text.strip() == "":
                print("⚠️  [DOC-LLM] Empty response from LLM")
                return self._create_empty_insights()
            
            # Try to extract JSON from response
            json_str = None
            
            print(f"🔍 [DOC-LLM] Attempting to extract JSON from response...")
            
            # Try different JSON extraction methods
            patterns = [
                r'```json\s*\n(.*?)\n```',  # Markdown code block
                r'```\s*\n(.*?)\n```',      # Generic code block
                r'(\{.*\})',                # Direct JSON object
            ]
            
            for i, pattern in enumerate(patterns):
                print(f"🔍 [DOC-LLM] Trying pattern {i+1}: {pattern}")
                try:
                    json_match = re.search(pattern, response_text, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1).strip()
                        print(f"✅ [DOC-LLM] JSON found with pattern {i+1}")
                        print(f"🔍 [DOC-LLM] Extracted JSON length: {len(json_str)} chars")
                        print(f"🔍 [DOC-LLM] Extracted JSON preview: {json_str[:200]}...")
                        break
                    else:
                        print(f"❌ [DOC-LLM] Pattern {i+1} failed to match")
                except Exception as e:
                    print(f"❌ [DOC-LLM] Pattern {i+1} caused error: {e}")
            
            if not json_str:
                print(f"❌ [DOC-LLM] No JSON found in LLM response")
                print(f"🔍 [DOC-LLM] Full response text for debugging:")
                print("=" * 80)
                print(response_text)
                print("=" * 80)
                return self._create_empty_insights()
            
            print(f"🔍 [DOC-LLM] Attempting to parse JSON...")
            try:
                data = json.loads(json_str)
                print(f"✅ [DOC-LLM] JSON parsed successfully")
                print(f"🔍 [DOC-LLM] Parsed data type: {type(data)}")
                print(f"🔍 [DOC-LLM] Parsed data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # Log the values we're extracting
                for key in ['APPLICATION_PURPOSE', 'BUSINESS_CRITICALITY', 'TECHNOLOGY_STACK']:
                    value = data.get(key, 'NOT_FOUND')
                    print(f"🔍 [DOC-LLM] {key}: {value}")
                
            except json.JSONDecodeError as e:
                print(f"❌ [DOC-LLM] Invalid JSON from LLM: {e}")
                print(f"🔍 [DOC-LLM] JSON parse error details:")
                print(f"   Error message: {e.msg}")
                print(f"   Error position: line {e.lineno}, column {e.colno}")
                print(f"🔍 [DOC-LLM] Failed JSON string (first 1000 chars): {json_str[:1000]}...")
                return self._create_empty_insights()
            
            print(f"🔍 [DOC-LLM] Creating DocumentationInsights object...")
            insights = DocumentationInsights(
                application_purpose=data.get('APPLICATION_PURPOSE', 'Unknown'),
                business_criticality=data.get('BUSINESS_CRITICALITY', 'MEDIUM'),
                compliance_requirements=data.get('COMPLIANCE_REQUIREMENTS', []),
                security_considerations=data.get('SECURITY_CONSIDERATIONS', []),
                technology_stack=data.get('TECHNOLOGY_STACK', []),
                deployment_model=data.get('DEPLOYMENT_MODEL', 'Unknown'),
                user_types=data.get('USER_TYPES', []),
                integration_points=data.get('INTEGRATION_POINTS', []),
                performance_requirements=data.get('PERFORMANCE_REQUIREMENTS', []),
                business_context_keywords=data.get('BUSINESS_CONTEXT_KEYWORDS', []),
                architecture_patterns=data.get('ARCHITECTURE_PATTERNS', [])
            )
            
            print(f"✅ [DOC-LLM] Documentation analysis completed successfully")
            print(f"🔍 [DOC-LLM] Final insights:")
            print(f"   Purpose: {insights.application_purpose}")
            print(f"   Criticality: {insights.business_criticality}")
            print(f"   Tech Stack: {insights.technology_stack}")
            print(f"   Deployment: {insights.deployment_model}")
            
            return insights
            
        except Exception as e:
            print(f"❌ [DOC-LLM] Error using LLM for documentation analysis: {e}")
            print(f"🔍 [DOC-LLM] Exception type: {type(e)}")
            print(f"🔍 [DOC-LLM] Exception details: {str(e)}")
            print(f"🔍 [DOC-LLM] Full traceback:")
            traceback.print_exc()
            return self._create_empty_insights()
    
    def _enhance_with_patterns(self, insights: DocumentationInsights, documentation: Dict[str, str]):
        """Enhance insights with pattern-based analysis"""
        print(f"🔍 [DOC-ANALYZER] Enhancing insights with pattern-based analysis...")
        
        combined_content = " ".join(documentation.values()).lower()
        
        # Business criticality keywords
        criticality_keywords = {
            'critical': ['critical', 'mission-critical', 'production', 'live', 'customer-facing'],
            'high': ['important', 'core', 'essential', 'primary', 'main', 'revenue'],
            'medium': ['secondary', 'supporting', 'helper', 'utility'],
            'low': ['development', 'testing', 'experimental', 'prototype', 'poc']
        }
        
        # Enhance business criticality
        if insights.business_criticality == 'MEDIUM':  # Only enhance if LLM didn't determine it
            for level, keywords in criticality_keywords.items():
                if any(keyword in combined_content for keyword in keywords):
                    insights.business_criticality = level.upper()
                    print(f"🔍 [DOC-ANALYZER] Enhanced criticality to {level.upper()} based on keywords")
                    break
        
        # Look for additional technology stack items
        db_keywords = ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra']
        for db in db_keywords:
            if db in combined_content:
                if db not in insights.technology_stack:
                    insights.technology_stack.append(db)
                    print(f"🔍 [DOC-ANALYZER] Added {db} to technology stack")
        
        print(f"✅ [DOC-ANALYZER] Pattern-based enhancement completed")
    
    def _create_empty_insights(self) -> DocumentationInsights:
        """Create empty insights when no documentation is found"""
        print(f"🔍 [DOC-ANALYZER] Creating empty insights")
        return DocumentationInsights(
            application_purpose="Unknown - No documentation found",
            business_criticality="MEDIUM",
            compliance_requirements=[],
            security_considerations=[],
            technology_stack=[],
            deployment_model="Unknown",
            user_types=[],
            integration_points=[],
            performance_requirements=[],
            business_context_keywords=[],
            architecture_patterns=[]
        )