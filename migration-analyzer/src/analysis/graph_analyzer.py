"""
Graph Analyzer for Sprint 2 - Dependency Mapping and Architecture Analysis
"""

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

from typing import Dict, List, Tuple, Optional, Set
import re
import os
from urllib.parse import urlparse
from core.models import (
    SemanticCodeMap, ServiceDependency, ComponentInfo, 
    HttpCall, DatabaseInteraction, ApiEndpoint
)

class GraphAnalyzer:
    """
    Analyzes service dependencies and builds graph representations
    """
    
    def __init__(self):
        if HAS_NETWORKX:
            self.dependency_graph = nx.DiGraph()
        else:
            self.dependency_graph = None
        self.component_info = {}
        
    def analyze_dependencies(self, semantic_maps: Dict[str, List[SemanticCodeMap]]) -> List[ServiceDependency]:
        """
        Analyze semantic maps to identify inter-service dependencies
        
        Args:
            semantic_maps: Dictionary mapping component names to their semantic code maps
            
        Returns:
            List of ServiceDependency objects
        """
        dependencies = []
        
        # Create component info
        for component_name, code_maps in semantic_maps.items():
            self.component_info[component_name] = self._create_component_info(
                component_name, code_maps
            )
            
        # Analyze HTTP dependencies
        http_dependencies = self._analyze_http_dependencies(semantic_maps)
        dependencies.extend(http_dependencies)
        
        # Analyze database dependencies  
        db_dependencies = self._analyze_database_dependencies(semantic_maps)
        dependencies.extend(db_dependencies)
        
        # Analyze internal dependencies
        internal_dependencies = self._analyze_internal_dependencies(semantic_maps)
        dependencies.extend(internal_dependencies)
        
        # Build the dependency graph
        self._build_dependency_graph(dependencies)
        
        return dependencies
    
    def _create_component_info(self, component_name: str, code_maps: List[SemanticCodeMap]) -> ComponentInfo:
        """Create ComponentInfo from semantic code maps"""
        files_count = len(code_maps)
        lines_of_code = self._estimate_lines_of_code(code_maps)
        
        api_endpoints_count = sum(len(cm.api_endpoints) for cm in code_maps)
        database_operations_count = sum(len(cm.database_interactions) for cm in code_maps)
        http_calls_count = sum(len(cm.outbound_http_calls) for cm in code_maps)
        
        # Determine primary language
        languages = [cm.language for cm in code_maps]
        primary_language = max(set(languages), key=languages.count) if languages else "unknown"
        
        return ComponentInfo(
            name=component_name,
            path=os.path.dirname(code_maps[0].file_path) if code_maps else "",
            language=primary_language,
            files_count=files_count,
            lines_of_code=lines_of_code,
            api_endpoints_count=api_endpoints_count,
            database_operations_count=database_operations_count,
            http_calls_count=http_calls_count
        )
    
    def _estimate_lines_of_code(self, code_maps: List[SemanticCodeMap]) -> int:
        """Estimate lines of code based on functions and classes"""
        total_lines = 0
        for code_map in code_maps:
            # Estimate based on functions and classes
            function_lines = sum(
                func.end_line - func.start_line + 1 
                for func in code_map.functions
            )
            class_lines = sum(
                cls.end_line - cls.start_line + 1 
                for cls in code_map.classes
            )
            total_lines += max(function_lines, class_lines, 50)  # Minimum 50 lines per file
        return total_lines
    
    def _analyze_http_dependencies(self, semantic_maps: Dict[str, List[SemanticCodeMap]]) -> List[ServiceDependency]:
        """Analyze HTTP calls to identify service dependencies"""
        dependencies = []
        
        for component_name, code_maps in semantic_maps.items():
            for code_map in code_maps:
                for http_call in code_map.outbound_http_calls:
                    target_component = self._identify_target_component(
                        http_call.url, semantic_maps
                    )
                    
                    if target_component and target_component != component_name:
                        dependency = ServiceDependency(
                            source_component=component_name,
                            target_component=target_component,
                            dependency_type="http",
                            endpoint=http_call.url,
                            method=http_call.method,
                            criticality=self._assess_http_criticality(http_call)
                        )
                        dependencies.append(dependency)
                    elif not target_component:
                        # External dependency
                        external_service = self._extract_external_service_name(http_call.url)
                        dependency = ServiceDependency(
                            source_component=component_name,
                            target_component=external_service,
                            dependency_type="http",
                            endpoint=http_call.url,
                            method=http_call.method,
                            criticality="high"  # External dependencies are typically critical
                        )
                        dependencies.append(dependency)
        
        return dependencies
    
    def _analyze_database_dependencies(self, semantic_maps: Dict[str, List[SemanticCodeMap]]) -> List[ServiceDependency]:
        """Analyze database interactions to identify shared data dependencies"""
        dependencies = []
        table_usage = {}  # table_name -> [components using it]
        
        # First pass: collect table usage
        for component_name, code_maps in semantic_maps.items():
            for code_map in code_maps:
                for db_interaction in code_map.database_interactions:
                    table_name = db_interaction.table or "unknown_table"
                    if table_name not in table_usage:
                        table_usage[table_name] = []
                    if component_name not in table_usage[table_name]:
                        table_usage[table_name].append(component_name)
        
        # Second pass: create dependencies for shared tables
        for table_name, components in table_usage.items():
            if len(components) > 1:
                # Create dependencies between components sharing the same table
                for i, source_component in enumerate(components):
                    for target_component in components[i+1:]:
                        dependency = ServiceDependency(
                            source_component=source_component,
                            target_component=target_component,
                            dependency_type="database",
                            endpoint=table_name,
                            method="SHARED_TABLE",
                            criticality="medium"
                        )
                        dependencies.append(dependency)
        
        return dependencies
    
    def _analyze_internal_dependencies(self, semantic_maps: Dict[str, List[SemanticCodeMap]]) -> List[ServiceDependency]:
        """Analyze internal API calls between components"""
        dependencies = []
        
        # Create a mapping of API endpoints to components
        endpoint_to_component = {}
        for component_name, code_maps in semantic_maps.items():
            for code_map in code_maps:
                for endpoint in code_map.api_endpoints:
                    endpoint_to_component[endpoint.path] = component_name
        
        # Look for internal API calls
        for component_name, code_maps in semantic_maps.items():
            for code_map in code_maps:
                for http_call in code_map.outbound_http_calls:
                    if http_call.is_internal:
                        # Extract path from URL
                        path = self._extract_path_from_url(http_call.url)
                        if path in endpoint_to_component:
                            target_component = endpoint_to_component[path]
                            if target_component != component_name:
                                dependency = ServiceDependency(
                                    source_component=component_name,
                                    target_component=target_component,
                                    dependency_type="internal",
                                    endpoint=path,
                                    method=http_call.method,
                                    criticality="medium"
                                )
                                dependencies.append(dependency)
        
        return dependencies
    
    def _identify_target_component(self, url: str, semantic_maps: Dict[str, List[SemanticCodeMap]]) -> Optional[str]:
        """Identify which component serves a given URL"""
        path = self._extract_path_from_url(url)
        
        for component_name, code_maps in semantic_maps.items():
            for code_map in code_maps:
                for endpoint in code_map.api_endpoints:
                    if self._paths_match(path, endpoint.path):
                        return component_name
        
        return None
    
    def _extract_path_from_url(self, url: str) -> str:
        """Extract path from URL"""
        try:
            parsed = urlparse(url)
            return parsed.path
        except:
            return url
    
    def _paths_match(self, request_path: str, endpoint_path: str) -> bool:
        """Check if request path matches endpoint path (with parameter substitution)"""
        # Simple matching - can be enhanced with regex patterns
        if request_path == endpoint_path:
            return True
        
        # Handle parameterized paths like /api/users/{id}
        endpoint_pattern = re.sub(r'\{[^}]+\}', r'[^/]+', endpoint_path)
        endpoint_pattern = f"^{endpoint_pattern}$"
        
        return bool(re.match(endpoint_pattern, request_path))
    
    def _extract_external_service_name(self, url: str) -> str:
        """Extract external service name from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc
            # Extract main domain (remove subdomains)
            domain_parts = domain.split('.')
            if len(domain_parts) >= 2:
                return f"{domain_parts[-2]}.{domain_parts[-1]}"
            return domain
        except:
            return "external-service"
    
    def _assess_http_criticality(self, http_call: HttpCall) -> str:
        """Assess criticality of HTTP call based on method and URL"""
        if http_call.method in ["POST", "PUT", "DELETE"]:
            return "high"
        elif "auth" in http_call.url.lower() or "login" in http_call.url.lower():
            return "critical"
        else:
            return "medium"
    
    def _build_dependency_graph(self, dependencies: List[ServiceDependency]):
        """Build NetworkX graph from dependencies"""
        if not HAS_NETWORKX or self.dependency_graph is None:
            return
            
        self.dependency_graph.clear()
        
        for dependency in dependencies:
            self.dependency_graph.add_edge(
                dependency.source_component,
                dependency.target_component,
                dependency_type=dependency.dependency_type,
                endpoint=dependency.endpoint,
                method=dependency.method,
                criticality=dependency.criticality
            )
    
    def get_dependency_graph(self):
        """Get the dependency graph"""
        return self.dependency_graph
    
    def get_component_info(self) -> Dict[str, ComponentInfo]:
        """Get component information"""
        return self.component_info
    
    def analyze_graph_metrics(self) -> Dict[str, any]:
        """Analyze graph metrics for insights"""
        if not HAS_NETWORKX or not self.dependency_graph:
            return {}
        
        metrics = {
            "node_count": self.dependency_graph.number_of_nodes(),
            "edge_count": self.dependency_graph.number_of_edges(),
            "density": nx.density(self.dependency_graph),
            "is_connected": nx.is_weakly_connected(self.dependency_graph),
            "components": nx.number_weakly_connected_components(self.dependency_graph)
        }
        
        # Calculate centrality metrics
        try:
            metrics["in_degree_centrality"] = nx.in_degree_centrality(self.dependency_graph)
            metrics["out_degree_centrality"] = nx.out_degree_centrality(self.dependency_graph)
            metrics["betweenness_centrality"] = nx.betweenness_centrality(self.dependency_graph)
        except:
            pass
        
        return metrics
    
    def identify_critical_components(self) -> List[str]:
        """Identify components that are critical based on graph analysis"""
        if not HAS_NETWORKX or not self.dependency_graph:
            return []
        
        critical_components = []
        
        # Components with high in-degree (many depend on them)
        in_degrees = dict(self.dependency_graph.in_degree())
        max_in_degree = max(in_degrees.values()) if in_degrees else 0
        
        for component, in_degree in in_degrees.items():
            if in_degree >= max_in_degree * 0.7:  # Top 30% by in-degree
                critical_components.append(component)
        
        # Components that are articulation points (removing them disconnects the graph)
        try:
            undirected_graph = self.dependency_graph.to_undirected()
            articulation_points = list(nx.articulation_points(undirected_graph))
            critical_components.extend(articulation_points)
        except:
            pass
        
        return list(set(critical_components))
    
    def get_dependency_paths(self, source: str, target: str) -> List[List[str]]:
        """Get all paths between two components"""
        if not HAS_NETWORKX or not self.dependency_graph:
            return []
        try:
            return list(nx.all_simple_paths(self.dependency_graph, source, target))
        except:
            return []
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies in the graph"""
        if not HAS_NETWORKX or not self.dependency_graph:
            return []
        try:
            cycles = list(nx.simple_cycles(self.dependency_graph))
            return cycles
        except:
            return []