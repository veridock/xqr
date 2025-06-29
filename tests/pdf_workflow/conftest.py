"""
Test configuration for PDF workflow tests.
"""

import pytest
import os
import shutil
from pathlib import Path

# Skip tests if required system dependencies are not available
REQUIRED_BINARIES = ['pdftoppm', 'tesseract']

def pytest_configure(config):
    """Configure test environment."""
    # Add a marker for tests that require external dependencies
    config.addinivalue_line(
        "markers",
        "requires_deps: mark test as requiring external dependencies"
    )

def pytest_runtest_setup(item):
    """Skip tests if required dependencies are not installed."""
    requires_deps = any(item.iter_markers(name='requires_deps'))
    if requires_deps:
        missing = [cmd for cmd in REQUIRED_BINARIES if not shutil.which(cmd)]
        if missing:
            pytest.skip(f"Required dependencies not found: {', '.join(missing)}")

@pytest.fixture(scope="session")
def test_data_dir():
    """Create and return the test data directory."""
    test_dir = Path(__file__).parent / 'data'
    test_dir.mkdir(exist_ok=True)
    return test_dir

@pytest.fixture(scope="session")
def sample_pdf_path(test_data_dir):
    """Create a sample PDF file for testing."""
    from create_sample_pdf import create_sample_pdf
    
    pdf_path = test_data_dir / 'sample_document.pdf'
    if not pdf_path.exists():
        create_sample_pdf(str(pdf_path))
    
    return pdf_path

@pytest.fixture
def temp_dir():
    """Create and return a temporary directory that will be cleaned up."""
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)
