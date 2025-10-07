#!/usr/bin/env python3
"""
Airguard System Health Check
Cross-platform health monitoring (Windows, macOS, Linux)
"""

import sys
import socket
import platform
from pathlib import Path
from datetime import datetime

# ANSI color codes
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
    print_color(text, Colors.YELLOW + Colors.BOLD)

def check_port(port, service_name):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        
        if result == 0:
            print_color(f"  ✓ Port {port} ({service_name}) is open", Colors.GREEN)
            return True
        else:
            print_color(f"  ✗ Port {port} ({service_name}) is closed", Colors.RED)
            return False
    except Exception as e:
        print_color(f"  ⚠ Could not check port {port}: {e}", Colors.YELLOW)
        return False

def check_processes():
    """Check for running Airguard processes"""
    try:
        import psutil
        
        node_count = 0
        python_count = 0
        
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name'].lower()
                if 'node' in proc_name or 'node.exe' in proc_name:
                    node_count += 1
                elif 'python' in proc_name:
                    python_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return node_count, python_count
    except ImportError:
        return None, None

def check_database():
    """Check SQLite database"""
    db_path = Path(__file__).parent / "host" / "python-gateway" / "airguard.db"
    
    if db_path.exists():
        size_bytes = db_path.stat().st_size
        size_kb = size_bytes / 1024
        size_mb = size_kb / 1024
        
        if size_mb >= 1:
            print_color(f"  SQLite database size: {size_mb:.2f} MB", Colors.GREEN)
        else:
            print_color(f"  SQLite database size: {size_kb:.2f} KB", Colors.GREEN)
        return True
    else:
        print_color("  SQLite database not found", Colors.YELLOW)
        return False

def check_serial_ports():
    """Check available serial ports"""
    try:
        import serial.tools.list_ports
        
        ports = list(serial.tools.list_ports.comports())
        
        if ports:
            port_names = [p.device for p in ports]
            print_color(f"  Available ports: {', '.join(port_names)}", Colors.GREEN)
            
            for port in ports:
                if any(x in port.description.lower() for x in ['ch340', 'ch343', 'cp210', 'esp32', 'usb-serial']):
                    print_color(f"    → {port.device}: {port.description}", Colors.CYAN)
            return True
        else:
            print_color("  No serial ports detected", Colors.YELLOW)
            return False
            
    except ImportError:
        print_color("  pyserial not installed (run: pip install pyserial)", Colors.YELLOW)
        return False

def check_env_files():
    """Check if .env files exist"""
    project_root = Path(__file__).parent
    
    env_files = [
        "host/python-gateway/.env",
        "host/node-backend/.env",
        "bridges/mqtt-mongo/.env"
    ]
    
    missing = []
    for env_file in env_files:
        path = project_root / env_file
        if not path.exists():
            missing.append(env_file)
    
    if missing:
        print_color(f"  ⚠ Missing .env files:", Colors.YELLOW)
        for f in missing:
            print_color(f"    - {f}", Colors.YELLOW)
        return False
    else:
        print_color(f"  ✓ All .env files present", Colors.GREEN)
        return True

def main():
    """Main health check"""
    print()
    print_color("=" * 60, Colors.CYAN)
    print_color("🔍 Airguard System Health Check", Colors.CYAN + Colors.BOLD)
    print_color("=" * 60, Colors.CYAN)
    
    # System info
    print_header("💻 System Information")
    print_color(f"  OS: {platform.system()} {platform.release()}", Colors.WHITE)
    print_color(f"  Python: {platform.python_version()}", Colors.WHITE)
    print_color(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Colors.WHITE)
    
    # Check ports
    print_header("🌐 Port Status")
    ports = [
        (27017, "MongoDB"),
        (1883, "MQTT Broker"),
        (8080, "Node Backend HTTP"),
        (8081, "WebSocket")
    ]
    
    open_ports = 0
    for port, name in ports:
        if check_port(port, name):
            open_ports += 1
    
    # Check processes
    print_header("⚙️  Process Status")
    node_count, python_count = check_processes()
    
    if node_count is not None:
        if node_count > 0:
            print_color(f"  ✓ Node.js processes running: {node_count}", Colors.GREEN)
        else:
            print_color(f"  ⚠ No Node.js processes detected", Colors.YELLOW)
        
        if python_count > 0:
            print_color(f"  ✓ Python processes running: {python_count}", Colors.GREEN)
        else:
            print_color(f"  ⚠ No Python processes detected", Colors.YELLOW)
    else:
        print_color("  ⚠ psutil not installed (run: pip install psutil)", Colors.YELLOW)
        print_color("  Cannot check process status", Colors.YELLOW)
    
    # Check database
    print_header("💾 Database Status")
    check_database()
    
    # Check serial ports
    print_header("🔌 Serial Ports")
    check_serial_ports()
    
    # Check configuration
    print_header("⚙️  Configuration")
    check_env_files()
    
    # Summary
    print()
    print_color("=" * 60, Colors.CYAN)
    
    if open_ports == len(ports):
        print_color("✓ All services appear to be running!", Colors.GREEN + Colors.BOLD)
    elif open_ports > 0:
        print_color(f"⚠ {open_ports}/{len(ports)} services are running", Colors.YELLOW + Colors.BOLD)
        print_color("  Run 'python start-services.py' to start missing services", Colors.CYAN)
    else:
        print_color("✗ No services detected", Colors.RED + Colors.BOLD)
        print_color("  Run 'python start-services.py' to start all services", Colors.CYAN)
    
    print_color("=" * 60, Colors.CYAN)
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_color("Health check cancelled", Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        print_color(f"Health check failed: {e}", Colors.RED)
        sys.exit(1)
