"""
Enhanced Diagram Generator for Professional Word Documents
Supports various diagram types including architecture, network, timeline, and more
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Arrow
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import networkx as nx
from datetime import datetime, timedelta
import seaborn as sns

class EnhancedDiagramGenerator:
    """
    Enhanced diagram generator with support for multiple diagram types
    """
    
    def __init__(self, charts_dir: Path):
        self.charts_dir = charts_dir
        self.charts_dir.mkdir(exist_ok=True)
        
        # Professional color palette with gradients
        self.colors = {
            'primary': '#007bd3',
            'secondary': '#48b0f1', 
            'accent': '#16a085',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'success': '#27ae60',
            'info': '#3498db',
            'light': '#ecf0f1',
            'dark': '#2c3e50'
        }
        
        # Professional gradient colors
        self.professional_colors = {
            'gradient_primary': ['#007bd3', '#005a9e'],
            'gradient_secondary': ['#48b0f1', '#2e86ab'],
            'gradient_accent': ['#16a085', '#0e6251'],
            'gradient_warning': ['#f39c12', '#d68910'],
            'gradient_danger': ['#e74c3c', '#c0392b'],
            'gradient_success': ['#27ae60', '#1e8449'],
            'shadows': '#2c3e50',
            'highlights': '#ffffff',
            'text_primary': '#2c3e50',
            'text_secondary': '#7f8c8d',
            'background': '#f8f9fa',
            'grid': '#e0e0e0'
        }
        
        # Professional typography
        self.fonts = {
            'title': {'family': 'Arial', 'size': 18, 'weight': 'bold'},
            'subtitle': {'family': 'Arial', 'size': 14, 'weight': 'bold'},
            'label': {'family': 'Arial', 'size': 11, 'weight': 'normal'},
            'annotation': {'family': 'Arial', 'size': 9, 'weight': 'italic'}
        }
        
        # Set professional style
        self._setup_professional_style()
        sns.set_palette([self.colors['primary'], self.colors['secondary'], 
                        self.colors['accent'], self.colors['warning'], 
                        self.colors['danger'], self.colors['success']])
    
    def _setup_professional_style(self):
        """Configure matplotlib for professional output"""
        import matplotlib as mpl
        
        # Set default figure parameters
        mpl.rcParams['figure.dpi'] = 300
        mpl.rcParams['savefig.dpi'] = 300
        mpl.rcParams['font.size'] = 10
        mpl.rcParams['axes.labelsize'] = 12
        mpl.rcParams['axes.titlesize'] = 14
        mpl.rcParams['xtick.labelsize'] = 10
        mpl.rcParams['ytick.labelsize'] = 10
        mpl.rcParams['legend.fontsize'] = 10
        mpl.rcParams['figure.titlesize'] = 16
        
        # Grid styling
        mpl.rcParams['axes.grid'] = True
        mpl.rcParams['grid.alpha'] = 0.3
        mpl.rcParams['grid.linestyle'] = '-'
        mpl.rcParams['grid.linewidth'] = 0.5
        
        # Spine styling
        mpl.rcParams['axes.spines.top'] = False
        mpl.rcParams['axes.spines.right'] = False
        
        # Color cycle
        mpl.rcParams['axes.prop_cycle'] = mpl.cycler(
            color=[self.colors['primary'], self.colors['secondary'], 
                   self.colors['accent'], self.colors['warning'], 
                   self.colors['danger'], self.colors['success']]
        )
    
    def _add_gradient_fill(self, ax, x, y, color_start, color_end):
        """Add gradient fill to areas"""
        import matplotlib.colors as mcolors
        
        # Create gradient
        gradient = mcolors.LinearSegmentedColormap.from_list(
            'gradient', [color_start, color_end]
        )
        
        # Apply gradient fill
        z = np.linspace(0, 1, 100)
        im = ax.imshow([z], aspect='auto', cmap=gradient, 
                       extent=[x.min(), x.max(), y.min(), y.max()],
                       alpha=0.7)
        return im
    
    def _add_shadow(self, element, ax, offset_x=0.05, offset_y=-0.05):
        """Add drop shadow to elements"""
        from matplotlib.patches import Shadow
        shadow = Shadow(element, offset_x, offset_y)
        shadow.set_facecolor(self.professional_colors['shadows'])
        shadow.set_alpha(0.3)
        ax.add_patch(shadow)
        return shadow
    
    def _draw_3d_component(self, ax, name, x, y, color, tier='service'):
        """Draw enhanced 3D-style component boxes with professional styling"""
        from matplotlib.patches import FancyBboxPatch, Polygon
        
        # Enhanced 3D effect with multiple shadow layers
        shadow_depths = [0.08, 0.06, 0.04]
        shadow_alphas = [0.3, 0.2, 0.1]
        
        for depth, alpha in zip(shadow_depths, shadow_alphas):
            shadow_points = [
                (x-0.4, y-0.3),
                (x-0.4+depth, y-0.3-depth),
                (x+0.4+depth, y-0.3-depth),
                (x+0.4+depth, y+0.3-depth),
                (x+0.4, y+0.3),
                (x-0.4, y+0.3)
            ]
            shadow = Polygon(shadow_points, facecolor='black', alpha=alpha, zorder=1)
            ax.add_patch(shadow)
        
        # Main box with enhanced styling
        box = FancyBboxPatch((x-0.4, y-0.3), 0.8, 0.6,
                             boxstyle="round,pad=0.05",
                             facecolor=color, edgecolor='white',
                             alpha=0.95, linewidth=3, zorder=3)
        ax.add_patch(box)
        
        # Add inner border for professional look
        inner_box = FancyBboxPatch((x-0.38, y-0.28), 0.76, 0.56,
                                   boxstyle="round,pad=0.04",
                                   facecolor='none', edgecolor='white',
                                   alpha=0.4, linewidth=1, zorder=4)
        ax.add_patch(inner_box)
        
        # Add gradient overlay with tier-based styling
        if tier == 'presentation':
            gradient_color = self.professional_colors['gradient_primary'][0]
        elif tier == 'business':
            gradient_color = self.professional_colors['gradient_secondary'][0]
        else:
            gradient_color = self.professional_colors['gradient_accent'][0]
            
        gradient_box = FancyBboxPatch((x-0.4, y-0.1), 0.8, 0.2,
                                      boxstyle="round,pad=0.05",
                                      facecolor=gradient_color, alpha=0.3, zorder=5)
        ax.add_patch(gradient_box)
        
        # Add component name with text shadow
        ax.text(x+0.002, y-0.002, name, ha='center', va='center',
                fontsize=self.fonts['label']['size'],
                fontweight='bold', color='black', alpha=0.3, zorder=6)
        
        ax.text(x, y, name, ha='center', va='center',
                fontsize=self.fonts['label']['size'],
                fontweight='bold', color='white', zorder=7)
        
        # Add tier indicator
        if tier != 'service':
            tier_text = tier.upper()
            ax.text(x+0.3, y+0.25, tier_text, ha='center', va='center',
                    fontsize=8, fontweight='bold', color=color,
                    bbox=dict(boxstyle="round,pad=0.02", facecolor='white', alpha=0.8))
        
        return box
    
    def _add_watermark(self, fig, text="CONFIDENTIAL"):
        """Add professional watermark to figure"""
        fig.text(0.5, 0.5, text, fontsize=50, color='gray',
                 alpha=0.1, ha='center', va='center', rotation=45,
                 transform=fig.transFigure)
    
    def _get_component_tier(self, component: Dict[str, Any]) -> str:
        """Determine component tier based on its characteristics"""
        files = component.get('files', [])
        language = component.get('language', '').lower()
        
        # Check for web/UI components
        if any(f.endswith(('.html', '.jsx', '.tsx', '.vue', '.angular.js')) for f in files):
            return 'presentation'
        
        # Check for database components
        if any(f.endswith(('.sql', '.db', '.sqlite')) for f in files) or 'database' in language:
            return 'data'
        
        # Check for business logic
        if any(f.endswith(('.service.js', '.service.ts', '.business.py')) for f in files):
            return 'business'
        
        return 'service'
    
    def _calculate_connection_strength(self, comp1: Dict[str, Any], comp2: Dict[str, Any]) -> float:
        """Calculate connection strength between two components"""
        score = 0.0
        
        # Same language increases connection strength
        if comp1.get('language') == comp2.get('language'):
            score += 0.3
        
        # Similar file patterns
        files1 = set(comp1.get('files', []))
        files2 = set(comp2.get('files', []))
        common_patterns = len(files1 & files2)
        if common_patterns > 0:
            score += min(common_patterns * 0.1, 0.4)
        
        # Infrastructure dependencies
        if comp1.get('dockerfile_found') and comp2.get('dockerfile_found'):
            score += 0.2
        
        return min(score, 1.0)
    
    def _add_professional_annotations(self, ax, data):
        """Add data insights and annotations"""
        # Add key metrics box
        textstr = f'Key Metrics:\n'
        textstr += f'• Total Components: {data.get("total_components", 0)}\n'
        textstr += f'• Critical Issues: {data.get("critical_issues", 0)}\n'
        textstr += f'• Last Updated: {datetime.now().strftime("%Y-%m-%d")}'
        
        props = dict(boxstyle='round,pad=0.5', facecolor='lightblue', 
                     alpha=0.8, edgecolor='navy', linewidth=2)
        ax.text(0.95, 0.95, textstr, transform=ax.transAxes, 
                fontsize=10, verticalalignment='top',
                horizontalalignment='right', bbox=props)
    
    def _save_professional_diagram(self, fig, output_path):
        """Save diagram with professional settings"""
        fig.savefig(
            output_path,
            dpi=300,
            bbox_inches='tight',
            pad_inches=0.2,
            facecolor='white',
            edgecolor='none',
            format='png',
            transparent=False,
            metadata={
                'Title': 'Professional System Diagram',
                'Author': 'Application Intelligence Platform',
                'Description': 'Auto-generated technical diagram',
                'Software': 'matplotlib'
            }
        )
        plt.close(fig)
    
    def generate_all_diagrams(self, intelligence_data: Dict[str, Any]) -> List[str]:
        """Generate all applicable diagrams based on intelligence data"""
        generated_diagrams = []
        
        try:
            # 1. Language Distribution (Pie Chart)
            lang_chart = self.create_language_distribution_chart(intelligence_data)
            if lang_chart:
                generated_diagrams.append(lang_chart)
            
            # 2. Component Status (Bar Chart)
            comp_chart = self.create_component_status_chart(intelligence_data)
            if comp_chart:
                generated_diagrams.append(comp_chart)
            
            # 3. Architecture Diagram
            arch_diagram = self.create_architecture_diagram(intelligence_data)
            if arch_diagram:
                generated_diagrams.append(arch_diagram)
            
            # 4. Security Assessment (Radar Chart)
            security_chart = self.create_security_radar_chart(intelligence_data)
            if security_chart:
                generated_diagrams.append(security_chart)
            
            # 5. Vulnerability Timeline
            vuln_timeline = self.create_vulnerability_timeline(intelligence_data)
            if vuln_timeline:
                generated_diagrams.append(vuln_timeline)
            
            # 6. Component Relationship Network
            network_diagram = self.create_component_network_diagram(intelligence_data)
            if network_diagram:
                generated_diagrams.append(network_diagram)
            
            # 7. Technology Stack Visualization
            tech_stack = self.create_technology_stack_diagram(intelligence_data)
            if tech_stack:
                generated_diagrams.append(tech_stack)
            
            # 8. Development Activity Heatmap
            dev_heatmap = self.create_development_activity_heatmap(intelligence_data)
            if dev_heatmap:
                generated_diagrams.append(dev_heatmap)
            
            # 9. Migration Readiness Assessment
            migration_chart = self.create_migration_readiness_chart(intelligence_data)
            if migration_chart:
                generated_diagrams.append(migration_chart)
            
            # 10. Risk Assessment Matrix
            risk_matrix = self.create_risk_assessment_matrix(intelligence_data)
            if risk_matrix:
                generated_diagrams.append(risk_matrix)
            
            # 11. CI/CD Pipeline Visualization
            cicd_pipeline = self.create_cicd_pipeline_diagram(intelligence_data)
            if cicd_pipeline:
                generated_diagrams.append(cicd_pipeline)
            
            # 12. User Flow Diagram
            user_flow = self.create_user_flow_diagram(intelligence_data)
            if user_flow:
                generated_diagrams.append(user_flow)
            
            # 13. High-Level Architecture Overview
            high_level_arch = self.create_high_level_architecture_diagram(intelligence_data)
            if high_level_arch:
                generated_diagrams.append(high_level_arch)
            
            # 14. System Overview Diagram
            system_overview = self.create_system_overview_diagram(intelligence_data)
            if system_overview:
                generated_diagrams.append(system_overview)
            
            print(f"INFO [DIAGRAMS] Generated {len(generated_diagrams)} diagrams")
            return generated_diagrams
            
        except Exception as e:
            print(f"WARNING [DIAGRAMS] Error generating diagrams: {e}")
            return generated_diagrams
    
    def create_language_distribution_chart(self, intelligence_data: Dict[str, Any]) -> Optional[str]:
        """Create language distribution pie chart"""
        try:
            languages = intelligence_data.get('summary', {}).get('languages', [])
            if not languages:
                return None
            
            # Count languages
            lang_counts = {}
            for lang in languages:
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
            
            # Create pie chart
            fig, ax = plt.subplots(figsize=(10, 8))
            colors = list(self.colors.values())[:len(lang_counts)]
            
            wedges, texts, autotexts = ax.pie(
                lang_counts.values(),
                labels=lang_counts.keys(),
                autopct='%1.1f%%',
                colors=colors,
                startangle=90,
                textprops={'fontsize': 12, 'fontweight': 'bold'}
            )
            
            ax.set_title('Programming Language Distribution', 
                        fontsize=16, fontweight='bold', pad=20)
            
            # Add legend
            ax.legend(wedges, lang_counts.keys(), 
                     title="Languages", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            
            plt.tight_layout()
            chart_path = self.charts_dir / "language_distribution.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            print(f"WARNING [DIAGRAMS] Error creating language chart: {e}")
            return None
    
    def create_component_status_chart(self, intelligence_data: Dict[str, Any]) -> Optional[str]:
        """Create component status bar chart"""
        try:
            summary = intelligence_data.get('summary', {})
            
            # Handle datasources safely - it could be an integer or a list
            datasources_data = summary.get('datasources', 0)
            datasources_count = len(datasources_data) if isinstance(datasources_data, list) else datasources_data if isinstance(datasources_data, int) else 0
            
            categories = ['Total Components', 'Containerized', 'With Security Issues', 'Data Sources']
            values = [
                summary.get('total_components', 0),
                summary.get('containerization_status', 0),
                summary.get('security_findings', {}).get('vulnerabilities', 0),
                datasources_count
            ]
            
            fig, ax = plt.subplots(figsize=(12, 8))
            bars = ax.bar(categories, values, 
                         color=[self.colors['primary'], self.colors['success'], 
                               self.colors['danger'], self.colors['info']])
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       f'{value}', ha='center', va='bottom', 
                       fontweight='bold', fontsize=12)
            
            ax.set_title('Component Status Overview', 
                        fontsize=16, fontweight='bold', pad=20)
            ax.set_ylabel('Count', fontsize=12, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            chart_path = self.charts_dir / "component_status.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            print(f"WARNING [DIAGRAMS] Error creating component chart: {e}")
            return None
    
    def create_architecture_diagram(self, intelligence_data: Dict[str, Any]) -> Optional[str]:
        """Create architecture diagram showing component relationships"""
        try:
            components = intelligence_data.get('components', {})
            if not components:
                return None
            
            fig, ax = plt.subplots(figsize=(14, 10))
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 10)
            ax.set_aspect('equal')
            
            # Component positions and connections
            positions = {}
            y_pos = 8
            x_spacing = 2
            
            # Arrange components in layers
            web_components = []
            service_components = []
            data_components = []
            
            for name, comp in components.items():
                comp_type = comp.get('type', 'unknown')
                if 'web' in comp_type or 'frontend' in comp_type:
                    web_components.append(name)
                elif 'database' in comp_type or 'data' in comp_type or 'redis' in name or 'postgres' in name:
                    data_components.append(name)
                else:
                    service_components.append(name)
            
            # Draw web tier
            for i, comp in enumerate(web_components):
                x = 1 + i * x_spacing
                positions[comp] = (x, 8)
                self._draw_component(ax, comp, x, 8, self.colors['primary'], 'Web')
            
            # Draw service tier
            for i, comp in enumerate(service_components):
                x = 1 + i * x_spacing
                positions[comp] = (x, 5)
                self._draw_component(ax, comp, x, 5, self.colors['secondary'], 'Service')
            
            # Draw data tier
            for i, comp in enumerate(data_components):
                x = 1 + i * x_spacing
                positions[comp] = (x, 2)
                self._draw_component(ax, comp, x, 2, self.colors['accent'], 'Data')
            
            # Draw connections
            self._draw_connections(ax, positions, components)
            
            # Add legend
            legend_elements = [
                mpatches.Patch(color=self.colors['primary'], label='Web Tier'),
                mpatches.Patch(color=self.colors['secondary'], label='Service Tier'),
                mpatches.Patch(color=self.colors['accent'], label='Data Tier')
            ]
            ax.legend(handles=legend_elements, loc='upper right')
            
            ax.set_title('Application Architecture Diagram', 
                        fontsize=16, fontweight='bold', pad=20)
            ax.axis('off')
            
            plt.tight_layout()
            chart_path = self.charts_dir / "architecture_diagram.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            print(f"WARNING [DIAGRAMS] Error creating architecture diagram: {e}")
            return None
    
    def create_security_radar_chart(self, intelligence_data: Dict[str, Any]) -> Optional[str]:
        """Create security assessment radar chart"""
        try:
            # Security metrics
            metrics = [
                'Vulnerability Management',
                'Authentication',
                'Authorization', 
                'Data Protection',
                'Network Security',
                'Compliance'
            ]
            
            # Mock scores based on analysis (in real implementation, extract from security_posture)
            vuln_count = intelligence_data.get('summary', {}).get('security_findings', {}).get('vulnerabilities', 0)
            base_score = max(1, 10 - min(vuln_count, 9))  # Inverse relationship with vulnerabilities
            
            scores = [
                base_score,  # Vulnerability Management
                7,  # Authentication
                6,  # Authorization
                5,  # Data Protection
                6,  # Network Security
                4   # Compliance
            ]
            
            # Create radar chart
            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
            
            # Calculate angles for each metric
            angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
            scores += scores[:1]  # Complete the circle
            angles += angles[:1]
            
            # Plot
            ax.plot(angles, scores, 'o-', linewidth=2, color=self.colors['primary'])
            ax.fill(angles, scores, alpha=0.25, color=self.colors['primary'])
            
            # Add labels
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(metrics, fontsize=11)
            ax.set_ylim(0, 10)
            ax.set_yticks([2, 4, 6, 8, 10])
            ax.set_yticklabels(['2', '4', '6', '8', '10'], fontsize=10)
            ax.grid(True)
            
            ax.set_title('Security Assessment Radar', 
                        fontsize=16, fontweight='bold', pad=30)
            
            plt.tight_layout()
            chart_path = self.charts_dir / "security_radar.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            print(f"WARNING [DIAGRAMS] Error creating security radar chart: {e}")
            return None
    
    def create_vulnerability_timeline(self, intelligence_data: Dict[str, Any]) -> Optional[str]:
        """Create vulnerability timeline chart"""
        try:
            vuln_assessment = intelligence_data.get('vulnerability_assessment', {})
            findings = vuln_assessment.get('findings', [])
            
            if not findings:
                return None
            
            # Group findings by severity
            severity_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
            for finding in findings:
                severity = finding.get('severity', 'MEDIUM')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Create timeline-style chart
            fig, ax = plt.subplots(figsize=(12, 6))
            
            severities = list(severity_counts.keys())
            counts = list(severity_counts.values())
            colors = [self.colors['danger'], self.colors['warning'], self.colors['info']]
            
            bars = ax.barh(severities, counts, color=colors)
            
            # Add value labels
            for bar, count in zip(bars, counts):
                width = bar.get_width()
                ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                       f'{count}', ha='left', va='center', 
                       fontweight='bold', fontsize=12)
            
            ax.set_title('Vulnerability Distribution by Severity', 
                        fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Number of Vulnerabilities', fontsize=12, fontweight='bold')
            ax.grid(axis='x', alpha=0.3)
            
            plt.tight_layout()
            chart_path = self.charts_dir / "vulnerability_timeline.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            print(f"WARNING [DIAGRAMS] Error creating vulnerability timeline: {e}")
            return None
    
    def create_component_network_diagram(self, intelligence_data: Dict[str, Any]) -> Optional[str]:
        """Create enhanced component network diagram with 3D styling"""
        try:
            components = intelligence_data.get('components', {})
            if len(components) < 2:
                return None
            
            # Create graph
            G = nx.Graph()
            
            # Add nodes
            for name, comp in components.items():
                G.add_node(name, type=comp.get('type', 'unknown'))
            
            # Add edges based on likely connections
            comp_names = list(components.keys())
            for i, comp1 in enumerate(comp_names):
                for comp2 in comp_names[i+1:]:
                    # Simple heuristic: connect different types
                    if components[comp1].get('type') != components[comp2].get('type'):
                        G.add_edge(comp1, comp2)
            
            # Create layout with better algorithm
            fig, ax = plt.subplots(figsize=(14, 10))
            ax.set_facecolor(self.professional_colors['background'])
            
            # Use kamada_kawai_layout for better positioning
            pos = nx.kamada_kawai_layout(G, scale=2)
            
            # Draw enhanced edges with curves
            from matplotlib.patches import FancyArrowPatch
            
            for edge in G.edges():
                x1, y1 = pos[edge[0]]
                x2, y2 = pos[edge[1]]
                
                # Add curved arrows
                arrow = FancyArrowPatch((x1, y1), (x2, y2),
                                        connectionstyle="arc3,rad=0.1",
                                        arrowstyle='-',
                                        mutation_scale=20,
                                        linewidth=2,
                                        color=self.professional_colors['text_secondary'],
                                        alpha=0.6)
                ax.add_patch(arrow)
            
            # Draw enhanced nodes with 3D effects
            for node, (x, y) in pos.items():
                comp_type = components[node].get('type', 'unknown')
                
                if 'web' in comp_type:
                    color = self.colors['primary']
                elif 'data' in comp_type or 'redis' in node or 'postgres' in node:
                    color = self.colors['accent']
                else:
                    color = self.colors['secondary']
                
                # Draw 3D component
                self._draw_3d_component(ax, node, x, y, color)
            
            ax.set_title('Component Network Topology', 
                        fontsize=self.fonts['title']['size'], 
                        fontweight=self.fonts['title']['weight'], 
                        pad=20, color=self.professional_colors['text_primary'])
            
            # Add professional annotations
            self._add_professional_annotations(ax, intelligence_data.get('summary', {}))
            
            ax.axis('off')
            ax.set_xlim(-2.5, 2.5)
            ax.set_ylim(-2.5, 2.5)
            
            plt.tight_layout()
            chart_path = self.charts_dir / "component_network.png"
            self._save_professional_diagram(fig, chart_path)
            
            return str(chart_path)
            
        except Exception as e:
            print(f"WARNING [DIAGRAMS] Error creating network diagram: {e}")
            return None
    
    def create_technology_stack_diagram(self, intelligence_data: Dict[str, Any]) -> Optional[str]:
        """Create technology stack visualization"""
        try:
            components = intelligence_data.get('components', {})
            if not components:
                return None
            
            # Extract technologies
            languages = set()
            runtimes = set()
            frameworks = set()
            
            for comp in components.values():
                if comp.get('language'):
                    languages.add(comp['language'])
                if comp.get('runtime'):
                    runtimes.add(comp['runtime'])
                if comp.get('build_tool'):
                    frameworks.add(comp['build_tool'])
            
            # Create stacked visualization
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Stack layers
            layers = [
                ('Languages', list(languages), self.colors['primary']),
                ('Runtimes', list(runtimes), self.colors['secondary']),
                ('Build Tools', list(frameworks), self.colors['accent'])
            ]
            
            y_pos = 0
            for layer_name, items, color in layers:
                if items:
                    height = 1.5
                    rect = Rectangle((0, y_pos), 8, height, 
                                   facecolor=color, alpha=0.7, edgecolor='black')
                    ax.add_patch(rect)
                    
                    # Add text
                    ax.text(4, y_pos + height/2, f"{layer_name}: {', '.join(items)}", 
                           ha='center', va='center', fontweight='bold', 
                           fontsize=11, wrap=True)
                    
                    y_pos += height + 0.5
            
            ax.set_xlim(0, 8)
            ax.set_ylim(0, y_pos)
            ax.set_title('Technology Stack Overview', 
                        fontsize=16, fontweight='bold', pad=20)
            ax.axis('off')
            
            plt.tight_layout()
            chart_path = self.charts_dir / "technology_stack.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            print(f"WARNING [DIAGRAMS] Error creating technology stack diagram: {e}")
            return None
    
    def create_development_activity_heatmap(self, intelligence_data: Dict[str, Any]) -> Optional[str]:
        """Create development activity heatmap"""
        try:
            git_history = intelligence_data.get('git_history', {})
            if not git_history or git_history.get('total_commits', 0) == 0:
                return None
            
            # Mock activity data (in real implementation, extract from git history)
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            hours = [f'{i:02d}:00' for i in range(24)]
            
            # Create random activity matrix for demonstration
            np.random.seed(42)
            activity_matrix = np.random.rand(len(days), len(hours)) * 10
            
            # Create heatmap
            fig, ax = plt.subplots(figsize=(15, 6))
            im = ax.imshow(activity_matrix, cmap='Blues', aspect='auto')
            
            # Set ticks and labels
            ax.set_xticks(range(len(hours)))
            ax.set_yticks(range(len(days)))
            ax.set_xticklabels(hours, rotation=45, ha='right')
            ax.set_yticklabels(days)
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('Activity Level', rotation=270, labelpad=20)
            
            ax.set_title('Development Activity Heatmap', 
                        fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Hour of Day', fontsize=12, fontweight='bold')
            ax.set_ylabel('Day of Week', fontsize=12, fontweight='bold')
            
            plt.tight_layout()
            chart_path = self.charts_dir / "development_activity.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            print(f"WARNING [DIAGRAMS] Error creating development activity heatmap: {e}")
            return None
    
    def _draw_component(self, ax, name: str, x: float, y: float, color: str, tier: str):
        """Draw a component box in the architecture diagram"""
        # Draw component box
        rect = FancyBboxPatch((x-0.4, y-0.3), 0.8, 0.6, 
                             boxstyle="round,pad=0.1", 
                             facecolor=color, edgecolor='black', 
                             alpha=0.8, linewidth=2)
        ax.add_patch(rect)
        
        # Add component name
        ax.text(x, y, name, ha='center', va='center', 
               fontweight='bold', fontsize=10, color='white')
        
        # Add tier label
        ax.text(x, y-0.6, tier, ha='center', va='center', 
               fontweight='bold', fontsize=8, color='gray')
    
    def _draw_connections(self, ax, positions: Dict, components: Dict):
        """Draw connections between components"""
        # Simple connection logic - connect different types
        for comp1, pos1 in positions.items():
            for comp2, pos2 in positions.items():
                if comp1 != comp2:
                    type1 = components[comp1].get('type', 'unknown')
                    type2 = components[comp2].get('type', 'unknown')
                    
                    # Connect web to services, services to data
                    if (('web' in type1 and 'service' in type2) or 
                        ('service' in type1 and 'data' in type2) or
                        ('redis' in comp2 and 'web' in type1) or
                        ('postgres' in comp2 and 'service' in type1)):
                        
                        ax.arrow(pos1[0], pos1[1], 
                                pos2[0] - pos1[0], pos2[1] - pos1[1],
                                head_width=0.1, head_length=0.1, 
                                fc='gray', ec='gray', alpha=0.6)
    
    def create_migration_readiness_chart(self, intelligence_data: Dict[str, Any]) -> Optional[str]:
        """Create migration readiness assessment chart"""
        try:
            # Migration readiness factors
            factors = [
                'Containerization',
                'Documentation',
                'Testing',
                'Dependencies',
                'Configuration',
                'Security'
            ]
            
            # Calculate readiness scores based on analysis
            summary = intelligence_data.get('summary', {})
            container_rate = summary.get('containerization_status', 0) / max(summary.get('total_components', 1), 1)
            
            # Handle datasources safely - it could be an integer or a list
            datasources_data = summary.get('datasources', 0)
            datasources_count = len(datasources_data) if isinstance(datasources_data, list) else datasources_data if isinstance(datasources_data, int) else 0
            
            scores = [
                min(10, container_rate * 10),  # Containerization
                5,  # Documentation (placeholder)
                6,  # Testing (placeholder)
                7,  # Dependencies (placeholder)
                datasources_count + 3,  # Configuration
                max(1, 10 - summary.get('security_findings', {}).get('vulnerabilities', 0))  # Security
            ]
            
            # Create horizontal bar chart
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Color code based on score
            colors = []
            for score in scores:
                if score >= 8:
                    colors.append(self.colors['success'])
                elif score >= 5:
                    colors.append(self.colors['warning'])
                else:
                    colors.append(self.colors['danger'])
            
            bars = ax.barh(factors, scores, color=colors)
            
            # Add score labels
            for bar, score in zip(bars, scores):
                width = bar.get_width()
                ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                       f'{score:.1f}', ha='left', va='center', 
                       fontweight='bold', fontsize=11)
            
            ax.set_xlim(0, 10)
            ax.set_title('Migration Readiness Assessment', 
                        fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Readiness Score (0-10)', fontsize=12, fontweight='bold')
            ax.grid(axis='x', alpha=0.3)
            
            # Add legend
            legend_elements = [
                mpatches.Patch(color=self.colors['success'], label='Ready (8-10)'),
                mpatches.Patch(color=self.colors['warning'], label='Needs Work (5-7)'),
                mpatches.Patch(color=self.colors['danger'], label='Critical (0-4)')
            ]
            ax.legend(handles=legend_elements, loc='lower right')
            
            plt.tight_layout()
            chart_path = self.charts_dir / "migration_readiness.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            print(f"WARNING [DIAGRAMS] Error creating migration readiness chart: {e}")
            return None
    
    def create_risk_assessment_matrix(self, intelligence_data: Dict[str, Any]) -> Optional[str]:
        """Create risk assessment matrix"""
        try:
            # Risk categories and their impact/probability
            risks = {
                'Security Vulnerabilities': (9, 7),  # High impact, likely
                'Legacy Dependencies': (6, 8),      # Medium impact, very likely
                'Limited Documentation': (5, 6),     # Medium impact, likely
                'Configuration Complexity': (4, 5),   # Low impact, possible
                'Testing Gaps': (7, 4),             # High impact, unlikely
                'Deployment Issues': (8, 3)          # High impact, rare
            }
            
            # Create scatter plot matrix
            fig, ax = plt.subplots(figsize=(12, 10))
            
            # Plot risks
            for risk, (impact, probability) in risks.items():
                # Color based on overall risk score
                risk_score = impact * probability
                if risk_score >= 50:
                    color = self.colors['danger']
                elif risk_score >= 30:
                    color = self.colors['warning']
                else:
                    color = self.colors['success']
                
                ax.scatter(probability, impact, s=risk_score*3, 
                          color=color, alpha=0.7, edgecolors='black')
                
                # Add risk label
                ax.annotate(risk, (probability, impact), 
                           xytext=(5, 5), textcoords='offset points',
                           fontsize=10, fontweight='bold')
            
            # Add quadrant lines
            ax.axhline(y=5, color='gray', linestyle='--', alpha=0.5)
            ax.axvline(x=5, color='gray', linestyle='--', alpha=0.5)
            
            # Add quadrant labels
            ax.text(2.5, 8.5, 'High Impact\nLow Probability', 
                   ha='center', va='center', fontsize=11, 
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))
            ax.text(7.5, 8.5, 'High Impact\nHigh Probability', 
                   ha='center', va='center', fontsize=11,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='lightcoral', alpha=0.7))
            ax.text(2.5, 2.5, 'Low Impact\nLow Probability', 
                   ha='center', va='center', fontsize=11,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen', alpha=0.7))
            ax.text(7.5, 2.5, 'Low Impact\nHigh Probability', 
                   ha='center', va='center', fontsize=11,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='lightyellow', alpha=0.7))
            
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 10)
            ax.set_xlabel('Probability', fontsize=12, fontweight='bold')
            ax.set_ylabel('Impact', fontsize=12, fontweight='bold')
            ax.set_title('Risk Assessment Matrix', 
                        fontsize=16, fontweight='bold', pad=20)
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            chart_path = self.charts_dir / "risk_assessment_matrix.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            print(f"WARNING [DIAGRAMS] Error creating risk assessment matrix: {e}")
            return None
    
    def create_cicd_pipeline_diagram(self, intelligence_data: Dict[str, Any]) -> Optional[str]:
        """Create CI/CD pipeline visualization"""
        try:
            ci_cd_pipelines = intelligence_data.get('ci_cd_pipelines', {})
            
            # Pipeline stages
            stages = [
                'Source Code',
                'Build',
                'Test',
                'Security Scan',
                'Package',
                'Deploy'
            ]
            
            # Create pipeline flow diagram
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # Draw pipeline stages
            stage_width = 1.5
            stage_height = 0.8
            y_center = 2
            
            for i, stage in enumerate(stages):
                x = i * 2
                
                # Determine stage color based on analysis
                if 'Security' in stage:
                    color = self.colors['danger']
                elif 'Test' in stage:
                    color = self.colors['warning']
                elif 'Deploy' in stage:
                    color = self.colors['success']
                else:
                    color = self.colors['primary']
                
                # Draw stage box
                rect = FancyBboxPatch((x-stage_width/2, y_center-stage_height/2), 
                                     stage_width, stage_height,
                                     boxstyle="round,pad=0.1",
                                     facecolor=color, edgecolor='black', 
                                     alpha=0.8, linewidth=2)
                ax.add_patch(rect)
                
                # Add stage text
                ax.text(x, y_center, stage, ha='center', va='center', 
                       fontweight='bold', fontsize=10, color='white')
                
                # Add arrow to next stage
                if i < len(stages) - 1:
                    ax.arrow(x + stage_width/2, y_center, 
                            2 - stage_width, 0,
                            head_width=0.1, head_length=0.1, 
                            fc='gray', ec='gray', alpha=0.8)
            
            # Add quality gates
            quality_gates = ci_cd_pipelines.get('quality_gates', [])
            if quality_gates:
                ax.text(len(stages), 3, f'Quality Gates: {len(quality_gates)}', 
                       ha='center', va='center', fontsize=12, fontweight='bold',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))
            
            ax.set_xlim(-1, len(stages) + 1)
            ax.set_ylim(0, 4)
            ax.set_title('CI/CD Pipeline Overview', 
                        fontsize=16, fontweight='bold', pad=20)
            ax.axis('off')
            
            plt.tight_layout()
            chart_path = self.charts_dir / "cicd_pipeline.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            print(f"WARNING [DIAGRAMS] Error creating CI/CD pipeline diagram: {e}")
            return None
    
    def create_user_flow_diagram(self, intelligence_data: Dict[str, Any]) -> Optional[str]:
        """Create user flow diagram showing user interaction patterns"""
        try:
            components = intelligence_data.get('components', {})
            external_services = intelligence_data.get('summary', {}).get('external_services', [])
            # Handle case where external_services is an integer instead of a list
            if isinstance(external_services, int):
                external_services = []
            
            if not components:
                return None
            
            fig, ax = plt.subplots(figsize=(16, 10))
            
            # Define user flow stages
            user_stages = [
                'User Access',
                'Authentication',
                'Load Balancer',
                'Application Layer',
                'Business Logic',
                'Data Layer',
                'External Services'
            ]
            
            # Create flow layout
            stage_positions = {}
            for i, stage in enumerate(user_stages):
                x = 2 + (i % 3) * 5
                y = 8 - (i // 3) * 3
                stage_positions[stage] = (x, y)
            
            # Draw user flow stages
            for stage, (x, y) in stage_positions.items():
                # Determine stage color and size based on components
                if stage == 'User Access':
                    color = self.colors['info']
                    size = 1.2
                elif stage == 'Authentication':
                    color = self.colors['warning']
                    size = 1.0
                elif stage == 'Application Layer':
                    color = self.colors['primary']
                    size = 1.5
                elif stage == 'Data Layer':
                    color = self.colors['success']
                    size = 1.0
                elif stage == 'External Services':
                    color = self.colors['accent']
                    size = 1.0
                else:
                    color = self.colors['secondary']
                    size = 1.0
                
                # Draw stage circle
                circle = Circle((x, y), size, facecolor=color, edgecolor='black', 
                              alpha=0.8, linewidth=2)
                ax.add_patch(circle)
                
                # Add stage text
                ax.text(x, y, stage.replace(' ', '\\n'), ha='center', va='center', 
                       fontweight='bold', fontsize=9, color='white')
                
                # Add component count for relevant stages
                if stage == 'Application Layer':
                    ax.text(x, y-2, f'{len(components)} Components', ha='center', va='center', 
                           fontsize=8, style='italic')
                elif stage == 'External Services':
                    ext_services = external_services if isinstance(external_services, list) else []
                    ax.text(x, y-2, f'{len(ext_services)} Services', ha='center', va='center', 
                           fontsize=8, style='italic')
            
            # Draw flow arrows
            flow_connections = [
                ('User Access', 'Authentication'),
                ('Authentication', 'Load Balancer'),
                ('Load Balancer', 'Application Layer'),
                ('Application Layer', 'Business Logic'),
                ('Business Logic', 'Data Layer'),
                ('Application Layer', 'External Services')
            ]
            
            for start, end in flow_connections:
                start_pos = stage_positions[start]
                end_pos = stage_positions[end]
                
                # Calculate arrow direction
                dx = end_pos[0] - start_pos[0]
                dy = end_pos[1] - start_pos[1]
                
                if dx != 0 or dy != 0:
                    ax.annotate('', xy=end_pos, xytext=start_pos,
                              arrowprops=dict(arrowstyle='->', lw=2, color='gray', alpha=0.7))
            
            # Add user flow complexity assessment
            complexity_text = f"Flow Complexity: {'Simple' if len(components) <= 3 else 'Moderate' if len(components) <= 6 else 'Complex'}"
            ax.text(1, 1, complexity_text, fontsize=12, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.5", facecolor='lightblue', alpha=0.7))
            
            ax.set_xlim(0, 14)
            ax.set_ylim(0, 10)
            ax.set_title('User Flow Diagram', fontsize=18, fontweight='bold', pad=20)
            ax.axis('off')
            
            plt.tight_layout()
            chart_path = self.charts_dir / "user_flow_diagram.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            print(f"WARNING [DIAGRAMS] Error creating user flow diagram: {e}")
            return None
    
    def create_high_level_architecture_diagram(self, intelligence_data: Dict[str, Any]) -> Optional[str]:
        """Create high-level architecture overview diagram"""
        try:
            components = intelligence_data.get('components', {})
            languages = intelligence_data.get('summary', {}).get('languages', {})
            external_services = intelligence_data.get('summary', {}).get('external_services', [])
            datasources = intelligence_data.get('summary', {}).get('datasources', [])
            
            # Handle case where external_services is an integer instead of a list
            if isinstance(external_services, int):
                external_services = []
            
            # Handle case where datasources is an integer instead of a list
            if isinstance(datasources, int):
                datasources = []
            arch_assessment = intelligence_data.get('architecture_assessment', {})
            
            if not components:
                return None
            
            fig, ax = plt.subplots(figsize=(16, 12))
            
            # Define architecture layers
            layers = [
                {'name': 'Presentation Layer', 'y': 9, 'color': self.colors['info']},
                {'name': 'Application Layer', 'y': 7, 'color': self.colors['primary']},
                {'name': 'Business Logic Layer', 'y': 5, 'color': self.colors['secondary']},
                {'name': 'Data Access Layer', 'y': 3, 'color': self.colors['success']},
                {'name': 'External Services Layer', 'y': 1, 'color': self.colors['accent']}
            ]
            
            # Draw architecture layers
            for layer in layers:
                # Draw layer background
                rect = FancyBboxPatch((1, layer['y']-0.8), 12, 1.6,
                                     boxstyle="round,pad=0.1",
                                     facecolor=layer['color'], alpha=0.2,
                                     edgecolor=layer['color'], linewidth=2)
                ax.add_patch(rect)
                
                # Add layer label
                ax.text(0.5, layer['y'], layer['name'], ha='right', va='center',
                       fontsize=12, fontweight='bold', rotation=90)
            
            # Position components in layers
            component_positions = {}
            app_components = list(components.keys())
            
            # Distribute application components
            for i, comp_name in enumerate(app_components):
                x = 2 + (i * 3.5)
                y = 7  # Application layer
                component_positions[comp_name] = (x, y)
                
                # Draw component
                rect = FancyBboxPatch((x-0.8, y-0.6), 1.6, 1.2,
                                     boxstyle="round,pad=0.1",
                                     facecolor=self.colors['primary'], alpha=0.8,
                                     edgecolor='black', linewidth=1)
                ax.add_patch(rect)
                
                # Add component name
                ax.text(x, y, comp_name, ha='center', va='center',
                       fontsize=10, fontweight='bold', color='white')
            
            # Add external services
            ext_services = external_services if isinstance(external_services, list) else []
            for i, service in enumerate(ext_services):
                x = 2 + (i * 3)
                y = 1  # External services layer
                
                # Draw service
                rect = FancyBboxPatch((x-0.6, y-0.4), 1.2, 0.8,
                                     boxstyle="round,pad=0.1",
                                     facecolor=self.colors['accent'], alpha=0.8,
                                     edgecolor='black', linewidth=1)
                ax.add_patch(rect)
                
                # Add service name
                ax.text(x, y, service, ha='center', va='center',
                       fontsize=9, fontweight='bold', color='white')
            
            # Add datasources
            ds_list = datasources if isinstance(datasources, list) else []
            for i, datasource in enumerate(ds_list):
                x = 2 + (i * 3)
                y = 3  # Data access layer
                
                # Draw datasource
                rect = FancyBboxPatch((x-0.6, y-0.4), 1.2, 0.8,
                                     boxstyle="round,pad=0.1",
                                     facecolor=self.colors['success'], alpha=0.8,
                                     edgecolor='black', linewidth=1)
                ax.add_patch(rect)
                
                # Add datasource name
                ax.text(x, y, datasource, ha='center', va='center',
                       fontsize=9, fontweight='bold', color='white')
            
            # Add architecture style annotation
            arch_style = arch_assessment.get('style', 'Unknown')
            ax.text(14, 9, f'Architecture: {arch_style}', ha='left', va='center',
                   fontsize=12, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='lightyellow', alpha=0.8))
            
            # Add language summary
            if isinstance(languages, dict):
                lang_text = f"Languages: {', '.join(languages.keys())}"
            elif isinstance(languages, list):
                lang_text = f"Languages: {', '.join(languages)}"
            else:
                lang_text = f"Languages: {str(languages)}"
            ax.text(14, 8, lang_text, ha='left', va='center',
                   fontsize=10, style='italic',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgray', alpha=0.7))
            
            # Add system complexity indicator
            total_components = len(components)
            ext_services_count = len(external_services) if isinstance(external_services, list) else 0
            datasources_count = len(datasources) if isinstance(datasources, list) else 0
            integration_points = ext_services_count + datasources_count
            complexity = "High" if total_components > 5 or integration_points > 3 else "Moderate" if total_components > 2 else "Low"
            
            ax.text(14, 7, f'Complexity: {complexity}', ha='left', va='center',
                   fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='lightcoral', alpha=0.7))
            
            ax.set_xlim(0, 16)
            ax.set_ylim(0, 11)
            ax.set_title('High-Level Architecture Overview', fontsize=18, fontweight='bold', pad=20)
            ax.axis('off')
            
            plt.tight_layout()
            chart_path = self.charts_dir / "high_level_architecture.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            print(f"WARNING [DIAGRAMS] Error creating high-level architecture diagram: {e}")
            return None
    
    def create_system_overview_diagram(self, intelligence_data: Dict[str, Any]) -> Optional[str]:
        """Create comprehensive system overview diagram"""
        try:
            components = intelligence_data.get('components', {})
            summary = intelligence_data.get('summary', {})
            
            if not components:
                return None
            
            fig, ax = plt.subplots(figsize=(14, 10))
            
            # Create system overview layout
            center_x, center_y = 7, 5
            
            # Draw central system core
            core_circle = Circle((center_x, center_y), 2, facecolor=self.colors['primary'],
                               edgecolor='black', alpha=0.8, linewidth=3)
            ax.add_patch(core_circle)
            
            ax.text(center_x, center_y, f'System\\nCore\\n{len(components)} Components', 
                   ha='center', va='center', fontsize=14, fontweight='bold', color='white')
            
            # Position components around the core
            component_names = list(components.keys())
            for i, comp_name in enumerate(component_names):
                angle = (2 * np.pi * i) / len(component_names)
                x = center_x + 4 * np.cos(angle)
                y = center_y + 4 * np.sin(angle)
                
                # Draw component
                comp_circle = Circle((x, y), 1, facecolor=self.colors['secondary'],
                                   edgecolor='black', alpha=0.7, linewidth=2)
                ax.add_patch(comp_circle)
                
                ax.text(x, y, comp_name, ha='center', va='center',
                       fontsize=10, fontweight='bold', color='white')
                
                # Draw connection to core
                ax.plot([center_x, x], [center_y, y], 'gray', alpha=0.6, linewidth=2)
            
            # Add system metrics
            # Handle different data types safely
            languages_data = summary.get('languages', {})
            languages_count = len(languages_data) if isinstance(languages_data, (dict, list)) else 0
            
            external_services_data = summary.get('external_services', [])
            external_services_count = len(external_services_data) if isinstance(external_services_data, list) else external_services_data if isinstance(external_services_data, int) else 0
            
            metrics_text = [
                f"Total Components: {summary.get('total_components', 0)}",
                f"Languages: {languages_count}",
                f"Containerized: {summary.get('containerization_status', 0)}",
                f"External Services: {external_services_count}"
            ]
            
            for i, metric in enumerate(metrics_text):
                ax.text(1, 9 - i * 0.5, metric, fontsize=11, fontweight='bold',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))
            
            ax.set_xlim(0, 14)
            ax.set_ylim(0, 10)
            ax.set_title('System Overview Diagram', fontsize=18, fontweight='bold', pad=20)
            ax.axis('off')
            
            plt.tight_layout()
            chart_path = self.charts_dir / "system_overview.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return str(chart_path)
            
        except Exception as e:
            print(f"WARNING [DIAGRAMS] Error creating system overview diagram: {e}")
            return None