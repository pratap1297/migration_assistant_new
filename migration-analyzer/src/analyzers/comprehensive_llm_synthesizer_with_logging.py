"""
Comprehensive LLM Synthesizer with detailed logging for diagnosing issues
"""
import os
import json
import re
import traceback
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

class ComprehensiveLLMSynthesizerWithLogging:
    """LLM synthesizer with comprehensive logging for debugging"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        print(f"🔍 [LLM-SYNTH] Initializing synthesizer...")
        print(f"🔍 [LLM-SYNTH] API key provided: {bool(api_key)}")
        print(f"🔍 [LLM-SYNTH] GENAI_AVAILABLE: {GENAI_AVAILABLE}")
        
        if GENAI_AVAILABLE and api_key:
            try:
                genai.configure(api_key=api_key)
                model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash-lite-preview-06-17')
                print(f"🔍 [LLM-SYNTH] Using model: {model_name}")
                self.model = genai.GenerativeModel(model_name)
                print(f"✅ [LLM-SYNTH] Model initialized successfully")
            except Exception as e:
                print(f"❌ [LLM-SYNTH] Error initializing model: {e}")
                self.model = None
        else:
            self.model = None
            if not GENAI_AVAILABLE:
                print("⚠️  [LLM-SYNTH] google.generativeai not available")
            if not api_key:
                print("⚠️  [LLM-SYNTH] No API key provided")
    
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
        
        print(f"🔍 [LLM-SYNTH] Starting comprehensive synthesis...")
        print(f"🔍 [LLM-SYNTH] Input data summary:")
        print(f"   Components: {len(components)} items")
        print(f"   Infrastructure: {len(infrastructure)} items")
        print(f"   CI/CD: {len(ci_cd_pipelines)} items")
        print(f"   Configuration: {len(configuration)} items")
        print(f"   Security: {len(security_posture)} items")
        print(f"   Semantic: {len(semantic_analysis)} items")
        print(f"   Documentation: {documentation_insights.application_purpose}")
        print(f"   Git History: {git_history.total_commits if git_history else 'None'} commits")
        
        if not GENAI_AVAILABLE or not self.model:
            print("⚠️  [LLM-SYNTH] LLM not available, using fallback synthesis")
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
        
        print(f"🔍 [LLM-SYNTH] Serialized data structure created")
        
        # Create comprehensive prompt
        prompt = self._build_comprehensive_prompt(analysis_data)
        
        print(f"🔍 [LLM-SYNTH] Prompt built, length: {len(prompt)} chars")
        print(f"🔍 [LLM-SYNTH] Making LLM call...")
        
        try:
            response = self.model.generate_content(prompt)
            print(f"✅ [LLM-SYNTH] LLM call completed successfully")
            print(f"🔍 [LLM-SYNTH] Response object type: {type(response)}")
            
            if hasattr(response, 'text'):
                response_text = response.text
                print(f"🔍 [LLM-SYNTH] Response text type: {type(response_text)}")
                print(f"🔍 [LLM-SYNTH] Response text length: {len(response_text) if response_text else 0} chars")
                
                if response_text:
                    print(f"🔍 [LLM-SYNTH] Response preview (first 300 chars): {response_text[:300]}...")
                else:
                    print("❌ [LLM-SYNTH] Response text is None or empty")
            else:
                print(f"❌ [LLM-SYNTH] Response has no 'text' attribute")
                print(f"🔍 [LLM-SYNTH] Available attributes: {[attr for attr in dir(response) if not attr.startswith('_')]}")
                return self._create_fallback_synthesis()
            
            if not response_text or response_text.strip() == "":
                print("⚠️  [LLM-SYNTH] Empty response from LLM synthesis")
                return self._create_fallback_synthesis()
            
            return self._parse_synthesis_response(response_text)
            
        except Exception as e:
            print(f"❌ [LLM-SYNTH] Error generating comprehensive synthesis: {e}")
            print(f"🔍 [LLM-SYNTH] Exception type: {type(e)}")
            print(f"🔍 [LLM-SYNTH] Full traceback:")
            traceback.print_exc()
            return self._create_fallback_synthesis()
    
    def _build_comprehensive_prompt(self, analysis_data: Dict[str, Any]) -> str:
        """Build comprehensive prompt for LLM synthesis"""
        
        # Convert to JSON for structured input
        try:
            data_json = json.dumps(analysis_data, indent=2, default=str)
            print(f"🔍 [LLM-SYNTH] Analysis data serialized to JSON: {len(data_json)} chars")
        except Exception as e:
            print(f"❌ [LLM-SYNTH] Error serializing analysis data: {e}")
            data_json = str(analysis_data)
        
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
        
        print(f"🔍 [LLM-SYNTH] Prompt created, total length: {len(prompt)} chars")
        return prompt
    
    def _parse_synthesis_response(self, response_text: str) -> ComprehensiveSynthesis:
        """Parse LLM response into ComprehensiveSynthesis object"""
        print(f"🔍 [LLM-SYNTH] Parsing synthesis response...")
        print(f"🔍 [LLM-SYNTH] Response length: {len(response_text)} chars")
        
        try:
            if not response_text or response_text.strip() == "":
                print("⚠️  [LLM-SYNTH] Empty response text for synthesis")
                return self._create_fallback_synthesis()
            
            # Extract JSON from response
            json_str = None
            
            print(f"🔍 [LLM-SYNTH] Attempting to extract JSON from response...")
            
            # Try different JSON extraction methods
            patterns = [
                r'```json\s*\n(.*?)\n```',  # Markdown code block
                r'```\s*\n(.*?)\n```',      # Generic code block
                r'(\{.*\})',                # Direct JSON object
            ]
            
            for i, pattern in enumerate(patterns):
                print(f"🔍 [LLM-SYNTH] Trying pattern {i+1}: {pattern}")
                try:
                    json_match = re.search(pattern, response_text, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1).strip()
                        print(f"✅ [LLM-SYNTH] JSON found with pattern {i+1}")
                        print(f"🔍 [LLM-SYNTH] Extracted JSON length: {len(json_str)} chars")
                        print(f"🔍 [LLM-SYNTH] JSON preview: {json_str[:200]}...")
                        break
                    else:
                        print(f"❌ [LLM-SYNTH] Pattern {i+1} failed to match")
                except Exception as e:
                    print(f"❌ [LLM-SYNTH] Pattern {i+1} caused error: {e}")
            
            if not json_str:
                print(f"❌ [LLM-SYNTH] No JSON found in synthesis response")
                print(f"🔍 [LLM-SYNTH] Full response text for debugging:")
                print("=" * 80)
                print(response_text)
                print("=" * 80)
                return self._create_fallback_synthesis()
            
            print(f"🔍 [LLM-SYNTH] Attempting to parse JSON...")
            try:
                data = json.loads(json_str)
                print(f"✅ [LLM-SYNTH] JSON parsed successfully")
                print(f"🔍 [LLM-SYNTH] Parsed data type: {type(data)}")
                print(f"🔍 [LLM-SYNTH] Parsed data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # Log key extracted values
                for key in ['executive_summary', 'architecture_assessment', 'migration_strategy']:
                    value = data.get(key, 'NOT_FOUND')
                    print(f"🔍 [LLM-SYNTH] {key}: {value[:100] if isinstance(value, str) else value}...")
                
            except json.JSONDecodeError as e:
                print(f"❌ [LLM-SYNTH] Invalid JSON from synthesis: {e}")
                print(f"🔍 [LLM-SYNTH] JSON parse error details:")
                print(f"   Error message: {e.msg}")
                print(f"   Error position: line {e.lineno}, column {e.colno}")
                print(f"🔍 [LLM-SYNTH] Failed JSON (first 1000 chars): {json_str[:1000]}...")
                return self._create_fallback_synthesis()
            
            print(f"🔍 [LLM-SYNTH] Creating ComprehensiveSynthesis object...")
            synthesis = ComprehensiveSynthesis(
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
            
            print(f"✅ [LLM-SYNTH] Synthesis completed successfully")
            print(f"🔍 [LLM-SYNTH] Executive summary length: {len(synthesis.executive_summary)} chars")
            print(f"🔍 [LLM-SYNTH] Recommendations count: {len(synthesis.recommendations)}")
            
            return synthesis
            
        except Exception as e:
            print(f"❌ [LLM-SYNTH] Error parsing synthesis response: {e}")
            print(f"🔍 [LLM-SYNTH] Exception type: {type(e)}")
            print(f"🔍 [LLM-SYNTH] Full traceback:")
            traceback.print_exc()
            return self._create_fallback_synthesis()
    
    def _serialize_components(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize component data for LLM"""
        serialized = {}
        print(f"🔍 [LLM-SYNTH] Serializing {len(components)} components...")
        
        for name, component in components.items():
            try:
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
            except Exception as e:
                print(f"⚠️  [LLM-SYNTH] Error serializing component {name}: {e}")
                serialized[name] = {"error": str(e)}
        
        return serialized
    
    def _serialize_configuration(self, configuration: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize configuration data for LLM"""
        print(f"🔍 [LLM-SYNTH] Serializing configuration data...")
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
        print(f"🔍 [LLM-SYNTH] Serializing security posture data...")
        serialized = {}
        
        for component, findings in security_posture.items():
            try:
                serialized[component] = {
                    "authentication_mechanisms": findings.authentication_mechanisms,
                    "authorization_patterns": findings.authorization_patterns,
                    "encryption_usage": findings.encryption_usage,
                    "hardcoded_secrets_count": len(findings.hardcoded_secrets),
                    "vulnerabilities_count": len(findings.potential_vulnerabilities),
                    "sample_vulnerabilities": [v.get('type', 'unknown') for v in findings.potential_vulnerabilities[:3]]
                }
            except Exception as e:
                print(f"⚠️  [LLM-SYNTH] Error serializing security data for {component}: {e}")
                serialized[component] = {"error": str(e)}
        
        return serialized
    
    def _serialize_semantic_analysis(self, semantic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize semantic analysis data for LLM"""
        print(f"🔍 [LLM-SYNTH] Serializing semantic analysis data...")
        serialized = {}
        
        for component, maps in semantic_analysis.items():
            try:
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
                else:
                    serialized[component] = {"error": "Invalid semantic analysis data format"}
            except Exception as e:
                print(f"⚠️  [LLM-SYNTH] Error serializing semantic data for {component}: {e}")
                serialized[component] = {"error": str(e)}
        
        return serialized
    
    def _serialize_documentation_insights(self, documentation_insights: DocumentationInsights) -> Dict[str, Any]:
        """Serialize documentation insights for LLM"""
        print(f"🔍 [LLM-SYNTH] Serializing documentation insights...")
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
        print(f"🔍 [LLM-SYNTH] Serializing git history insights...")
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
    
    def _create_fallback_synthesis(self) -> ComprehensiveSynthesis:
        """Create fallback synthesis when LLM is not available"""
        print(f"🔍 [LLM-SYNTH] Creating fallback synthesis")
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