#!/bin/bash

# xqr Installation Script
# This script installs all necessary dependencies for the xqr package

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print status messages
status() {
    echo -e "${GREEN}[*]${NC} $1"
}

# Function to print warnings
warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Function to print errors and exit
error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    exit 1
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        warning "This script requires root privileges for system package installation."
        warning "Please run with sudo or as root."
        exit 1
    fi
}

# Detect OS and install system dependencies
install_system_deps() {
    status "Detecting operating system..."
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        case $ID in
            debian|ubuntu|linuxmint)
                status "Detected Debian-based system. Installing dependencies..."
                apt-get update
                apt-get install -y \
                    python3-pip \
                    python3-venv \
                    poppler-utils \
                    tesseract-ocr \
                    libxml2-dev \
                    libxslt1-dev \
                    zlib1g-dev
                ;;
            fedora|rhel|centos)
                status "Detected Red Hat-based system. Installing dependencies..."
                dnf install -y \
                    python3-pip \
                    python3-virtualenv \
                    poppler-utils \
                    tesseract \
                    libxml2-devel \
                    libxslt-devel \
                    zlib-devel
                ;;
            arch|manjaro)
                status "Detected Arch-based system. Installing dependencies..."
                pacman -Syu --noconfirm \
                    python-pip \
                    python-virtualenv \
                    poppler \
                    tesseract \
                    libxml2 \
                    libxslt \
                    zlib
                ;;
            *)
                warning "Unsupported Linux distribution. You may need to install dependencies manually."
                ;;
        esac
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        status "Detected macOS. Checking for Homebrew..."
        if ! command -v brew &> /dev/null; then
            error "Homebrew is required for macOS installation. Please install it first."
        fi
        
        status "Installing dependencies with Homebrew..."
        brew update
        brew install \
            python \
            poppler \
            tesseract \
            libxml2 \
            libxslt
    else
        warning "Could not detect OS. You may need to install dependencies manually."
    fi
}

# Create and activate virtual environment
setup_virtualenv() {
    local venv_dir="$1"
    
    status "Setting up Python virtual environment in $venv_dir..."
    python3 -m venv "$venv_dir"
    source "$venv_dir/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
}

# Install Python dependencies
install_python_deps() {
    local project_dir="$1"
    
    status "Installing Python dependencies..."
    cd "$project_dir"
    
    # Install package in development mode
    pip install -e .
    
    # Install development dependencies
    if [ -f "dev-requirements.txt" ]; then
        pip install -r dev-requirements.txt
    fi
    
    # Install additional packages for examples
    pip install lxml beautifulsoup4 cssselect
}

# Verify installation
verify_installation() {
    status "Verifying installation..."
    
    # Check Python packages
    if ! python3 -c "import lxml, bs4, cssselect" &> /dev/null; then
        warning "Some Python packages failed to import. There may be installation issues."
    else
        echo "✓ Python packages verified"
    fi
    
    # Check system tools
    for cmd in tesseract pdftotext; do
        if ! command -v $cmd &> /dev/null; then
            warning "$cmd not found. Some functionality may be limited."
        else
            echo "✓ $cmd found"
        fi
    done
    
    status "Installation complete!"
}

# Main function
main() {
    local project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    local venv_dir="$project_dir/venv"
    
    echo -e "\n${GREEN}=== xqr Installation Script ===${NC}\n"
    
    # Check if running as root (only needed for system package installation)
    if [ "$1" = "--system" ]; then
        check_root
        install_system_deps
    fi
    
    # Setup virtual environment
    if [ ! -d "$venv_dir" ]; then
        setup_virtualenv "$venv_dir"
    else
        status "Virtual environment already exists at $venv_dir"
        source "$venv_dir/bin/activate"
    fi
    
    # Install Python dependencies
    install_python_deps "$project_dir"
    
    # Verify installation
    verify_installation
    
    echo -e "\n${GREEN}=== Installation Complete ===${NC}"
    echo -e "To activate the virtual environment, run:"
    echo -e "  source $venv_dir/bin/activate\n"
    echo -e "To run the xqr CLI:"
    echo -e "  xqr --help\n"
}

# Run the script
main "$@"
