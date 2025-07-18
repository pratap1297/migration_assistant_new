"""
Diagram Summary Analyzer
Generates intelligent summaries and business insights for each diagram type using LLM
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json
import os
import re
from pathlib import Path
import google.generativeai as genai

class DiagramSummaryAnalyzer:
    """
    Analyzes diagrams and generates comprehensive summaries with business insights using LLM
    """
    
    def __init__(self):
        self.risk_thresholds = {
            'vulnerability_critical': 5,
            'vulnerability_high': 10,
            'containerization_low': 0.5,
            'language_diversity_high': 5,
            'component_complexity_high': 10
        }
        
        # Initialize LLM
        self.llm = None
        self._initialize_llm()
        
    def _initialize_llm(self):
        """Initialize the Gemini LLM for intelligent analysis"""
        try:
            # Load API key from .env file
            env_path = Path('.env')
            if env_path.exists():
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.strip() and not line.startswith('#'):
                            key, value = line.strip().split('=', 1)
                            os.environ[key] = value
            
            api_key = os.environ.get('GEMINI_API_KEY')
            if not api_key:
                print("WARNING [DIAGRAM-SUMMARY] No GEMINI_API_KEY found in .env file")
                return
            
            genai.configure(api_key=api_key)
            self.llm = genai.GenerativeModel('gemini-2.5-flash-lite-preview-06-17')
            print("OK [DIAGRAM-SUMMARY] Gemini LLM initialized successfully")
            
        except Exception as e:
            print(f"WARNING [DIAGRAM-SUMMARY] Error initializing LLM: {e}")
            self.llm = None
    
    def generate_diagram_summary(self, diagram_type: str, intelligence_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate comprehensive summary for a specific diagram type using LLM
        
        Returns:
            dict: {
                'context': 'What this diagram shows',
                'key_insights': 'Main takeaways',
                'business_impact': 'Why this matters',
                'recommendations': 'What to do about it',
                'technical_details': 'Additional technical context'
            }
        """
        
        # If LLM is not available, fall back to enhanced data-driven summary
        if not self.llm:
            return self._generate_enhanced_fallback_summary(diagram_type, intelligence_data)
        
        try:
            # Get diagram-specific context and data
            diagram_context = self._get_diagram_context(diagram_type, intelligence_data)
            
            # Generate LLM analysis
            prompt = self._create_analysis_prompt(diagram_type, diagram_context, intelligence_data)
            
            print(f"LLM [DIAGRAM-SUMMARY] Analyzing {diagram_type} with LLM...")
            
            response = self.llm.generate_content(prompt)
            
            # Parse LLM response
            summary = self._parse_llm_response(response.text)
            
            return summary
            
        except Exception as e:
            print(f"WARNING [DIAGRAM-SUMMARY] Error generating LLM summary for {diagram_type}: {e}")
            return self._generate_enhanced_fallback_summary(diagram_type, intelligence_data)
    
    def _get_diagram_context(self, diagram_type: str, intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant context for the specific diagram type"""
        
        # Diagram type mappings and their relevant data
        diagram_contexts = {
            'language_distribution.png': {
                'type': 'Programming Language Distribution',
                'data_keys': ['summary.languages', 'summary.total_components', 'components'],
                'focus': 'Programming languages used across components'
            },
            'component_status.png': {
                'type': 'Component Status Overview',
                'data_keys': ['summary.total_components', 'summary.containerization_status', 'summary.security_findings'],
                'focus': 'Overall health and status of application components'
            },
            'architecture_diagram.png': {
                'type': 'Application Architecture',
                'data_keys': ['architecture_assessment', 'components', 'summary.total_components'],
                'focus': 'System architecture style and component relationships'
            },
            'security_radar.png': {
                'type': 'Security Assessment Radar',
                'data_keys': ['vulnerability_assessment', 'security_posture', 'summary.security_findings'],
                'focus': 'Multi-dimensional security posture analysis'
            },
            'vulnerability_timeline.png': {
                'type': 'Vulnerability Timeline',
                'data_keys': ['vulnerability_assessment.findings', 'summary.security_findings'],
                'focus': 'Security vulnerabilities by severity and timeline'
            },
            'migration_readiness.png': {
                'type': 'Migration Readiness Assessment',
                'data_keys': ['summary.containerization_status', 'summary.security_findings', 'summary.total_components'],
                'focus': 'Readiness for cloud migration across multiple factors'
            },
            'architecture_flowchart.png': {
                'type': 'Architecture Flowchart (Mermaid)',
                'data_keys': ['architecture_assessment', 'components'],
                'focus': 'Component flow and interaction patterns'
            },
            'component_relationship_graph.png': {
                'type': 'Component Relationship Graph (Graphviz)',
                'data_keys': ['components', 'architecture_assessment'],
                'focus': 'Detailed component dependencies and relationships'
            },
            'data_flow_diagram.png': {
                'type': 'Data Flow Diagram (Graphviz)',
                'data_keys': ['components', 'summary.datasources'],
                'focus': 'Data movement and processing flows'
            },
            'component_network.png': {
                'type': 'Component Network Topology',
                'data_keys': ['components', 'architecture_assessment'],
                'focus': 'Network-style component connections and dependencies'
            },
            'technology_stack.png': {
                'type': 'Technology Stack Visualization',
                'data_keys': ['components', 'summary.languages'],
                'focus': 'Layered technology stack overview'
            },
            'development_activity.png': {
                'type': 'Development Activity Heatmap',
                'data_keys': ['git_analysis', 'summary'],
                'focus': 'Development patterns and Git activity'
            },
            'risk_assessment_matrix.png': {
                'type': 'Risk Assessment Matrix',
                'data_keys': ['vulnerability_assessment', 'summary.security_findings'],
                'focus': 'Risk evaluation and prioritization matrix'
            },
            'cicd_pipeline.png': {
                'type': 'CI/CD Pipeline Overview',
                'data_keys': ['ci_cd_pipelines', 'summary'],
                'focus': 'Continuous integration and deployment pipeline'
            },
            'security_flow_diagram.png': {
                'type': 'Security Flow Diagram (Mermaid)',
                'data_keys': ['security_posture', 'vulnerability_assessment'],
                'focus': 'Security process workflows and controls'
            },
            'cicd_pipeline_mermaid.png': {
                'type': 'CI/CD Pipeline Flow (Mermaid)',
                'data_keys': ['ci_cd_pipelines', 'components'],
                'focus': 'Development pipeline visualization with flow'
            },
            'deployment_architecture.png': {
                'type': 'Deployment Architecture (Mermaid)',
                'data_keys': ['components', 'architecture_assessment'],
                'focus': 'Container deployment structure and relationships'
            },
            'risk_assessment_flow.png': {
                'type': 'Risk Assessment Flow (Mermaid)',
                'data_keys': ['vulnerability_assessment', 'summary.security_findings'],
                'focus': 'Risk evaluation process and decision flow'
            },
            'migration_strategy_diagram.png': {
                'type': 'Migration Strategy Diagram (Graphviz)',
                'data_keys': ['summary.containerization_status', 'components', 'architecture_assessment'],
                'focus': 'Migration planning and execution phases'
            },
            'user_flow_diagram.png': {
                'type': 'User Flow Diagram (Mermaid)',
                'data_keys': ['components', 'architecture_assessment', 'summary.external_services'],
                'focus': 'User interaction patterns and system workflows'
            },
            'user_journey_map.png': {
                'type': 'User Journey Map',
                'data_keys': ['components', 'architecture_assessment', 'summary.external_services'],
                'focus': 'End-to-end user experience and touchpoints'
            },
            'high_level_architecture.png': {
                'type': 'High-Level Architecture Overview',
                'data_keys': ['architecture_assessment', 'components', 'summary.external_services', 'summary.datasources'],
                'focus': 'System overview and major architectural components'
            },
            'system_overview.png': {
                'type': 'System Overview Diagram',
                'data_keys': ['architecture_assessment', 'components', 'summary.total_components', 'summary.languages'],
                'focus': 'Complete system landscape and component relationships'
            },
            'business_flow_diagram.png': {
                'type': 'Business Flow Diagram',
                'data_keys': ['components', 'architecture_assessment', 'summary.external_services'],
                'focus': 'Business process flows and system interactions'
            },
            'application_flow.png': {
                'type': 'Application Flow Diagram',
                'data_keys': ['components', 'architecture_assessment', 'summary.external_services'],
                'focus': 'Application logic flow and component interactions'
            }
        }
        
        context = diagram_contexts.get(diagram_type, {
            'type': diagram_type.replace('.png', '').replace('_', ' ').title(),
            'data_keys': ['summary', 'components'],
            'focus': 'General application analysis'
        })
        
        # Extract relevant data
        relevant_data = {}
        for key_path in context['data_keys']:
            try:
                current_data = intelligence_data
                for key in key_path.split('.'):
                    current_data = current_data.get(key, {})
                if current_data:
                    relevant_data[key_path] = current_data
            except:
                pass
        
        context['relevant_data'] = relevant_data
        return context
    
    def _sanitize_data_for_json(self, data: Any) -> str:
        """Sanitize data for JSON serialization by converting problematic types"""
        import datetime
        
        def sanitize_recursive(obj):
            if isinstance(obj, dict):
                return {k: sanitize_recursive(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [sanitize_recursive(item) for item in obj]
            elif isinstance(obj, datetime.datetime):
                return obj.isoformat()
            elif isinstance(obj, datetime.date):
                return obj.isoformat()
            elif hasattr(obj, '__dict__'):
                # Handle custom objects like ConfidenceLevel
                if hasattr(obj, 'value'):
                    return str(obj.value)
                elif hasattr(obj, 'name'):
                    return str(obj.name)
                else:
                    return str(obj)
            elif isinstance(obj, (str, int, float, bool)):
                return obj
            elif obj is None:
                return None
            else:
                return str(obj)
        
        try:
            sanitized_data = sanitize_recursive(data)
            return json.dumps(sanitized_data, indent=2)
        except Exception as e:
            # Fallback to string representation if JSON serialization still fails
            return str(data)
    
    def _create_analysis_prompt(self, diagram_type: str, diagram_context: Dict[str, Any], intelligence_data: Dict[str, Any]) -> str:
        """Create a comprehensive analysis prompt for the LLM"""
        
        diagram_name = diagram_context['type']
        focus_area = diagram_context['focus']
        relevant_data = diagram_context['relevant_data']
        
        # Create data summary for context - sanitize for JSON serialization
        data_summary = self._sanitize_data_for_json(relevant_data)
        
        prompt = f"""
You are an expert application intelligence analyst. Analyze the following diagram and provide a comprehensive business-focused summary.

## Diagram Information
- **Diagram Type**: {diagram_name}
- **Focus Area**: {focus_area}
- **Analysis Context**: This diagram is part of a comprehensive application intelligence report for modernization and migration planning

## Relevant Data for Analysis
```json
{data_summary}
```

## Analysis Framework
Please provide a detailed analysis in the following structure:

**CONTEXT**: (2-3 sentences) What this specific diagram shows and why it was generated
**KEY_INSIGHTS**: (3-4 sentences) The most important technical findings and patterns revealed
**BUSINESS_IMPACT**: (2-3 sentences) What this means for the business - risks, opportunities, costs, timeline implications
**RECOMMENDATIONS**: (2-3 sentences) Specific, actionable next steps prioritized by impact
**TECHNICAL_DETAILS**: (2-3 sentences) Additional technical context that supports the analysis

## Analysis Requirements
- Be specific and data-driven - reference actual numbers and findings from the data
- Focus on business impact and actionable insights, not just technical description
- Identify risks, opportunities, and priorities
- Use professional language appropriate for technical and business stakeholders
- Avoid generic statements - make it unique to this specific application's data
- Consider the context of application modernization and cloud migration
- If data is limited, focus on what can be inferred and what additional analysis might be needed

## Output Format
Return your analysis in this exact JSON format:
```json
{{
    "context": "Your context analysis here",
    "key_insights": "Your key insights here",
    "business_impact": "Your business impact analysis here", 
    "recommendations": "Your recommendations here",
    "technical_details": "Your technical details here"
}}
```

Analyze the diagram data now and provide your comprehensive assessment.
"""
        
        return prompt
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, str]:
        """Parse LLM response and extract JSON summary"""
        
        try:
            # Try to extract JSON from response
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                parsed = json.loads(json_str)
                
                # Validate required fields
                required_fields = ['context', 'key_insights', 'business_impact', 'recommendations', 'technical_details']
                result = {}
                
                for field in required_fields:
                    result[field] = parsed.get(field, f"Analysis not available for {field}")
                
                return result
            
            # If no JSON found, try to parse structured text
            lines = response_text.split('\n')
            result = {}
            current_field = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('**CONTEXT**'):
                    current_field = 'context'
                    result[current_field] = line.replace('**CONTEXT**:', '').strip()
                elif line.startswith('**KEY_INSIGHTS**'):
                    current_field = 'key_insights'
                    result[current_field] = line.replace('**KEY_INSIGHTS**:', '').strip()
                elif line.startswith('**BUSINESS_IMPACT**'):
                    current_field = 'business_impact'
                    result[current_field] = line.replace('**BUSINESS_IMPACT**:', '').strip()
                elif line.startswith('**RECOMMENDATIONS**'):
                    current_field = 'recommendations'
                    result[current_field] = line.replace('**RECOMMENDATIONS**:', '').strip()
                elif line.startswith('**TECHNICAL_DETAILS**'):
                    current_field = 'technical_details'
                    result[current_field] = line.replace('**TECHNICAL_DETAILS**:', '').strip()
                elif current_field and line:
                    result[current_field] += ' ' + line
            
            # Fill in any missing fields
            for field in ['context', 'key_insights', 'business_impact', 'recommendations', 'technical_details']:
                if field not in result:
                    result[field] = f"Analysis not available for {field}"
            
            return result
            
        except Exception as e:
            print(f"WARNING [DIAGRAM-SUMMARY] Error parsing LLM response: {e}")
            return self._generate_fallback_summary_dict()
    
    def _generate_enhanced_fallback_summary(self, diagram_type: str, intelligence_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate fallback summary when LLM is not available"""
        
        diagram_name = diagram_type.replace('.png', '').replace('_', ' ').title()
        
        # Extract specific data for this diagram type
        context = self._get_diagram_context(diagram_type, intelligence_data)
        summary_data = intelligence_data.get('summary', {})
        
        # Generate specific insights based on diagram type and actual data
        if 'language' in diagram_type:
            languages = summary_data.get('languages', {})
            if languages:
                lang_list = ', '.join(languages.keys()) if isinstance(languages, dict) else str(languages)
                return {
                    'context': f"Shows the programming languages used across {summary_data.get('total_components', 0)} components.",
                    'key_insights': f"Primary languages: {lang_list}. Language diversity indicates technology stack complexity.",
                    'business_impact': "Language diversity affects maintenance costs, hiring, and technical debt.",
                    'recommendations': "Consider standardizing on fewer languages for better maintainability.",
                    'technical_details': f"Languages detected: {lang_list}. Analysis based on source code and build configurations."
                }
        
        elif 'component' in diagram_type:
            total_components = summary_data.get('total_components', 0)
            containerized = summary_data.get('containerization_status', 0)
            
            # Dynamic recommendation based on actual containerization status
            if containerized == total_components:
                recommendation = "All components are containerized. Focus on optimizing container configurations and deployment strategies."
            else:
                remaining = total_components - containerized
                recommendation = f"Complete containerization of {remaining} remaining components for full cloud readiness."
            
            return {
                'context': f"Shows status of {total_components} application components.",
                'key_insights': f"{containerized} of {total_components} components are containerized. {'Fully ready for cloud deployment.' if containerized == total_components else 'Partial cloud readiness.'}",
                'business_impact': "Containerization status directly impacts cloud migration readiness and deployment flexibility.",
                'recommendations': recommendation,
                'technical_details': f"Containerization rate: {containerized}/{total_components}. Analysis includes Docker and orchestration configurations."
            }
        
        elif 'security' in diagram_type:
            security_findings = summary_data.get('security_findings', {})
            total_findings = security_findings.get('total_findings', 0) if isinstance(security_findings, dict) else 0
            
            # Get vulnerability assessment data
            vuln_data = intelligence_data.get('vulnerability_assessment', {})
            base_image_risks = vuln_data.get('base_image_risks', [])
            
            # Generate specific insights based on actual findings
            if total_findings == 0:
                risk_level = "low"
                recommendation = "Maintain security scanning practices and monitor for new vulnerabilities."
            elif total_findings <= 2:
                risk_level = "moderate"
                recommendation = "Address identified vulnerabilities within next sprint cycle."
            else:
                risk_level = "high"
                recommendation = "Prioritize security remediation - address critical findings immediately."
            
            return {
                'context': f"Security radar shows {total_findings} security findings across application components.",
                'key_insights': f"Security posture assessment reveals {risk_level} risk profile with {len(base_image_risks)} base image vulnerabilities.",
                'business_impact': f"Current security posture represents {risk_level} risk to system reliability and compliance requirements.",
                'recommendations': recommendation,
                'technical_details': f"Analysis includes {len(base_image_risks)} base image risks and code pattern analysis. Security score based on vulnerability severity."
            }
        
        elif 'migration' in diagram_type:
            total_components = summary_data.get('total_components', 0)
            containerized = summary_data.get('containerization_status', 0)
            security_findings = summary_data.get('security_findings', {})
            vuln_count = security_findings.get('total_findings', 0) if isinstance(security_findings, dict) else 0
            
            # Calculate migration readiness score
            containerization_score = (containerized / total_components * 100) if total_components > 0 else 0
            
            if containerization_score == 100 and vuln_count == 0:
                readiness = "high"
                timeline = "immediate"
            elif containerization_score >= 80 and vuln_count <= 2:
                readiness = "moderate"
                timeline = "next quarter"
            else:
                readiness = "requires preparation"
                timeline = "6+ months"
            
            return {
                'context': f"Migration strategy analysis for {total_components} components shows {readiness} cloud readiness.",
                'key_insights': f"System is {containerization_score:.0f}% containerized with {vuln_count} security concerns. Migration complexity: {readiness}.",
                'business_impact': f"Migration timeline estimated at {timeline} with {readiness} current readiness state.",
                'recommendations': f"Priority actions: {'Proceed with migration planning' if readiness == 'high' else 'Address containerization gaps and security issues before migration'}.",
                'technical_details': f"Readiness factors: {containerized}/{total_components} containerized, {vuln_count} security findings. Strategy: lift-and-shift feasible for containerized components."
            }
        
        elif 'architecture' in diagram_type:
            arch_data = intelligence_data.get('architecture_assessment', {})
            arch_style = arch_data.get('style', 'unknown') if isinstance(arch_data, dict) else 'unknown'
            total_components = summary_data.get('total_components', 0)
            
            # Generate architecture-specific insights
            if arch_style == 'microservices':
                complexity = "high" if total_components > 5 else "moderate"
                benefit = "excellent scalability and deployment flexibility"
                challenge = "service coordination and monitoring complexity"
            elif arch_style == 'monolithic':
                complexity = "low"
                benefit = "simpler deployment and debugging"
                challenge = "scaling and technology diversity limitations"
            else:
                complexity = "unknown"
                benefit = "requires further analysis"
                challenge = "architectural patterns need assessment"
            
            return {
                'context': f"Architecture diagram shows {arch_style} pattern with {total_components} components.",
                'key_insights': f"System follows {arch_style} architecture with {complexity} operational complexity. Offers {benefit}.",
                'business_impact': f"Architecture supports {'independent scaling' if arch_style == 'microservices' else 'unified deployment'} with {challenge} considerations.",
                'recommendations': f"{'Optimize service boundaries and monitoring' if arch_style == 'microservices' else 'Consider componentization for better scalability'} for improved maintainability.",
                'technical_details': f"Architecture style: {arch_style}. Component count: {total_components}. Complexity assessment: {complexity}."
            }
        
        elif 'git' in diagram_type or 'activity' in diagram_type:
            git_data = intelligence_data.get('git_analysis', {})
            commits = git_data.get('total_commits', 0) if isinstance(git_data, dict) else 0
            contributors = git_data.get('active_contributors', 0) if isinstance(git_data, dict) else 0
            
            if commits == 0:
                activity_level = "no recent activity"
                recommendation = "Investigate repository status and development activity"
            elif commits < 10:
                activity_level = "low activity"
                recommendation = "Review development velocity and team capacity"
            else:
                activity_level = "active development"
                recommendation = "Maintain current development practices"
            
            return {
                'context': f"Development activity analysis shows {commits} commits from {contributors} contributors.",
                'key_insights': f"Repository demonstrates {activity_level} with {commits} commits indicating {'healthy' if commits > 10 else 'limited'} development velocity.",
                'business_impact': f"Development activity level affects {'delivery timelines and maintenance capabilities' if commits > 10 else 'project sustainability and knowledge transfer'}.",
                'recommendations': recommendation,
                'technical_details': f"Git analysis: {commits} commits, {contributors} contributors. Activity pattern supports {'continuous development' if commits > 10 else 'periodic maintenance'}."
            }
        
        elif 'user_flow' in diagram_type or 'user_journey' in diagram_type:
            total_components = summary_data.get('total_components', 0)
            external_services = summary_data.get('external_services', [])
            arch_data = intelligence_data.get('architecture_assessment', {})
            arch_style = arch_data.get('style', 'unknown') if isinstance(arch_data, dict) else 'unknown'
            
            # Assess user flow complexity
            if total_components <= 3:
                flow_complexity = "simple"
                user_experience = "streamlined user experience"
            elif total_components <= 7:
                flow_complexity = "moderate"
                user_experience = "multi-step user interactions"
            else:
                flow_complexity = "complex"
                user_experience = "complex user journey with multiple touchpoints"
            
            return {
                'context': f"User flow analysis shows {flow_complexity} interaction patterns across {total_components} components with {len(external_services)} external dependencies.",
                'key_insights': f"System supports {user_experience} with {arch_style} architecture enabling {'independent user paths' if arch_style == 'microservices' else 'unified user experience'}.",
                'business_impact': f"User flow complexity affects {'user adoption and training requirements' if flow_complexity == 'complex' else 'user satisfaction and support costs'}.",
                'recommendations': f"{'Simplify user paths and reduce friction points' if flow_complexity == 'complex' else 'Maintain current user experience while monitoring usage patterns'}.",
                'technical_details': f"Flow complexity: {flow_complexity}. Components: {total_components}. External dependencies: {len(external_services)}. Architecture supports {'distributed user flows' if arch_style == 'microservices' else 'centralized user experience'}."
            }
        
        elif 'high_level' in diagram_type or 'system_overview' in diagram_type:
            total_components = summary_data.get('total_components', 0)
            languages = summary_data.get('languages', {})
            external_services = summary_data.get('external_services', [])
            datasources = summary_data.get('datasources', [])
            arch_data = intelligence_data.get('architecture_assessment', {})
            arch_style = arch_data.get('style', 'unknown') if isinstance(arch_data, dict) else 'unknown'
            
            # Calculate system complexity
            lang_count = len(languages) if isinstance(languages, dict) else 0
            system_complexity = "high" if (total_components > 5 or lang_count > 3) else "moderate" if total_components > 2 else "low"
            
            # Integration complexity
            integration_points = len(external_services) + len(datasources)
            integration_complexity = "high" if integration_points > 3 else "moderate" if integration_points > 1 else "low"
            
            return {
                'context': f"High-level architecture shows {arch_style} system with {total_components} components, {lang_count} languages, and {integration_points} integration points.",
                'key_insights': f"System demonstrates {system_complexity} architectural complexity with {integration_complexity} integration complexity. Architecture supports {'distributed processing' if arch_style == 'microservices' else 'unified processing'}.",
                'business_impact': f"System complexity affects {'operational overhead and scaling costs' if system_complexity == 'high' else 'maintenance efficiency and team productivity'}.",
                'recommendations': f"{'Consider architectural simplification and service consolidation' if system_complexity == 'high' else 'Maintain current architecture while planning for growth'}.",
                'technical_details': f"Architecture: {arch_style}. Components: {total_components}. Languages: {lang_count}. External integrations: {integration_points}. Complexity assessment: {system_complexity}."
            }
        
        elif 'business_flow' in diagram_type or 'application_flow' in diagram_type:
            total_components = summary_data.get('total_components', 0)
            external_services = summary_data.get('external_services', [])
            arch_data = intelligence_data.get('architecture_assessment', {})
            arch_style = arch_data.get('style', 'unknown') if isinstance(arch_data, dict) else 'unknown'
            
            # Business process complexity
            if total_components <= 3 and len(external_services) <= 2:
                process_complexity = "streamlined"
                business_impact = "efficient process execution"
            elif total_components <= 6 and len(external_services) <= 4:
                process_complexity = "moderate"
                business_impact = "balanced process efficiency"
            else:
                process_complexity = "complex"
                business_impact = "intricate process orchestration"
            
            return {
                'context': f"Business flow analysis reveals {process_complexity} processes across {total_components} components with {len(external_services)} external touchpoints.",
                'key_insights': f"System enables {business_impact} with {arch_style} architecture supporting {'distributed business logic' if arch_style == 'microservices' else 'centralized business processes'}.",
                'business_impact': f"Process complexity affects {'operational efficiency and error handling' if process_complexity == 'complex' else 'process reliability and performance'}.",
                'recommendations': f"{'Optimize process flows and reduce external dependencies' if process_complexity == 'complex' else 'Monitor process performance and plan for scaling'}.",
                'technical_details': f"Process complexity: {process_complexity}. Business components: {total_components}. External touchpoints: {len(external_services)}. Flow architecture: {arch_style}."
            }
        
        # Default fallback for unknown diagram types
        return {
            'context': f"This {diagram_name} provides insights into application characteristics and technical architecture.",
            'key_insights': f"Analysis of {summary_data.get('total_components', 0)} components reveals system patterns and technical dependencies.",
            'business_impact': "Technical insights support strategic planning, risk assessment, and modernization decisions.",
            'recommendations': "Review detailed findings with technical teams to prioritize actions and plan next steps.",
            'technical_details': f"Diagram type: {diagram_name}. Analysis includes component assessment, technology stack evaluation, and architectural patterns."
        }
    
    def _generate_fallback_summary_dict(self) -> Dict[str, str]:
        """Generate fallback summary dictionary when parsing fails"""
        return {
            'context': "Diagram analysis provides insights into application characteristics.",
            'key_insights': "Key findings support technical decision-making and planning.",
            'business_impact': "Analysis supports strategic planning and risk assessment.",
            'recommendations': "Review findings with technical teams for action planning.",
            'technical_details': "Generated from comprehensive application intelligence analysis."
        }