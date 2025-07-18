"""
Criticality Analyzer for Sprint 2 - Business Criticality Assessment
"""

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

from typing import Dict, List, Optional, Tuple
import re
from core.models import (
    SemanticCodeMap, ServiceCriticality, ServiceDependency, 
    SecurityFindings, ComponentInfo, ApiEndpoint, DatabaseInteraction
)

class CriticalityAnalyzer:
    """
    Analyzes business criticality and technical complexity of components
    """
    
    def __init__(self):
        self.component_metrics = {}
        self.security_keywords = {
            "auth": ["login", "authenticate", "authorization", "jwt", "oauth", "token"],
            "payment": ["payment", "billing", "checkout", "transaction", "stripe", "paypal"],
            "user": ["user", "profile", "account", "registration", "signup"],
            "admin": ["admin", "administration", "manage", "control", "dashboard"],
            "data": ["database", "db", "storage", "backup", "migration"],
            "security": ["security", "encryption", "certificate", "ssl", "tls", "crypto"]
        }
    
    def analyze_criticality(
        self,
        semantic_maps: Dict[str, List[SemanticCodeMap]],
        security_findings: Dict[str, SecurityFindings],
        dependencies: List[ServiceDependency],
        dependency_graph
    ) -> List[ServiceCriticality]:
        """
        Analyze business criticality for all components
        
        Args:
            semantic_maps: Dictionary mapping component names to their semantic code maps
            security_findings: Security analysis results
            dependencies: List of service dependencies
            dependency_graph: NetworkX graph of dependencies
            
        Returns:
            List of ServiceCriticality objects
        """
        criticality_assessments = []
        
        for component_name, code_maps in semantic_maps.items():
            assessment = self._analyze_component_criticality(
                component_name, code_maps, security_findings.get(component_name),
                dependencies, dependency_graph
            )
            criticality_assessments.append(assessment)
            
        return criticality_assessments
    
    def _analyze_component_criticality(
        self,
        component_name: str,
        code_maps: List[SemanticCodeMap],
        security_findings: Optional[SecurityFindings],
        dependencies: List[ServiceDependency],
        dependency_graph
    ) -> ServiceCriticality:
        """Analyze criticality for a single component"""
        
        # Calculate individual scores
        business_score = self._calculate_business_criticality(component_name, code_maps)
        technical_score = self._calculate_technical_complexity(code_maps)
        user_impact_score = self._calculate_user_impact(component_name, code_maps)
        data_sensitivity_score = self._calculate_data_sensitivity(code_maps, security_findings)
        
        # Calculate graph-based metrics
        graph_score = self._calculate_graph_criticality(component_name, dependency_graph)
        
        # Combine scores with weights
        weights = {
            "business": 0.3,
            "technical": 0.2,
            "user_impact": 0.25,
            "data_sensitivity": 0.15,
            "graph": 0.1
        }
        
        final_score = (
            business_score * weights["business"] +
            technical_score * weights["technical"] +
            user_impact_score * weights["user_impact"] +
            data_sensitivity_score * weights["data_sensitivity"] +
            graph_score * weights["graph"]
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            component_name, business_score, technical_score, 
            user_impact_score, data_sensitivity_score, graph_score
        )
        
        return ServiceCriticality(
            component_name=component_name,
            business_criticality=self._score_to_level(business_score),
            technical_complexity=self._score_to_level(technical_score),
            user_impact=self._score_to_level(user_impact_score),
            data_sensitivity=self._score_to_level(data_sensitivity_score),
            reasoning=reasoning,
            score=final_score
        )
    
    def _calculate_business_criticality(self, component_name: str, code_maps: List[SemanticCodeMap]) -> float:
        """Calculate business criticality score (0.0 to 1.0)"""
        score = 0.0
        
        # Check component name for business-critical keywords
        name_lower = component_name.lower()
        for category, keywords in self.security_keywords.items():
            for keyword in keywords:
                if keyword in name_lower:
                    if category == "payment":
                        score += 0.4
                    elif category == "auth":
                        score += 0.3
                    elif category == "user":
                        score += 0.2
                    elif category == "admin":
                        score += 0.3
                    else:
                        score += 0.1
        
        # Check API endpoints for business-critical patterns
        for code_map in code_maps:
            for endpoint in code_map.api_endpoints:
                path_lower = endpoint.path.lower()
                for category, keywords in self.security_keywords.items():
                    for keyword in keywords:
                        if keyword in path_lower:
                            if category == "payment":
                                score += 0.2
                            elif category == "auth":
                                score += 0.15
                            elif category == "admin":
                                score += 0.15
                            else:
                                score += 0.05
        
        # Check for database operations (data manipulation is business-critical)
        total_db_ops = sum(len(cm.database_interactions) for cm in code_maps)
        if total_db_ops > 0:
            score += min(total_db_ops * 0.05, 0.3)
        
        return min(score, 1.0)
    
    def _calculate_technical_complexity(self, code_maps: List[SemanticCodeMap]) -> float:
        """Calculate technical complexity score (0.0 to 1.0)"""
        score = 0.0
        
        # File count complexity
        file_count = len(code_maps)
        score += min(file_count * 0.02, 0.2)
        
        # Function/class count complexity
        total_functions = sum(len(cm.functions) for cm in code_maps)
        total_classes = sum(len(cm.classes) for cm in code_maps)
        score += min((total_functions + total_classes) * 0.01, 0.3)
        
        # API endpoint complexity
        total_endpoints = sum(len(cm.api_endpoints) for cm in code_maps)
        score += min(total_endpoints * 0.05, 0.25)
        
        # Database operation complexity
        total_db_ops = sum(len(cm.database_interactions) for cm in code_maps)
        score += min(total_db_ops * 0.02, 0.15)
        
        # HTTP call complexity (external dependencies)
        total_http_calls = sum(len(cm.outbound_http_calls) for cm in code_maps)
        score += min(total_http_calls * 0.03, 0.1)
        
        return min(score, 1.0)
    
    def _calculate_user_impact(self, component_name: str, code_maps: List[SemanticCodeMap]) -> float:
        """Calculate user impact score (0.0 to 1.0)"""
        score = 0.0
        
        # User-facing component indicators
        name_lower = component_name.lower()
        user_facing_keywords = ["api", "web", "frontend", "ui", "service", "gateway"]
        for keyword in user_facing_keywords:
            if keyword in name_lower:
                score += 0.2
        
        # API endpoints indicate user interaction
        total_endpoints = sum(len(cm.api_endpoints) for cm in code_maps)
        if total_endpoints > 0:
            score += 0.4
            
        # Check for user-specific endpoints
        for code_map in code_maps:
            for endpoint in code_map.api_endpoints:
                path_lower = endpoint.path.lower()
                if any(keyword in path_lower for keyword in ["user", "profile", "account"]):
                    score += 0.1
                if any(method in endpoint.methods for method in ["GET"]):
                    score += 0.05  # Read operations impact users
                if any(method in endpoint.methods for method in ["POST", "PUT", "DELETE"]):
                    score += 0.1  # Write operations have higher impact
        
        # Database operations affecting user data
        for code_map in code_maps:
            for db_op in code_map.database_interactions:
                if db_op.table and any(keyword in db_op.table.lower() for keyword in ["user", "profile", "account"]):
                    score += 0.05
        
        return min(score, 1.0)
    
    def _calculate_data_sensitivity(self, code_maps: List[SemanticCodeMap], security_findings: Optional[SecurityFindings]) -> float:
        """Calculate data sensitivity score (0.0 to 1.0)"""
        score = 0.0
        
        # Check for sensitive data in database operations
        for code_map in code_maps:
            for db_op in code_map.database_interactions:
                if db_op.table:
                    table_lower = db_op.table.lower()
                    if any(keyword in table_lower for keyword in ["user", "account", "profile"]):
                        score += 0.1
                    if any(keyword in table_lower for keyword in ["payment", "billing", "transaction"]):
                        score += 0.2
                    if any(keyword in table_lower for keyword in ["admin", "credential", "token"]):
                        score += 0.15
        
        # Check security findings
        if security_findings:
            # Authentication indicates sensitive data
            if security_findings.authentication_mechanisms:
                score += 0.2
            
            # Encryption usage indicates sensitive data
            if security_findings.encryption_usage:
                score += 0.15
            
            # Hardcoded secrets are a major sensitivity issue
            if security_findings.hardcoded_secrets:
                score += 0.3
        
        # Check for sensitive API endpoints
        for code_map in code_maps:
            for endpoint in code_map.api_endpoints:
                path_lower = endpoint.path.lower()
                if any(keyword in path_lower for keyword in ["auth", "login", "token"]):
                    score += 0.1
                if any(keyword in path_lower for keyword in ["payment", "billing"]):
                    score += 0.2
                if any(keyword in path_lower for keyword in ["admin", "manage"]):
                    score += 0.15
        
        return min(score, 1.0)
    
    def _calculate_graph_criticality(self, component_name: str, dependency_graph) -> float:
        """Calculate criticality based on graph position"""
        if not HAS_NETWORKX or not dependency_graph or component_name not in dependency_graph:
            return 0.0
        
        score = 0.0
        
        # In-degree: components that many others depend on are critical
        in_degree = dependency_graph.in_degree(component_name)
        score += min(in_degree * 0.1, 0.4)
        
        # Out-degree: components that depend on many others are complex
        out_degree = dependency_graph.out_degree(component_name)
        score += min(out_degree * 0.05, 0.2)
        
        # Betweenness centrality: components that bridge others are critical
        try:
            betweenness = nx.betweenness_centrality(dependency_graph)[component_name]
            score += betweenness * 0.4
        except:
            pass
        
        return min(score, 1.0)
    
    def _score_to_level(self, score: float) -> str:
        """Convert numeric score to level string"""
        if score >= 0.8:
            return "critical"
        elif score >= 0.6:
            return "high"
        elif score >= 0.4:
            return "medium"
        else:
            return "low"
    
    def _generate_reasoning(
        self, 
        component_name: str, 
        business_score: float, 
        technical_score: float,
        user_impact_score: float, 
        data_sensitivity_score: float, 
        graph_score: float
    ) -> str:
        """Generate human-readable reasoning for the criticality assessment"""
        reasons = []
        
        # Business criticality reasons
        if business_score >= 0.6:
            reasons.append("Contains business-critical functionality")
        elif business_score >= 0.4:
            reasons.append("Supports important business operations")
        
        # Technical complexity reasons
        if technical_score >= 0.7:
            reasons.append("High technical complexity with many components")
        elif technical_score >= 0.5:
            reasons.append("Moderate technical complexity")
        
        # User impact reasons
        if user_impact_score >= 0.6:
            reasons.append("High user impact with direct user interaction")
        elif user_impact_score >= 0.4:
            reasons.append("Moderate user impact")
        
        # Data sensitivity reasons
        if data_sensitivity_score >= 0.6:
            reasons.append("Handles sensitive data requiring protection")
        elif data_sensitivity_score >= 0.4:
            reasons.append("Processes moderately sensitive information")
        
        # Graph criticality reasons
        if graph_score >= 0.5:
            reasons.append("Central role in system architecture")
        elif graph_score >= 0.3:
            reasons.append("Important connections to other components")
        
        if not reasons:
            reasons.append("Standard component with typical criticality")
        
        return "; ".join(reasons)
    
    def get_criticality_distribution(self, assessments: List[ServiceCriticality]) -> Dict[str, int]:
        """Get distribution of criticality levels"""
        distribution = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for assessment in assessments:
            level = self._score_to_level(assessment.score)
            distribution[level] += 1
            
        return distribution
    
    def get_top_critical_components(self, assessments: List[ServiceCriticality], limit: int = 5) -> List[ServiceCriticality]:
        """Get top N most critical components"""
        sorted_assessments = sorted(assessments, key=lambda x: x.score, reverse=True)
        return sorted_assessments[:limit]
    
    def generate_criticality_insights(self, assessments: List[ServiceCriticality]) -> List[str]:
        """Generate insights about criticality patterns"""
        insights = []
        
        if not assessments:
            return ["No components analyzed for criticality"]
        
        # Overall distribution
        distribution = self.get_criticality_distribution(assessments)
        total = len(assessments)
        
        critical_pct = (distribution["critical"] / total) * 100
        high_pct = (distribution["high"] / total) * 100
        
        insights.append(f"Criticality distribution: {distribution['critical']} critical, {distribution['high']} high, {distribution['medium']} medium, {distribution['low']} low")
        
        if critical_pct > 30:
            insights.append("High percentage of critical components may indicate system complexity")
        
        if critical_pct == 0:
            insights.append("No critical components identified - consider reviewing business impact assessment")
        
        # Top critical components
        top_critical = self.get_top_critical_components(assessments, 3)
        if top_critical:
            top_names = [comp.component_name for comp in top_critical]
            insights.append(f"Most critical components: {', '.join(top_names)}")
        
        # Technical complexity insights
        high_complexity = [a for a in assessments if a.technical_complexity in ["high", "critical"]]
        if len(high_complexity) > len(assessments) * 0.4:
            insights.append("High technical complexity across multiple components may impact migration")
        
        return insights