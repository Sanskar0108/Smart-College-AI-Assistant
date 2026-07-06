import os
import http.server
import socketserver
import webbrowser
from http.server import SimpleHTTPRequestHandler

PORT = 8000
DIRECTORY = "frontend"

class SafeHandler(SimpleHTTPRequestHandler):
    """
    Custom handler to serve files from the designated directory.
    """
    def __init__(self, *args, **kwargs):
        # We specify the directory to serve from using standard Python 3.7+ parameters
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def main():
    # Set the working directory to the script's root folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    
    if not os.path.exists(DIRECTORY):
        print(f"Error: Directory '{DIRECTORY}' not found. Please ensure it exists.")
        return

    print("=" * 65)
    print("        SMART COLLEGE AI ASSISTANT - FRONTEND DEV WORKSPACE      ")
    print("=" * 65)
    print(f"Serving static frontend files from: {os.path.join(current_dir, DIRECTORY)}")
    print(f"URL: http://localhost:{PORT}")
    print("Press Ctrl+C to stop the local preview server.")
    print("=" * 65)

    # Automatically open default web browser to the server URL
    try:
        webbrowser.open(f"http://localhost:{PORT}")
    except Exception as e:
        print(f"Could not open browser automatically: {e}")

    try:
        # Allow port reuse to avoid 'Address already in use' errors on quick restarts
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("", PORT), SafeHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nPreview server stopped. Happy hackathon!")
    except Exception as e:
        print(f"\nError running server: {e}")

if __name__ == "__main__":
    main()
