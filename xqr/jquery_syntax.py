"""
jQuery-like syntax support for XQR
"""
from typing import Any, Dict, List, Optional, Union
from lxml import etree
import cssselect
from pathlib import Path

class JQuerySyntax:
    """Wrapper class to provide jQuery-like syntax for element operations."""
    
    def __init__(self, editor, selector: str):
        """Initialize with a FileEditor instance and a CSS selector.
        
        Args:
            editor: Instance of FileEditor
            selector: CSS selector string
        """
        self.editor = editor
        self.selector = selector
        self._compile_selector(selector)
    
    def _compile_selector(self, selector: str) -> None:
        """Compile CSS selector to XPath."""
        try:
            self.xpath_expr = cssselect.CSSSelector(selector, translator='xhtml').path
            # Convert the compiled XPath to string
            self.xpath = ''.join(etree.tostring(step, encoding='unicode') 
                               for step in self.xpath_expr)
        except cssselect.SelectorError as e:
            raise ValueError(f"Invalid CSS selector: {selector}") from e
    
    def css(self, property_name: str, value: Optional[str] = None) -> Union['JQuerySyntax', List[Dict[str, str]]]:
        """Get or set CSS properties on matched elements.
        
        Args:
            property_name: CSS property name
            value: Optional CSS property value. If None, returns current value(s).
            
        Returns:
            If value is None, returns list of current values for each matched element.
            Otherwise, returns self for method chaining.
        """
        if value is None:
            # Get CSS property
            return self.editor.get_element_attribute(self.xpath, 'style')
        else:
            # Set CSS property
            self.editor.set_element_css(self.xpath, property_name, value)
            return self
    
    def attr(self, name: str, value: Optional[Any] = None) -> Union['JQuerySyntax', str]:
        """Get or set attributes on matched elements.
        
        Args:
            name: Attribute name
            value: Optional attribute value. If None, returns current value.
            
        Returns:
            If value is None, returns attribute value for first matched element.
            Otherwise, returns self for method chaining.
        """
        if value is None:
            # Get attribute
            return self.editor.get_element_attribute(self.xpath, name)
        else:
            # Set attribute
            self.editor.set_element_attribute(self.xpath, name, str(value))
            return self
    
    def text(self, text: Optional[str] = None) -> Union['JQuerySyntax', str]:
        """Get or set text content of matched elements.
        
        Args:
            text: Optional text content. If None, returns current text.
            
        Returns:
            If text is None, returns text content of first matched element.
            Otherwise, returns self for method chaining.
        """
        if text is None:
            # Get text
            return self.editor.get_element_text(self.xpath)
        else:
            # Set text
            self.editor.set_element_text(self.xpath, text)
            return self
    
    def html(self, html: Optional[str] = None) -> Union['JQuerySyntax', str]:
        """Get or set HTML content of matched elements.
        
        Args:
            html: Optional HTML content. If None, returns current HTML.
            
        Returns:
            If html is None, returns HTML content of first matched element.
            Otherwise, returns self for method chaining.
        """
        if html is None:
            # Get HTML
            return self.editor.get_element_html(self.xpath)
        else:
            # Set HTML
            self.editor.set_element_html(self.xpath, html)
            return self

def process_jquery_syntax(command: str, editor) -> str:
    """Process a jQuery-like command and execute it.
    
    Args:
        command: jQuery-like command string (e.g., "$('.element').css('color', 'red')")
        editor: FileEditor instance
        
    Returns:
        Result of the operation as a string
    """
    try:
        # Simple parser for the jQuery-like syntax
        # This is a basic implementation that handles simple cases
        if not command.startswith('$(') or not (command.endswith(')') or ').' in command):
            raise ValueError("Invalid jQuery syntax. Expected format: $(selector).method(...)")
        
        # Extract selector
        selector_end = command.find(')')
        if selector_end == -1:
            raise ValueError("Missing closing parenthesis in selector")
            
        selector = command[2:selector_end].strip('"\'')
        
        # Create jQuery-like wrapper
        jq = JQuerySyntax(editor, selector)
        
        # Parse method calls
        method_calls = command[selector_end+1:].strip()
        
        # Simple evaluation of method calls (this is a simplified version)
        # In a real implementation, you'd want a proper parser
        if method_calls.startswith('.'):
            method_calls = method_calls[1:]
            
            # Simple method call parser (supports only basic cases)
            if '(' in method_calls and method_calls.endswith(')'):
                method_name = method_calls.split('(')[0]
                args_str = method_calls[method_calls.find('(')+1:-1]
                
                # Simple argument parsing (supports only string and number literals)
                args = []
                current_arg = ''
                in_quotes = False
                quote_char = None
                
                for char in args_str:
                    if char in ("'", '"') and (not in_quotes or char == quote_char):
                        in_quotes = not in_quotes
                        if in_quotes:
                            quote_char = char
                        else:
                            args.append(current_arg)
                            current_arg = ''
                    elif char == ',' and not in_quotes:
                        if current_arg.strip():
                            args.append(current_arg.strip())
                        current_arg = ''
                    else:
                        current_arg += char
                
                if current_arg.strip():
                    args.append(current_arg.strip())
                
                # Clean up arguments (remove quotes, convert types)
                processed_args = []
                for arg in args:
                    arg = arg.strip()
                    if (arg.startswith("'") and arg.endswith("'")) or \
                       (arg.startswith('"') and arg.endswith('"')):
                        processed_args.append(arg[1:-1])
                    elif arg.lower() == 'true':
                        processed_args.append(True)
                    elif arg.lower() == 'false':
                        processed_args.append(False)
                    elif arg.isdigit():
                        processed_args.append(int(arg))
                    elif arg.replace('.', '', 1).isdigit():
                        processed_args.append(float(arg))
                    else:
                        processed_args.append(arg)
                
                # Call the method
                method = getattr(jq, method_name, None)
                if not callable(method):
                    raise ValueError(f"Unknown method: {method_name}")
                
                result = method(*processed_args)
                
                # If the method returns self, indicate success
                if result is jq:
                    return f"✅ Applied {method_name} to {len(editor.find_elements(jq.xpath))} elements"
                return str(result)
        
        return f"✅ Selected {len(editor.find_elements(jq.xpath))} elements"
    
    except Exception as e:
        return f"❌ Error processing jQuery command: {e}"
