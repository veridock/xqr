"""
Tests for the jQuery-like syntax functionality
"""

import pytest
from pathlib import Path
from typing import Generator, Any

from xqr.core import FileEditor
from xqr.jquery_syntax import JQuerySyntax, process_jquery_syntax


class TestJQuerySyntax:
    """Test cases for jQuery-like syntax functionality"""

    def test_css_getter(self, sample_svg: str) -> None:
        """Test getting CSS properties with jQuery-like syntax"""
        editor = FileEditor(sample_svg)
        jq = JQuerySyntax(editor, "#test-rect")
        style = jq.css("fill")
        assert style == "red"

    def test_css_setter(self, sample_svg: str, tmp_path: Path) -> None:
        """Test setting CSS properties with jQuery-like syntax"""
        # Create a copy of the sample file to avoid modifying the original
        test_file = tmp_path / "test.svg"
        test_file.write_text(Path(sample_svg).read_text())
        
        editor = FileEditor(str(test_file))
        jq = JQuerySyntax(editor, "#test-rect")
        result = jq.css("fill", "blue")
        
        # Should return self for chaining
        assert result is jq
        
        # Verify the change was made
        assert editor.get_element_attribute("//*[@id='test-rect']", "fill") == "blue"

    def test_attr_getter(self, sample_svg: str) -> None:
        """Test getting attributes with jQuery-like syntax"""
        editor = FileEditor(sample_svg)
        jq = JQuerySyntax(editor, "#test-rect")
        width = jq.attr("width")
        assert width == "50"

    def test_attr_setter(self, sample_svg: str, tmp_path: Path) -> None:
        """Test setting attributes with jQuery-like syntax"""
        test_file = tmp_path / "test.svg"
        test_file.write_text(Path(sample_svg).read_text())
        
        editor = FileEditor(str(test_file))
        jq = JQuerySyntax(editor, "#test-rect")
        result = jq.attr("width", "100")
        
        assert result is jq
        assert editor.get_element_attribute("//*[@id='test-rect']", "width") == "100"

    def test_text_getter(self, sample_svg: str) -> None:
        """Test getting text content with jQuery-like syntax"""
        editor = FileEditor(sample_svg)
        jq = JQuerySyntax(editor, "#test-text")
        text = jq.text()
        assert text == "Hello World"

    def test_text_setter(self, sample_svg: str, tmp_path: Path) -> None:
        """Test setting text content with jQuery-like syntax"""
        test_file = tmp_path / "test.svg"
        test_file.write_text(Path(sample_svg).read_text())
        
        editor = FileEditor(str(test_file))
        jq = JQuerySyntax(editor, "#test-text")
        result = jq.text("Updated Text")
        
        assert result is jq
        assert editor.get_element_text("//*[@id='test-text']") == "Updated Text"

    def test_html_getter(self, sample_svg: str) -> None:
        """Test getting HTML content with jQuery-like syntax"""
        editor = FileEditor(sample_svg)
        jq = JQuerySyntax(editor, "#test-text")
        html = jq.html()
        assert html == "Hello World"  # In this case, same as text for simple text node

    def test_html_setter(self, sample_svg: str, tmp_path: Path) -> None:
        """Test setting HTML content with jQuery-like syntax"""
        test_file = tmp_path / "test.svg"
        test_file.write_text(Path(sample_svg).read_text())
        
        editor = FileEditor(str(test_file))
        jq = JQuerySyntax(editor, "#test-text")
        result = jq.html("<tspan>Updated</tspan>")
        
        assert result is jq
        assert "<tspan>Updated</tspan>" in editor.get_element_html("//*[@id='test-text']")


class TestProcessJQuerySyntax:
    """Test cases for the process_jquery_syntax function"""

    def test_process_css_setter(self, sample_svg: str, tmp_path: Path) -> None:
        """Test processing a CSS setter command"""
        test_file = tmp_path / "test.svg"
        test_file.write_text(Path(sample_svg).read_text())
        
        editor = FileEditor(str(test_file))
        result = process_jquery_syntax(
            "$('#test-rect').css('fill', 'green')",
            editor
        )
        
        assert "Applied css to 1 elements" in result
        assert editor.get_element_attribute("//*[@id='test-rect']", "fill") == "green"

    def test_process_attr_setter(self, sample_svg: str, tmp_path: Path) -> None:
        """Test processing an attribute setter command"""
        test_file = tmp_path / "test.svg"
        test_file.write_text(Path(sample_svg).read_text())
        
        editor = FileEditor(str(test_file))
        result = process_jquery_syntax(
            "$('#test-rect').attr('width', '75')",
            editor
        )
        
        assert "Applied attr to 1 elements" in result
        assert editor.get_element_attribute("//*[@id='test-rect']", "width") == "75"

    def test_process_text_setter(self, sample_svg: str, tmp_path: Path) -> None:
        """Test processing a text setter command"""
        test_file = tmp_path / "test.svg"
        test_file.write_text(Path(sample_svg).read_text())
        
        editor = FileEditor(str(test_file))
        result = process_jquery_syntax(
            "$('#test-text').text('New Text')",
            editor
        )
        
        assert "Applied text to 1 elements" in result
        assert editor.get_element_text("//*[@id='test-text']") == "New Text"

    def test_process_html_setter(self, sample_svg: str, tmp_path: Path) -> None:
        """Test processing an HTML setter command"""
        test_file = tmp_path / "test.svg"
        test_file.write_text(Path(sample_svg).read_text())
        
        editor = FileEditor(str(test_file))
        result = process_jquery_syntax(
            "$('#test-text').html('<tspan>HTML</tspan>')",
            editor
        )
        
        assert "Applied html to 1 elements" in result
        assert "<tspan>HTML</tspan>" in editor.get_element_html("//*[@id='test-text']")

    def test_invalid_selector(self, sample_svg: str) -> None:
        """Test handling of invalid CSS selector"""
        editor = FileEditor(sample_svg)
        result = process_jquery_syntax(
            "$('invalid[selector').css('color', 'red')",
            editor
        )
        assert "Error processing jQuery command" in result

    def test_invalid_method(self, sample_svg: str) -> None:
        """Test handling of invalid method"""
        editor = FileEditor(sample_svg)
        result = process_jquery_syntax(
            "$('#test-rect').invalid_method('arg')",
            editor
        )
        assert "Unknown method" in result or "Error processing" in result
