#!/usr/bin/env python3
"""
LLM-Enhanced Classifier for Infrastructure Components
Uses Google Gemini LLM to intelligently classify infrastructure components
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Use centralized LLM configuration
from ..config import get_llm_config, is_llm_available, get_classification_model

@dataclass
class ComponentClassification:
    """Result of LLM classification"""
    classification: str  # "Data Source", "Application Component", "CI/CD Pipeline", "Configuration"
    type: str  # "PostgreSQL", "Redis", "Java Application", etc.
    deployment_model: Optional[str] = None  # "ephemeral", "persistent", "stateless"
    confidence: float = 0.0
    reasoning: str = ""

class LLMEnhancedClassifier:
    """LLM-powered classifier for infrastructure components"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """Initialize the LLM classifier"""
        # Use centralized LLM configuration
        self.llm_config = get_llm_config()
        self.llm = get_classification_model()
        self.gemini_available = is_llm_available()
        
        if self.gemini_available:
            print("OK [LLM-CLASSIFIER] Gemini LLM initialized successfully")
        else:
            print("WARNING [LLM-CLASSIFIER] LLM not available - falling back to rule-based classification")
    
    def classify_infrastructure_component(self, 
                                        file_path: str, 
                                        yaml_content: Dict[str, Any]) -> ComponentClassification:
        """
        Classify an infrastructure component using LLM analysis
        
        Args:
            file_path: Path to the YAML file
            yaml_content: Parsed YAML content
            
        Returns:
            ComponentClassification with intelligent analysis
        """
        
        if not self.gemini_available or not self.llm:
            return self._fallback_classification(file_path, yaml_content)
        
        try:
            # Extract key fields for LLM analysis
            kind = yaml_content.get('kind', '')
            metadata = yaml_content.get('metadata', {})
            name = metadata.get('name', '')
            annotations = metadata.get('annotations', {})
            
            # Build context for LLM
            context = self._build_context(file_path, kind, name, annotations, yaml_content)
            
            # Generate LLM prompt
            prompt = self._create_classification_prompt(context)
            
            print(f"LLM [LLM-CLASSIFIER] Analyzing {name} ({kind})")
            
            # Get LLM response
            response = self.llm.generate_content(prompt)
            
            # Parse response
            classification = self._parse_llm_response(response.text)
            
            return classification
            
        except Exception as e:
            print(f"WARNING [LLM-CLASSIFIER] Error classifying {file_path}: {e}")
            return self._fallback_classification(file_path, yaml_content)
    
    def _build_context(self, file_path: str, kind: str, name: str, 
                      annotations: Dict[str, Any], yaml_content: Dict[str, Any]) -> Dict[str, Any]:
        """Build context for LLM analysis"""
        
        # Extract meaningful fields
        display_name = annotations.get('openshift.io/display-name', '')
        description = annotations.get('description', '')
        
        # Get spec information
        spec = yaml_content.get('spec', {})
        template = yaml_content.get('template', {})
        
        # Build container information
        containers = []
        if 'template' in yaml_content:
            containers = template.get('spec', {}).get('containers', [])
        elif 'spec' in yaml_content:
            containers = spec.get('template', {}).get('spec', {}).get('containers', [])
        
        container_images = [c.get('image', '') for c in containers if c.get('image')]
        
        return {
            'file_path': file_path,
            'kind': kind,
            'name': name,
            'display_name': display_name,
            'description': description,
            'container_images': container_images,
            'has_volumes': bool(spec.get('volumes') or template.get('spec', {}).get('volumes')),
            'has_env_vars': bool(containers and any(c.get('env') for c in containers)),
            'ports': [p.get('containerPort') for c in containers for p in c.get('ports', [])],
            'labels': metadata.get('labels', {}),
            'annotations': annotations
        }
    
    def _create_classification_prompt(self, context: Dict[str, Any]) -> str:
        """Create LLM prompt for classification"""
        
        return f"""You are an infrastructure analysis assistant. Based on the following Kubernetes/OpenShift resource information, classify this component and provide detailed analysis.

Resource Information:
- File: {context['file_path']}
- Kind: {context['kind']}
- Name: {context['name']}
- Display Name: {context['display_name']}
- Description: {context['description']}
- Container Images: {context['container_images']}
- Has Volumes: {context['has_volumes']}
- Exposed Ports: {context['ports']}
- Labels: {context['labels']}

Classification Task:
Based on the name, description, container images, and configuration, classify this resource into one of these categories:
1. "Data Source" - Databases, caches, message queues, data stores
2. "Application Component" - Business logic, web services, APIs
3. "CI/CD Pipeline" - Build, test, deployment automation
4. "Configuration" - Config maps, secrets, settings
5. "Infrastructure" - Load balancers, ingress, monitoring

