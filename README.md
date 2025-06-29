# 🛠️ XQR - XPath Query & Replace

[![PyPI](https://img.shields.io/pypi/v/xqr)](https://pypi.org/project/xqr/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/pypi/pyversions/xqr)](https://pypi.org/project/xqr/)

XQR is a powerful command-line tool for editing and converting structured documents (SVG, HTML, XML) using XPath and CSS selectors. It's designed for developers, data engineers, and designers who need to manipulate structured data efficiently.

## ✨ Features

- **Universal Document Editor**: Edit SVG, HTML, and XML files with XPath/CSS selectors
- **PDF to SVG Conversion**: Convert PDFs to SVG with embedded metadata and text extraction
- **SVG to PDF/Image**: Convert SVGs to PDF, PNG, and JPG formats
- **Batch Processing**: Process multiple files with a single command
- **REST API**: Built-in web server for programmatic access
- **Cross-Platform**: Works on Linux, macOS, and Windows

## 🚀 Quick Start

### Installation

See the [Installation Guide](docs/INSTALLATION.md) for complete setup instructions.

```bash
# Basic installation with pip
pip install xqr
```

### Basic Usage

Check out the [Examples](docs/EXAMPLES.md) for comprehensive usage patterns.

```bash
# Query elements with XPath
xqr query document.html "//h1"

# Update content
xqr set document.html "//title" "New Title"

# Convert between formats
xqr convert input.pdf output.svg
```

## 📚 Documentation

For detailed documentation, please visit our [documentation website](https://veridock.github.io/xqr/) or check the following resources:

- [Installation Guide](docs/INSTALLATION.md) - Complete setup instructions
- [PDF to SVG Workflow](docs/WORKFLOW_PDF_TO_SVG.md) - Working with PDF files
- [SVG to PDF/Image](docs/WORKFLOW_SVG_TO_PDF.md) - Converting SVG files
- [API Reference](docs/API.md) - Detailed API documentation
- [Examples](docs/EXAMPLES.md) - Practical usage examples
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Solutions to common issues

## 💡 Features in Detail

### Document Editing
- XPath 1.0 and CSS selector support
- Batch processing of multiple files
- Automatic backup system
- Interactive shell for complex operations

### PDF to SVG Conversion
- Extract text and metadata
- Handle password-protected PDFs
- Custom DPI settings for OCR
- Multiple output formats (SVG, HTML, JSON)

### SVG Processing
- Convert to PDF, PNG, and JPG
- Handle embedded resources
- Advanced image processing options
- Batch conversion tools

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](docs/CONTRIBUTING.md) for details on how to contribute to this project.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Getting Help

Having trouble with XQR? Check out our [Troubleshooting Guide](docs/TROUBLESHOOTING.md) or [open an issue](https://github.com/veridock/xqr/issues) if you can't find what you need.

You can run the XQR CLI in several ways depending on your setup:

#### From Poetry (recommended for development):
```bash
# Run a single command
poetry run xqr --help

# Or activate the environment first
poetry shell
xqr --help
```

#### From virtual environment:
```bash
# Activate your virtual environment first
source /path/to/venv/bin/activate

# Then run xqr
xqr --help
```

#### Using Python module syntax (works without installation):
```bash
python -m xqr.cli --help
```

#### Install globally (not recommended for development):
```bash
# Install in development mode
pip install -e .

# Or install from PyPI
pip install xqr

# Then run from anywhere
xqr --help
```

### 1. Create Example Files
```bash
xqr examples
```

### 2. Basic Usage - Standard Commands
```bash
# Load and query a file
xqr load example.svg
xqr query "//text[@id='text1']"

# Update content
xqr set "//text[@id='text1']" "New Content"
xqr save

# The file remains loaded between commands
xqr query "//text[@id='text2']"  # Works without reloading

# To load a different file
xqr load other_file.xml
```

### 3. Concise File/XPath Operations
For quick operations, you can directly specify the file and XPath in one command:

```bash
xqr example.svg//svg

# Read element content
xqr example.svg//text[@id='text1']

# Update element content
xqr example.svg//text[@id='text1'] "New Value"

# Delete element content (set to empty string)
xqr example.svg//text[@id='text1'] ""

# Read from XML/HTML files
xqr config.xml//setting[@name='timeout']
xqr index.html//title "New Page Title"

# This syntax is especially useful for one-off operations and scripts.
```

### 4. Interactive Shell
```bash
xqr shell
📝 > load example.html
📝 > query //title
📝 > set //title "Updated Title"
📝 > save
📝 > exit

# The shell maintains state between commands automatically
```

### 5. Web Interface
```bash
xqr server --port 8080
# Open http://localhost:8080 in your browser

# The web interface shares the same state as the CLI
# Any file loaded in the web interface will be available to the CLI and vice versa
```

## 🔄 State Persistence

XQR maintains state between commands, making it easy to work with files across multiple operations:

```bash
# Load a file (state is saved to ~/.local/state/xqr/state.json)
xqr load example.svg

# The file remains loaded for subsequent commands
xqr query "//title"
xqr set "//version" "2.0"
xqr save

# The state persists even if you close the terminal
# Next time you run xqr, it will remember the last loaded file
xqr query "//title"  # Still works with the last loaded file

# To clear the state or load a different file
xqr load different_file.html
```

### State Management
- State is stored in `~/.local/state/xqr/state.json`
- The state includes the path to the last loaded file
- If the file is moved or deleted, XQR will prompt you to load a new file

## 📖 Usage Examples

### SVG Files - Update Charts & Graphics
```bash
# Update chart title
xqr set "//text[@id='title']" "Q4 Sales Results"

# Change visualization colors
xqr set "//rect[@id='bar1']" "blue" --type attribute --attr fill

# Update metadata for better organization
xqr set "//metadata/description" "Updated quarterly sales chart"

# Batch update multiple SVG files
for file in charts/*.svg; do
    xqr load "$file"
    xqr set "//metadata/updated" "$(date)"
    xqr save
done
```

### HTML Files - Content Management
```bash
# Update page titles across multiple pages
xqr set "//title" "New Site Title"

# Change meta descriptions for SEO
xqr set "//meta[@name='description']" "Updated SEO description" --type attribute --attr content

# Update navigation links
xqr set "//nav//a[@href='/old-page']" "/new-page" --type attribute --attr href

# CSS selector support in shell mode
xqr shell
📝 > load index.html
📝 > query #main-heading
📝 > set #main-heading "Welcome to Our New Site"
```

### XML Data Files - Configuration & Data
```bash
# Update configuration values
xqr set "//config/timeout" "60" --type attribute --attr value

# Modify data records
xqr set "//record[@id='1']/email" "newemail@example.com"

# Update version information
xqr set "//metadata/version" "2.0"

# Batch configuration updates
find /etc/configs -name "*.xml" -exec xqr load {} \; \
    -exec xqr set "//config/debug" "false" \; \
    -exec xqr save {} \;
```

## 🔧 Advanced Features

### Batch Processing Scripts
```bash
#!/bin/bash
# Update copyright year across all HTML files
for file in **/*.html; do
    echo "Processing $file..."
    xqr load "$file"
    xqr set "//span[@class='copyright-year']" "2025"
    xqr save
done

# Update SVG chart data
#!/bin/bash
# Replace old data with new values
for chart in reports/*.svg; do
    xqr load "$chart"
    xqr set "//metadata/data-source" "Q1-2025-data.json"
    xqr set "//text[@class='last-updated']" "$(date '+%Y-%m-%d')"
    xqr save
done
```

### REST API Integration
```bash
# Start server
xqr server --port 8080

# Load file via API
curl -X POST http://localhost:8080/api/load \
  -H "Content-Type: application/json" \
  -d '{"file_path": "dashboard.svg"}'

# Query elements
curl -X POST http://localhost:8080/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "//text[@class=\"metric-value\"]", "type": "xpath"}'

# Update values
curl -X POST http://localhost:8080/api/update \
  -H "Content-Type: application/json" \
  -d '{"xpath": "//text[@class=\"revenue\"]", "type": "text", "value": "$1.2M"}'

# Save changes
curl -X POST http://localhost:8080/api/save \
  -H "Content-Type: application/json" \
  -d '{"output_path": "updated_dashboard.svg"}'
```

### XPath Examples
```bash
# Find elements by ID
//element[@id='myid']

# Find elements by attribute value
//rect[@fill='red']

# Find elements containing specific text
//text[contains(., 'Revenue')]

# Find elements by position
//record[position()=1]

# Find parent elements with specific children
//record[email='john@example.com']

# Complex queries with multiple conditions
//svg//text[@font-size='16' and contains(@class, 'title')]
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

# Complex selectors
nav.primary ul.menu li a[href^="/products"]
```

## 🏗️ Project Structure

```
xqr/
├── pyproject.toml          # Poetry configuration
├── README.md              # This file
├── Makefile               # Development automation
├── xqr/                   # Main package
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
git clone https://github.com/veridock/xqr.git
cd xqr

# Install with development dependencies
poetry install

# Create example files and run tests
make dev-setup

# Run full development cycle
make dev
```

### Available Make Commands
```bash
make help           # Show all available commands
make install        # Install package
make test           # Run test suite
make test-cov       # Run tests with coverage
make format         # Format code with black
make lint           # Run linting
make examples       # Create example files
make demo-svg       # Run SVG demo
make run-server     # Start web server
make run-shell      # Start interactive shell
```

### Running Tests
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=xqr --cov-report=html

# Run specific test file
poetry run pytest tests/test_core.py -v
```

## 📋 Requirements

- **Python**: 3.8+
- **lxml**: For XPath support (automatically installed)
- **beautifulsoup4**: For CSS selector support (automatically installed)

## 🎯 Use Cases

### DevOps & Configuration Management
```bash
# Update configuration across multiple environments
for env in dev staging prod; do
    xqr load "config-${env}.xml"
    xqr set "//database/host" "db-${env}.company.com"
    xqr set "//cache/ttl" "3600"
    xqr save
done
```

### Content Management
```bash
# Update copyright notices across all HTML files
find . -name "*.html" -exec xqr load {} \; \
    -exec xqr set "//footer//span[@class='year']" "2025" \; \
    -exec xqr save {} \;
```

### Data Processing
```bash
# Extract and transform data from XML files
xqr shell << EOF
load sales-data.xml
list //record[sales>10000]
set //record[sales>10000]/status "high-performer"
xqr save
```

## Documentation

* [Full Documentation](https://github.com/veridock/xqr#readme)
* [XPath Examples](https://github.com/veridock/xqr#xpath-examples)
* [CSS Selector Examples](https://github.com/veridock/xqr#css-selector-examples)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/xpath-improvements`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`make test`)
6. Format your code (`make format`)
7. Commit your changes (`git commit -am 'Add XPath improvements'`)
8. Push to the branch (`git push origin feature/xpath-improvements`)
9. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Homepage**: https://github.com/veridock/xqr
- **Documentation**: https://github.com/veridock/xqr#readme
- **Issues**: https://github.com/veridock/xqr/issues
- **PyPI**: https://pypi.org/project/xqr/

## 🌟 Why XQR?

Traditional approaches require different tools for each format:
- **SVG files** → Inkscape, Adobe Illustrator, manual editing
- **HTML files** → Web browsers, text editors, sed/awk scripts  
- **XML files** → XML editors, custom parsers, XSLT

**XQR provides a unified interface** using standard web technologies:
- **XPath** - W3C standard for XML/HTML navigation
- **CSS Selectors** - Familiar syntax for web developers
- **Command Line** - Scriptable and automation-friendly
- **REST API** - Integration with existing workflows

Perfect for:
- **CI/CD pipelines** - automated content updates
- **Content management** - bulk HTML modifications
- **Data processing** - XML transformation workflows  
- **Design automation** - SVG batch processing
- **Configuration management** - XML config updates

### Real-world Examples

**E-commerce**: Update product prices across thousands of XML files
```bash
find products/ -name "*.xml" -exec xqr set "//price[@currency='USD']" "$(calc_new_price {})" \;
```

**Documentation**: Update version numbers in all HTML docs
```bash
xqr set "//meta[@name='version']" "v2.1.0" --type attribute --attr content
```

**Analytics**: Update dashboard charts with new data
```bash
xqr set "//svg//text[@class='metric']" "$REVENUE_METRIC"
```

---

**XQR - Making structured data editing simple, fast, and scriptable.**