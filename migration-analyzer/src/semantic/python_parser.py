import ast
import re
from typing import List, Optional
from src.semantic.base_parser import LanguageParser
from src.core.models import *

class PythonParser(LanguageParser):
    def can_parse(self, file_extension: str) -> bool:
        return file_extension.lower() in ['.py']
    
    def parse(self, file_content: str, file_path: str) -> SemanticCodeMap:
        code_map = SemanticCodeMap(
            file_path=file_path,
            language="python"
        )
        
        try:
            tree = ast.parse(file_content)
            self._extract_functions(tree, code_map)
            self._extract_classes(tree, code_map)
            self._extract_api_endpoints(tree, file_content, code_map)
            self._extract_database_operations(tree, file_content, code_map)
            self._extract_http_calls(tree, code_map)
        except SyntaxError as e:
            code_map.notes.append(f"Syntax error in parsing: {str(e)}")
        
        return code_map
    
    def _extract_functions(self, tree: ast.AST, code_map: SemanticCodeMap):
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = FunctionInfo(
                    name=node.name,
                    start_line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                    decorators=[d.id if isinstance(d, ast.Name) else 
                               ast.unparse(d) for d in node.decorator_list]
                )
                
                # Extract function calls within this function
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            func_info.calls.append(child.func.id)
                        elif isinstance(child.func, ast.Attribute):
                            func_info.calls.append(ast.unparse(child.func))
                
                code_map.functions.append(func_info)
    
    def _extract_classes(self, tree: ast.AST, code_map: SemanticCodeMap):
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = ClassInfo(
                    name=node.name,
                    start_line=node.lineno,
                    end_line=node.end_lineno or node.lineno,
                    methods=[method.name for method in node.body if isinstance(method, ast.FunctionDef)],
                    base_classes=[base.id if isinstance(base, ast.Name) else ast.unparse(base) for base in node.bases]
                )
                code_map.classes.append(class_info)
    
    def _extract_api_endpoints(self, tree: ast.AST, content: str, code_map: SemanticCodeMap):
        # Flask pattern
        flask_pattern = r'@app\.route\s*\(\s*[\'"]([^\'"]+)[\'"](?:\s*,\s*methods\s*=\s*\[([^\]]+)\])?'
        
        for match in re.finditer(flask_pattern, content):
            path = match.group(1)
            methods = []
            if match.group(2):
                methods = [m.strip().strip('"\'') for m in match.group(2).split(',')]
            else:
                methods = ['GET']  # Default Flask method
            
            # Find the function after this decorator
            lines = content[:match.end()].count('\n') + 1
            
            endpoint = ApiEndpoint(
                path=path,
                methods=methods,
                handler_function="",  # Will be filled by AST walk
                line_number=lines
            )
            code_map.api_endpoints.append(endpoint)
    
    def _extract_database_operations(self, tree: ast.AST, content: str, code_map: SemanticCodeMap):
        # Look for common database patterns
        db_patterns = [
            (r'\.execute\s*\(\s*[\'"]([^\'"]*)[\'"]\s*', 'execute'),
            (r'\.query\s*\(\s*[\'"]([^\'"]*)[\'"]\s*', 'query'),
            (r'redis\.\w+\s*\(', 'redis'),
        ]
        
        for pattern, op_type in db_patterns:
            for match in re.finditer(pattern, content):
                query = match.group(1) if match.lastindex else ""
                line_num = content[:match.start()].count('\n') + 1
                
                # Try to extract operation type from query
                operation = "UNKNOWN"
                if query:
                    first_word = query.strip().split()[0].upper()
                    if first_word in ['SELECT', 'INSERT', 'UPDATE', 'DELETE']:
                        operation = first_word
                elif op_type == 'redis':
                    operation = 'REDIS_OP'
                
                db_interaction = DatabaseInteraction(
                    operation=operation,
                    line_number=line_num,
                    raw_query=query[:100] if query else None
                )
                code_map.database_interactions.append(db_interaction)
    
    def _extract_http_calls(self, tree: ast.AST, code_map: SemanticCodeMap):
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for requests library calls
                if (isinstance(node.func, ast.Attribute) and 
                    isinstance(node.func.value, ast.Name) and 
                    node.func.value.id == 'requests'):
                    
                    method = node.func.attr.upper()
                    url = ""
                    
                    if node.args and isinstance(node.args[0], ast.Constant):
                        url = node.args[0].value
                    
                    if url:
                        http_call = HttpCall(
                            url=url,
                            method=method,
                            line_number=node.lineno,
                            is_internal=False  # Could be enhanced with logic
                        )
                        code_map.outbound_http_calls.append(http_call)