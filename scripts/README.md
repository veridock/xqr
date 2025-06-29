# Installation Scripts

This directory contains installation scripts for the xqr package.

## Available Scripts

### Linux/macOS
- `install.sh` - Main installation script for Unix-like systems

### Windows
- `install.ps1` - PowerShell script for Windows installation

## Prerequisites

### Linux/macOS
- bash
- sudo access (for system package installation)
- curl or wget

### Windows
- PowerShell 5.1 or later
- Administrative privileges
- Internet connection

## Usage

### Linux/macOS

1. Make the script executable:
   ```bash
   chmod +x scripts/install.sh
   ```

2. Run the installation:
   ```bash
   # Install system dependencies (requires sudo)
   sudo ./scripts/install.sh --system
   
   # Or without system dependencies (you'll need to install them manually)
   ./scripts/install.sh
   ```

### Windows

1. Open PowerShell as Administrator
2. Run the installation script:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force
   .\scripts\install.ps1
   ```

## What's Installed

### System Dependencies
- Python 3.8+
- poppler-utils (for PDF processing)
- tesseract (for OCR)
- libxml2 and libxslt (for XML processing)

### Python Dependencies
- xqr package (in development mode)
- lxml
- beautifulsoup4
- cssselect
- Other dependencies from requirements.txt

## Virtual Environment

The installation script creates a Python virtual environment in the project root directory (`venv` by default).

To activate the virtual environment:

### Linux/macOS
```bash
source venv/bin/activate
```

### Windows
```powershell
.\venv\Scripts\Activate.ps1
```

## Verifying Installation

After installation, you can verify everything is working by running:

```bash
xqr --version
```

## Troubleshooting

### Common Issues

1. **Permission Denied**
   - Make sure to run the script with appropriate permissions
   - On Linux/macOS, use `sudo` for system package installation
   - On Windows, run PowerShell as Administrator

2. **Python Not Found**
   - Ensure Python 3.8+ is installed and in your PATH
   - On Windows, you may need to check "Add Python to PATH" during installation

3. **Tesseract Not Found**
   - Make sure Tesseract is installed and in your system PATH
   - On Windows, the default installation path is `C:\Program Files\Tesseract-OCR`

## Manual Installation

If the automated scripts don't work for your system, you can install the dependencies manually:

1. Install Python 3.8+ from [python.org](https://www.python.org/downloads/)
2. Install system dependencies:
   - **Ubuntu/Debian**: `sudo apt-get install python3-pip python3-venv poppler-utils tesseract-ocr libxml2-dev libxslt1-dev`
   - **macOS**: `brew install python poppler tesseract libxml2 libxslt`
   - **Windows**: Use the [Tesseract installer](https://github.com/UB-Mannheim/tesseract/wiki)
3. Create and activate a virtual environment
4. Install the package: `pip install -e .`

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
