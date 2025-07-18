"""
Directory structure analyzer that fixes component naming issues
This prevents components from being named 'src' instead of their actual names
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass

@dataclass
class DirectoryStructureInfo:
    """Information about the directory structure"""
    name: str
    path: str
    parent: Optional[str]
    children: List[str]
    depth: int
    is_source_directory: bool
    is_component_root: bool
    contains_build_files: bool
    contains_source_files: bool
    language_indicators: Dict[str, List[str]]

class DirectoryStructureAnalyzer:
    """Analyzes directory structure to properly identify component boundaries"""
    
    def __init__(self):
        # Build file indicators
        self.build_file_indicators = {
            'java': ['pom.xml', 'build.gradle', 'gradle.properties', 'settings.gradle'],
            'nodejs': ['package.json', 'package-lock.json', 'yarn.lock'],
            'python': ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile'],
            'dotnet': ['*.csproj', '*.sln', 'project.json', 'packages.config'],
            'go': ['go.mod', 'go.sum'],
            'rust': ['Cargo.toml', 'Cargo.lock'],
            'ruby': ['Gemfile', 'Gemfile.lock'],
            'php': ['composer.json', 'composer.lock']
        }
        
        # Source directory patterns
        self.source_directory_patterns = [
            'src', 'source', 'lib', 'app', 'main', 'code',
            'pkg', 'internal', 'cmd', 'api', 'web', 'ui',
            'frontend', 'backend', 'server', 'client'
        ]
        
        # Non-component directories to skip
        self.skip_directories = {
            '.git', '.svn', '.hg', 'node_modules', '__pycache__',
            'target', 'build', 'dist', 'out', 'bin', 'obj',
            '.idea', '.vscode', '.settings', 'tmp', 'temp',
            'logs', 'log', 'cache', '.cache', 'coverage',
            'test_results', 'reports', 'documentation', 'docs'
        }
    
    def analyze_directory_structure(self, repo_path: str) -> Dict[str, DirectoryStructureInfo]:
        """Analyze the directory structure to identify component boundaries"""
        print(f"DIR-ANALYZER Analyzing directory structure for {repo_path}")
        
        directory_info = {}
        
        # Walk through all directories
        for root, dirs, files in os.walk(repo_path):
            # Filter out directories to skip
            dirs[:] = [d for d in dirs if d not in self.skip_directories]
            
            relative_path = os.path.relpath(root, repo_path)
            if relative_path == '.':
                dir_name = os.path.basename(repo_path)
                relative_path = '.'
            else:
                dir_name = os.path.basename(root)
            
            # Analyze this directory
            dir_info = self._analyze_directory(root, relative_path, dir_name, files)
            directory_info[relative_path] = dir_info
        
        # Post-process to identify component roots
        self._identify_component_roots(directory_info)
        
        print(f"DIR-ANALYZER Found {len(directory_info)} directories")
        return directory_info
    
    def _analyze_directory(self, full_path: str, relative_path: str, dir_name: str, files: List[str]) -> DirectoryStructureInfo:
        """Analyze a single directory"""
        
        # Determine parent
        parent = None
        if relative_path != '.':
            parent_path = os.path.dirname(relative_path)
            parent = parent_path if parent_path != '.' else None
        
        # Determine depth
        depth = len(relative_path.split(os.sep)) - 1 if relative_path != '.' else 0
        
        # Check if it's a source directory
        is_source_directory = dir_name.lower() in self.source_directory_patterns
        
        # Check for build files
        contains_build_files = False
        language_indicators = {}
        
        for language, indicators in self.build_file_indicators.items():
            found_files = []
            for indicator in indicators:
                if indicator.startswith('*'):
                    # Handle glob patterns
                    pattern = indicator[1:]
                    found_files.extend([f for f in files if f.endswith(pattern)])
                else:
                    # Exact match
                    if indicator in files:
                        found_files.append(indicator)
            
            if found_files:
                contains_build_files = True
                language_indicators[language] = found_files
        
        # Check for source files
        contains_source_files = any(
            f.endswith(('.py', '.java', '.js', '.ts', '.go', '.rs', '.rb', '.php', '.cs', '.scala', '.kt'))
            for f in files
        )
        
        # Check for Docker files
        has_docker = any(f.lower().startswith('dockerfile') for f in files)
        if has_docker:
            contains_build_files = True
            language_indicators['docker'] = [f for f in files if f.lower().startswith('dockerfile')]
        
        return DirectoryStructureInfo(
            name=dir_name,
            path=relative_path,
            parent=parent,
            children=[],  # Will be populated later
            depth=depth,
            is_source_directory=is_source_directory,
            is_component_root=False,  # Will be determined later
            contains_build_files=contains_build_files,
            contains_source_files=contains_source_files,
            language_indicators=language_indicators
        )
    
    def _identify_component_roots(self, directory_info: Dict[str, DirectoryStructureInfo]):
        """Identify which directories are component roots"""
        
        # Populate children relationships
        for path, info in directory_info.items():
            if info.parent and info.parent in directory_info:
                directory_info[info.parent].children.append(path)
        
        # Identify component roots based on various criteria
        for path, info in directory_info.items():
            info.is_component_root = self._is_component_root(info, directory_info)
    
    def _is_component_root(self, info: DirectoryStructureInfo, all_dirs: Dict[str, DirectoryStructureInfo]) -> bool:
        """Determine if a directory is a component root"""
        
        # Rule 1: Has build files (strongest indicator)
        if info.contains_build_files:
            return True
        
        # Rule 2: Has Docker files
        if 'docker' in info.language_indicators:
            return True
        
        # Rule 3: Top-level directories with source files
        if info.depth == 1 and info.contains_source_files:
            return True
        
        # Rule 4: Named like a service/component and has source files
        service_like_names = ['service', 'api', 'web', 'app', 'server', 'client', 'worker', 'processor']
        if any(name in info.name.lower() for name in service_like_names) and info.contains_source_files:
            return True
        
        # Rule 5: Has children that are source directories
        for child_path in info.children:
            if child_path in all_dirs:
                child = all_dirs[child_path]
                if child.is_source_directory:
                    return True
        
        return False
    
    def get_component_roots(self, directory_info: Dict[str, DirectoryStructureInfo]) -> List[DirectoryStructureInfo]:
        """Get all directories that are component roots"""
        return [info for info in directory_info.values() if info.is_component_root]
    
    def get_proper_component_name(self, component_root: DirectoryStructureInfo, 
                                 directory_info: Dict[str, DirectoryStructureInfo]) -> str:
        """Get the proper component name, avoiding 'src' naming issues"""
        
        # If the component root is 'src', look at its parent
        if component_root.name.lower() == 'src' and component_root.parent:
            parent_info = directory_info.get(component_root.parent)
            if parent_info:
                return parent_info.name
        
        # If the component root is a source directory, look at its parent
        if component_root.is_source_directory and component_root.parent:
            parent_info = directory_info.get(component_root.parent)
            if parent_info:
                return parent_info.name
        
        # Otherwise, use the directory name
        return component_root.name
    
    def get_component_language(self, component_root: DirectoryStructureInfo,
                              directory_info: Dict[str, DirectoryStructureInfo]) -> str:
        """Get the primary language for a component"""
        
        # Collect language indicators from this directory and its children
        all_indicators = {}
        
        # Add indicators from this directory
        for lang, files in component_root.language_indicators.items():
            all_indicators[lang] = all_indicators.get(lang, 0) + len(files)
        
        # Add indicators from children
        for child_path in component_root.children:
            if child_path in directory_info:
                child = directory_info[child_path]
                for lang, files in child.language_indicators.items():
                    all_indicators[lang] = all_indicators.get(lang, 0) + len(files)
        
        # Remove docker from language consideration
        if 'docker' in all_indicators:
            del all_indicators['docker']
        
        # Return the language with the most indicators
        if all_indicators:
            return max(all_indicators.items(), key=lambda x: x[1])[0]
        
        return 'unknown'
    
    def get_component_summary(self, component_root: DirectoryStructureInfo,
                             directory_info: Dict[str, DirectoryStructureInfo]) -> Dict[str, Any]:
        """Get a summary of the component"""
        
        proper_name = self.get_proper_component_name(component_root, directory_info)
        language = self.get_component_language(component_root, directory_info)
        
        return {
            'name': proper_name,
            'directory_name': component_root.name,
            'path': component_root.path,
            'language': language,
            'depth': component_root.depth,
            'has_build_files': component_root.contains_build_files,
            'has_source_files': component_root.contains_source_files,
            'language_indicators': component_root.language_indicators,
            'children_count': len(component_root.children),
            'naming_fixed': proper_name != component_root.name
        }