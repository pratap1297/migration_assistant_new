"""
Comprehensive LLM Synthesizer that processes ALL structured data from the analysis
"""
import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from src.core.utils import RateLimiter
from src.analyzers.git_history_analyzer import GitHistoryInsights
from src.analyzers.documentation_analyzer import DocumentationInsights

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

@dataclass
class ComprehensiveSynthesis:
    """Complete synthesis of all application data"""
    executive_summary: str
    architecture_assessment: str
    technology_modernization_plan: str
    security_recommendations: str
    operational_maturity: str
    business_impact_analysis: str
    migration_strategy: str
    risk_assessment: str
    effort_estimation: str
    recommendations: List[str]

class ComprehensiveLLMSynthesizer:
    """LLM synthesizer that processes ALL structured data for comprehensive insights"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        if GENAI_AVAILABLE and api_key:
            genai.configure(api_key=api_key)
            model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash-lite-preview-06-17')
            self.model = genai.GenerativeModel(model_name)
        else:
            self.model = None
    
    @RateLimiter(max_calls=10, period=60)
    def synthesize_comprehensive_insights(self, 
                                        components: Dict[str, Any],
                                        infrastructure: Dict[str, Any],
                                        ci_cd_pipelines: Dict[str, Any],
                                        configuration: Dict[str, Any],
                                        security_posture: Dict[str, Any],
                                        semantic_analysis: Dict[str, Any],
                                        documentation_insights: DocumentationInsights,
                                        git_history: Optional[GitHistoryInsights] = None) -> ComprehensiveSynthesis:
        """Synthesize comprehensive insights from all structured data"""
        
        if not GENAI_AVAILABLE or not self.model:
            return self._create_fallback_synthesis()
        
        # Prepare comprehensive data structure
        analysis_data = {
            "components": self._serialize_components(components),
            "infrastructure": infrastructure,
            "ci_cd_pipelines": ci_cd_pipelines,
            "configuration": self._serialize_configuration(configuration),
            "security_posture": self._serialize_security_posture(security_posture),
            "semantic_analysis": self._serialize_semantic_analysis(semantic_analysis),
            "documentation_insights": self._serialize_documentation_insights(documentation_insights),
            "git_history": self._serialize_git_history(git_history) if git_history else None
        }
        
        # Create comprehensive prompt
        prompt = self._build_comprehensive_prompt(analysis_data)
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            if not response_text or response_text.strip() == "":
                print("Warning: Empty response from LLM synthesis")
                return self._create_fallback_synthesis()
            
            return self._parse_synthesis_response(response_text)
        except Exception as e:
            print(f"Error generating comprehensive synthesis: {e}")
            return self._create_fallback_synthesis()
    
    def _build_comprehensive_prompt(self, analysis_data: Dict[str, Any]) -> str:
        """Build comprehensive prompt for LLM synthesis"""
        
        # Convert to JSON for structured input
        data_json = json.dumps(analysis_data, indent=2, default=str)
        
        prompt = f"""
You are an expert software architect and technical consultant. Analyze the following comprehensive application data and provide strategic insights for technology leadership.

# APPLICATION ANALYSIS DATA

{data_json}

# REQUIRED ANALYSIS

Please provide a comprehensive analysis with the following sections:

## 1. EXECUTIVE_SUMMARY
- High-level overview of the application
- Key findings and strategic implications
- Business value and criticality assessment
- 3-5 key points for executive leadership

## 2. ARCHITECTURE_ASSESSMENT
- Current architecture style and maturity
- Technology stack evaluation
- Scalability and performance considerations
- Architecture strengths and weaknesses

## 3. TECHNOLOGY_MODERNIZATION_PLAN
- Current technology debt assessment
- Modernization priorities and recommendations
- Cloud readiness evaluation
- Technology upgrade roadmap

## 4. SECURITY_RECOMMENDATIONS
- Current security posture evaluation
- Critical security gaps and vulnerabilities
- Compliance and regulatory considerations
- Security improvement recommendations

## 5. OPERATIONAL_MATURITY
- CI/CD pipeline maturity assessment
- DevOps practices evaluation
- Monitoring and observability gaps
- Operational excellence recommendations

## 6. BUSINESS_IMPACT_ANALYSIS
- Business criticality assessment
- User impact analysis
- Revenue and operational implications
- Stakeholder considerations

