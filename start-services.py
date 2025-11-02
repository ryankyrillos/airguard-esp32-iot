#!/usr/bin/env python3
"""
Airguard Full Stack Startup Script
Cross-platform service launcher (Windows, macOS, Linux)
"""

import os
import sys
import time
import subprocess
import platform
from pathlib import Path

# ANSI color codes for cross-platform colored output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_color(text, color=Colors.WHITE):
    """Print colored text"""
    print(f"{color}{text}{Colors.RESET}")

def print_header(text):
    """Print section header"""
    print()
    print_color(text, Colors.YELLOW)

def print_success(text):
    """Print success message"""
    print_color(f"[OK] {text}", Colors.GREEN)

def print_error(text):
    """Print error message"""
    print_color(f"[ERROR] {text}", Colors.RED)

def get_project_root():
    """Get project root directory"""
    return Path(__file__).parent.absolute()

def is_port_open(port):
    """Check if a port is open"""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False

def check_mongodb():
    """Check if MongoDB is running"""
    print_header("Checking MongoDB...")
    
    if is_port_open(27017):
        print_success("MongoDB is running")
        return True
    
    print_color("MongoDB not detected, attempting to start...", Colors.YELLOW)
    
    system = platform.system()
    try:
        if system == "Windows":
            # Try to start Windows service
            subprocess.run(["net", "start", "MongoDB"], 
                         capture_output=True, check=False)
        elif system == "Darwin":  # macOS
            subprocess.run(["brew", "services", "start", "mongodb-community"], 
                         capture_output=True, check=False)
        else:  # Linux
            subprocess.run(["sudo", "systemctl", "start", "mongod"], 
                         capture_output=True, check=False)
        
        time.sleep(2)
        
        if is_port_open(27017):
            print_success("MongoDB started successfully")
            return True
        else:
            print_error("MongoDB failed to start")
            return False
    except Exception as e:
        print_error(f"Could not start MongoDB: {e}")
        return False

def start_service(name, command, cwd, wait_time=3):
    """Start a service in a new terminal/console"""
    print_header(f"Starting {name}...")
    
    system = platform.system()
    project_root = get_project_root()
    working_dir = project_root / cwd
    
    try:
        if system == "Windows":
            # Windows: Start in new PowerShell window
            full_cmd = f'powershell -NoExit -Command "cd {working_dir}; {command}"'
            subprocess.Popen(full_cmd, shell=True, cwd=working_dir)
            
        elif system == "Darwin":  # macOS
            # macOS: Use Terminal.app
            applescript = f'''
            tell application "Terminal"
                do script "cd {working_dir} && {command}"
            end tell
            '''
            subprocess.Popen(['osascript', '-e', applescript])
            
        else:  # Linux
            # Linux: Try gnome-terminal, then xterm, then konsole
            terminals = [
                ['gnome-terminal', '--', 'bash', '-c', f'cd {working_dir} && {command}; exec bash'],
                ['xterm', '-e', f'cd {working_dir} && {command}; bash'],
                ['konsole', '-e', f'cd {working_dir} && {command}'],
            ]
            
            for term_cmd in terminals:
                try:
                    subprocess.Popen(term_cmd)
                    break
                except FileNotFoundError:
                    continue
        
        time.sleep(wait_time)
        print_success(f"{name} started")
        return True
        
    except Exception as e:
        print_error(f"Failed to start {name}: {e}")
        return False

def main():
    """Main startup sequence"""
    print_color("=" * 50, Colors.CYAN)
    print_color("Starting Airguard Full Stack...", Colors.GREEN + Colors.BOLD)
    print_color("=" * 50, Colors.CYAN)
    
    # Check MongoDB first
    if not check_mongodb():
        print_error("MongoDB is required. Please install and start MongoDB manually.")
        print_color("\nWindows: choco install mongodb", Colors.CYAN)
        print_color("macOS:   brew install mongodb-community", Colors.CYAN)
        print_color("Linux:   sudo apt install mongodb-org", Colors.CYAN)
        sys.exit(1)
    
    # Start MQTT Broker
    start_service(
        "MQTT Broker",
        "npm start",
        "mqtt-broker"
    )
    
    # Start Node.js Backend
    start_service(
        "Node.js Backend",
        "npm start",
        "host/node-backend"
    )
    
    # Start MQTT-MongoDB Bridge
    start_service(
        "MQTT-MongoDB Bridge",
        "node bridge.js",
        "bridges/mqtt-mongo",
        wait_time=2
    )
    
    # Start Python Gateway
    python_cmd = "python" if platform.system() == "Windows" else "python3"
    start_service(
        "Python Gateway",
        f"{python_cmd} gateway_enhanced.py",
        "host/python-gateway",
        wait_time=2
    )
    
    # Optionally start dashboard server for remote/SSH access
    print()
    print_color("Start Dashboard Web Server? (for SSH/remote access)", Colors.YELLOW)
    print_color("  Press 'y' to start on port 8082, or Enter to skip", Colors.CYAN)
    
    try:
        import select
        import sys
        
        # Give user 5 seconds to respond
        if platform.system() != "Windows":
            # Unix-like systems
            import sys, select
            ready, _, _ = select.select([sys.stdin], [], [], 5)
            if ready:
                response = sys.stdin.readline().strip().lower()
                if response == 'y':
                    start_service(
                        "Dashboard Server",
                        f"{python_cmd} serve-dashboard.py",
                        ".",
                        wait_time=2
                    )
        else:
            # Windows - just ask without timeout
            response = input().strip().lower()
            if response == 'y':
                start_service(
                    "Dashboard Server",
                    f"{python_cmd} serve-dashboard.py",
                    ".",
                    wait_time=2
                )
    except:
        pass  # Skip if any issues
    
    # Summary
    print()
    print_color("=" * 50, Colors.CYAN)
    print_color("ALL SERVICES RUNNING!", Colors.GREEN + Colors.BOLD)
    print_color("=" * 50, Colors.CYAN)
    print()
    
    print_color("Services:", Colors.YELLOW)
    print_color("  MongoDB:        mongodb://localhost:27017", Colors.WHITE)
    print_color("  MQTT Broker:    mqtt://localhost:1883", Colors.WHITE)
    print_color("  REST API:       http://localhost:8080/v1/samples", Colors.WHITE)
    print_color("  WebSocket:      ws://localhost:8081", Colors.WHITE)
    print_color("  Python Gateway: Reading from configured serial port", Colors.WHITE)
    print()
    
    print_color("Dashboard:", Colors.YELLOW)
    dashboard_path = get_project_root() / "host" / "dashboard.html"
    print_color(f"  Local: file://{dashboard_path}", Colors.WHITE)
    print_color(f"  Remote (SSH): python3 serve-dashboard.py", Colors.CYAN)
    print_color(f"               Then visit: http://<server-ip>:8082/dashboard.html", Colors.CYAN)
    print()
    
    print_color("Press button on ESP32 sender to see data flow!", Colors.GREEN)
    print()
    
    print_color("Tip: Run 'python health-check.py' to verify all services", Colors.CYAN)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_color("Startup cancelled by user", Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        print_error(f"Startup failed: {e}")
        sys.exit(1)
