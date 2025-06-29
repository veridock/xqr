# Installation Guide

## Prerequisites

- Python 3.8+
- Poetry (recommended) or pip
- System dependencies (varies by platform)

## Using Poetry (Recommended)

```bash
# Clone the repository
git clone https://github.com/veridock/xqr.git
cd xqr

# Install with Poetry
poetry install

# Activate the environment
poetry shell
```

## Using pip

```bash
pip install xqr
```

## System Dependencies

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    pdf2svg \
    python3-magic \
    libmagic1
```

### macOS (Homebrew)
```bash
brew install poppler \
             tesseract \
             pdf2svg \
             libmagic
```

## Verifying Installation

```bash
xqr --version
```

## Troubleshooting

If you encounter any issues during installation, please check the [Troubleshooting Guide](TROUBLESHOOTING.md).
