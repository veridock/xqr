"""
HTTP server for the XQR package.

This module provides functionality to start and manage the HTTP server
for the XQR file editor.
"""

from http.server import HTTPServer
from typing import Optional, Type

from .handlers import FileEditorServer

def start_server(port: int = 8080, server_class: Type[HTTPServer] = HTTPServer) -> None:
    """Start the HTTP server for the file editor.
    
    Args:
        port: The port number to listen on (default: 8080)
        server_class: The HTTP server class to use (for testing)
    """
    server_address = ('', port)
    httpd = server_class(server_address, FileEditorServer)
    
    print(f"🌐 Starting File Editor Server on port {port}")
    print(f"Open http://localhost:{port} in your browser")
    print("Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
    finally:
        httpd.server_close()
        print("Server stopped")
