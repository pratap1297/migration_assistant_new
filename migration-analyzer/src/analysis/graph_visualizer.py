"""
Graph Visualizer for Sprint 2 - Architecture and Dependency Visualization
"""

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False

from typing import Dict, List, Optional, Tuple, Any
import os
from datetime import datetime

from core.models import (
    ServiceDependency, ServiceCriticality, ComponentInfo, RepositoryAnalysis
)

class GraphVisualizer:
    """
    Creates visualizations for dependency graphs and architecture diagrams
    """
    
    def __init__(self, output_dir: str = "visualizations"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Color schemes
        self.criticality_colors = {
            "critical": "#FF4444",
            "high": "#FF8800", 
            "medium": "#FFDD00",
            "low": "#88DD88"
        }
        
        self.dependency_colors = {
            "http": "#4444FF",
            "database": "#44FF44",
            "internal": "#FF44FF",
            "queue": "#44FFFF"
        }
        
        # Style settings
        if HAS_MATPLOTLIB:
            plt.style.use('default')
        
    def create_dependency_graph(
        self,
        dependencies: List[ServiceDependency],
        criticality_assessments: List[ServiceCriticality],
        title: str = "Service Dependency Graph",
        output_filename: Optional[str] = None
    ) -> str:
        """
        Create a dependency graph visualization
        
        Args:
            dependencies: List of service dependencies
            criticality_assessments: List of criticality assessments
            title: Graph title
            output_filename: Custom output filename
            
        Returns:
            Path to generated visualization file
        """
        if not HAS_MATPLOTLIB or not HAS_NETWORKX:
            # Create a simple text file instead
            if output_filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"dependency_graph_{timestamp}.txt"
            
            output_path = os.path.join(self.output_dir, output_filename)
            with open(output_path, 'w') as f:
                f.write(f"# {title}\n\n")
                f.write("Visualization libraries not available. Dependencies:\n")
                for dep in dependencies:
                    f.write(f"- {dep.source_component} -> {dep.target_component} ({dep.dependency_type})\n")
            return output_path
        
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"dependency_graph_{timestamp}.png"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Create NetworkX graph
        G = nx.DiGraph()
        
        # Add nodes and edges
        for dep in dependencies:
            G.add_edge(dep.source_component, dep.target_component, 
                      dep_type=dep.dependency_type, 
                      criticality=dep.criticality)
        
        # Create criticality mapping
        criticality_map = {assess.component_name: assess.business_criticality 
                          for assess in criticality_assessments}
        
        # Create layout
        pos = self._create_layout(G)
        
        # Create figure
        fig, ax = plt.subplots(1, 1, figsize=(16, 12))
        
        # Draw nodes
        node_colors = []
        node_sizes = []
        
        for node in G.nodes():
            criticality = criticality_map.get(node, "low")
            node_colors.append(self.criticality_colors.get(criticality, "#CCCCCC"))
            
            # Size based on in-degree (how many depend on this)
            in_degree = G.in_degree(node)
            node_sizes.append(max(300, min(1000, 300 + in_degree * 200)))
        
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, 
                              node_size=node_sizes, alpha=0.8, ax=ax)
        
        # Draw edges by type
        edge_types = set(nx.get_edge_attributes(G, 'dep_type').values())
        
        for edge_type in edge_types:
            edges = [(u, v) for u, v, d in G.edges(data=True) if d['dep_type'] == edge_type]
            if edges:
                nx.draw_networkx_edges(G, pos, edgelist=edges,
                                     edge_color=self.dependency_colors.get(edge_type, "#666666"),
                                     arrows=True, arrowsize=20, 
                                     arrowstyle='->', width=2, alpha=0.7, ax=ax)
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', ax=ax)
        
        # Add title and legend
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        # Criticality legend
        criticality_legend = []
        for level, color in self.criticality_colors.items():
            criticality_legend.append(patches.Patch(color=color, label=f"{level.title()} Criticality"))
        
        # Dependency type legend
        dependency_legend = []
        for dep_type, color in self.dependency_colors.items():
            if dep_type in edge_types:
                dependency_legend.append(patches.Patch(color=color, label=f"{dep_type.title()} Dependency"))
        
        # Create legends
        legend1 = ax.legend(handles=criticality_legend, loc='upper left', title="Component Criticality")
        legend2 = ax.legend(handles=dependency_legend, loc='upper right', title="Dependency Types")
        ax.add_artist(legend1)  # Add first legend back
        
        ax.axis('off')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def create_architecture_overview(
        self,
        analysis: RepositoryAnalysis,
        title: str = "System Architecture Overview",
        output_filename: Optional[str] = None
    ) -> str:
        """
        Create an architecture overview diagram
        
        Args:
            analysis: Complete repository analysis
            title: Diagram title
            output_filename: Custom output filename
            
        Returns:
            Path to generated visualization file
        """
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"architecture_overview_{timestamp}.png"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
        fig.suptitle(title, fontsize=18, fontweight='bold')
        
        # 1. Component metrics
        self._create_component_metrics_chart(analysis.components, ax1)
        
        # 2. Criticality distribution
        self._create_criticality_distribution_chart(analysis.criticality_assessments, ax2)
        
        # 3. Dependency types
        self._create_dependency_types_chart(analysis.dependencies, ax3)
        
        # 4. Language distribution
        self._create_language_distribution_chart(analysis.components, ax4)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def create_criticality_heatmap(
        self,
        criticality_assessments: List[ServiceCriticality],
        title: str = "Component Criticality Heatmap",
        output_filename: Optional[str] = None
    ) -> str:
        """
        Create a criticality heatmap visualization
        
        Args:
            criticality_assessments: List of criticality assessments
            title: Heatmap title
            output_filename: Custom output filename
            
        Returns:
            Path to generated visualization file
        """
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"criticality_heatmap_{timestamp}.png"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        if not criticality_assessments:
            # Create empty plot
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, "No criticality assessments available", 
                   ha='center', va='center', fontsize=16)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            plt.title(title, fontsize=16, fontweight='bold')
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            return output_path
        
        # Prepare data
        components = [assess.component_name for assess in criticality_assessments]
        dimensions = ["Business\\nCriticality", "Technical\\nComplexity", "User\\nImpact", "Data\\nSensitivity"]
        
        # Convert levels to numeric scores
        level_scores = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        
        data = []
        for assess in criticality_assessments:
            row = [
                level_scores.get(assess.business_criticality, 1),
                level_scores.get(assess.technical_complexity, 1),
                level_scores.get(assess.user_impact, 1),
                level_scores.get(assess.data_sensitivity, 1)
            ]
            data.append(row)
        
        data = np.array(data)
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(12, max(8, len(components) * 0.5)))
        
        im = ax.imshow(data, cmap='RdYlGn_r', aspect='auto', vmin=1, vmax=4)
        
        # Set ticks and labels
        ax.set_xticks(range(len(dimensions)))
        ax.set_xticklabels(dimensions)
        ax.set_yticks(range(len(components)))
        ax.set_yticklabels(components)
        
        # Rotate x-axis labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        # Add text annotations
        for i in range(len(components)):
            for j in range(len(dimensions)):
                score = data[i, j]
                level = {1: "Low", 2: "Medium", 3: "High", 4: "Critical"}[score]
                ax.text(j, i, level, ha="center", va="center", color="white" if score > 2 else "black")
        
        # Add colorbar
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.set_ylabel("Criticality Level", rotation=-90, va="bottom")
        cbar.set_ticks([1, 2, 3, 4])
        cbar.set_ticklabels(["Low", "Medium", "High", "Critical"])
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def create_dependency_matrix(
        self,
        dependencies: List[ServiceDependency],
        title: str = "Dependency Matrix",
        output_filename: Optional[str] = None
    ) -> str:
        """
        Create a dependency matrix visualization
        
        Args:
            dependencies: List of service dependencies
            title: Matrix title
            output_filename: Custom output filename
            
        Returns:
            Path to generated visualization file
        """
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"dependency_matrix_{timestamp}.png"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        # Get all unique components
        components = set()
        for dep in dependencies:
            components.add(dep.source_component)
            components.add(dep.target_component)
        
        components = sorted(list(components))
        
        if not components:
            # Create empty plot
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, "No dependencies to visualize", 
                   ha='center', va='center', fontsize=16)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            plt.title(title, fontsize=16, fontweight='bold')
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            return output_path
        
        # Create matrix
        matrix = np.zeros((len(components), len(components)))
        
        for dep in dependencies:
            source_idx = components.index(dep.source_component)
            target_idx = components.index(dep.target_component)
            matrix[source_idx][target_idx] = 1
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(max(10, len(components) * 0.6), max(10, len(components) * 0.6)))
        
        im = ax.imshow(matrix, cmap='Blues', aspect='auto')
        
        # Set ticks and labels
        ax.set_xticks(range(len(components)))
        ax.set_xticklabels(components, rotation=45, ha='right')
        ax.set_yticks(range(len(components)))
        ax.set_yticklabels(components)
        
        # Add grid
        ax.set_xticks(np.arange(len(components) + 1) - 0.5, minor=True)
        ax.set_yticks(np.arange(len(components) + 1) - 0.5, minor=True)
        ax.grid(which="minor", color="gray", linestyle='-', linewidth=0.5)
        
        # Add title
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel("Target Component", fontsize=12)
        ax.set_ylabel("Source Component", fontsize=12)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def _create_layout(self, G) -> Dict[str, Tuple[float, float]]:
        """Create an optimal layout for the graph"""
        try:
            # Try hierarchical layout first
            pos = nx.spring_layout(G, k=3, iterations=50)
            
            # If the graph is small, use circular layout
            if len(G.nodes()) <= 6:
                pos = nx.circular_layout(G)
            # For larger graphs, use spring layout with good spacing
            elif len(G.nodes()) <= 20:
                pos = nx.spring_layout(G, k=2, iterations=100)
            else:
                pos = nx.spring_layout(G, k=1, iterations=50)
                
        except:
            # Fallback to random layout
            pos = nx.random_layout(G)
        
        return pos
    
    def _create_component_metrics_chart(self, components: List[ComponentInfo], ax):
        """Create component metrics chart"""
        if not components:
            ax.text(0.5, 0.5, "No components to display", ha='center', va='center')
            ax.set_title("Component Metrics")
            return
        
        # Sort by lines of code
        sorted_components = sorted(components, key=lambda x: x.lines_of_code, reverse=True)[:10]
        
        names = [comp.name for comp in sorted_components]
        loc = [comp.lines_of_code for comp in sorted_components]
        
        bars = ax.barh(names, loc, color='skyblue')
        ax.set_xlabel("Lines of Code")
        ax.set_title("Top Components by Size")
        
        # Add value labels on bars
        for bar, value in zip(bars, loc):
            ax.text(bar.get_width() + max(loc) * 0.01, bar.get_y() + bar.get_height()/2, 
                   f'{value:,}', ha='left', va='center')
    
    def _create_criticality_distribution_chart(self, assessments: List[ServiceCriticality], ax):
        """Create criticality distribution chart"""
        if not assessments:
            ax.text(0.5, 0.5, "No criticality data", ha='center', va='center')
            ax.set_title("Criticality Distribution")
            return
        
        # Count criticality levels
        levels = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for assess in assessments:
            if assess.business_criticality in levels:
                levels[assess.business_criticality] += 1
        
        # Create pie chart
        labels = list(levels.keys())
        sizes = list(levels.values())
        colors = [self.criticality_colors[level] for level in labels]
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
        ax.set_title("Criticality Distribution")
    
    def _create_dependency_types_chart(self, dependencies: List[ServiceDependency], ax):
        """Create dependency types chart"""
        if not dependencies:
            ax.text(0.5, 0.5, "No dependencies to display", ha='center', va='center')
            ax.set_title("Dependency Types")
            return
        
        # Count dependency types
        types = {}
        for dep in dependencies:
            if dep.dependency_type not in types:
                types[dep.dependency_type] = 0
            types[dep.dependency_type] += 1
        
        # Create bar chart
        labels = list(types.keys())
        values = list(types.values())
        colors = [self.dependency_colors.get(label, "#666666") for label in labels]
        
        bars = ax.bar(labels, values, color=colors)
        ax.set_ylabel("Count")
        ax.set_title("Dependency Types")
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values) * 0.01,
                   str(value), ha='center', va='bottom')
    
    def _create_language_distribution_chart(self, components: List[ComponentInfo], ax):
        """Create language distribution chart"""
        if not components:
            ax.text(0.5, 0.5, "No components to display", ha='center', va='center')
            ax.set_title("Language Distribution")
            return
        
        # Count languages
        languages = {}
        for comp in components:
            if comp.language not in languages:
                languages[comp.language] = 0
            languages[comp.language] += 1
        
        # Create pie chart
        labels = list(languages.keys())
        sizes = list(languages.values())
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')
        ax.set_title("Language Distribution")
    
    def create_all_visualizations(self, analysis: RepositoryAnalysis) -> List[str]:
        """
        Create all visualization types for the analysis
        
        Args:
            analysis: Complete repository analysis
            
        Returns:
            List of paths to generated visualization files
        """
        generated_files = []
        
        try:
            # Dependency graph
            dep_graph = self.create_dependency_graph(
                analysis.dependencies,
                analysis.criticality_assessments,
                f"Dependency Graph - {os.path.basename(analysis.repository_url)}"
            )
            generated_files.append(dep_graph)
        except Exception as e:
            print(f"Warning: Could not create dependency graph: {e}")
        
        try:
            # Architecture overview
            arch_overview = self.create_architecture_overview(
                analysis,
                f"Architecture Overview - {os.path.basename(analysis.repository_url)}"
            )
            generated_files.append(arch_overview)
        except Exception as e:
            print(f"Warning: Could not create architecture overview: {e}")
        
        try:
            # Criticality heatmap
            crit_heatmap = self.create_criticality_heatmap(
                analysis.criticality_assessments,
                f"Criticality Heatmap - {os.path.basename(analysis.repository_url)}"
            )
            generated_files.append(crit_heatmap)
        except Exception as e:
            print(f"Warning: Could not create criticality heatmap: {e}")
        
        try:
            # Dependency matrix
            dep_matrix = self.create_dependency_matrix(
                analysis.dependencies,
                f"Dependency Matrix - {os.path.basename(analysis.repository_url)}"
            )
            generated_files.append(dep_matrix)
        except Exception as e:
            print(f"Warning: Could not create dependency matrix: {e}")
        
        return generated_files