"""
LENA Agent Demo Server.

Serves the demo web UI for testing the LENA Agent API.

Usage:
    lena-agent-demo           # If installed via pip/uv
    python -m demo.server     # Direct module execution
    python demo/server.py     # Script execution

Then open http://localhost:3000 in your browser.
"""

import http.server
import socketserver
import os
import sys
import webbrowser
import argparse
from functools import partial
from pathlib import Path

try:
    from importlib.resources import files, as_file
except ImportError:
    from importlib_resources import files, as_file


def get_demo_dir() -> Path:
    """Get the demo directory path, works both in dev and installed mode."""
    # First try: package resources (when installed)
    try:
        demo_package = files("demo")
        # Check if index.html exists in package
        if (demo_package / "index.html").is_file():
            return Path(demo_package._path)
    except (TypeError, AttributeError):
        pass

    # Second try: relative to this file (development mode)
    script_dir = Path(__file__).parent.resolve()
    if (script_dir / "index.html").exists():
        return script_dir

    # Third try: current working directory
    cwd = Path.cwd()
    if (cwd / "demo" / "index.html").exists():
        return cwd / "demo"

    raise FileNotFoundError("Could not find demo/index.html")


class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler with CORS headers for local development."""

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def log_message(self, format, *args):
        """Custom log format."""
        print(f"[Demo] {args[0]}")


def main():
    """Main entry point for the demo server."""
    parser = argparse.ArgumentParser(
        description="LENA Agent Demo Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    lena-agent-demo                    # Start on default port 3000
    lena-agent-demo --port 8080        # Start on port 8080
    lena-agent-demo --no-browser       # Don't open browser automatically
    lena-agent-demo --api-url http://api.example.com:8000
        """
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=3000,
        help="Port to run the demo server on (default: 3000)"
    )
    parser.add_argument(
        "--api-url",
        type=str,
        default="http://localhost:8000",
        help="LENA Agent API URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't open browser automatically"
    )

    args = parser.parse_args()

    try:
        demo_dir = get_demo_dir()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    os.chdir(demo_dir)

    handler = partial(CORSHTTPRequestHandler, directory=str(demo_dir))

    try:
        with socketserver.TCPServer(("", args.port), handler) as httpd:
            print(f"""
================================================================
                    LENA Agent Demo Server
================================================================

  Demo site:  http://localhost:{args.port}
  API URL:    {args.api_url}

  Before using the demo, make sure the API server is running:

    lena-agent-api
    # or
    uv run api_server.py

  Press Ctrl+C to stop the server.

================================================================
""")

            # Try to open browser automatically
            if not args.no_browser:
                try:
                    webbrowser.open(f'http://localhost:{args.port}')
                except Exception:
                    pass

            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nDemo server stopped.")

    except OSError as e:
        if "Address already in use" in str(e) or "10048" in str(e):
            print(f"Error: Port {args.port} is already in use.")
            print(f"Try: lena-agent-demo --port {args.port + 1}")
        else:
            print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
