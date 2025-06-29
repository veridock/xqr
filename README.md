# 🛠️ XQR - XPath Query & Replace

Powerful CLI tool for editing SVG, HTML, and XML files using XPath and CSS selectors. Edit your structured documents directly from the command line or through a web interface.

## 🎯 What is XQR?

**XQR** (XPath Query & Replace) is a universal file editor that treats SVG, HTML, and XML as structured data containers. Use familiar XPath expressions and CSS selectors to query, modify, and manipulate content without specialized applications.

Perfect for:
- **Data Engineers** - batch processing XML/SVG files
- **DevOps** - configuration management and automation
- **Web Developers** - HTML content manipulation
- **Designers** - SVG batch editing and metadata management

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
git clone https://github.com/veridock/xqr.git
cd xqr

# Install with Poetry
poetry install

# Activate the environment
poetry shell
```

### Using pip

```bash
pip install xqr
```

## 🎯 Quick Start

### 1. Create Example Files
```bash
xqr examples
```

### 2. Basic Usage
```bash
# Load and query a file
xqr load example.svg
xqr query "//text[@id='text1']"

# Update content
xqr set "//text[@id='text1']" "New Content"
xqr save
```

### 3. Interactive Shell
```bash
xqr shell
📝 > load example.html
📝 > query //title
📝 > set //title "Updated Title"
📝 > save
📝 > exit
```

### 4. Web Interface
```bash
xqr server --port 8080
# Open http://localhost:8080 in your browser
```

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
save processed-sales.xml
exit
EOF
```

### SVG Automation
```bash
# Update chart data and metadata
xqr load quarterly-chart.svg
xqr set "//text[@class='chart-title']" "Q1 2025 Results"
xqr set "//metadata/generated" "$(date)"
xqr setattr "//rect[@class='revenue-bar']" height "250"
xqr save
```

## 🤝 Contributing

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