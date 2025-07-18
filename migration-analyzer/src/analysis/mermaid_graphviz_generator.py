"""
Mermaid and Graphviz Diagram Generator for Professional Word Documents
Supports various diagram types using Mermaid and Graphviz syntax
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import json
import base64
import requests
from datetime import datetime

class MermaidGraphvizGenerator:
    """
    Professional diagram generator using Mermaid and Graphviz
    """
    
    def __init__(self, charts_dir: Path):
        self.charts_dir = charts_dir
        self.charts_dir.mkdir(exist_ok=True)
        
        # Check available rendering engines
        self.mermaid_available = self._check_mermaid_cli()
        self.graphviz_available = self._check_graphviz()
        self.puppeteer_available = self._check_puppeteer()
        
        # Professional color scheme
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
        
        print(f"MERMAID-GRAPHVIZ [MERMAID-GRAPHVIZ] Initialized diagram generator")
        print(f"   - Mermaid CLI: {'YES' if self.mermaid_available else 'NO'}")
        print(f"   - Graphviz: {'YES' if self.graphviz_available else 'NO'}")
        print(f"   - Puppeteer: {'YES' if self.puppeteer_available else 'NO'}")
    
    def _check_mermaid_cli(self) -> bool:
        """Check if Mermaid CLI is available"""
        try:
            result = subprocess.run(['mmdc', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _check_graphviz(self) -> bool:
        """Check if Graphviz is available"""
        try:
            result = subprocess.run(['dot', '-V'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _check_puppeteer(self) -> bool:
        """Check if Puppeteer is available"""
        try:
            result = subprocess.run(['node', '-e', 'require("puppeteer")'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def generate_all_professional_diagrams(self, intelligence_data: Dict[str, Any]) -> List[str]:
        """Generate all professional diagrams using Mermaid and Graphviz"""
        generated_diagrams = []
        
        try:
            # 1. Architecture Flowchart (Mermaid)
            arch_flowchart = self.create_architecture_flowchart(intelligence_data)
            if arch_flowchart:
                generated_diagrams.append(arch_flowchart)
            
            # 2. Component Relationship Graph (Graphviz)
            comp_graph = self.create_component_relationship_graph(intelligence_data)
            if comp_graph:
                generated_diagrams.append(comp_graph)
            
            # 3. Security Flow Diagram (Mermaid)
            security_flow = self.create_security_flow_diagram(intelligence_data)
            if security_flow:
                generated_diagrams.append(security_flow)
            
            # 4. CI/CD Pipeline (Mermaid)
            cicd_pipeline = self.create_cicd_pipeline_mermaid(intelligence_data)
            if cicd_pipeline:
                generated_diagrams.append(cicd_pipeline)
            
            # 5. Data Flow Diagram (Graphviz)
            data_flow = self.create_data_flow_diagram(intelligence_data)
            if data_flow:
                generated_diagrams.append(data_flow)
            
            # 6. Deployment Architecture (Mermaid)
            deployment_arch = self.create_deployment_architecture(intelligence_data)
            if deployment_arch:
                generated_diagrams.append(deployment_arch)
            
            # 7. Risk Assessment Flow (Mermaid)
            risk_flow = self.create_risk_assessment_flow(intelligence_data)
            if risk_flow:
                generated_diagrams.append(risk_flow)
            
            # 8. Migration Strategy Diagram (Graphviz)
            migration_strategy = self.create_migration_strategy_diagram(intelligence_data)
            if migration_strategy:
                generated_diagrams.append(migration_strategy)
            
            # 9. User Journey Map (Mermaid)
            user_journey = self.create_user_journey_map(intelligence_data)
            if user_journey:
                generated_diagrams.append(user_journey)
            
            # 10. Business Flow Diagram (Mermaid)
            business_flow = self.create_business_flow_diagram(intelligence_data)
            if business_flow:
                generated_diagrams.append(business_flow)
            
            print(f"MERMAID-GRAPHVIZ [MERMAID-GRAPHVIZ] Generated {len(generated_diagrams)} professional diagrams")
            return generated_diagrams
            
        except Exception as e:
            print(f"WARNING [MERMAID-GRAPHVIZ] Error generating diagrams: {e}")
            return generated_diagrams
    
    def create_architecture_flowchart(self, intelligence_data: Dict[str, Any]) -> Optional[str]:
        """Create architecture flowchart using Mermaid"""
        try:
            components = intelligence_data.get('components', {})
            if not components:
                return None
            
            # Generate Mermaid flowchart
            mermaid_code = self._generate_architecture_flowchart_mermaid(components)
            
            # Render diagram
            output_path = self.charts_dir / "architecture_flowchart.png"
            success = self._render_mermaid_diagram(mermaid_code, output_path)
            
            if success:
                return str(output_path)
            return None
            
        except Exception as e:
            print(f"WARNING [MERMAID-GRAPHVIZ] Error creating architecture flowchart: {e}")
            return None
    
    def create_component_relationship_graph(self, intelligence_data: Dict[str, Any]) -> Optional[str]:
        """Create component relationship graph using Graphviz"""
        try:
            components = intelligence_data.get('components', {})
            if not components:
                return None
            
            # Generate Graphviz DOT code
            dot_code = self._generate_component_relationship_dot(components)
            
            # Render diagram
            output_path = self.charts_dir / "component_relationship_graph.png"
            success = self._render_graphviz_diagram(dot_code, output_path)
            
            if success:
                return str(output_path)
            return None
            
        except Exception as e:
            print(f"WARNING [MERMAID-GRAPHVIZ] Error creating component relationship graph: {e}")
            return None
    
    def create_security_flow_diagram(self, intelligence_data: Dict[str, Any]) -> Optional[str]:
        """Create security flow diagram using Mermaid"""
        try:
            security_data = intelligence_data.get('security_posture', {})
            vuln_data = intelligence_data.get('vulnerability_assessment', {})
            
            # Generate Mermaid flowchart for security
            mermaid_code = self._generate_security_flow_mermaid(security_data, vuln_data)
            
            # Render diagram
            output_path = self.charts_dir / "security_flow_diagram.png"
            success = self._render_mermaid_diagram(mermaid_code, output_path)
            
            if success:
                return str(output_path)
            return None
            
        except Exception as e:
            print(f"WARNING [MERMAID-GRAPHVIZ] Error creating security flow diagram: {e}")
            return None
    
    def create_cicd_pipeline_mermaid(self, intelligence_data: Dict[str, Any]) -> Optional[str]:
        """Create CI/CD pipeline diagram using Mermaid"""
        try:
            cicd_data = intelligence_data.get('ci_cd_pipelines', {})
            
            # Generate Mermaid flowchart for CI/CD
            mermaid_code = self._generate_cicd_pipeline_mermaid(cicd_data)
            
            # Render diagram
            output_path = self.charts_dir / "cicd_pipeline_mermaid.png"
            success = self._render_mermaid_diagram(mermaid_code, output_path)
            
            if success:
                return str(output_path)
            return None
            
        except Exception as e:
            print(f"WARNING [MERMAID-GRAPHVIZ] Error creating CI/CD pipeline diagram: {e}")
            return None
    
    def create_data_flow_diagram(self, intelligence_data: Dict[str, Any]) -> Optional[str]:
        """Create data flow diagram using Graphviz"""
        try:
            components = intelligence_data.get('components', {})
            datasources = intelligence_data.get('summary', {}).get('datasources', 0)
            
            if not components or datasources == 0:
                return None
            
            # Generate Graphviz DOT code for data flow
            dot_code = self._generate_data_flow_dot(components, intelligence_data)
            
            # Render diagram
            output_path = self.charts_dir / "data_flow_diagram.png"
            success = self._render_graphviz_diagram(dot_code, output_path)
            
            if success:
                return str(output_path)
            return None
            
        except Exception as e:
            print(f"WARNING [MERMAID-GRAPHVIZ] Error creating data flow diagram: {e}")
            return None
    
    def create_deployment_architecture(self, intelligence_data: Dict[str, Any]) -> Optional[str]:
        """Create deployment architecture using Mermaid"""
        try:
            components = intelligence_data.get('components', {})
            architecture = intelligence_data.get('architecture_assessment', {})
            
            # Generate Mermaid diagram for deployment
            mermaid_code = self._generate_deployment_architecture_mermaid(components, architecture)
            
            # Render diagram
            output_path = self.charts_dir / "deployment_architecture.png"
            success = self._render_mermaid_diagram(mermaid_code, output_path)
            
            if success:
                return str(output_path)
            return None
            
        except Exception as e:
            print(f"WARNING [MERMAID-GRAPHVIZ] Error creating deployment architecture: {e}")
            return None
    
    def create_risk_assessment_flow(self, intelligence_data: Dict[str, Any]) -> Optional[str]:
        """Create risk assessment flow using Mermaid"""
        try:
            vuln_data = intelligence_data.get('vulnerability_assessment', {})
            
            # Generate Mermaid flowchart for risk assessment
            mermaid_code = self._generate_risk_assessment_flow_mermaid(vuln_data)
            
            # Render diagram
            output_path = self.charts_dir / "risk_assessment_flow.png"
            success = self._render_mermaid_diagram(mermaid_code, output_path)
            
            if success:
                return str(output_path)
            return None
            
        except Exception as e:
            print(f"WARNING [MERMAID-GRAPHVIZ] Error creating risk assessment flow: {e}")
            return None
    
    def create_migration_strategy_diagram(self, intelligence_data: Dict[str, Any]) -> Optional[str]:
        """Create migration strategy diagram using Graphviz"""
        try:
            components = intelligence_data.get('components', {})
            
            # Generate Graphviz DOT code for migration strategy
            dot_code = self._generate_migration_strategy_dot(components, intelligence_data)
            
            # Render diagram
            output_path = self.charts_dir / "migration_strategy_diagram.png"
            success = self._render_graphviz_diagram(dot_code, output_path)
            
            if success:
                return str(output_path)
            return None
            
        except Exception as e:
            print(f"WARNING [MERMAID-GRAPHVIZ] Error creating migration strategy diagram: {e}")
            return None
    
    def _generate_architecture_flowchart_mermaid(self, components: Dict[str, Any]) -> str:
        """Generate Mermaid code for architecture flowchart"""
        mermaid_code = """
