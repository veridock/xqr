"""
Tests for the core FileEditor functionality
"""

import pytest
import tempfile
import os
from pathlib import Path
from typing import Generator

from xqr.core import FileEditor


@pytest.fixture
def sample_svg() -> Generator[str, None, None]:
    """Create a temporary SVG file for testing

    Returns:
        str: Path to the temporary SVG file
    """
    svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
    <metadata>
        <title>Test SVG</title>
        <description>Test file</description>
    </metadata>
    <rect
        x="10"
        y="10"
        width="50"
        height="50"
        fill="red"
        id="test-rect"
    />
    <text
        x="50"
        y="150"
        id="test-text"
        font-size="16"
    >Hello World</text>
</svg>'''

    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.svg',
        delete=False,
        encoding='utf-8'
    ) as f:
        f.write(svg_content)
        f.flush()
        yield f.name

    # Cleanup
    os.unlink(f.name)


@pytest.fixture
def sample_xml() -> Generator[str, None, None]:
    """Create a temporary XML file for testing

    Returns:
        str: Path to the temporary XML file
    """
    xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<data>
    <metadata>
        <title>Test Data</title>
        <version>1.0</version>
    </metadata>
    <records>
        <record id="1">
            <name>John Doe</name>
            <age>30</age>
        </record>
        <record id="2">
            <name>Jane Smith</name>
            <age>25</age>
        </record>
    </records>
</data>'''

    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.xml',
        delete=False,
        encoding='utf-8'
    ) as f:
        f.write(xml_content)
        f.flush()
        yield f.name

    # Cleanup
    os.unlink(f.name)


@pytest.fixture
def sample_html() -> Generator[str, None, None]:
    """Create a temporary HTML file for testing

    Returns:
        str: Path to the temporary HTML file
    """
    html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>Test HTML</title>
    <meta name="description" content="Test file">
</head>
<body>
    <h1 id="main-title">Welcome</h1>
    <p class="intro">This is a test.</p>
    <ul>
        <li class="item">Item 1</li>
        <li class="item">Item 2</li>
    </ul>
