"""
Enhanced Document Generator for Sprint 2 - AS-IS Documentation and Reports
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

from src.core.models import (
    RepositoryAnalysis, ComponentInfo, ServiceDependency, 
    ServiceCriticality, SecurityFindings, SemanticCodeMap
)

class EnhancedDocumentGenerator:
    """
    Generates comprehensive AS-IS documentation and analysis reports
    """
    
    def __init__(self):
        self.template_dir = "templates"
        self.output_dir = "output"
        
    def generate_as_is_document(
        self, 
        repository_analysis: RepositoryAnalysis,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate comprehensive AS-IS documentation
        
        Args:
            repository_analysis: Complete repository analysis results
            output_path: Optional custom output path
            
        Returns:
            Path to generated document
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"as_is_analysis_{timestamp}.md"
        
        # Generate document content
        content = self._generate_document_content(repository_analysis)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return output_path
    
    def _generate_document_content(self, analysis: RepositoryAnalysis) -> str:
        """Generate the main document content"""
        content = []
        
        # Title and metadata
        content.append(self._generate_title_section(analysis))
        content.append(self._generate_executive_summary(analysis))
        content.append(self._generate_system_overview(analysis))
        content.append(self._generate_component_analysis(analysis))
        content.append(self._generate_dependency_analysis(analysis))
        content.append(self._generate_criticality_analysis(analysis))
        content.append(self._generate_security_analysis(analysis))
        content.append(self._generate_architecture_insights(analysis))
        content.append(self._generate_migration_recommendations(analysis))
        content.append(self._generate_appendices(analysis))
        
        return "\\n\\n".join(content)
    
    def _generate_title_section(self, analysis: RepositoryAnalysis) -> str:
        """Generate title section with metadata"""
        return f"""# AS-IS System Analysis Report

## System Information
- **Repository**: {analysis.repository_url}
- **Analysis Date**: {analysis.analysis_date.strftime('%Y-%m-%d %H:%M:%S')}
- **Components Analyzed**: {len(analysis.components)}
- **Dependencies Identified**: {len(analysis.dependencies)}
- **Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---"""
    
    def _generate_executive_summary(self, analysis: RepositoryAnalysis) -> str:
        """Generate executive summary"""
        content = ["## Executive Summary"]
        
        # System metrics
        total_files = sum(comp.files_count for comp in analysis.components)
        total_loc = sum(comp.lines_of_code for comp in analysis.components)
        total_endpoints = sum(comp.api_endpoints_count for comp in analysis.components)
        
        content.append(f"""
### System Metrics
- **Total Components**: {len(analysis.components)}
- **Total Files**: {total_files}
- **Total Lines of Code**: {total_loc:,}
- **Total API Endpoints**: {total_endpoints}
- **External Dependencies**: {len([d for d in analysis.dependencies if d.dependency_type == 'http'])}
""")
        
        # Criticality overview
        if analysis.criticality_assessments:
            critical_count = len([c for c in analysis.criticality_assessments if c.business_criticality == 'critical'])
            high_count = len([c for c in analysis.criticality_assessments if c.business_criticality == 'high'])
            
            content.append(f"""
### Criticality Assessment
- **Critical Components**: {critical_count}
- **High Priority Components**: {high_count}
- **Standard Components**: {len(analysis.criticality_assessments) - critical_count - high_count}
""")
        
        # Key findings
        content.append("### Key Findings")
        if analysis.architecture_insights:
            for insight in analysis.architecture_insights[:3]:
                content.append(f"- {insight}")
        
        return "\\n".join(content)
    
    def _generate_system_overview(self, analysis: RepositoryAnalysis) -> str:
        """Generate system overview section"""
        content = ["## System Overview"]
        
        # Component distribution
        language_dist = {}
        for comp in analysis.components:
            if comp.language not in language_dist:
                language_dist[comp.language] = 0
            language_dist[comp.language] += 1
            
        content.append("### Language Distribution")
        for language, count in sorted(language_dist.items()):
            content.append(f"- **{language.title()}**: {count} components")
        
        # Architecture pattern detection
        content.append("\\n### Architecture Patterns")
        patterns = self._detect_architecture_patterns(analysis)
        for pattern in patterns:
            content.append(f"- {pattern}")
        
        return "\\n".join(content)
    
    def _generate_component_analysis(self, analysis: RepositoryAnalysis) -> str:
        """Generate detailed component analysis"""
        content = ["## Component Analysis"]
        
        # Sort components by criticality
        sorted_components = sorted(
            analysis.components,
            key=lambda c: self._get_component_criticality_score(c, analysis.criticality_assessments),
            reverse=True
        )
        
        for component in sorted_components:
            content.append(f"### {component.name}")
            
            # Basic info
            content.append(f"""
