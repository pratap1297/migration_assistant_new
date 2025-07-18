import os
from typing import List, Dict, Optional
from pathlib import Path
from src.semantic.base_parser import LanguageParser
from src.semantic.python_parser import PythonParser
from src.semantic.java_parser import JavaParser
from src.semantic.js_parser import JavaScriptParser
from src.semantic.csharp_parser import CSharpParser
from src.core.models import SemanticCodeMap

class FactualExtractor:
    def __init__(self):
        self.parsers: Dict[str, LanguageParser] = {
            '.py': PythonParser(),
            '.java': JavaParser(),
            '.js': JavaScriptParser(),
            '.jsx': JavaScriptParser(),
            '.ts': JavaScriptParser(),
            '.tsx': JavaScriptParser(),
            '.cs': CSharpParser(),
        }
        
    def extract_repository_semantics(self, repo_path: str) -> Dict[str, List[SemanticCodeMap]]:
        """Extract semantic information from entire repository"""
        results = {}
        
        # Identify components (directories with source code)
        components = self._identify_components(repo_path)
        
        for component_name, component_path in components.items():
            results[component_name] = self.extract_component_semantics(component_path)
            
        return results
    
    def extract_component_semantics(self, component_path: str) -> List[SemanticCodeMap]:
        """Extract semantic information from a single component"""
        results = []
        
        for file_path in self._walk_source_files(component_path):
            parser = self._get_parser(file_path)
            if parser:
                try:
                    content = self._read_file(file_path)
                    result = parser.parse(content, file_path)
                    results.append(result)
                except Exception as e:
                    # Create error result
                    error_result = SemanticCodeMap(
                        file_path=file_path,
                        language="unknown",
                        notes=[f"Error parsing file: {str(e)}"]
                    )
                    results.append(error_result)
                    
        return results
    
    def _identify_components(self, repo_path: str) -> Dict[str, str]:
        """Identify components in the repository"""
        components = {}
        
        # Look for subdirectories that are components first
        found_subcomponents = False
        try:
            for item in os.listdir(repo_path):
                item_path = os.path.join(repo_path, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    if self._is_component_directory(item_path):
                        components[item] = item_path
                        found_subcomponents = True
        except (OSError, PermissionError):
            pass
            
        # If no subcomponents found, check if root is a component
        if not found_subcomponents and self._is_component_directory(repo_path):
            components['root'] = repo_path
                    
        return components
    
    def _is_component_directory(self, path: str) -> bool:
        """Check if directory contains source code"""
        indicators = [
            'package.json', 'requirements.txt', 'pom.xml', 
            'build.gradle', 'go.mod', 'Cargo.toml', 'Dockerfile',
            # .NET project files
            '*.csproj', '*.fsproj', '*.vbproj', '*.sln',
            'project.json', 'global.json', 'Directory.Build.props'
        ]
        
        # Check for indicator files
        import glob
        for indicator in indicators:
            if indicator.startswith('*'):
                # Handle glob patterns
                pattern_path = os.path.join(path, indicator)
                if glob.glob(pattern_path):
                    return True
            else:
                # Handle exact file names
                if os.path.exists(os.path.join(path, indicator)):
                    return True
                
        # Check for source files in current directory and subdirectories
        try:
            for root, dirs, files in os.walk(path):
                # Skip hidden directories but check a few levels deep
                dirs[:] = [d for d in dirs if not d.startswith('.') and 
                          d not in ['node_modules', '__pycache__', 'target', 'build']]
                
                for file in files:
                    if any(file.endswith(ext) for ext in self.parsers.keys()):
                        return True
                        
                # Don't go too deep to avoid infinite recursion
                if root.count(os.sep) - path.count(os.sep) >= 3:
                    dirs.clear()
        except (OSError, PermissionError):
            pass
                
        return False
    
    def _walk_source_files(self, directory: str) -> List[str]:
        """Walk directory and return source files"""
        source_files = []
        
        for root, dirs, files in os.walk(directory):
            # Skip hidden and common non-source directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and 
                      d not in ['node_modules', '__pycache__', 'target', 'build']]
            
            for file in files:
                if any(file.endswith(ext) for ext in self.parsers.keys()):
                    source_files.append(os.path.join(root, file))
                    
        return source_files
    
    def _get_parser(self, file_path: str) -> Optional[LanguageParser]:
        """Get appropriate parser for file"""
        ext = Path(file_path).suffix.lower()
        return self.parsers.get(ext)
    
    def _read_file(self, file_path: str) -> str:
        """Read file content"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()