</body>
</html>'''

    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.html',
        delete=False,
        encoding='utf-8'
    ) as f:
        f.write(html_content)
        f.flush()
        yield f.name

    # Cleanup
    os.unlink(f.name)


class TestFileEditor:
    """Test cases for FileEditor class"""

    def test_load_svg_file(self, sample_svg: str) -> None:
        """Test loading SVG file

        Args:
            sample_svg: Path to a sample SVG file (fixture)
        """
        editor = FileEditor(sample_svg)
        assert editor is not None
        assert str(editor.file_path) == sample_svg
        assert editor.file_type == 'svg'
        assert editor.tree is not None
        assert editor.original_content is not None

    def test_load_xml_file(self, sample_xml: str) -> None:
        """Test loading XML file

        Args:
            sample_xml: Path to a sample XML file (fixture)
        """
        editor = FileEditor(sample_xml)
        assert editor is not None
        assert str(editor.file_path) == sample_xml
        assert editor.file_type == 'xml'
        assert editor.tree is not None

    def test_load_html_file(self, sample_html: str) -> None:
        """Test loading HTML file

        Args:
            sample_html: Path to a sample HTML file (fixture)
        """
        editor = FileEditor(sample_html)
        assert editor is not None
        assert str(editor.file_path) == sample_html
        assert editor.file_type == 'html'
        assert editor.tree is not None

    def test_file_not_found(self) -> None:
        """Test handling of non-existent file"""
        with pytest.raises(FileNotFoundError):
            FileEditor("non_existent_file.xml")

    @pytest.mark.skipif(
        not hasattr(FileEditor, 'find_by_xpath'),
        reason="XPath support requires lxml"
    )
    def test_xpath_query_text(self, sample_svg: str) -> None:
        """Test XPath text query

        Args:
            sample_svg: Path to a sample SVG file (fixture)
        """
        editor = FileEditor(sample_svg)
        text = editor.get_element_text("//text[@id='test-text']")
        assert text == "Hello World"

    @pytest.mark.skipif(
        not hasattr(FileEditor, 'find_by_xpath'),
        reason="XPath support requires lxml"
    )
    def test_xpath_query_attribute(self, sample_svg: str) -> None:
        """Test XPath attribute query

        Args:
            sample_svg: Path to a sample SVG file (fixture)
        """
        editor = FileEditor(sample_svg)
        fill = editor.get_element_attribute("//rect[@id='test-rect']", "fill")
        assert fill == "red"

    @pytest.mark.skipif(
        not hasattr(FileEditor, 'find_by_xpath'),
        reason="XPath support requires lxml"
    )
    def test_set_element_text(self, sample_svg: str) -> None:
        """Test setting element text

        Args:
            sample_svg: Path to a sample SVG file (fixture)
        """
        editor = FileEditor(sample_svg)
        xpath = "//text[@id='test-text']"
        success = editor.set_element_text(xpath, "Updated Text")
        assert success is True

        # Verify the change
        updated_text = editor.get_element_text(xpath)
        assert updated_text == "Updated Text"

    @pytest.mark.skipif(
        not hasattr(FileEditor, 'find_by_xpath'),
        reason="XPath support requires lxml"
    )
    def test_set_element_attribute(self, sample_svg: str) -> None:
        """Test setting element attribute

        Args:
            sample_svg: Path to a sample SVG file (fixture)
        """
        editor = FileEditor(sample_svg)
        xpath = "//rect[@id='test-rect']"
        success = editor.set_element_attribute(xpath, "fill", "blue")
        assert success is True

        # Verify the change
        updated_fill = editor.get_element_attribute(xpath, "fill")
        assert updated_fill == "blue"

    @pytest.mark.skipif(
        not hasattr(FileEditor, 'find_by_xpath'),
        reason="XPath support requires lxml"
    )
    def test_list_elements(self, sample_xml: str) -> None:
        """Test listing elements"""
        editor = FileEditor(sample_xml)
        elements = editor.list_elements("//record")
        assert len(elements) == 2
        assert elements[0]['tag'] == 'record'
        assert 'id' in elements[0]['attributes']

    def test_backup_creation(self, sample_svg: str) -> None:
        """Test backup file creation"""
        editor = FileEditor(sample_svg)
        backup_path = editor.backup()

        assert Path(backup_path).exists()

        # Verify backup content matches original
        with open(backup_path, 'r', encoding='utf-8') as f:
            backup_content = f.read()

        assert backup_content == editor.original_content

        os.unlink(backup_path)  # Cleanup backup file

    def test_save_file(self, sample_svg: str) -> None:
        """Test saving file"""
        editor = FileEditor(sample_svg)

        # Make a change
        if hasattr(editor, 'find_by_xpath'):
            editor.set_element_text("//text[@id='test-text']", "Modified Text")

        # Save to a new file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.svg',
            delete=False,
            encoding='utf-8'
        ) as tmp:
            tmp_path = tmp.name

        success = editor.save(tmp_path)
        assert success is True
        assert Path(tmp_path).exists()

        # Cleanup
        os.unlink(tmp_path)

    def test_invalid_xpath(self, sample_svg: str) -> None:
        """Test handling of invalid XPath expressions"""
        editor = FileEditor(sample_svg)

        if hasattr(editor, 'find_by_xpath'):
            with pytest.raises(ValueError):
                editor.find_by_xpath("invalid[xpath[")

    def test_nonexistent_element(self, sample_svg: str) -> None:
        """Test querying non-existent elements"""
        editor = FileEditor(sample_svg)

        if hasattr(editor, 'find_by_xpath'):
            # Test the find_by_xpath method
            elements = editor.find_by_xpath('//text')
            assert isinstance(elements, list)