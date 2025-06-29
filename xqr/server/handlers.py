"""
Request handlers for the XQR HTTP server.

This module contains the request handlers for the HTTP server that provides
remote file editing functionality.
"""

import json
from http.server import BaseHTTPRequestHandler
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs

from xqr.core.editor import FileEditor
from xqr.server.static import HTML_TEMPLATE


class FileEditorServer(BaseHTTPRequestHandler):
    """HTTP Server for remote file editing.
    
    This class handles HTTP requests and delegates them to appropriate handlers
    for loading, querying, and modifying files.
    """
    
    # Store file editors by file path
    editors: Dict[str, FileEditor] = {}
    
    def do_GET(self) -> None:
        """Handle GET requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path == '/':
            self._serve_interface()
        elif path == '/api/files':
            self._list_files()
        elif path.startswith('/api/file/'):
            file_path = path[10:]  # Remove '/api/file/'
            self._serve_file_info(file_path)
        else:
            self._send_error(404, "Not Found")
    
    def do_POST(self) -> None:
        """Handle POST requests."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            data = json.loads(post_data)
        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON")
            return
        
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path == '/api/load':
            self._load_file(data)
        elif path == '/api/query':
            self._query_elements(data)
        elif path == '/api/update':
            self._update_element(data)
        elif path == '/api/save':
            self._save_file(data)
        else:
            self._send_error(404, "Not Found")
    
    def _serve_interface(self) -> None:
        """Serve the web interface."""
        self._send_response(200, HTML_TEMPLATE, 'text/html')
    
    def _load_file(self, data: Dict[str, Any]) -> None:
        """Load a file for editing."""
        try:
            file_path = data['file_path']
            editor = FileEditor(file_path)
            self.editors[file_path] = editor
            
            response = {
                'success': True,
                'message': f'File loaded: {file_path}',
                'file_type': editor.file_type,
                'elements_count': len(editor.find_by_xpath("//*"))
            }
        except Exception as e:
            response = {'success': False, 'error': str(e)}
        
        self._send_json_response(response)
    
    def _query_elements(self, data: Dict[str, Any]) -> None:
        """Execute XPath/CSS query on the loaded file."""
        try:
            query = data['query']
            query_type = data.get('type', 'xpath')
            
            if not self.editors:
                raise ValueError("No files loaded")
            
            editor = list(self.editors.values())[0]
            
            if query_type == 'xpath':
                elements = editor.list_elements(query)
            else:
                # For CSS selectors, we need to use the original content
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(editor.original_content, 'html.parser')
                elements = [
                    {'tag': str(elem.name), 'text': elem.get_text(), 'attributes': elem.attrs}
                    for elem in soup.select(query)
                ]
            
            response = {
                'success': True,
                'elements': elements,
                'count': len(elements)
            }
        except Exception as e:
            response = {'success': False, 'error': str(e)}
        
        self._send_json_response(response)
    
    def _update_element(self, data: Dict[str, Any]) -> None:
        """Update an element in the loaded file."""
        try:
            xpath = data['xpath']
            update_type = data['type']
            value = data['value']
            
            if not self.editors:
                raise ValueError("No files loaded")
            
            editor = list(self.editors.values())[0]
            
            if update_type == 'text':
                success = editor.set_element_text(xpath, value)
            elif update_type == 'attribute':
                attribute = data['attribute']
                success = editor.set_element_attribute(xpath, attribute, value)
            else:
                raise ValueError(f"Unknown update type: {update_type}")
            
            response = {
                'success': success,
                'message': 'Element updated successfully' if success else 'Element not found'
            }
        except Exception as e:
            response = {'success': False, 'error': str(e)}
        
        self._send_json_response(response)
    
    def _save_file(self, data: Dict[str, Any]) -> None:
        """Save the current file."""
        try:
            output_path = data.get('output_path')
            
            if not self.editors:
                raise ValueError("No files loaded")
            
            editor = list(self.editors.values())[0]
            success = editor.save(output_path)
            
            response = {
                'success': success,
                'message': f'File saved successfully to {output_path or editor.file_path}'
            }
        except Exception as e:
            response = {'success': False, 'error': str(e)}
        
        self._send_json_response(response)
    
    def _list_files(self) -> None:
        """List all loaded files."""
        files = [
            {
                'path': path,
                'file_type': editor.file_type,
                'elements_count': len(editor.find_by_xpath("//*"))
            }
            for path, editor in self.editors.items()
        ]
        
        response = {
            'success': True,
            'files': files,
            'count': len(files)
        }
        
        self._send_json_response(response)
    
    def _serve_file_info(self, file_path: str) -> None:
        """Serve information about a specific file."""
        try:
            if file_path not in self.editors:
                raise ValueError(f"File not loaded: {file_path}")
            
            editor = self.editors[file_path]
            
            response = {
                'success': True,
                'file_path': file_path,
                'file_type': editor.file_type,
                'elements_count': len(editor.find_by_xpath("//*"))
            }
        except Exception as e:
            response = {'success': False, 'error': str(e)}
        
        self._send_json_response(response)
    
    def _send_response(self, status_code: int, content: str, content_type: str = 'text/plain') -> None:
        """Send an HTTP response."""
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))
    
    def _send_json_response(self, data: Dict[str, Any]) -> None:
        """Send a JSON response."""
        self._send_response(200, json.dumps(data, indent=2), 'application/json')
    
    def _send_error(self, status_code: int, message: str) -> None:
        """Send an error response."""
        self._send_response(status_code, json.dumps({'error': message}), 'application/json')