graph TD
    %% Professional Architecture Flowchart
    %% Generated by Application Intelligence Platform
    
    classDef webTier fill:#007bd3,stroke:#333,stroke-width:2px,color:#fff
    classDef serviceTier fill:#48b0f1,stroke:#333,stroke-width:2px,color:#fff
    classDef dataTier fill:#16a085,stroke:#333,stroke-width:2px,color:#fff
    classDef external fill:#f39c12,stroke:#333,stroke-width:2px,color:#fff
    
    subgraph "Web Tier"
"""
        
        # Add web components
        web_components = []
        service_components = []
        data_components = []
        
        for name, comp in components.items():
            comp_type = comp.get('type', 'unknown')
            language = comp.get('language', 'unknown')
            
            node_id = name.replace('-', '_').replace(' ', '_')
            node_label = f"{name}\\n({language})"
            
            if 'web' in comp_type.lower() or 'frontend' in comp_type.lower():
                web_components.append((node_id, node_label))
            elif 'redis' in name.lower() or 'postgres' in name.lower() or 'database' in comp_type.lower():
                data_components.append((node_id, node_label))
            else:
                service_components.append((node_id, node_label))
        
        # Add web tier nodes
        for node_id, node_label in web_components:
            mermaid_code += f"        {node_id}[{node_label}]\n"
        
        mermaid_code += "    end\n\n"
        
        # Add service tier
        if service_components:
            mermaid_code += '    subgraph "Service Tier"\n'
            for node_id, node_label in service_components:
                mermaid_code += f"        {node_id}[{node_label}]\n"
            mermaid_code += "    end\n\n"
        
        # Add data tier
        if data_components:
            mermaid_code += '    subgraph "Data Tier"\n'
            for node_id, node_label in data_components:
                mermaid_code += f"        {node_id}[{node_label}]\n"
            mermaid_code += "    end\n\n"
        
        # Add connections
        mermaid_code += "    %% Component Connections\n"
        
        # Connect web to services
        for web_id, _ in web_components:
            for service_id, _ in service_components:
                mermaid_code += f"    {web_id} --> {service_id}\n"
        
        # Connect services to data
        for service_id, _ in service_components:
            for data_id, _ in data_components:
                mermaid_code += f"    {service_id} --> {data_id}\n"
        
        # Apply styles
        mermaid_code += "\n    %% Apply styles\n"
        for node_id, _ in web_components:
            mermaid_code += f"    class {node_id} webTier\n"
        for node_id, _ in service_components:
            mermaid_code += f"    class {node_id} serviceTier\n"
        for node_id, _ in data_components:
            mermaid_code += f"    class {node_id} dataTier\n"
        
        return mermaid_code
    
    def _generate_component_relationship_dot(self, components: Dict[str, Any]) -> str:
        """Generate Graphviz DOT code for component relationships"""
        dot_code = """
