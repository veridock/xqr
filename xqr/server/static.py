"""
Static content for the XQR web interface.

This module contains the HTML, CSS, and JavaScript code for the web interface.
"""

# Main HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>File Editor Server</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .section { 
            margin: 20px 0; 
            padding: 15px; 
            border: 1px solid #ddd; 
            border-radius: 5px; 
        }
        input, textarea, select { 
            padding: 8px; 
            margin: 5px; 
            width: 300px; 
            max-width: 100%;
            box-sizing: border-box;
        }
        button { 
            padding: 10px 15px; 
            background: #007cba; 
            color: white; 
            border: none; 
            border-radius: 3px; 
            cursor: pointer; 
            margin: 5px;
        }
        button:hover { 
            background: #005a87; 
        }
        .result { 
            background: #f5f5f5; 
            padding: 10px; 
            margin: 10px 0; 
            border-radius: 3px; 
            font-family: monospace; 
            white-space: pre-wrap;
            overflow-x: auto;
            max-height: 300px;
        }
        .error { 
            background: #ffe6e6; 
            color: #d00; 
        }
        .success { 
            background: #e6ffe6; 
            color: #0a0; 
        }
        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛠️ Universal File Editor Server</h1>

        <div class="section">
            <h3>1. Load File</h3>
            <input type="text" id="filePath" placeholder="File path (e.g., ./data.svg)" value="./example.svg">
            <button onclick="loadFile()">Load</button>
            <div id="loadResult" class="result"></div>
        </div>

        <div class="section">
            <h3>2. XPath/CSS Queries</h3>
            <input type="text" id="query" placeholder="XPath (e.g., //text[@id='title']) or CSS (e.g., .my-class)">
            <select id="queryType">
                <option value="xpath">XPath</option>
                <option value="css">CSS Selector</option>
            </select>
            <button onclick="queryElements()">Execute</button>
            <div id="queryResult" class="result"></div>
        </div>

        <div class="section">
            <h3>3. Edit Elements</h3>
            <input type="text" id="updateXPath" placeholder="XPath of element to edit">
            <select id="updateType">
                <option value="text">Text</option>
                <option value="attribute">Attribute</option>
            </select>
            <input type="text" id="attributeName" placeholder="Attribute name (if attribute)" class="hidden">
            <div style="margin: 10px 5px;">
                <textarea id="newValue" placeholder="New value" style="width: 100%; min-height: 80px;"></textarea>
            </div>
            <button onclick="updateElement()">Update</button>
            <div id="updateResult" class="result"></div>
        </div>

        <div class="section">
            <h3>4. Save Changes</h3>
            <input type="text" id="savePath" placeholder="Save path (empty = overwrite)">
            <button onclick="saveFile()">Save</button>
            <div id="saveResult" class="result"></div>
        </div>
    </div>

    <script>
        // Toggle attribute name field based on update type
        document.getElementById('updateType').addEventListener('change', function() {
            const attributeField = document.getElementById('attributeName');
            attributeField.classList.toggle('hidden', this.value !== 'attribute');
        });

        // Initialize hidden state
        document.getElementById('attributeName').classList.add('hidden');

        // API client
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

        // Load file
        async function loadFile() {
            const filePath = document.getElementById('filePath').value;
            const result = await apiCall('/api/load', {file_path: filePath});
            const resultElement = document.getElementById('loadResult');
            resultElement.textContent = JSON.stringify(result, null, 2);
            resultElement.className = 'result ' + (result.success ? 'success' : 'error');
        }

        // Query elements
        async function queryElements() {
            const query = document.getElementById('query').value;
            const queryType = document.getElementById('queryType').value;
            const result = await apiCall('/api/query', {query, type: queryType});
            const resultElement = document.getElementById('queryResult');
            resultElement.textContent = JSON.stringify(result, null, 2);
            resultElement.className = 'result ' + (result.success ? 'success' : 'error');
        }

        // Update element
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
            const resultElement = document.getElementById('updateResult');
            resultElement.textContent = JSON.stringify(result, null, 2);
            resultElement.className = 'result ' + (result.success ? 'success' : 'error');
        }

        // Save file
        async function saveFile() {
            const savePath = document.getElementById('savePath').value;
            const result = await apiCall('/api/save', {output_path: savePath || null});
            const resultElement = document.getElementById('saveResult');
            resultElement.textContent = JSON.stringify(result, null, 2);
            resultElement.className = 'result ' + (result.success ? 'success' : 'error');
        }
    </script>
</body>
</html>
"""
