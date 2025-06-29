"""
HTTP Server for remote file editing
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict

from .core import FileEditor, LXML_AVAILABLE


class FileEditorServer(BaseHTTPRequestHandler):
    """HTTP Server dla zdalnej edycji plików"""

    editors: Dict[str, FileEditor] = {}

    def do_GET(self):
        """Obsługa żądań GET"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)

        if path == '/':
            self._serve_interface()
        elif path == '/api/files':
            self._list_files()
        elif path.startswith('/api/file/'):
            file_path = path[10:]  # usuń /api/file/
            self._serve_file_info(file_path)
        else:
            self._send_error(404, "Not Found")

    def do_POST(self):
        """Obsługa żądań POST"""
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

    def _serve_interface(self):
        """Serwuj interfejs webowy"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>File Editor Server</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .container { max-width: 1200px; margin: 0 auto; }
                .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
                input, textarea, select { padding: 8px; margin: 5px; width: 300px; }
                button { padding: 10px 15px; background: #007cba; color: white; border: none; border-radius: 3px; cursor: pointer; }
                button:hover { background: #005a87; }
                .result { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 3px; font-family: monospace; white-space: pre-wrap; }
                .error { background: #ffe6e6; color: #d00; }
                .success { background: #e6ffe6; color: #0a0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🛠️ Universal File Editor Server</h1>

                <div class="section">
                    <h3>1. Załaduj plik</h3>
                    <input type="text" id="filePath" placeholder="Ścieżka do pliku (np. ./data.svg)" value="./example.svg">
                    <button onclick="loadFile()">Załaduj</button>
                    <div id="loadResult" class="result"></div>
                </div>

                <div class="section">
                    <h3>2. Zapytania XPath/CSS</h3>
                    <input type="text" id="query" placeholder="XPath (np. //text[@id='title']) lub CSS (np. .my-class)">
                    <select id="queryType">
                        <option value="xpath">XPath</option>
                        <option value="css">CSS Selector</option>
                    </select>
                    <button onclick="queryElements()">Wykonaj</button>
                    <div id="queryResult" class="result"></div>
                </div>

                <div class="section">
                    <h3>3. Edycja elementów</h3>
                    <input type="text" id="updateXPath" placeholder="XPath elementu do edycji">
                    <select id="updateType">
                        <option value="text">Tekst</option>
                        <option value="attribute">Atrybut</option>
                    </select>
                    <input type="text" id="attributeName" placeholder="Nazwa atrybutu (jeśli atrybut)">
                    <textarea id="newValue" placeholder="Nowa wartość"></textarea>
                    <button onclick="updateElement()">Aktualizuj</button>
                    <div id="updateResult" class="result"></div>
                </div>

                <div class="section">
                    <h3>4. Zapisz zmiany</h3>
                    <input type="text" id="savePath" placeholder="Ścieżka zapisu (puste = nadpisz)">
                    <button onclick="saveFile()">Zapisz</button>
                    <div id="saveResult" class="result"></div>
                </div>
            </div>

            <script>
                async function apiCall(endpoint, data) {
                    try {
                        const response = await fetch(endpoint, {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify(data)
                        });
                        return await response.json();
                    } catch (error) {
                        return {success: false, error: error.message};
                    }
                }

                async function loadFile() {
                    const filePath = document.getElementById('filePath').value;
                    const result = await apiCall('/api/load', {file_path: filePath});
                    document.getElementById('loadResult').textContent = JSON.stringify(result, null, 2);
                    document.getElementById('loadResult').className = 'result ' + (result.success ? 'success' : 'error');
                }

                async function queryElements() {
                    const query = document.getElementById('query').value;
                    const queryType = document.getElementById('queryType').value;
                    const result = await apiCall('/api/query', {query, type: queryType});
                    document.getElementById('queryResult').textContent = JSON.stringify(result, null, 2);
                    document.getElementById('queryResult').className = 'result ' + (result.success ? 'success' : 'error');
                }

                async function updateElement() {
                    const xpath = document.getElementById('updateXPath').value;
                    const updateType = document.getElementById('updateType').value;
                    const attributeName = document.getElementById('attributeName').value;
                    const newValue = document.getElementById('newValue').value;

                    const data = {xpath, type: updateType, value: newValue};
                    if (updateType === 'attribute') {
                        data.attribute = attributeName;
                    }

                    const result = await apiCall('/api/update', data);
                    document.getElementById('updateResult').textContent = JSON.stringify(result, null, 2);
                    document.getElementById('updateResult').className = 'result ' + (result.success ? 'success' : 'error');
                }

                async function saveFile() {
                    const savePath = document.getElementById('savePath').value;
                    const result = await apiCall('/api/save', {output_path: savePath || null});
                    document.getElementById('saveResult').textContent = JSON.stringify(result, null, 2);
                    document.getElementById('saveResult').className = 'result ' + (result.success ? 'success' : 'error');
                }
            </script>
        </body>
        </html>
        """
        self._send_response(200, html, 'text/html')

    def _load_file(self, data):
        """Załaduj plik do edycji"""
        try:
            file_path = data['file_path']
            editor = FileEditor(file_path)
            self.editors[file_path] = editor

            response = {
                'success': True,
                'message': f'File loaded: {file_path}',
                'file_type': editor.file_type,
                'elements_count': len(editor.find_by_xpath("//*")) if LXML_AVAILABLE else 0
            }
        except Exception as e:
            response = {'success': False, 'error': str(e)}

        self._send_json_response(response)

    def _query_elements(self, data):
        """Wykonaj zapytanie XPath/CSS"""
        try:
            query = data['query']
            query_type = data.get('type', 'xpath')

            # Znajdź pierwszy załadowany plik
            if not self.editors:
                raise ValueError("No files loaded")

            editor = list(self.editors.values())[0]

            if query_type == 'xpath':
                elements = editor.list_elements(query)
            else:
                elements = editor.find_by_css(query)
                # Konwertuj wyniki CSS na format podobny do XPath
                elements = [{'tag': str(elem.name), 'text': elem.get_text(), 'attributes': elem.attrs}
                            for elem in elements]

            response = {
                'success': True,
                'elements': elements,
                'count': len(elements)
            }
        except Exception as e:
            response = {'success': False, 'error': str(e)}

        self._send_json_response(response)

    def _update_element(self, data):
        """Aktualizuj element"""
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
                'message': f'Element updated successfully' if success else 'Element not found'
            }
        except Exception as e:
            response = {'success': False, 'error': str(e)}

        self._send_json_response(response)

    def _save_file(self, data):
        """Zapisz plik"""
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

    def _send_response(self, status_code, content, content_type='text/plain'):
        """Wyślij odpowiedź HTTP"""
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

    def _send_json_response(self, data):
        """Wyślij odpowiedź JSON"""
        self._send_response(200, json.dumps(data, indent=2), 'application/json')

    def _send_error(self, status_code, message):
        """Wyślij błąd"""
        self._send_response(status_code, json.dumps({'error': message}), 'application/json')


def start_server(port: int = 8080):
    """Uruchom serwer HTTP"""
    print(f"🌐 Starting File Editor Server on port {port}")
    print(f"Open http://localhost:{port} in your browser")

    server = HTTPServer(('localhost', port), FileEditorServer)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")