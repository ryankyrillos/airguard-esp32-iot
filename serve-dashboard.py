#!/usr/bin/env python3
"""
Simple HTTP server for Airguard Dashboard
Serves dashboard.html on port 8082 for remote access via SSH
"""

import http.server
import socketserver
import os
import sys

# Configuration
PORT = 8082
DIRECTORY = os.path.join(os.path.dirname(__file__), 'host')

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Add CORS headers to allow WebSocket connections
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

def main():
    # Change to the host directory
    os.chdir(DIRECTORY)
    
    with socketserver.TCPServer(("0.0.0.0", PORT), MyHTTPRequestHandler) as httpd:
        print("=" * 60)
        print("🌐 Airguard Dashboard Server")
        print("=" * 60)
        print(f"\n✓ Serving dashboard from: {DIRECTORY}")
        print(f"✓ Server running on port: {PORT}")
        print(f"\n📱 Access the dashboard at:")
        print(f"   • Local: http://localhost:{PORT}/dashboard.html")
        print(f"   • Remote: http://<your-server-ip>:{PORT}/dashboard.html")
        print(f"\n💡 SSH Port Forward:")
        print(f"   ssh -L {PORT}:localhost:{PORT} -L 8080:localhost:8080 -L 8081:localhost:8081 user@remote-host")
        print(f"   Then visit: http://localhost:{PORT}/dashboard.html")
        print(f"\n⏸  Press Ctrl+C to stop the server\n")
        print("=" * 60)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down server...")
            httpd.shutdown()
            print("✓ Server stopped\n")
            sys.exit(0)

if __name__ == "__main__":
    main()
