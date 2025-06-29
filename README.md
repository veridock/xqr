# xqr
xpath xquery xqr
# 🛠️ Universal File Editor

Powerful CLI tool for editing SVG, HTML, and XML files using XPath and CSS selectors. Edit your structured documents directly from the command line or through a web interface.

## 🚀 Features

- **Multiple File Formats**: SVG, HTML, XML support with automatic format detection
- **XPath Queries**: Full XPath 1.0 support for precise element selection
- **CSS Selectors**: CSS selector support for HTML files
- **Multiple Interfaces**: CLI commands, interactive shell, and web server
- **REST API**: Programmatic access via HTTP endpoints
- **Batch Processing**: Automate edits across multiple files
- **Backup System**: Automatic backup creation before modifications

## 📦 Installation

### Using Poetry (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/universal-file-editor.git
cd universal-file-editor

# Install with Poetry
poetry install

# Activate the environment
poetry shell
```

### Using pip

```bash
pip install universal-file-editor
```

## 🎯 Quick Start

### 1. Create Example Files
```bash
file-editor examples
```

### 2. Basic Usage
```bash
# Load and query a file
file-editor load example.svg
file-editor query "//text[@id='text1']"

# Update content
file-editor set "//text[@id='text1']" "New Content"
file-editor save
```

### 3. Interactive Shell
```bash
file-editor shell
📝 > load example.html
📝 > query //title
📝 > set //title "Updated Title"
📝 > save
📝 > exit
```

### 4. Web Interface
```bash
file-editor server --port 8080
# Open http://localhost:8080 in your browser
```

## 📖 Usage Examples

### SVG Files
```bash
# Update text elements
file-editor set "//text[@id='title']" "New Chart Title"

# Change colors
file-editor set "//rect[@id='bar1']" "blue" --type attribute --attr fill

# Update metadata
file-editor set "//metadata/description" "Updated chart description"
```

### HTML Files
```bash
# Update page title
file-editor set "//title" "New Page Title"

# Change meta description
file-editor set "//meta[@name='description']" "New description" --type attribute --attr content

# Update content by CSS selector (in shell mode)
query #main-heading
set #main-heading "Welcome to Our Site"
```

### XML Data Files
```bash
# Update configuration values
file-editor set "//setting[@name='timeout']" "60" --type attribute --attr value

# Modify data records
file-editor set "//record[@id='1']/email" "newemail@example.com"

# Update metadata
file-editor set "//metadata/version" "2.0"
```

## 🔧 Advanced Features

### Batch Processing
```bash
#!/bin/bash
# Update multiple files
for file in *.svg; do
    file-editor load "$file"
    file-editor set "//metadata/updated" "$(date)"
    file-editor save
done
```

### REST API Usage
```bash
# Load file
curl -X POST http://localhost:8080/api/load \
  -H "Content-Type: application/json" \
  -d '{"file_path": "example.svg"}'

# Query elements
curl -X POST http://localhost:8080/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "//text[@id=\"title\"]", "type": "xpath"}'

# Update element
curl -X POST http://localhost:8080/api/update \
  -H "Content-Type: application/json" \
  -d '{"xpath": "//text[@id=\"title\"]", "type": "text", "value": "New Title"}'
```

### XPath Examples
```bash
# Find elements by ID
//element[@id='myid']

# Find elements by attribute value
//rect[@fill='red']

# Find elements containing text
//text[contains(., 'Hello')]

# Find elements by position
//record[position()=1]

# Find elements with specific child
//record[email='john@example.com']
```

### CSS Selector Examples (HTML only)
```bash
# By ID
#main-title

# By class
.navigation-item

# By attribute
input[type='text']

# Descendant selectors
div.content p

# Pseudo-selectors
li:first-child
```

## 🏗️ Project Structure

```
universal-file-editor/
├── pyproject.toml          # Poetry configuration
├── README.md              # This file
├── file_editor/           # Main package
│   ├── __init__.py        # Package initialization
│   ├── core.py           # Core FileEditor class
│   ├── cli.py            # Command-line interface
│   ├── server.py         # HTTP server
│   └── examples.py       # Example file generator
└── tests/                # Test suite
    ├── __init__.py
    ├── test_core.py
    ├── test_cli.py
    └── test_server.py
```

## 🧪 Development

### Setting up Development Environment
```bash
# Clone repository
git clone https://github.com/yourusername/universal-file-editor.git
cd universal-file-editor

# Install with development dependencies
poetry install

# Install pre-commit hooks
pre-commit install

# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=file_editor

# Format code
poetry run black file_editor/

# Type checking
poetry run mypy file_editor/
```

### Running Tests
```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_core.py

# Run with verbose output
poetry run pytest -v

# Run with coverage report
poetry run pytest --cov=file_editor --cov-report=html
```

## 📋 Requirements

- **Python**: 3.8+
- **lxml**: For XPath support (automatically installed)
- **beautifulsoup4**: For CSS selector support (automatically installed)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`poetry run pytest`)
6. Format your code (`poetry run black file_editor/`)
7. Commit your changes (`git commit -am 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Homepage**: https://github.com/yourusername/universal-file-editor
- **Documentation**: https://github.com/yourusername/universal-file-editor#readme
- **Issues**: https://github.com/yourusername/universal-file-editor/issues
- **PyPI**: https://pypi.org/project/universal-file-editor/

## 🌟 Why Universal File Editor?

Traditional file editing requires specialized tools for each format:
- SVG files → Inkscape, Adobe Illustrator
- HTML files → Web browsers, text editors  
- XML files → XML editors, IDEs

**Universal File Editor** provides a single, consistent interface for all structured document formats, enabling:

- **Automation**: Script repetitive edits across thousands of files
- **Integration**: Embed in CI/CD pipelines and build processes  
- **Consistency**: Use the same XPath/CSS knowledge across all formats
- **Accessibility**: No specialized software required - works anywhere Python runs

Perfect for developers, system administrators, and content managers who work with structured data files.