## 7. MIGRATION_STRATEGY
- Migration complexity assessment
- Recommended migration approach
- Phased migration plan
- Risk mitigation strategies

## 8. RISK_ASSESSMENT
- Technical risks and dependencies
- Business continuity risks
- Migration and modernization risks
- Risk mitigation priorities

## 9. EFFORT_ESTIMATION
- Development effort estimation
- Resource requirements
- Timeline considerations
- Budget implications

## 10. RECOMMENDATIONS
- Top 10 prioritized recommendations
- Quick wins and long-term investments
- Implementation roadmap
- Success metrics

# OUTPUT FORMAT

Please format your response as a JSON object with the following structure:

```json
{{
  "executive_summary": "...",
  "architecture_assessment": "...",
  "technology_modernization_plan": "...",
  "security_recommendations": "...",
  "operational_maturity": "...",
  "business_impact_analysis": "...",
  "migration_strategy": "...",
  "risk_assessment": "...",
  "effort_estimation": "...",
  "recommendations": ["recommendation1", "recommendation2", ...]
}}
```

Focus on actionable insights that can guide technology and business decisions. Consider the full context of the application ecosystem, not just individual components.
"""
        
        return prompt
    
    def _serialize_components(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize component data for LLM"""
        serialized = {}
        for name, component in components.items():
            serialized[name] = {
                "type": component.type,
                "language": component.language,
                "runtime": component.runtime,
                "packaging": component.packaging,
                "dependencies": component.dependencies,
                "external_dependencies": component.external_dependencies,
                "exposed_ports": component.exposed_ports,
                "deployment_info": component.deployment_info,
                "business_context": component.business_context
            }
        return serialized
    
    def _serialize_configuration(self, configuration: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize configuration data for LLM"""
        return {
            "external_services_count": len(configuration.get('external_services', [])),
            "datasources_count": len(configuration.get('datasources', [])),
            "secrets_management_count": len(configuration.get('secrets_management', [])),
            "external_services": configuration.get('external_services', [])[:5],  # Limit for token usage
            "datasources": configuration.get('datasources', [])[:5],
            "secrets_management": configuration.get('secrets_management', [])[:5]
        }
    
    def _serialize_security_posture(self, security_posture: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize security posture data for LLM"""
        # Handle new security posture structure
        serialized = {
            "overall_security": {
                "authentication_mechanisms": security_posture.get('authentication_mechanisms', []),
                "authorization_framework": security_posture.get('authorization_framework', 'unknown'),
                "security_protocols": security_posture.get('security_protocols', []),
                "encryption_standards": security_posture.get('encryption_standards', []),
                "compliance_frameworks": security_posture.get('compliance_frameworks', []),
                "audit_logging": security_posture.get('audit_logging', False),
                "vulnerability_management": security_posture.get('vulnerability_management', 'basic')
            },
            "component_findings": {}
        }
        
        # Process component findings
        component_findings = security_posture.get('component_findings', {})
        for component, findings in component_findings.items():
            if findings and isinstance(findings, dict):
                # Handle case where findings is a dict
                serialized["component_findings"][component] = {
                    "authentication_mechanisms": findings.get('authentication_mechanisms', []),
                    "authorization_patterns": findings.get('authorization_patterns', []),
                    "encryption_usage": findings.get('encryption_usage', []),
                    "hardcoded_secrets_count": len(findings.get('hardcoded_secrets', [])),
                    "vulnerabilities_count": len(findings.get('potential_vulnerabilities', [])),
                    "sample_vulnerabilities": [v.get('type', 'unknown') for v in findings.get('potential_vulnerabilities', [])[:3]]
                }
            elif hasattr(findings, 'authentication_mechanisms'):
                # Handle case where findings is an object with attributes
                serialized["component_findings"][component] = {
                    "authentication_mechanisms": findings.authentication_mechanisms,
                    "authorization_patterns": findings.authorization_patterns,
                    "encryption_usage": findings.encryption_usage,
                    "hardcoded_secrets_count": len(findings.hardcoded_secrets),
                    "vulnerabilities_count": len(findings.potential_vulnerabilities),
                    "sample_vulnerabilities": [v.get('type', 'unknown') for v in findings.potential_vulnerabilities[:3]]
                }
            else:
                # Handle case where findings is None or empty
                serialized["component_findings"][component] = {
                    "authentication_mechanisms": [],
                    "authorization_patterns": [],
                    "encryption_usage": [],
                    "hardcoded_secrets_count": 0,
                    "vulnerabilities_count": 0,
                    "sample_vulnerabilities": []
                }
        
        return serialized
    
    def _serialize_semantic_analysis(self, semantic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize semantic analysis data for LLM"""
        serialized = {}
        for component, maps in semantic_analysis.items():
            if isinstance(maps, list):
                total_endpoints = sum(len(m.api_endpoints) for m in maps if hasattr(m, 'api_endpoints'))
                total_db_ops = sum(len(m.database_interactions) for m in maps if hasattr(m, 'database_interactions'))
                total_http_calls = sum(len(m.outbound_http_calls) for m in maps if hasattr(m, 'outbound_http_calls'))
                
                serialized[component] = {
                    "files_analyzed": len(maps),
                    "total_endpoints": total_endpoints,
                    "total_db_operations": total_db_ops,
                    "total_http_calls": total_http_calls
                }
        return serialized
    
    def _serialize_documentation_insights(self, documentation_insights: DocumentationInsights) -> Dict[str, Any]:
        """Serialize documentation insights for LLM"""
        return {
            "application_purpose": documentation_insights.application_purpose,
            "business_criticality": documentation_insights.business_criticality,
            "compliance_requirements": documentation_insights.compliance_requirements,
            "security_considerations": documentation_insights.security_considerations,
            "technology_stack": documentation_insights.technology_stack,
            "deployment_model": documentation_insights.deployment_model,
            "user_types": documentation_insights.user_types,
            "integration_points": documentation_insights.integration_points,
            "architecture_patterns": documentation_insights.architecture_patterns
        }
    
    def _serialize_git_history(self, git_history: GitHistoryInsights) -> Dict[str, Any]:
        """Serialize git history insights for LLM"""
        return {
            "total_commits": git_history.total_commits,
            "active_contributors": git_history.active_contributors,
            "commit_frequency": git_history.commit_frequency,
            "commit_types": git_history.commit_types,
            "hotspot_files_count": len(git_history.hotspot_files),
            "development_patterns": git_history.development_patterns,
            "release_cadence": git_history.release_cadence,
            "code_stability": git_history.code_stability,
            "team_velocity": git_history.team_velocity
        }
    
    def _parse_synthesis_response(self, response_text: str) -> ComprehensiveSynthesis:
        """Parse LLM response into ComprehensiveSynthesis object"""
        try:
            if not response_text or response_text.strip() == "":
                print("Warning: Empty response text for synthesis")
                return self._create_fallback_synthesis()
            
            # Extract JSON from response
            import re
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
                print(f"Warning: No JSON found in synthesis response: {response_text[:200]}...")
                return self._create_fallback_synthesis()
            
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON from synthesis: {e}")
                print(f"Response text: {response_text[:500]}...")
                return self._create_fallback_synthesis()
            
            return ComprehensiveSynthesis(
                executive_summary=data.get('executive_summary', ''),
                architecture_assessment=data.get('architecture_assessment', ''),
                technology_modernization_plan=data.get('technology_modernization_plan', ''),
                security_recommendations=data.get('security_recommendations', ''),
                operational_maturity=data.get('operational_maturity', ''),
                business_impact_analysis=data.get('business_impact_analysis', ''),
                migration_strategy=data.get('migration_strategy', ''),
                risk_assessment=data.get('risk_assessment', ''),
                effort_estimation=data.get('effort_estimation', ''),
                recommendations=data.get('recommendations', [])
            )
            
        except Exception as e:
            print(f"Error parsing synthesis response: {e}")
            return self._create_fallback_synthesis()
    
    def _create_fallback_synthesis(self) -> ComprehensiveSynthesis:
        """Create fallback synthesis when LLM is not available"""
        return ComprehensiveSynthesis(
            executive_summary="LLM synthesis not available - comprehensive analysis requires API key",
            architecture_assessment="Manual review required",
            technology_modernization_plan="Manual assessment required",
            security_recommendations="Manual security review required",
            operational_maturity="Manual DevOps assessment required",
            business_impact_analysis="Manual business analysis required",
            migration_strategy="Manual migration planning required",
            risk_assessment="Manual risk analysis required",
            effort_estimation="Manual effort estimation required",
            recommendations=["Enable LLM synthesis for comprehensive insights"]
        )