- **Language**: {component.language}
- **Files**: {component.files_count}
- **Lines of Code**: {component.lines_of_code:,}
- **API Endpoints**: {component.api_endpoints_count}
- **Database Operations**: {component.database_operations_count}
- **External HTTP Calls**: {component.http_calls_count}
""")
            
            # Criticality information
            criticality = self._get_component_criticality(component.name, analysis.criticality_assessments)
            if criticality:
                content.append(f"""
**Criticality Assessment**:
- **Business Criticality**: {criticality.business_criticality}
- **Technical Complexity**: {criticality.technical_complexity}
- **User Impact**: {criticality.user_impact}
- **Data Sensitivity**: {criticality.data_sensitivity}
- **Score**: {criticality.score:.2f}
- **Reasoning**: {criticality.reasoning}
""")
            
            # Dependencies
            incoming_deps = [d for d in analysis.dependencies if d.target_component == component.name]
            outgoing_deps = [d for d in analysis.dependencies if d.source_component == component.name]
            
            if incoming_deps:
                content.append("\\n**Incoming Dependencies**:")
                for dep in incoming_deps[:5]:  # Show top 5
                    content.append(f"- {dep.source_component} → {dep.dependency_type} → {dep.endpoint or 'N/A'}")
            
            if outgoing_deps:
                content.append("\\n**Outgoing Dependencies**:")
                for dep in outgoing_deps[:5]:  # Show top 5
                    content.append(f"- {dep.target_component} ← {dep.dependency_type} ← {dep.endpoint or 'N/A'}")
            
            # API endpoints
            if component.api_endpoints_count > 0:
                semantic_maps = analysis.semantic_maps.get(component.name, [])
                endpoints = []
                for code_map in semantic_maps:
                    endpoints.extend(code_map.api_endpoints)
                
                if endpoints:
                    content.append("\\n**API Endpoints**:")
                    for endpoint in endpoints[:10]:  # Show top 10
                        methods = ", ".join(endpoint.methods)
                        content.append(f"- `{methods}` {endpoint.path}")
        
        return "\\n".join(content)
    
    def _generate_dependency_analysis(self, analysis: RepositoryAnalysis) -> str:
        """Generate dependency analysis section"""
        content = ["## Dependency Analysis"]
        
        # Dependency types
        dep_types = {}
        for dep in analysis.dependencies:
            if dep.dependency_type not in dep_types:
                dep_types[dep.dependency_type] = 0
            dep_types[dep.dependency_type] += 1
        
        content.append("### Dependency Types")
        for dep_type, count in sorted(dep_types.items()):
            content.append(f"- **{dep_type.title()}**: {count}")
        
        # Critical dependencies
        critical_deps = [d for d in analysis.dependencies if d.criticality in ['high', 'critical']]
        if critical_deps:
            content.append("\\n### Critical Dependencies")
            for dep in critical_deps[:10]:  # Show top 10
                content.append(f"- **{dep.source_component}** → **{dep.target_component}** ({dep.dependency_type})")
        
        # External dependencies
        external_deps = [d for d in analysis.dependencies if d.dependency_type == 'http' and '.' in d.target_component]
        if external_deps:
            content.append("\\n### External Dependencies")
            external_services = set(d.target_component for d in external_deps)
            for service in sorted(external_services):
                count = len([d for d in external_deps if d.target_component == service])
                content.append(f"- **{service}**: {count} connections")
        
        # Circular dependencies
        content.append("\\n### Circular Dependencies")
        circular_deps = self._detect_circular_dependencies(analysis.dependencies)
        if circular_deps:
            for cycle in circular_deps[:5]:  # Show top 5
                content.append(f"- {' → '.join(cycle + [cycle[0]])}")
        else:
            content.append("- No circular dependencies detected")
        
        return "\\n".join(content)
    
    def _generate_criticality_analysis(self, analysis: RepositoryAnalysis) -> str:
        """Generate criticality analysis section"""
        content = ["## Criticality Analysis"]
        
        if not analysis.criticality_assessments:
            content.append("No criticality assessments available.")
            return "\\n".join(content)
        
        # Criticality distribution
        distribution = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for assessment in analysis.criticality_assessments:
            level = assessment.business_criticality
            if level in distribution:
                distribution[level] += 1
        
        content.append("### Criticality Distribution")
        for level, count in distribution.items():
            percentage = (count / len(analysis.criticality_assessments)) * 100
            content.append(f"- **{level.title()}**: {count} ({percentage:.1f}%)")
        
        # Top critical components
        top_critical = sorted(
            analysis.criticality_assessments,
            key=lambda x: x.score,
            reverse=True
        )[:5]
        
        content.append("\\n### Top Critical Components")
        for i, assessment in enumerate(top_critical, 1):
            content.append(f"{i}. **{assessment.component_name}** (Score: {assessment.score:.2f})")
            content.append(f"   - {assessment.reasoning}")
        
        return "\\n".join(content)
    
    def _generate_security_analysis(self, analysis: RepositoryAnalysis) -> str:
        """Generate security analysis section"""
        content = ["## Security Analysis"]
        
        if not analysis.security_findings:
            content.append("No security findings available.")
            return "\\n".join(content)
        
        # Security overview
        auth_mechanisms = set()
        encryption_methods = set()
        total_vulnerabilities = 0
        total_secrets = 0
        
        for findings in analysis.security_findings.values():
            auth_mechanisms.update(findings.authentication_mechanisms)
            encryption_methods.update(findings.encryption_usage)
            total_vulnerabilities += len(findings.potential_vulnerabilities)
            total_secrets += len(findings.hardcoded_secrets)
        
        content.append("### Security Overview")
        content.append(f"- **Authentication Mechanisms**: {len(auth_mechanisms)}")
        content.append(f"- **Encryption Methods**: {len(encryption_methods)}")
        content.append(f"- **Potential Vulnerabilities**: {total_vulnerabilities}")
        content.append(f"- **Hardcoded Secrets**: {total_secrets}")
        
        # Authentication mechanisms
        if auth_mechanisms:
            content.append("\\n### Authentication Mechanisms")
            for mechanism in sorted(auth_mechanisms):
                content.append(f"- {mechanism}")
        
        # Encryption usage
        if encryption_methods:
            content.append("\\n### Encryption Usage")
            for method in sorted(encryption_methods):
                content.append(f"- {method}")
        
        # Security risks
        if total_vulnerabilities > 0 or total_secrets > 0:
            content.append("\\n### Security Risks")
            if total_secrets > 0:
                content.append("- **⚠️ Hardcoded secrets detected** - Review and migrate to secure configuration")
            if total_vulnerabilities > 0:
                content.append("- **⚠️ Potential vulnerabilities identified** - Requires security review")
        
        return "\\n".join(content)
    
    def _generate_architecture_insights(self, analysis: RepositoryAnalysis) -> str:
        """Generate architecture insights section"""
        content = ["## Architecture Insights"]
        
        if analysis.architecture_insights:
            for insight in analysis.architecture_insights:
                content.append(f"- {insight}")
        else:
            content.append("No specific architecture insights available.")
        
        return "\\n".join(content)
    
    def _generate_migration_recommendations(self, analysis: RepositoryAnalysis) -> str:
        """Generate migration recommendations section"""
        content = ["## Migration Recommendations"]
        
        if analysis.migration_recommendations:
            for recommendation in analysis.migration_recommendations:
                content.append(f"- {recommendation}")
        else:
            # Generate basic recommendations
            content.append("### General Recommendations")
            content.append("- Prioritize migration of critical components first")
            content.append("- Address circular dependencies before migration")
            content.append("- Implement proper authentication and authorization")
            content.append("- Review and secure hardcoded secrets")
        
        return "\\n".join(content)
    
    def _generate_appendices(self, analysis: RepositoryAnalysis) -> str:
        """Generate appendices section"""
        content = ["## Appendices"]
        
        # Appendix A: Component Details
        content.append("### Appendix A: Component Details")
        content.append("| Component | Language | Files | LOC | Endpoints | DB Ops |")
        content.append("|-----------|----------|-------|-----|-----------|---------|")
        
        for comp in sorted(analysis.components, key=lambda x: x.name):
            content.append(f"| {comp.name} | {comp.language} | {comp.files_count} | {comp.lines_of_code:,} | {comp.api_endpoints_count} | {comp.database_operations_count} |")
        
        # Appendix B: Dependency Matrix
        content.append("\\n### Appendix B: Dependency Matrix")
        content.append("| Source | Target | Type | Endpoint |")
        content.append("|--------|--------|------|----------|")
        
        for dep in sorted(analysis.dependencies, key=lambda x: (x.source_component, x.target_component)):
            endpoint = dep.endpoint or "N/A"
            content.append(f"| {dep.source_component} | {dep.target_component} | {dep.dependency_type} | {endpoint} |")
        
        return "\\n".join(content)
    
    def generate_json_report(self, analysis: RepositoryAnalysis, output_path: Optional[str] = None) -> str:
        """Generate JSON report for programmatic use"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"sprint2_analysis_{timestamp}.json"
        
        # Convert to serializable format
        report_data = {
            "metadata": {
                "repository_url": analysis.repository_url,
                "analysis_date": analysis.analysis_date.isoformat(),
                "report_generated": datetime.now().isoformat()
            },
            "components": [self._component_to_dict(comp) for comp in analysis.components],
            "dependencies": [self._dependency_to_dict(dep) for dep in analysis.dependencies],
            "criticality_assessments": [self._criticality_to_dict(crit) for crit in analysis.criticality_assessments],
            "security_findings": {name: self._security_to_dict(findings) for name, findings in analysis.security_findings.items()},
            "architecture_insights": analysis.architecture_insights,
            "migration_recommendations": analysis.migration_recommendations
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def _component_to_dict(self, comp: ComponentInfo) -> Dict[str, Any]:
        """Convert ComponentInfo to dictionary"""
        return {
            "name": comp.name,
            "path": comp.path,
            "language": comp.language,
            "files_count": comp.files_count,
            "lines_of_code": comp.lines_of_code,
            "api_endpoints_count": comp.api_endpoints_count,
            "database_operations_count": comp.database_operations_count,
            "http_calls_count": comp.http_calls_count
        }
    
    def _dependency_to_dict(self, dep: ServiceDependency) -> Dict[str, Any]:
        """Convert ServiceDependency to dictionary"""
        return {
            "source_component": dep.source_component,
            "target_component": dep.target_component,
            "dependency_type": dep.dependency_type,
            "endpoint": dep.endpoint,
            "method": dep.method,
            "criticality": dep.criticality
        }
    
    def _criticality_to_dict(self, crit: ServiceCriticality) -> Dict[str, Any]:
        """Convert ServiceCriticality to dictionary"""
        return {
            "component_name": crit.component_name,
            "business_criticality": crit.business_criticality,
            "technical_complexity": crit.technical_complexity,
            "user_impact": crit.user_impact,
            "data_sensitivity": crit.data_sensitivity,
            "reasoning": crit.reasoning,
            "score": crit.score
        }
    
    def _security_to_dict(self, findings: SecurityFindings) -> Dict[str, Any]:
        """Convert SecurityFindings to dictionary"""
        return {
            "component_name": findings.component_name,
            "authentication_mechanisms": findings.authentication_mechanisms,
            "authorization_patterns": findings.authorization_patterns,
            "encryption_usage": findings.encryption_usage,
            "potential_vulnerabilities": findings.potential_vulnerabilities,
            "hardcoded_secrets": findings.hardcoded_secrets
        }
    
    def _detect_architecture_patterns(self, analysis: RepositoryAnalysis) -> List[str]:
        """Detect common architecture patterns"""
        patterns = []
        
        # Microservices pattern
        if len(analysis.components) > 3:
            patterns.append("Microservices architecture with multiple independent components")
        
        # API Gateway pattern
        gateway_components = [c for c in analysis.components if "gateway" in c.name.lower() or "api" in c.name.lower()]
        if gateway_components:
            patterns.append("API Gateway pattern detected")
        
        # Database-per-service pattern
        db_components = [c for c in analysis.components if c.database_operations_count > 0]
        if len(db_components) > 1:
            patterns.append("Database-per-service pattern (multiple components with database access)")
        
        # Service mesh pattern
        high_interconnection = len(analysis.dependencies) > len(analysis.components) * 2
        if high_interconnection:
            patterns.append("High service interconnection suggesting service mesh architecture")
        
        return patterns
    
    def _get_component_criticality_score(self, component: ComponentInfo, assessments: List[ServiceCriticality]) -> float:
        """Get criticality score for a component"""
        for assessment in assessments:
            if assessment.component_name == component.name:
                return assessment.score
        return 0.0
    
    def _get_component_criticality(self, component_name: str, assessments: List[ServiceCriticality]) -> Optional[ServiceCriticality]:
        """Get criticality assessment for a component"""
        for assessment in assessments:
            if assessment.component_name == component_name:
                return assessment
        return None
    
    def _detect_circular_dependencies(self, dependencies: List[ServiceDependency]) -> List[List[str]]:
        """Detect circular dependencies"""
        if not HAS_NETWORKX:
            return []
        
        # Build graph
        graph = nx.DiGraph()
        for dep in dependencies:
            graph.add_edge(dep.source_component, dep.target_component)
        
        # Find cycles
        try:
            cycles = list(nx.simple_cycles(graph))
            return cycles
        except:
            return []