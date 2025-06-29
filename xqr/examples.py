"""
Example file generator for testing the Universal File Editor
"""


def create_example_files():
    """Utwórz przykładowe pliki do testowania"""

    # Przykładowy SVG
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
    <metadata>
        <title>Example SVG</title>
        <description>Test file for editor</description>
        <version>1.0</version>
        <author>File Editor</author>
    </metadata>
    <rect x="10" y="10" width="50" height="50" fill="red" id="square1"/>
    <circle cx="100" cy="100" r="30" fill="blue" id="circle1"/>
    <text x="50" y="150" id="text1" font-size="16">Hello World</text>
    <text x="120" y="170" id="text2" font-size="12" fill="green">Sample Text</text>
</svg>'''

    # Przykładowy XML
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<data>
    <metadata>
        <title>Example Data</title>
        <version>1.0</version>
        <created>2025-06-28</created>
        <format>sample-data</format>
    </metadata>
    <records>
        <record id="1">
            <name>John Doe</name>
            <age>30</age>
            <email>john@example.com</email>
            <department>Engineering</department>
        </record>
        <record id="2">
            <name>Jane Smith</name>
            <age>25</age>
            <email>jane@example.com</email>
            <department>Marketing</department>
        </record>
        <record id="3">
            <name>Bob Johnson</name>
            <age>35</age>
            <email>bob@example.com</email>
            <department>Sales</department>
        </record>
    </records>
    <configuration>
        <setting name="debug" value="true"/>
        <setting name="timeout" value="30"/>
        <setting name="max_records" value="1000"/>
    </configuration>
</data>'''

    # Przykładowy HTML
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Test HTML file for Universal File Editor">
    <meta name="author" content="File Editor">
    <title>Example HTML</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f0f0; padding: 20px; }
        .content { margin: 20px 0; }
        .item { margin: 10px 0; padding: 10px; border: 1px solid #ddd; }
    </style>
</head>
<body>
    <div class="header">
        <h1 id="main-title">Welcome to Test Page</h1>
        <p id="subtitle">This is a sample HTML file for testing</p>
    </div>

    <div class="content">
        <h2 id="section-title">Sample Content</h2>
        <p id="intro">This is a test paragraph with some sample content.</p>

        <h3>List of Items</h3>
        <ul id="item-list">
            <li class="item" data-type="feature">Interactive editing</li>
            <li class="item" data-type="feature">XPath support</li>
            <li class="item" data-type="feature">CSS selectors</li>
            <li class="item" data-type="bonus">Web interface</li>
        </ul>

        <div id="info-box" class="info">
            <h4>Information</h4>
            <p>You can edit this content using the Universal File Editor.</p>
            <a href="#" id="sample-link">Sample Link</a>
        </div>
    </div>

    <footer id="footer">
        <p>Created by Universal File Editor - <span id="year">2025</span></p>
    </footer>
</body>
</html>'''

    # Dodatkowy przykład - złożony SVG z danymi
    complex_svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" 
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="400" height="300" viewBox="0 0 400 300">

    <metadata>
        <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                 xmlns:dc="http://purl.org/dc/elements/1.1/">
            <rdf:Description>
                <dc:title>Sales Chart</dc:title>
                <dc:creator>Data Team</dc:creator>
                <dc:date>2025-06-28</dc:date>
                <dc:description>Monthly sales data visualization</dc:description>
            </rdf:Description>
        </rdf:RDF>

        <data-store>
        {
            "chart_data": [
                {"month": "Jan", "sales": 120, "color": "#3498db"},
                {"month": "Feb", "sales": 150, "color": "#e74c3c"},
                {"month": "Mar", "sales": 180, "color": "#2ecc71"}
            ],
            "config": {
                "title": "Q1 Sales Data",
                "currency": "USD",
                "scale": 1000
            }
        }
        </data-store>
    </metadata>

    <defs>
        <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#f8f9fa"/>
            <stop offset="100%" style="stop-color:#e9ecef"/>
        </linearGradient>
    </defs>

    <rect width="100%" height="100%" fill="url(#bg)"/>

    <text x="200" y="30" text-anchor="middle" font-size="18" font-weight="bold" id="chart-title">
        Q1 Sales Data
    </text>

    <g id="chart-bars">
        <rect x="50" y="200" width="40" height="80" fill="#3498db" id="bar-jan">
            <title>January: $120k</title>
        </rect>
        <text x="70" y="295" text-anchor="middle" font-size="12">Jan</text>

        <rect x="150" y="170" width="40" height="110" fill="#e74c3c" id="bar-feb">
            <title>February: $150k</title>
        </rect>
        <text x="170" y="295" text-anchor="middle" font-size="12">Feb</text>

        <rect x="250" y="140" width="40" height="140" fill="#2ecc71" id="bar-mar">
            <title>March: $180k</title>
        </rect>
        <text x="270" y="295" text-anchor="middle" font-size="12">Mar</text>
    </g>

    <text x="50" y="320" font-size="10" fill="#666" id="footer-text">
        Generated by Universal File Editor
    </text>
</svg>'''

    # Zapisz przykładowe pliki
    files_to_create = [
        ('example.svg', svg_content),
        ('example.xml', xml_content),
        ('example.html', html_content),
        ('complex_chart.svg', complex_svg_content)
    ]

    for filename, content in files_to_create:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

    print("✅ Created example files:")
    for filename, _ in files_to_create:
        print(f"   📄 {filename}")

    print("\n📖 Try these commands:")
    print("   file-editor load example.svg")
    print("   file-editor query '//text[@id=\"text1\"]'")
    print("   file-editor set '//text[@id=\"text1\"]' 'Updated Text'")
    print("   file-editor save")
    print("   file-editor server --port 8080")


def get_sample_xpath_queries():
    """Zwróć przykładowe zapytania XPath dla różnych typów plików"""
    return {
        'svg': [
            '//text[@id="text1"]',
            '//rect[@fill="red"]',
            '//metadata/title',
            '//*[@id="circle1"]',
            '//text[contains(@font-size, "16")]'
        ],
        'xml': [
            '//record[@id="1"]',
            '//record/name',
            '//metadata/title',
            '//setting[@name="debug"]',
            '//record[age>30]/name'
        ],
        'html': [
            '//*[@id="main-title"]',
            '//meta[@name="description"]',
            '//li[@class="item"]',
            '//a[@href="#"]',
            '//span[@id="year"]'
        ]
    }


def get_sample_css_queries():
    """Zwróć przykładowe zapytania CSS (tylko dla HTML)"""
    return [
        '#main-title',
        '.item',
        'li[data-type="feature"]',
        'meta[name="description"]',
        'div.content p',
        'footer#footer'
    ]