If it's a Data Source, identify the specific type (PostgreSQL, Redis, MySQL, etc.).

Provide your response in this exact JSON format:
{{
    "classification": "Data Source",
    "type": "PostgreSQL",
    "deployment_model": "ephemeral",
    "confidence": 0.95,
    "reasoning": "The resource name 'postgresql-ephemeral' and description clearly indicate this is a PostgreSQL database configured for ephemeral storage. The template creates PostgreSQL containers with temporary storage."
}}

Important: 
- Focus on the human-readable description and display name
- Consider the container images (e.g., postgresql:latest indicates PostgreSQL)
- "ephemeral" means temporary storage, "persistent" means permanent storage
- Be specific about database/cache types (PostgreSQL, Redis, MySQL, etc.)
- Confidence should be 0.0-1.0 based on how clear the classification is
"""
    
    def _parse_llm_response(self, response_text: str) -> ComponentClassification:
        """Parse LLM response into ComponentClassification"""
        
        try:
            # Try to extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                data = json.loads(json_str)
                
                return ComponentClassification(
                    classification=data.get('classification', 'Unknown'),
                    type=data.get('type', 'Unknown'),
                    deployment_model=data.get('deployment_model'),
                    confidence=data.get('confidence', 0.0),
                    reasoning=data.get('reasoning', '')
                )
            
        except json.JSONDecodeError as e:
            print(f"WARNING [LLM-CLASSIFIER] Error parsing JSON: {e}")
        except Exception as e:
            print(f"WARNING [LLM-CLASSIFIER] Error parsing response: {e}")
        
        # Fallback parsing
        return self._fallback_parse(response_text)
    
    def _fallback_parse(self, response_text: str) -> ComponentClassification:
        """Fallback parsing when JSON parsing fails"""
        
        text_lower = response_text.lower()
        
        # Simple classification based on keywords
        if 'data source' in text_lower:
            classification = 'Data Source'
        elif 'application' in text_lower:
            classification = 'Application Component'
        elif 'pipeline' in text_lower or 'ci/cd' in text_lower:
            classification = 'CI/CD Pipeline'
        else:
            classification = 'Unknown'
        
        # Simple type detection
        component_type = 'Unknown'
        if 'postgresql' in text_lower or 'postgres' in text_lower:
            component_type = 'PostgreSQL'
        elif 'redis' in text_lower:
            component_type = 'Redis'
        elif 'mysql' in text_lower:
            component_type = 'MySQL'
        elif 'mongodb' in text_lower:
            component_type = 'MongoDB'
        
        return ComponentClassification(
            classification=classification,
            type=component_type,
            deployment_model=None,
            confidence=0.5,
            reasoning="Fallback classification based on keywords"
        )
    
    def _fallback_classification(self, file_path: str, yaml_content: Dict[str, Any]) -> ComponentClassification:
        """Fallback classification when LLM is not available"""
        
        name = yaml_content.get('metadata', {}).get('name', '').lower()
        kind = yaml_content.get('kind', '').lower()
        
        # Rule-based classification
        if any(db in name for db in ['postgresql', 'postgres', 'redis', 'mysql', 'mongo']):
            if 'postgresql' in name or 'postgres' in name:
                return ComponentClassification(
                    classification='Data Source',
                    type='PostgreSQL',
                    deployment_model='ephemeral' if 'ephemeral' in name else 'persistent',
                    confidence=0.8,
                    reasoning='Rule-based classification from component name'
                )
            elif 'redis' in name:
                return ComponentClassification(
                    classification='Data Source',
                    type='Redis',
                    deployment_model='ephemeral' if 'ephemeral' in name else 'persistent',
                    confidence=0.8,
                    reasoning='Rule-based classification from component name'
                )
        
        # Default to application component
        return ComponentClassification(
            classification='Application Component',
            type='Unknown',
            deployment_model=None,
            confidence=0.3,
            reasoning='Default fallback classification'
        )
    
    def classify_multiple_components(self, 
                                   yaml_files: Dict[str, Dict[str, Any]]) -> Dict[str, ComponentClassification]:
        """Classify multiple components"""
        
        classifications = {}
        
        for file_path, yaml_content in yaml_files.items():
            classification = self.classify_infrastructure_component(file_path, yaml_content)
            classifications[file_path] = classification
        
        return classifications
    
    def get_data_sources_from_classifications(self, 
                                            classifications: Dict[str, ComponentClassification]) -> List[str]:
        """Extract data sources from classifications"""
        
        data_sources = set()
        
        for file_path, classification in classifications.items():
            if classification.classification == 'Data Source':
                data_sources.add(classification.type.lower())
        
        return sorted(list(data_sources))