digraph ComponentRelationships {
    rankdir=TB;
    node [shape=box, style=filled, fontname="Arial", fontsize=10];
    edge [fontname="Arial", fontsize=8];
    
    // Define colors
    node [fillcolor="#007bd3", fontcolor="white"] // Web tier
    {
"""
        
        # Categorize components
        web_components = []
        service_components = []
        data_components = []
        
        for name, comp in components.items():
            comp_type = comp.get('type', 'unknown')
            language = comp.get('language', 'unknown')
            
            node_id = name.replace('-', '_').replace(' ', '_')
            node_label = f"{name}\\n({language})"
            
            if 'web' in comp_type.lower() or 'frontend' in comp_type.lower():
                web_components.append((node_id, node_label))
            elif 'redis' in name.lower() or 'postgres' in name.lower() or 'database' in comp_type.lower():
                data_components.append((node_id, node_label))
            else:
                service_components.append((node_id, node_label))
        
        # Add web tier nodes
        for node_id, node_label in web_components:
            dot_code += f'        {node_id} [label="{node_label}"];\n'
        
        dot_code += "    }\n\n"
        
        # Service tier
        if service_components:
            dot_code += '    node [fillcolor="#48b0f1", fontcolor="white"] // Service tier\n'
            dot_code += "    {\n"
            for node_id, node_label in service_components:
                dot_code += f'        {node_id} [label="{node_label}"];\n'
            dot_code += "    }\n\n"
        
        # Data tier
        if data_components:
            dot_code += '    node [fillcolor="#16a085", fontcolor="white"] // Data tier\n'
            dot_code += "    {\n"
            for node_id, node_label in data_components:
                dot_code += f'        {node_id} [label="{node_label}"];\n'
            dot_code += "    }\n\n"
        
        # Add connections
        dot_code += "    // Component relationships\n"
        
        # Connect web to services
        for web_id, _ in web_components:
            for service_id, _ in service_components:
                dot_code += f'    {web_id} -> {service_id} [label="HTTP/REST"];\n'
        
        # Connect services to data
        for service_id, _ in service_components:
            for data_id, _ in data_components:
                dot_code += f'    {service_id} -> {data_id} [label="Data Access"];\n'
        
        dot_code += "}\n"
        
        return dot_code
    
    def _generate_security_flow_mermaid(self, security_data: Dict[str, Any], vuln_data: Dict[str, Any]) -> str:
        """Generate Mermaid code for security flow"""
        findings_count = len(vuln_data.get('findings', []))
        
        mermaid_code = f"""
flowchart TD
    %% Security Flow Diagram
    %% Generated by Application Intelligence Platform
    
    classDef securityGood fill:#27ae60,stroke:#333,stroke-width:2px,color:#fff
    classDef securityWarning fill:#f39c12,stroke:#333,stroke-width:2px,color:#fff
    classDef securityCritical fill:#e74c3c,stroke:#333,stroke-width:2px,color:#fff
    classDef process fill:#3498db,stroke:#333,stroke-width:2px,color:#fff
    
    A[Security Assessment] --> B{{Has Vulnerabilities?}}
    B -->|Yes| C[Vulnerability Analysis]
    B -->|No| D[Security Baseline]
    
    C --> E[{findings_count} Findings Detected]
    E --> F{{Severity Level}}
    
    F -->|High| G[Critical Action Required]
    F -->|Medium| H[Review and Plan]
    F -->|Low| I[Monitor and Track]
    
    G --> J[Immediate Remediation]
    H --> K[Planned Remediation]
    I --> L[Ongoing Monitoring]
    
    D --> M[Maintain Security Posture]
    
    J --> N[Security Validation]
    K --> N
    L --> N
    M --> N
    
    N --> O[Continuous Monitoring]
    
    class A,N,O process
    class D,M,L securityGood
    class H,K securityWarning
    class G,J securityCritical
"""
        
        return mermaid_code
    
    def _generate_cicd_pipeline_mermaid(self, cicd_data: Dict[str, Any]) -> str:
        """Generate Mermaid code for CI/CD pipeline"""
        quality_gates = len(cicd_data.get('quality_gates', []))
        
        mermaid_code = f"""
flowchart LR
    %% CI/CD Pipeline Diagram
    %% Generated by Application Intelligence Platform
    
    classDef source fill:#007bd3,stroke:#333,stroke-width:2px,color:#fff
    classDef build fill:#48b0f1,stroke:#333,stroke-width:2px,color:#fff
    classDef test fill:#f39c12,stroke:#333,stroke-width:2px,color:#fff
    classDef security fill:#e74c3c,stroke:#333,stroke-width:2px,color:#fff
    classDef deploy fill:#27ae60,stroke:#333,stroke-width:2px,color:#fff
    
    subgraph "Source Control"
        A[Source Code] --> B[Code Review]
        B --> C[Merge to Main]
    end
    
    subgraph "Build Stage"
        C --> D[Build Application]
        D --> E[Package Artifacts]
    end
    
    subgraph "Quality Gates"
        E --> F[Unit Tests]
        F --> G[Integration Tests]
        G --> H[Security Scan]
        H --> I[Code Quality Check]
    end
    
    subgraph "Deployment"
        I --> J{{Quality Gate Pass?}}
        J -->|Yes| K[Deploy to Staging]
        J -->|No| L[Build Failed]
        K --> M[Deploy to Production]
    end
    
    L --> A
    
    N["{quality_gates} Quality Gates Configured"] -.-> F
    
    class A,B,C source
    class D,E build
    class F,G,I test
    class H security
    class K,M deploy
"""
        
        return mermaid_code
    
    def _generate_data_flow_dot(self, components: Dict[str, Any], intelligence_data: Dict[str, Any]) -> str:
        """Generate Graphviz DOT code for data flow"""
        dot_code = """
digraph DataFlow {
    rankdir=LR;
    node [shape=box, style=filled, fontname="Arial", fontsize=10];
    edge [fontname="Arial", fontsize=8];
    
    // External systems
    node [fillcolor="#f39c12", fontcolor="white", shape=cylinder];
    {
        PostgreSQL [label="PostgreSQL\\nDatabase"];
        Redis [label="Redis\\nCache"];
    }
    
    // Application components
    node [fillcolor="#007bd3", fontcolor="white", shape=box];
    {
"""
        
        # Add application components
        for name, comp in components.items():
            if 'redis' not in name.lower() and 'postgres' not in name.lower():
                node_id = name.replace('-', '_').replace(' ', '_')
                language = comp.get('language', 'unknown')
                dot_code += f'        {node_id} [label="{name}\\n({language})"];\n'
        
        dot_code += """    }
    
    // Data flow connections
    User [fillcolor="#16a085", fontcolor="white", shape=ellipse];
    
    User -> vote [label="HTTP Request"];
    vote -> Redis [label="Store Vote"];
    worker -> Redis [label="Read Votes"];
    worker -> PostgreSQL [label="Store Results"];
    result -> PostgreSQL [label="Read Results"];
    result -> User [label="Display Results"];
    
    // Data flow labels
    edge [color="#666666", style=dashed];
    Redis -> worker [label="Vote Queue"];
    PostgreSQL -> result [label="Vote Results"];
}
"""
        
        return dot_code
    
    def _generate_deployment_architecture_mermaid(self, components: Dict[str, Any], architecture: Dict[str, Any]) -> str:
        """Generate Mermaid code for deployment architecture"""
        style = architecture.get('style', {})
        arch_type = style.get('value', 'microservices') if isinstance(style, dict) else 'microservices'
        
        mermaid_code = f"""
graph TB
    %% Deployment Architecture - {arch_type.title()}
    %% Generated by Application Intelligence Platform
    
    classDef loadBalancer fill:#007bd3,stroke:#333,stroke-width:2px,color:#fff
    classDef webTier fill:#48b0f1,stroke:#333,stroke-width:2px,color:#fff
    classDef serviceTier fill:#16a085,stroke:#333,stroke-width:2px,color:#fff
    classDef dataTier fill:#f39c12,stroke:#333,stroke-width:2px,color:#fff
    classDef infrastructure fill:#e74c3c,stroke:#333,stroke-width:2px,color:#fff
    
    subgraph "Load Balancer"
        LB[Load Balancer]
    end
    
    subgraph "Container Platform"
        subgraph "Web Tier"
"""
        
        # Add web components
        web_count = 0
        service_count = 0
        
        for name, comp in components.items():
            comp_type = comp.get('type', 'unknown')
            node_id = name.replace('-', '_').replace(' ', '_')
            
            if 'web' in comp_type.lower() or 'frontend' in comp_type.lower():
                web_count += 1
                mermaid_code += f"            {node_id}[{name}]\n"
        
        mermaid_code += "        end\n\n"
        mermaid_code += "        subgraph \"Service Tier\"\n"
        
        # Add service components
        for name, comp in components.items():
            comp_type = comp.get('type', 'unknown')
            node_id = name.replace('-', '_').replace(' ', '_')
            
            if ('web' not in comp_type.lower() and 'frontend' not in comp_type.lower() and 
                'redis' not in name.lower() and 'postgres' not in name.lower()):
                service_count += 1
                mermaid_code += f"            {node_id}[{name}]\n"
        
        mermaid_code += "        end\n\n"
        mermaid_code += "        subgraph \"Data Tier\"\n"
        
        # Add data components
        for name, comp in components.items():
            if 'redis' in name.lower() or 'postgres' in name.lower():
                node_id = name.replace('-', '_').replace(' ', '_')
                mermaid_code += f"            {node_id}[{name}]\n"
        
        mermaid_code += """        end
    end
    
    %% External connections
    Internet([Internet]) --> LB
    
    %% Apply styles
    class LB loadBalancer
    class Internet infrastructure
"""
        
        return mermaid_code
    
    def _generate_risk_assessment_flow_mermaid(self, vuln_data: Dict[str, Any]) -> str:
        """Generate Mermaid code for risk assessment flow"""
        findings = vuln_data.get('findings', [])
        high_count = len([f for f in findings if f.get('severity') == 'HIGH'])
        medium_count = len([f for f in findings if f.get('severity') == 'MEDIUM'])
        low_count = len([f for f in findings if f.get('severity') == 'LOW'])
        
        mermaid_code = f"""
flowchart TD
    %% Risk Assessment Flow
    %% Generated by Application Intelligence Platform
    
    classDef high fill:#e74c3c,stroke:#333,stroke-width:2px,color:#fff
    classDef medium fill:#f39c12,stroke:#333,stroke-width:2px,color:#fff
    classDef low fill:#27ae60,stroke:#333,stroke-width:2px,color:#fff
    classDef process fill:#3498db,stroke:#333,stroke-width:2px,color:#fff
    
    A[Risk Assessment] --> B[Vulnerability Scan]
    B --> C[Categorize Findings]
    
    C --> D[{high_count} High Risk]
    C --> E[{medium_count} Medium Risk]
    C --> F[{low_count} Low Risk]
    
    D --> G[Immediate Action Required]
    E --> H[Plan Remediation]
    F --> I[Monitor and Track]
    
    G --> J[Emergency Patch]
    H --> K[Scheduled Update]
    I --> L[Regular Review]
    
    J --> M[Validation Testing]
    K --> M
    L --> M
    
    M --> N[Risk Mitigation Complete]
    N --> O[Continuous Monitoring]
    
    class A,B,C,M,N,O process
    class D,G,J high
    class E,H,K medium
    class F,I,L low
"""
        
        return mermaid_code
    
    def _generate_migration_strategy_dot(self, components: Dict[str, Any], intelligence_data: Dict[str, Any]) -> str:
        """Generate Graphviz DOT code for migration strategy"""
        dot_code = """
digraph MigrationStrategy {
    rankdir=TB;
    node [shape=box, style=filled, fontname="Arial", fontsize=10];
    edge [fontname="Arial", fontsize=8];
    
    // Migration phases
    node [fillcolor="#007bd3", fontcolor="white"];
    {
        Assessment [label="Assessment\\nPhase"];
        Planning [label="Planning\\nPhase"];
        Execution [label="Execution\\nPhase"];
        Validation [label="Validation\\nPhase"];
    }
    
    // Current state
    node [fillcolor="#f39c12", fontcolor="white"];
    {
        CurrentState [label="Current State\\nLegacy System"];
    }
    
    // Target state
    node [fillcolor="#27ae60", fontcolor="white"];
    {
        TargetState [label="Target State\\nModernized System"];
    }
    
    // Migration components
    node [fillcolor="#48b0f1", fontcolor="white"];
    {
"""
        
        # Add components based on migration readiness
        for name, comp in components.items():
            node_id = name.replace('-', '_').replace(' ', '_')
            language = comp.get('language', 'unknown')
            dot_code += f'        {node_id} [label="{name}\\n({language})"];\n'
        
        dot_code += """    }
    
    // Migration flow
    CurrentState -> Assessment;
    Assessment -> Planning;
    Planning -> Execution;
    Execution -> Validation;
    Validation -> TargetState;
    
    // Component migration paths
    Assessment -> {
"""
        
        # Add component migration paths
        for name, comp in components.items():
            node_id = name.replace('-', '_').replace(' ', '_')
            dot_code += f'        {node_id};\n'
        
        dot_code += """    }
    
    // Components to target
    {
"""
        
        for name, comp in components.items():
            node_id = name.replace('-', '_').replace(' ', '_')
            dot_code += f'        {node_id};\n'
        
        dot_code += """    } -> TargetState;
    
    // Risk factors
    node [fillcolor="#e74c3c", fontcolor="white", shape=ellipse];
    {
        SecurityRisk [label="Security\\nRisks"];
        TechnicalDebt [label="Technical\\nDebt"];
        Dependencies [label="Legacy\\nDependencies"];
    }
    
    // Risk connections
    edge [color="red", style=dashed];
    SecurityRisk -> Planning;
    TechnicalDebt -> Planning;
    Dependencies -> Planning;
}
"""
        
        return dot_code
    
    def _render_mermaid_diagram(self, mermaid_code: str, output_path: Path) -> bool:
        """Render Mermaid diagram to PNG"""
        try:
            if not self.mermaid_available:
                print("WARNING [MERMAID] Mermaid CLI not available, trying online rendering")
                return self._render_mermaid_online(mermaid_code, output_path)
            
            # Create temporary file for Mermaid code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as tmp_file:
                tmp_file.write(mermaid_code)
                tmp_file_path = tmp_file.name
            
            try:
                # Render using Mermaid CLI
                result = subprocess.run([
                    'mmdc', '-i', tmp_file_path, '-o', str(output_path),
                    '--theme', 'default', '--backgroundColor', 'white',
                    '--width', '1200', '--height', '800'
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print(f"SUCCESS [MERMAID] Rendered diagram: {output_path.name}")
                    return True
                else:
                    print(f"ERROR [MERMAID] Error rendering diagram: {result.stderr}")
                    return False
                    
            finally:
                # Clean up temporary file
                os.unlink(tmp_file_path)
                
        except Exception as e:
            print(f"WARNING [MERMAID] Error rendering diagram: {e}")
            return False
    
    def _render_mermaid_online(self, mermaid_code: str, output_path: Path) -> bool:
        """Render Mermaid diagram using online service"""
        try:
            # Use Mermaid online service
            url = "https://mermaid.ink/img/" + base64.b64encode(mermaid_code.encode()).decode()
            
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"SUCCESS [MERMAID-ONLINE] Rendered diagram: {output_path.name}")
                return True
            else:
                print(f"ERROR [MERMAID-ONLINE] Error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"WARNING [MERMAID-ONLINE] Error: {e}")
            return False
    
    def _render_graphviz_diagram(self, dot_code: str, output_path: Path) -> bool:
        """Render Graphviz diagram to PNG"""
        try:
            if not self.graphviz_available:
                print("WARNING [GRAPHVIZ] Graphviz not available")
                return False
            
            # Render using Graphviz
            result = subprocess.run([
                'dot', '-Tpng', '-o', str(output_path)
            ], input=dot_code, text=True, capture_output=True, timeout=30)
            
            if result.returncode == 0:
                print(f"SUCCESS [GRAPHVIZ] Rendered diagram: {output_path.name}")
                return True
            else:
                print(f"ERROR [GRAPHVIZ] Error rendering diagram: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"WARNING [GRAPHVIZ] Error rendering diagram: {e}")
            return False
    
    def create_user_journey_map(self, intelligence_data: Dict[str, Any]) -> Optional[str]:
        """Create user journey map using Mermaid"""
        try:
            components = intelligence_data.get('components', {})
            external_services = intelligence_data.get('summary', {}).get('external_services', [])
            
            if not components:
                return None
            
            # Create user journey map
            mermaid_code = """
graph TD
    A[User] --> B[Access Application]
    B --> C{Authentication Required?}
    C -->|Yes| D[Login/Register]
    C -->|No| E[Direct Access]
    D --> E
    E --> F[Load Balancer]
    F --> G[Application Layer]
    G --> H[Business Logic]
    H --> I{Data Required?}
    I -->|Yes| J[Data Layer]
    I -->|No| K[Response]
    J --> L{External Services?}
    L -->|Yes| M[External APIs]
    L -->|No| N[Database]
    M --> O[Process Data]
    N --> O
    O --> K
    K --> P[User Interface]
    P --> Q[User Experience]
    
    classDef userClass fill:#3498db,stroke:#2980b9,stroke-width:2px,color:#fff
    classDef systemClass fill:#e74c3c,stroke:#c0392b,stroke-width:2px,color:#fff
    classDef dataClass fill:#27ae60,stroke:#229954,stroke-width:2px,color:#fff
    classDef externalClass fill:#f39c12,stroke:#e67e22,stroke-width:2px,color:#fff
    
    class A,Q userClass
    class B,C,D,E,F,G,H,I,K,P systemClass
    class J,N,O dataClass
    class L,M externalClass
"""
            
            output_path = self.charts_dir / "user_journey_map.png"
            
            if self._render_mermaid_diagram(mermaid_code, output_path):
                return str(output_path)
            else:
                return None
                
        except Exception as e:
            print(f"WARNING [MERMAID] Error creating user journey map: {e}")
            return None
    
    def create_business_flow_diagram(self, intelligence_data: Dict[str, Any]) -> Optional[str]:
        """Create business flow diagram using Mermaid"""
        try:
            components = intelligence_data.get('components', {})
            external_services = intelligence_data.get('summary', {}).get('external_services', [])
            
            if not components:
                return None
            
            # Create business flow diagram
            component_names = list(components.keys())
            
            mermaid_code = "graph LR\n"
            mermaid_code += "    Start([Business Process Start]) --> Input[Input/Request]\n"
            
            # Add components in flow
            for i, comp_name in enumerate(component_names):
                safe_name = comp_name.replace('-', '_').replace(' ', '_')
                if i == 0:
                    mermaid_code += f"    Input --> {safe_name}[{comp_name}]\n"
                else:
                    prev_comp = component_names[i-1].replace('-', '_').replace(' ', '_')
                    mermaid_code += f"    {prev_comp} --> {safe_name}[{comp_name}]\n"
            
            # Add external services
            if external_services:
                last_comp = component_names[-1].replace('-', '_').replace(' ', '_')
                mermaid_code += f"    {last_comp} --> External{{External Services}}\n"
                
                for service in external_services:
                    safe_service = service.replace('-', '_').replace(' ', '_')
                    mermaid_code += f"    External --> {safe_service}[{service}]\n"
                    mermaid_code += f"    {safe_service} --> Response[Response]\n"
                
                mermaid_code += "    Response --> End([Process Complete])\n"
            else:
                last_comp = component_names[-1].replace('-', '_').replace(' ', '_')
                mermaid_code += f"    {last_comp} --> End([Process Complete])\n"
            
            # Add styling
            mermaid_code += """
    classDef processClass fill:#3498db,stroke:#2980b9,stroke-width:2px,color:#fff
    classDef componentClass fill:#e74c3c,stroke:#c0392b,stroke-width:2px,color:#fff
    classDef externalClass fill:#f39c12,stroke:#e67e22,stroke-width:2px,color:#fff
    classDef endClass fill:#27ae60,stroke:#229954,stroke-width:2px,color:#fff
    
    class Start,End endClass
    class Input,Response processClass
    class External externalClass
"""
            
            # Apply component styling
            for comp_name in component_names:
                safe_name = comp_name.replace('-', '_').replace(' ', '_')
                mermaid_code += f"    class {safe_name} componentClass\n"
            
            # Apply external service styling
            for service in external_services:
                safe_service = service.replace('-', '_').replace(' ', '_')
                mermaid_code += f"    class {safe_service} externalClass\n"
            
            output_path = self.charts_dir / "business_flow_diagram.png"
            
            if self._render_mermaid_diagram(mermaid_code, output_path):
                return str(output_path)
            else:
                return None
                
        except Exception as e:
            print(f"WARNING [MERMAID] Error creating business flow diagram: {e}")
            return None