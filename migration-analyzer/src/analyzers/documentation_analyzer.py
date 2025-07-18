"""
Documentation analyzer for extracting business context and application purpose using LLM
"""
import os
import re
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

class DocumentationAnalyzer:
    """Analyzer for extracting business context from documentation"""
    
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
        
        # Business criticality keywords
        self.criticality_keywords = {
            'critical': ['critical', 'mission-critical', 'production', 'live', 'customer-facing'],
            'high': ['important', 'core', 'essential', 'primary', 'main', 'revenue'],
            'medium': ['secondary', 'supporting', 'helper', 'utility'],
            'low': ['development', 'testing', 'experimental', 'prototype', 'poc']
        }
        
        # Compliance keywords
        self.compliance_keywords = {
            'PCI-DSS': ['pci', 'credit card', 'payment', 'cardholder'],
            'HIPAA': ['hipaa', 'health', 'medical', 'patient', 'phi'],
            'SOX': ['sox', 'sarbanes', 'financial', 'audit'],
            'GDPR': ['gdpr', 'privacy', 'personal data', 'european'],
            'SOC2': ['soc2', 'security', 'availability', 'processing integrity'],
            'ISO27001': ['iso27001', 'information security', 'isms']
        }
    
    def analyze_documentation(self, repo_path: str) -> DocumentationInsights:
        """Analyze documentation files in repository"""
        documentation_content = self._collect_documentation(repo_path)
        
        if not documentation_content:
            return self._create_empty_insights()
        
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
                        print(f"Error reading {file_path}: {e}")
        
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
        """Use LLM to extract insights from documentation"""
        
        # Check if LLM is available
        if not GENAI_AVAILABLE or not self.model:
            return self._create_empty_insights()
        
        # Prepare content for LLM
        combined_content = ""
        for file_path, content in documentation.items():
            combined_content += f"\\n\\n=== {file_path} ===\\n{content}"
        
        # Limit content size to avoid token limits
        if len(combined_content) > 50000:
            combined_content = combined_content[:50000] + "\\n\\n[Content truncated...]"
        
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
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            if not response_text or response_text.strip() == "":
                print("Warning: Empty response from LLM")
                return self._create_empty_insights()
            
            # Try to extract JSON from response
            import json
            json_str = None
            
            # Try different JSON extraction methods
            patterns = [
                r'```json\s*\n(.*?)\n```',  # Markdown code block
                r'```\s*\n(.*?)\n```',      # Generic code block
                r'(\{.*\})',                # Direct JSON object
            ]
            
            for pattern in patterns:
                json_match = re.search(pattern, response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1).strip()
                    break
            
            if not json_str:
                print(f"Warning: No JSON found in LLM response: {response_text[:200]}...")
                return self._create_empty_insights()
            
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON from LLM: {e}")
                print(f"Response text: {response_text[:500]}...")
                return self._create_empty_insights()
            
            return DocumentationInsights(
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
            
        except Exception as e:
            print(f"Error using LLM for documentation analysis: {e}")
            return self._create_empty_insights()
    
    def _enhance_with_patterns(self, insights: DocumentationInsights, documentation: Dict[str, str]):
        """Enhance insights with pattern-based analysis"""
        combined_content = " ".join(documentation.values()).lower()
        
        # Enhance business criticality
        if insights.business_criticality == 'MEDIUM':  # Only enhance if LLM didn't determine it
            for level, keywords in self.criticality_keywords.items():
                if any(keyword in combined_content for keyword in keywords):
                    insights.business_criticality = level.upper()
                    break
        
        # Enhance compliance requirements
        for compliance, keywords in self.compliance_keywords.items():
            if any(keyword in combined_content for keyword in keywords):
                if compliance not in insights.compliance_requirements:
                    insights.compliance_requirements.append(compliance)
        
        # Extract URLs and external service references
        url_pattern = r'https?://[\\w\\.-]+(?:/[\\w\\.-]*)*'
        urls = re.findall(url_pattern, " ".join(documentation.values()))
        
        # Add external services from URLs
        for url in urls:
            domain = re.search(r'https?://([\\w\\.-]+)', url)
            if domain:
                domain_name = domain.group(1)
                # Filter out common domains that aren't integration points
                if not any(common in domain_name for common in ['github.com', 'gitlab.com', 'docker.com']):
                    if domain_name not in insights.integration_points:
                        insights.integration_points.append(domain_name)
        
        # Extract port numbers (might indicate exposed services)
        port_pattern = r'port\\s*:?\\s*(\\d{4,5})'
        ports = re.findall(port_pattern, combined_content)
        if ports:
            insights.performance_requirements.append(f"Exposed ports: {', '.join(set(ports))}")
        
        # Look for database mentions
        db_keywords = ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra']
        for db in db_keywords:
            if db in combined_content:
                if db not in insights.technology_stack:
                    insights.technology_stack.append(db)
        
        # Look for messaging systems
        msg_keywords = ['kafka', 'rabbitmq', 'activemq', 'redis', 'sqs', 'pubsub']
        for msg in msg_keywords:
            if msg in combined_content:
                if msg not in insights.technology_stack:
                    insights.technology_stack.append(msg)
        
        # Look for cloud providers
        cloud_keywords = ['aws', 'azure', 'gcp', 'google cloud', 'kubernetes', 'docker']
        for cloud in cloud_keywords:
            if cloud in combined_content:
                if cloud not in insights.technology_stack:
                    insights.technology_stack.append(cloud)
        
        # Look for architecture patterns
        arch_patterns = ['microservices', 'monolith', 'serverless', 'event-driven', 'rest api', 'graphql']
        for pattern in arch_patterns:
            if pattern in combined_content:
                if pattern not in insights.architecture_patterns:
                    insights.architecture_patterns.append(pattern)
    
    def _create_empty_insights(self) -> DocumentationInsights:
        """Create empty insights when no documentation is found"""
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
    
    def generate_summary_report(self, insights: DocumentationInsights) -> str:
        """Generate a human-readable summary report"""
        report = f"""
# Documentation Analysis Summary

## Application Purpose
{insights.application_purpose}

## Business Criticality
**Level:** {insights.business_criticality}

## Compliance Requirements
{', '.join(insights.compliance_requirements) if insights.compliance_requirements else 'None identified'}

## Technology Stack
{', '.join(insights.technology_stack) if insights.technology_stack else 'Not specified'}

## Architecture Patterns
{', '.join(insights.architecture_patterns) if insights.architecture_patterns else 'Not specified'}

## Deployment Model
{insights.deployment_model}

## User Types
{', '.join(insights.user_types) if insights.user_types else 'Not specified'}

## Integration Points
{', '.join(insights.integration_points) if insights.integration_points else 'None identified'}

## Security Considerations
{chr(10).join(f'- {item}' for item in insights.security_considerations) if insights.security_considerations else 'None specified'}

## Performance Requirements
{chr(10).join(f'- {item}' for item in insights.performance_requirements) if insights.performance_requirements else 'None specified'}

## Business Context Keywords
{', '.join(insights.business_context_keywords) if insights.business_context_keywords else 'None identified'}
"""
        return report