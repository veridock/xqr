# API Reference

This document provides detailed information about the XQR API, including core classes, methods, and their usage.

## Core Classes

### FileEditor

The main class for file operations.

#### Methods

##### `__init__(self, file_path: str, backup: bool = True)`
Initialize with a file path.

- `file_path`: Path to the file to edit
- `backup`: Whether to create a backup before modifications

##### `query(self, xpath: str) -> List[Element]`
Query elements using XPath.

- `xpath`: XPath expression
- Returns: List of matching elements

##### `set(self, xpath: str, value: str, attr: Optional[str] = None) -> bool`
Set element values or attributes.

- `xpath`: XPath to target element(s)
- `value`: Value to set
- `attr`: If specified, sets this attribute instead of text content
- Returns: True if successful, False otherwise

##### `save(self, output_path: Optional[str] = None) -> bool`
Save changes to a file.

- `output_path`: Optional output path (defaults to original file)
- Returns: True if successful

## SVGConverter

Handles SVG to PDF and image format conversions.

#### Methods

##### `__init__(self, input_path: str)`
Initialize with input SVG path.

- `input_path`: Path to input SVG file

##### `convert_to_pdf(self, output_path: Optional[str] = None) -> str`
Convert SVG to PDF.

- `output_path`: Output file path (defaults to input filename with .pdf)
- Returns: Path to converted file

##### `convert_to_png(self, output_path: Optional[str] = None, dpi: int = 300) -> str`
Convert SVG to PNG.

- `output_path`: Output file path
- `dpi`: Resolution in DPI
- Returns: Path to converted file

## Command Line Interface

### Basic Commands

#### Query
```bash
xqr query <file> <xpath>
```

#### Set Value
```bash
xqr set <file> <xpath> <value> [--attr <attribute>]
```

#### Convert SVG to PDF
```bash
xqr convert svg2pdf input.svg output.pdf
```

### Global Options

- `--backup`: Create backup before modification
- `--no-backup`: Skip backup creation
- `--verbose`: Show detailed output
- `--version`: Show version and exit

## REST API

### Endpoints

#### GET /api/query
Query elements using XPath.

**Parameters**:
- `xpath`: XPath expression
- `format`: Output format (json/xml, default: json)

**Example**:
```bash
curl "http://localhost:8080/api/query?xpath=//div&format=json"
```

#### POST /api/set
Set element values.

**Request Body**:
```json
{
  "xpath": "//div[@class='header']",
  "value": "New Header",
  "attr": "class"
}
```

#### POST /api/convert
Convert between formats.

**Request Body**:
```json
{
  "from": "svg",
  "to": "pdf",
  "content": "<svg>...</svg>"
}
```

## Error Handling

### Common Error Codes

- `400 Bad Request`: Invalid input parameters
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server-side error

### Error Response Format

```json
{
  "error": {
    "code": "invalid_xpath",
    "message": "Invalid XPath expression",
    "details": "..."
  }
}
```

## Rate Limiting

- 100 requests per minute per IP address
- 1000 requests per hour per API key

## Authentication

API keys can be provided in the `X-API-Key` header:

```
X-API-Key: your-api-key-here
```

## Versioning

API version is specified in the `Accept` header:

```
Accept: application/vnd.xqr.v1+json
```

## Deprecation Policy

- Endpoints marked as deprecated will be supported for at least 6 months
- Breaking changes will be introduced in major version updates only
