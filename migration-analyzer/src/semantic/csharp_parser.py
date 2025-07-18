import re
from typing import List, Dict, Optional
from src.semantic.base_parser import LanguageParser
from src.core.models import *

class CSharpParser(LanguageParser):
    def can_parse(self, file_extension: str) -> bool:
        return file_extension.lower() in ['.cs']
    
    def parse(self, file_content: str, file_path: str) -> SemanticCodeMap:
        code_map = SemanticCodeMap(
            file_path=file_path,
            language="csharp"
        )
        
        try:
            self._extract_classes_and_methods(file_content, code_map)
            self._extract_api_controllers(file_content, code_map)
            self._extract_minimal_api_endpoints(file_content, code_map)
            self._extract_database_operations(file_content, code_map)
            self._extract_http_calls(file_content, code_map)
            self._extract_wcf_services(file_content, code_map)
            self._extract_grpc_services(file_content, code_map)
        except Exception as e:
            code_map.notes.append(f"Error parsing C#: {str(e)}")
        
        return code_map
    
    def _extract_classes_and_methods(self, content: str, code_map: SemanticCodeMap):
        """Extract C# classes and methods"""
        # Class patterns
        class_pattern = r'(?:public|private|protected|internal)?\s*(?:static|abstract|sealed)?\s*class\s+(\w+)(?:\s*:\s*([^{]+))?'
        
        for match in re.finditer(class_pattern, content, re.MULTILINE):
            class_name = match.group(1)
            inheritance = match.group(2).strip() if match.group(2) else ""
            line_num = content[:match.start()].count('\n') + 1
            
            # Extract base classes/interfaces
            base_classes = []
            if inheritance:
                base_classes = [b.strip() for b in inheritance.split(',')]
            
            class_info = ClassInfo(
                name=class_name,
                start_line=line_num,
                end_line=line_num,  # Will be updated if we find the closing brace
                methods=[],
                base_classes=base_classes
            )
            
            # Find methods within this class
            class_start = match.end()
            brace_count = 0
            class_body_start = content.find('{', class_start)
            
            if class_body_start != -1:
                # Find the end of the class
                pos = class_body_start
                while pos < len(content):
                    if content[pos] == '{':
                        brace_count += 1
                    elif content[pos] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            class_body_end = pos
                            break
                    pos += 1
                else:
                    class_body_end = len(content)
                
                class_body = content[class_body_start:class_body_end]
                
                # Extract methods from class body
                method_pattern = r'(?:public|private|protected|internal)?\s*(?:static|virtual|override|abstract)?\s*(?:async\s+)?(?:Task<?[^>]*>?|void|\w+)\s+(\w+)\s*\('
                
                for method_match in re.finditer(method_pattern, class_body):
                    method_name = method_match.group(1)
                    method_line = content[:class_body_start + method_match.start()].count('\n') + 1
                    
                    # Skip constructors and properties
                    if method_name != class_name and not method_name.startswith('get_') and not method_name.startswith('set_'):
                        class_info.methods.append(method_name)
                        
                        # Create function info
                        func_info = FunctionInfo(
                            name=f"{class_name}.{method_name}",
                            start_line=method_line,
                            end_line=method_line,
                            decorators=[]
                        )
                        code_map.functions.append(func_info)
            
            code_map.classes.append(class_info)
    
    def _extract_api_controllers(self, content: str, code_map: SemanticCodeMap):
        """Extract ASP.NET Web API and MVC controller endpoints"""
        # Controller class detection
        controller_pattern = r'(?:public\s+)?class\s+(\w+Controller)\s*:\s*(?:ApiController|Controller|ControllerBase)'
        
        for controller_match in re.finditer(controller_pattern, content):
            controller_name = controller_match.group(1)
            controller_start = controller_match.end()
            
            # Find controller body
            brace_start = content.find('{', controller_start)
            if brace_start == -1:
                continue
                
            brace_count = 0
            pos = brace_start
            while pos < len(content):
                if content[pos] == '{':
                    brace_count += 1
                elif content[pos] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        controller_body = content[brace_start:pos]
                        break
                pos += 1
            else:
                controller_body = content[brace_start:]
            
            # Extract action methods with routing attributes
            self._extract_controller_actions(controller_body, controller_name, brace_start, content, code_map)
    
    def _extract_controller_actions(self, controller_body: str, controller_name: str, body_start: int, full_content: str, code_map: SemanticCodeMap):
        """Extract action methods from controller body"""
        # Extract base route from controller class or just above controller body
        base_route = ""
        class_route_match = re.search(r'\[Route\("([^"]+)"\)]', full_content[:body_start])
        if class_route_match:
            base_route = class_route_match.group(1)
        
        # Find all HTTP method attributes and their corresponding actions
        # Look for patterns like [HttpGet] followed by a method
        attribute_patterns = [
            (r'\[HttpGet(?:\("([^"]+)"\))?\]\s*(?:\[.*?\]\s*)*(?:public\s+)?(?:async\s+)?(?:Task<?[^>]*>?|ActionResult|IActionResult|\w+)\s+(\w+)\s*\(', 'GET'),
            (r'\[HttpPost(?:\("([^"]+)"\))?\]\s*(?:\[.*?\]\s*)*(?:public\s+)?(?:async\s+)?(?:Task<?[^>]*>?|ActionResult|IActionResult|\w+)\s+(\w+)\s*\(', 'POST'),
            (r'\[HttpPut(?:\("([^"]+)"\))?\]\s*(?:\[.*?\]\s*)*(?:public\s+)?(?:async\s+)?(?:Task<?[^>]*>?|ActionResult|IActionResult|\w+)\s+(\w+)\s*\(', 'PUT'),
            (r'\[HttpDelete(?:\("([^"]+)"\))?\]\s*(?:\[.*?\]\s*)*(?:public\s+)?(?:async\s+)?(?:Task<?[^>]*>?|ActionResult|IActionResult|\w+)\s+(\w+)\s*\(', 'DELETE'),
            (r'\[HttpPatch(?:\("([^"]+)"\))?\]\s*(?:\[.*?\]\s*)*(?:public\s+)?(?:async\s+)?(?:Task<?[^>]*>?|ActionResult|IActionResult|\w+)\s+(\w+)\s*\(', 'PATCH'),
        ]
        
        for pattern, http_method in attribute_patterns:
            for match in re.finditer(pattern, controller_body, re.DOTALL):
                route_path = match.group(1) if match.group(1) else ""
                action_name = match.group(2)
                
                # Skip if this looks like a constructor (same name as class)
                if action_name == controller_name.replace('Controller', ''):
                    continue
                
                # Construct full path
                if route_path:
                    # If route_path is specified in the attribute
                    if base_route:
                        # Replace [controller] placeholder
                        if '[controller]' in base_route:
                            controller_route = controller_name.replace('Controller', '').lower()
                            base_route = base_route.replace('[controller]', controller_route)
                        full_path = f"/{base_route.strip('/')}/{route_path.strip('/')}"
                    else:
                        full_path = f"/{route_path.strip('/')}"
                else:
                    # Use default routing convention
                    controller_route = controller_name.replace('Controller', '').lower()
                    if base_route:
                        if '[controller]' in base_route:
                            base_route = base_route.replace('[controller]', controller_route)
                        full_path = f"/{base_route.strip('/')}"
                    else:
                        full_path = f"/{controller_route}"
                
                # Clean up the path
                full_path = full_path.replace('//', '/')
                
                line_num = full_content[:body_start + match.start()].count('\n') + 1
                
                endpoint = ApiEndpoint(
                    path=full_path,
                    methods=[http_method],
                    handler_function=f"{controller_name}.{action_name}",
                    line_number=line_num
                )
                code_map.api_endpoints.append(endpoint)
    
    def _extract_minimal_api_endpoints(self, content: str, code_map: SemanticCodeMap):
        """Extract .NET 6+ Minimal API endpoints"""
        minimal_api_patterns = [
            (r'app\.MapGet\s*\(\s*"([^"]+)"\s*,', 'GET'),
            (r'app\.MapPost\s*\(\s*"([^"]+)"\s*,', 'POST'),
            (r'app\.MapPut\s*\(\s*"([^"]+)"\s*,', 'PUT'),
            (r'app\.MapDelete\s*\(\s*"([^"]+)"\s*,', 'DELETE'),
            (r'app\.MapPatch\s*\(\s*"([^"]+)"\s*,', 'PATCH'),
            (r'app\.Map\s*\(\s*"([^"]+)"\s*,', 'GET'),  # Generic Map defaults to GET
        ]
        
        for pattern, method in minimal_api_patterns:
            for match in re.finditer(pattern, content):
                path = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                
                endpoint = ApiEndpoint(
                    path=path,
                    methods=[method],
                    handler_function="MinimalAPI",
                    line_number=line_num
                )
                code_map.api_endpoints.append(endpoint)
    
    def _extract_database_operations(self, content: str, code_map: SemanticCodeMap):
        """Extract database operations from C# code"""
        # Entity Framework patterns
        ef_patterns = [
            (r'\.Find\s*\(', 'EF_FIND'),
            (r'\.FirstOrDefault\s*\(', 'EF_SELECT'),
            (r'\.Where\s*\(', 'EF_SELECT'),
            (r'\.Add\s*\(', 'EF_INSERT'),
            (r'\.Update\s*\(', 'EF_UPDATE'),
            (r'\.Remove\s*\(', 'EF_DELETE'),
            (r'\.SaveChanges\s*\(', 'EF_SAVE'),
            (r'\.SaveChangesAsync\s*\(', 'EF_SAVE_ASYNC'),
            (r'\.FromSqlRaw\s*\(', 'EF_RAW_SQL'),
            (r'\.ExecuteSqlRaw\s*\(', 'EF_EXECUTE_SQL'),
        ]
        
        for pattern, operation in ef_patterns:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                
                db_interaction = DatabaseInteraction(
                    operation=operation,
                    line_number=line_num
                )
                code_map.database_interactions.append(db_interaction)
        
        # ADO.NET patterns
        ado_patterns = [
            (r'SqlCommand\s*\(', 'ADO_COMMAND'),
            (r'ExecuteReader\s*\(', 'ADO_SELECT'),
            (r'ExecuteNonQuery\s*\(', 'ADO_EXECUTE'),
            (r'ExecuteScalar\s*\(', 'ADO_SCALAR'),
            (r'SqlConnection\s*\(', 'ADO_CONNECTION'),
        ]
        
        for pattern, operation in ado_patterns:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                
                db_interaction = DatabaseInteraction(
                    operation=operation,
                    line_number=line_num
                )
                code_map.database_interactions.append(db_interaction)
        
        # Dapper patterns
        dapper_patterns = [
            (r'\.Query\s*<', 'DAPPER_QUERY'),
            (r'\.QueryAsync\s*<', 'DAPPER_QUERY_ASYNC'),
            (r'\.Execute\s*\(', 'DAPPER_EXECUTE'),
            (r'\.ExecuteAsync\s*\(', 'DAPPER_EXECUTE_ASYNC'),
        ]
        
        for pattern, operation in dapper_patterns:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                
                db_interaction = DatabaseInteraction(
                    operation=operation,
                    line_number=line_num
                )
                code_map.database_interactions.append(db_interaction)
    
    def _extract_http_calls(self, content: str, code_map: SemanticCodeMap):
        """Extract HTTP client calls"""
        http_patterns = [
            (r'HttpClient\s*\(', 'HTTP_CLIENT'),
            (r'\.GetAsync\s*\(', 'GET'),
            (r'\.PostAsync\s*\(', 'POST'),
            (r'\.PutAsync\s*\(', 'PUT'),
            (r'\.DeleteAsync\s*\(', 'DELETE'),
            (r'\.SendAsync\s*\(', 'SEND'),
            (r'WebRequest\.Create\s*\(', 'WEB_REQUEST'),
            (r'RestClient\s*\(', 'REST_CLIENT'),
        ]
        
        for pattern, method in http_patterns:
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                
                # Try to extract URL from the same line
                line_start = content.rfind('\n', 0, match.start()) + 1
                line_end = content.find('\n', match.end())
                if line_end == -1:
                    line_end = len(content)
                
                line_content = content[line_start:line_end]
                
                # Look for string literals that might be URLs
                url_match = re.search(r'"(https?://[^"]+)"', line_content)
                url = url_match.group(1) if url_match else "unknown"
                
                if method != 'HTTP_CLIENT' and method != 'WEB_REQUEST' and method != 'REST_CLIENT':
                    http_call = HttpCall(
                        url=url,
                        method=method,
                        line_number=line_num
                    )
                    code_map.outbound_http_calls.append(http_call)
    
    def _extract_wcf_services(self, content: str, code_map: SemanticCodeMap):
        """Extract WCF service contracts and operations"""
        # ServiceContract attribute
        service_contract_pattern = r'\[ServiceContract\]'
        operation_contract_pattern = r'\[OperationContract\]'
        
        if re.search(service_contract_pattern, content):
            # Find operation contracts
            for match in re.finditer(operation_contract_pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                
                # Look for the method after the attribute
                remaining = content[match.end():]
                method_match = re.search(r'(\w+)\s+(\w+)\s*\(', remaining)
                if method_match:
                    method_name = method_match.group(2)
                    
                    endpoint = ApiEndpoint(
                        path=f"/wcf/{method_name}",
                        methods=['SOAP'],
                        handler_function=method_name,
                        line_number=line_num
                    )
                    code_map.api_endpoints.append(endpoint)
    
    def _extract_grpc_services(self, content: str, code_map: SemanticCodeMap):
        """Extract gRPC service definitions"""
        # gRPC service base class
        grpc_service_pattern = r'class\s+(\w+)\s*:\s*(\w+\.)?(\w+)Base'
        
        for match in re.finditer(grpc_service_pattern, content):
            service_name = match.group(1)
            base_class = match.group(3)
            
            if base_class and base_class.endswith('Base'):
                line_num = content[:match.start()].count('\n') + 1
                
                endpoint = ApiEndpoint(
                    path=f"/grpc/{service_name}",
                    methods=['GRPC'],
                    handler_function=service_name,
                    line_number=line_num
                )
                code_map.api_endpoints.append(endpoint)