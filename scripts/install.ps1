<#
.SYNOPSIS
    xqr Installation Script for Windows
.DESCRIPTION
    This script installs all necessary dependencies for the xqr package on Windows.
    It requires administrative privileges to install system packages.
#>

#Requires -RunAsAdministrator

# Set error action preference
$ErrorActionPreference = "Stop"

# Colors for output
$Green = '\033[0;32m'
$Yellow = '\033[1;33m'
$Red = '\033[0;31m'
$NoColor = '\033[0m'

# Function to print status messages
function Write-Status {
    param([string]$Message)
    Write-Host "${Green}[*]${NoColor} $Message"
}

# Function to print warnings
function Write-WarningMsg {
    param([string]$Message)
    Write-Host "${Yellow}[!]${NoColor} $Message"
}

# Function to print errors and exit
function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "${Red}[ERROR]${NoColor} $Message" -ForegroundColor Red
    exit 1
}

# Check if running as administrator
function Test-IsAdmin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Install Chocolatey if not present
function Install-Chocolatey {
    if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
        Write-Status "Installing Chocolatey package manager..."
        try {
            Set-ExecutionPolicy Bypass -Scope Process -Force
            [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
            Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            RefreshEnv
        } catch {
            Write-ErrorMsg "Failed to install Chocolatey: $_"
        }
    } else {
        Write-Status "Chocolatey is already installed."
    }
}

# Install system dependencies using Chocolatey
function Install-SystemDependencies {
    Write-Status "Installing system dependencies..."
    
    # Define required packages
    $packages = @(
        @{ Name = "python3"; Version = "3.10.0" },
        @{ Name = "poppler"; Version = "22.04.0" },
        @{ Name = "tesseract"; Version = "5.2.0" },
        @{ Name = "git"; Version = "2.36.1" }
    )
    
    foreach ($pkg in $packages) {
        $pkgName = $pkg.Name
        $pkgVersion = $pkg.Version
        
        Write-Status "Checking for $pkgName..."
        
        # Check if package is already installed
        $installed = choco list --local-only $pkgName -r | ConvertFrom-Csv -Delimiter '|' -Header 'Package', 'Version'
        
        if ($installed -and $installed.Version -ge $pkgVersion) {
            Write-Status "$pkgName $($installed.Version) is already installed."
        } else {
            Write-Status "Installing $pkgName $pkgVersion..."
            try {
                choco install $pkgName --version $pkgVersion -y --no-progress
                if ($LASTEXITCODE -ne 0) { throw "Failed to install $pkgName" }
            } catch {
                Write-WarningMsg "Failed to install $pkgName: $_"
            }
        }
    }
    
    # Add Tesseract to system PATH if not already there
    $tesseractPath = "C:\Program Files\Tesseract-OCR"
    $currentPath = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    if ($currentPath -notlike "*$tesseractPath*") {
        Write-Status "Adding Tesseract to system PATH..."
        [Environment]::SetEnvironmentVariable(
            'Path', 
            $currentPath + ";$tesseractPath", 
            [System.EnvironmentVariableTarget]::Machine
        )
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    }
}

# Create and activate virtual environment
function Setup-VirtualEnv {
    param(
        [string]$ProjectDir,
        [string]$VenvName = "venv"
    )
    
    $venvPath = Join-Path $ProjectDir $VenvName
    
    if (-not (Test-Path $venvPath)) {
        Write-Status "Creating Python virtual environment in $venvPath..."
        python -m venv $venvPath
    } else {
        Write-Status "Virtual environment already exists at $venvPath"
    }
    
    # Activate the virtual environment
    $activatePath = Join-Path $venvPath "Scripts\Activate.ps1"
    if (Test-Path $activatePath) {
        . $activatePath
    } else {
        throw "Failed to activate virtual environment. $activatePath not found."
    }
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    return $venvPath
}

# Install Python dependencies
function Install-PythonDependencies {
    param(
        [string]$ProjectDir
    )
    
    Write-Status "Installing Python dependencies..."
    Set-Location $ProjectDir
    
    # Install package in development mode
    pip install -e .
    
    # Install development dependencies if they exist
    $devReqPath = Join-Path $ProjectDir "dev-requirements.txt"
    if (Test-Path $devReqPath) {
        pip install -r $devReqPath
    }
    
    # Install additional packages for examples
    pip install lxml beautifulsoup4 cssselect
}

# Verify installation
function Verify-Installation {
    Write-Status "Verifying installation..."
    
    # Check Python packages
    $pythonPkgs = @("lxml", "bs4", "cssselect")
    foreach ($pkg in $pythonPkgs) {
        try {
            python -c "import $pkg"
            Write-Host "✓ Python package $pkg verified"
        } catch {
            Write-WarningMsg "Python package $pkg failed to import"
        }
    }
    
    # Check system tools
    $tools = @("tesseract", "pdftotext")
    foreach ($tool in $tools) {
        if (Get-Command $tool -ErrorAction SilentlyContinue) {
            Write-Host "✓ $tool found"
        } else {
            Write-Warning "$tool not found. Some functionality may be limited."
        }
    }
    
    Write-Status "Installation complete!"
}

# Main script execution
function Main {
    # Check if running as administrator
    if (-not (Test-IsAdmin)) {
        Write-ErrorMsg "This script requires administrative privileges. Please run as Administrator."
    }
    
    $projectDir = Split-Path -Parent $PSScriptRoot
    
    Write-Host "\n${Green}=== xqr Installation Script for Windows ===${NoColor}\n"
    
    try {
        # Install Chocolatey and system dependencies
        Install-Chocolatey
        Install-SystemDependencies
        
        # Set up Python environment
        $venvPath = Setup-VirtualEnv -ProjectDir $projectDir
        
        # Install Python dependencies
        Install-PythonDependencies -ProjectDir $projectDir
        
        # Verify installation
        Verify-Installation
        
        Write-Host "\n${Green}=== Installation Complete ===${NoColor}"
        Write-Host "To activate the virtual environment, run:"
        Write-Host "  .\$venvPath\Scripts\Activate.ps1"
        Write-Host ""
        Write-Host "To run the xqr CLI:"
        Write-Host "  xqr --help"
        Write-Host ""
        
    } catch {
        Write-ErrorMsg "Installation failed: $_"
    }
}

# Run the main function
Main
