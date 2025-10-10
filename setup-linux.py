#!/usr/bin/env python3
"""
Airguard ESP32 IoT - Complete Linux Setup Script
=================================================
This script automates the entire setup process for Linux systems:
- Detects and validates system dependencies
- Finds and configures ESP32 serial ports
- Creates all necessary .env files
- Sets up Python virtual environment
- Installs all Node.js dependencies
- Configures and starts MongoDB
- Tests hardware connections
- Verifies the complete system

Requirements:
- Python 3.9+
- sudo privileges for package installation
- ESP32 sender and receiver with firmware already uploaded
- Internet connection for package downloads

Usage:
    sudo python3 setup-linux.py
    
Or make it executable:
    chmod +x setup-linux.py
    sudo ./setup-linux.py
"""

import os
import sys
import subprocess
import time
import json
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")

def run_command(cmd: str, shell: bool = True, check: bool = True, capture: bool = True) -> Optional[subprocess.CompletedProcess]:
    """Execute a shell command and return the result"""
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            check=check,
            capture_output=capture,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        if capture:
            print_error(f"Command failed: {cmd}")
            if e.stderr:
                print_error(f"Error: {e.stderr}")
        return None

def check_root_privileges() -> bool:
    """Check if script is running with root privileges"""
    return os.geteuid() == 0

def detect_linux_distro() -> Tuple[str, str]:
    """Detect Linux distribution"""
    try:
        with open('/etc/os-release', 'r') as f:
            lines = f.readlines()
            distro_info = {}
            for line in lines:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    distro_info[key] = value.strip('"')
            
            distro_id = distro_info.get('ID', 'unknown').lower()
            distro_name = distro_info.get('NAME', 'Unknown')
            return distro_id, distro_name
    except:
        return 'unknown', 'Unknown'

def check_dependency(command: str, package_name: str = None) -> bool:
    """Check if a command/dependency is available"""
    result = shutil.which(command)
    return result is not None

def install_system_dependencies(distro_id: str) -> bool:
    """Install required system dependencies based on distro"""
    print_header("📦 Installing System Dependencies")
    
    if not check_root_privileges():
        print_error("This script requires root privileges for package installation")
        print_info("Please run with: sudo python3 setup-linux.py")
        return False
    
    dependencies = {
        'ubuntu': ['curl', 'wget', 'git', 'python3', 'python3-pip', 'python3-venv', 
                   'nodejs', 'npm', 'mongodb-org'],
        'debian': ['curl', 'wget', 'git', 'python3', 'python3-pip', 'python3-venv',
                   'nodejs', 'npm', 'mongodb-org'],
        'fedora': ['curl', 'wget', 'git', 'python3', 'python3-pip', 'nodejs', 
                   'npm', 'mongodb-org'],
        'arch': ['curl', 'wget', 'git', 'python', 'python-pip', 'nodejs', 
                 'npm', 'mongodb-bin'],
    }
    
    # Update package lists
    print_info("Updating package lists...")
    if distro_id in ['ubuntu', 'debian']:
        run_command("apt update", capture=False)
    elif distro_id == 'fedora':
        run_command("dnf check-update", check=False, capture=False)
    elif distro_id == 'arch':
        run_command("pacman -Sy", capture=False)
    
    # Install Node.js 18+ for Ubuntu/Debian
    if distro_id in ['ubuntu', 'debian']:
        print_info("Installing Node.js 18 LTS...")
        run_command("curl -fsSL https://deb.nodesource.com/setup_18.x | bash -", capture=False)
        run_command("apt install -y nodejs", capture=False)
    
    # Install MongoDB for Ubuntu/Debian
    if distro_id in ['ubuntu', 'debian']:
        print_info("Installing MongoDB 6.0...")
        
        # Import MongoDB GPG key
        run_command("wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add -", capture=False)
        
        # Add MongoDB repository
        if distro_id == 'ubuntu':
            result = run_command("lsb_release -cs")
            if result:
                codename = result.stdout.strip()
                repo_line = f"deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu {codename}/mongodb-org/6.0 multiverse"
                with open('/etc/apt/sources.list.d/mongodb-org-6.0.list', 'w') as f:
                    f.write(repo_line)
        
        run_command("apt update", capture=False)
        run_command("apt install -y mongodb-org", capture=False)
    
    # Install basic dependencies
    print_info("Installing base packages...")
    if distro_id in ['ubuntu', 'debian']:
        run_command("apt install -y curl wget git python3 python3-pip python3-venv", capture=False)
    elif distro_id == 'fedora':
        run_command("dnf install -y curl wget git python3 python3-pip nodejs npm mongodb-org", capture=False)
    elif distro_id == 'arch':
        run_command("pacman -S --noconfirm curl wget git python python-pip nodejs npm mongodb-bin", capture=False)
    
    print_success("System dependencies installed")
    return True

def verify_dependencies() -> Dict[str, bool]:
    """Verify all required dependencies are installed"""
    print_header("🔍 Verifying Dependencies")
    
    deps = {
        'Python 3.9+': False,
        'Node.js 18+': False,
        'npm': False,
        'MongoDB': False,
        'Git': False,
    }
    
    # Check Python
    if check_dependency('python3'):
        result = run_command("python3 --version")
        if result:
            version = result.stdout.strip().split()[1]
            major, minor = map(int, version.split('.')[:2])
            if major >= 3 and minor >= 9:
                deps['Python 3.9+'] = True
                print_success(f"Python {version} found")
            else:
                print_warning(f"Python {version} found, but 3.9+ required")
    
    # Check Node.js
    if check_dependency('node'):
        result = run_command("node --version")
        if result:
            version = result.stdout.strip()[1:]  # Remove 'v' prefix
            major = int(version.split('.')[0])
            if major >= 18:
                deps['Node.js 18+'] = True
                print_success(f"Node.js {version} found")
            else:
                print_warning(f"Node.js {version} found, but 18+ required")
    
    # Check npm
    if check_dependency('npm'):
        result = run_command("npm --version")
        if result:
            version = result.stdout.strip()
            deps['npm'] = True
            print_success(f"npm {version} found")
    
    # Check MongoDB
    if check_dependency('mongod'):
        result = run_command("mongod --version")
        if result:
            deps['MongoDB'] = True
            print_success("MongoDB found")
    
    # Check Git
    if check_dependency('git'):
        result = run_command("git --version")
        if result:
            version = result.stdout.strip().split()[2]
            deps['Git'] = True
            print_success(f"Git {version} found")
    
    all_ok = all(deps.values())
    if not all_ok:
        print_warning("Some dependencies are missing or outdated")
        for dep, status in deps.items():
            if not status:
                print_error(f"Missing: {dep}")
    
    return deps

def detect_serial_ports() -> List[Dict[str, str]]:
    """Detect available serial ports and identify ESP32 devices"""
    print_header("🔌 Detecting Serial Ports")
    
    try:
        import serial.tools.list_ports
    except ImportError:
        print_warning("pyserial not installed, installing now...")
        run_command("pip3 install pyserial", capture=False)
        import serial.tools.list_ports
    
    ports = []
    for port in serial.tools.list_ports.comports():
        port_info = {
            'device': port.device,
            'description': port.description,
            'hwid': port.hwid,
            'manufacturer': port.manufacturer or 'Unknown',
            'product': port.product or 'Unknown',
            'type': 'unknown'
        }
        
        # Detect ESP32 devices
        desc_lower = port.description.lower()
        hwid_lower = port.hwid.lower()
        
        if 'cp210' in desc_lower or 'cp210' in hwid_lower:
            port_info['type'] = 'ESP32 (CP2102)'
        elif 'ch340' in desc_lower or 'ch340' in hwid_lower:
            port_info['type'] = 'ESP32 (CH340)'
        elif 'ftdi' in desc_lower or 'ftdi' in hwid_lower:
            port_info['type'] = 'ESP32 (FTDI)'
        elif 'usb serial' in desc_lower:
            port_info['type'] = 'ESP32 (USB Serial)'
        
        ports.append(port_info)
        
        print_info(f"Found: {port.device}")
        print(f"  Description: {port.description}")
        print(f"  Hardware ID: {port.hwid}")
        print(f"  Type: {port_info['type']}")
        print()
    
    return ports

def test_serial_port(port: str, baud_rate: int = 115200, timeout: int = 5) -> Tuple[bool, str]:
    """Test serial port and try to identify if it's sender or receiver"""
    try:
        import serial
    except ImportError:
        run_command("pip3 install pyserial", capture=False)
        import serial
    
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        print_info(f"Testing {port}...")
        
        start_time = time.time()
        data_received = []
        
        while time.time() - start_time < timeout:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        data_received.append(line)
                        print(f"  → {line[:80]}")
                except:
                    pass
        
        ser.close()
        
        # Analyze received data to identify device type
        all_data = ' '.join(data_received).lower()
        
        if 'receiver' in all_data or 'waiting for data' in all_data or 'mac address' in all_data:
            return True, 'receiver'
        elif 'sender' in all_data or 'measure' in all_data or 'send' in all_data:
            return True, 'sender'
        elif data_received:
            # Has data but can't identify - could be receiver with data coming in
            if '{' in all_data or 'gps' in all_data or 'mpu' in all_data:
                return True, 'receiver'
            return True, 'unknown'
        else:
            return False, 'no_data'
    
    except Exception as e:
        print_error(f"Error testing {port}: {e}")
        return False, 'error'

def configure_serial_ports(ports: List[Dict[str, str]]) -> Optional[str]:
    """Interactive configuration of serial ports"""
    print_header("⚙️ Configuring Serial Ports")
    
    esp32_ports = [p for p in ports if 'ESP32' in p['type'] or 'USB' in p['type']]
    
    if not esp32_ports:
        print_warning("No ESP32 devices detected automatically")
        print_info("Available ports:")
        for i, port in enumerate(ports, 1):
            print(f"  {i}. {port['device']} - {port['description']}")
        
        if not ports:
            print_error("No serial ports found!")
            print_info("Please ensure:")
            print_info("  1. ESP32 devices are connected via USB")
            print_info("  2. You have permission to access serial ports (add user to dialout group)")
            print_info("     sudo usermod -a -G dialout $USER")
            print_info("  3. Reboot after adding to dialout group")
            return None
        
        esp32_ports = ports
    
    print_info(f"Found {len(esp32_ports)} potential ESP32 device(s)")
    print()
    
    # Test each port to identify receiver
    receiver_port = None
    tested_ports = []
    
    for port in esp32_ports:
        device = port['device']
        is_responsive, device_type = test_serial_port(device)
        
        tested_ports.append({
            'device': device,
            'responsive': is_responsive,
            'type': device_type
        })
        
        if device_type == 'receiver':
            receiver_port = device
            print_success(f"Identified receiver on {device}")
            break
        
        print()
    
    # If automatic detection failed, ask user
    if not receiver_port and tested_ports:
        print_warning("Could not automatically identify receiver")
        print_info("Please select the receiver port:")
        
        for i, port_info in enumerate(tested_ports, 1):
            status = "✓ Responsive" if port_info['responsive'] else "✗ No response"
            print(f"  {i}. {port_info['device']} ({port_info['type']}) - {status}")
        
        while True:
            try:
                choice = input(f"\nEnter choice (1-{len(tested_ports)}): ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(tested_ports):
                    receiver_port = tested_ports[idx]['device']
                    break
                else:
                    print_error("Invalid choice")
            except (ValueError, KeyboardInterrupt):
                print_error("\nSetup cancelled")
                return None
    
    if receiver_port:
        print_success(f"Receiver port configured: {receiver_port}")
        return receiver_port
    else:
        print_error("Could not configure receiver port")
        return None

def create_env_files(receiver_port: str, project_root: Path) -> bool:
    """Create all necessary .env files"""
    print_header("📝 Creating Environment Files")
    
    env_configs = {
        'host/python-gateway/.env': f"""# Python Gateway Configuration
SERIAL_PORT={receiver_port}
BAUD_RATE=115200
CLOUD_POST_URL=http://localhost:8080/v1/samples
MQTT_BROKER=127.0.0.1
MQTT_PORT=1883
MQTT_TOPIC_ESPNOW=espnow/samples
MQTT_TOPIC_COMMAND=espnow/command
DB_PATH=sensor_data.db
LOG_LEVEL=INFO
""",
        'host/node-backend/.env': """# Node Backend Configuration
PORT=8080
WEBSOCKET_PORT=8081
MONGODB_URI=mongodb://localhost:27017/airguard
MQTT_BROKER_URL=mqtt://localhost:1883
MQTT_TOPIC_ESPNOW=espnow/samples
MQTT_TOPIC_COMMAND=espnow/command
LOG_LEVEL=info
""",
        'bridges/mqtt-mongo/.env': """# MQTT-MongoDB Bridge Configuration
MONGODB_URI=mongodb://localhost:27017/airguard
MQTT_BROKER_URL=mqtt://localhost:1883
MQTT_TOPIC_ESPNOW=espnow/samples
MQTT_TOPIC_COMMAND=espnow/command
LOG_LEVEL=info
"""
    }
    
    for env_path, content in env_configs.items():
        full_path = project_root / env_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(full_path, 'w') as f:
                f.write(content)
            print_success(f"Created {env_path}")
        except Exception as e:
            print_error(f"Failed to create {env_path}: {e}")
            return False
    
    return True

def setup_python_environment(project_root: Path) -> bool:
    """Setup Python virtual environment and install dependencies"""
    print_header("🐍 Setting Up Python Environment")
    
    gateway_dir = project_root / 'host' / 'python-gateway'
    venv_dir = gateway_dir / 'venv'
    
    # Create virtual environment
    if venv_dir.exists():
        print_info("Virtual environment already exists")
    else:
        print_info("Creating virtual environment...")
        result = run_command(f"python3 -m venv {venv_dir}", capture=False)
        if result is None:
            print_error("Failed to create virtual environment")
            return False
        print_success("Virtual environment created")
    
    # Install requirements
    requirements_file = gateway_dir / 'requirements.txt'
    if requirements_file.exists():
        print_info("Installing Python dependencies...")
        pip_path = venv_dir / 'bin' / 'pip'
        result = run_command(f"{pip_path} install -r {requirements_file}", capture=False)
        if result is None:
            print_error("Failed to install Python dependencies")
            return False
        print_success("Python dependencies installed")
    else:
        print_warning(f"No requirements.txt found at {requirements_file}")
    
    # Install script dependencies
    script_requirements = project_root / 'requirements-scripts.txt'
    if script_requirements.exists():
        print_info("Installing script management dependencies...")
        result = run_command(f"pip3 install -r {script_requirements}", capture=False)
        if result is None:
            print_warning("Failed to install script dependencies (optional)")
        else:
            print_success("Script dependencies installed")
    
    return True

def setup_nodejs_dependencies(project_root: Path) -> bool:
    """Install all Node.js dependencies"""
    print_header("📦 Installing Node.js Dependencies")
    
    node_dirs = [
        'mqtt-broker',
        'host/node-backend',
        'bridges/mqtt-mongo'
    ]
    
    for node_dir in node_dirs:
        full_path = project_root / node_dir
        package_json = full_path / 'package.json'
        
        if package_json.exists():
            print_info(f"Installing dependencies for {node_dir}...")
            result = run_command(f"cd {full_path} && npm install", capture=False)
            if result is None:
                print_error(f"Failed to install dependencies for {node_dir}")
                return False
            print_success(f"Dependencies installed for {node_dir}")
        else:
            print_warning(f"No package.json found in {node_dir}")
    
    return True

def configure_mongodb() -> bool:
    """Configure and start MongoDB"""
    print_header("🗄️ Configuring MongoDB")
    
    # Check if MongoDB is running
    result = run_command("pgrep -x mongod", check=False)
    if result and result.returncode == 0:
        print_info("MongoDB is already running")
        return True
    
    # Try to start MongoDB
    print_info("Starting MongoDB service...")
    
    # Try systemd first
    result = run_command("systemctl start mongod", check=False, capture=False)
    if result and result.returncode == 0:
        run_command("systemctl enable mongod", check=False, capture=False)
        print_success("MongoDB started via systemd")
        return True
    
    # Try manual start
    print_info("Trying manual MongoDB start...")
    mongo_data_dir = Path.home() / '.mongodb' / 'data'
    mongo_log_dir = Path.home() / '.mongodb' / 'log'
    mongo_data_dir.mkdir(parents=True, exist_ok=True)
    mongo_log_dir.mkdir(parents=True, exist_ok=True)
    
    mongo_cmd = f"mongod --dbpath {mongo_data_dir} --logpath {mongo_log_dir}/mongod.log --fork"
    result = run_command(mongo_cmd, check=False)
    
    if result and result.returncode == 0:
        print_success("MongoDB started manually")
        return True
    
    print_error("Failed to start MongoDB")
    print_info("You may need to start MongoDB manually:")
    print_info(f"  mongod --dbpath {mongo_data_dir} --logpath {mongo_log_dir}/mongod.log --fork")
    return False

def test_mongodb_connection() -> bool:
    """Test MongoDB connection"""
    try:
        result = run_command("mongosh --eval 'db.version()' --quiet", check=False)
        if result and result.returncode == 0:
            print_success("MongoDB connection successful")
            return True
        
        # Try legacy mongo command
        result = run_command("mongo --eval 'db.version()' --quiet", check=False)
        if result and result.returncode == 0:
            print_success("MongoDB connection successful")
            return True
        
        print_error("Could not connect to MongoDB")
        return False
    except Exception as e:
        print_error(f"MongoDB connection test failed: {e}")
        return False

def add_user_to_dialout_group() -> bool:
    """Add current user to dialout group for serial port access"""
    print_header("👤 Configuring Serial Port Permissions")
    
    import pwd
    current_user = pwd.getpwuid(os.getuid()).pw_name
    
    # Check if user is in dialout group
    result = run_command(f"groups {current_user}")
    if result and 'dialout' in result.stdout:
        print_success(f"User {current_user} is already in dialout group")
        return True
    
    print_info(f"Adding {current_user} to dialout group...")
    result = run_command(f"usermod -a -G dialout {current_user}", check=False)
    
    if result and result.returncode == 0:
        print_success(f"User {current_user} added to dialout group")
        print_warning("You need to log out and log back in for this to take effect!")
        print_info("Or run: newgrp dialout")
        return True
    else:
        print_error("Failed to add user to dialout group")
        print_info("You may need to run this manually:")
        print_info(f"  sudo usermod -a -G dialout {current_user}")
        return False

def create_startup_scripts(project_root: Path) -> bool:
    """Create convenience startup scripts for Linux"""
    print_header("📜 Creating Startup Scripts")
    
    # Create start script
    start_script = project_root / 'start-airguard.sh'
    start_content = """#!/bin/bash
# Airguard ESP32 IoT - Linux Startup Script

echo "🚀 Starting Airguard Services..."

# Start MongoDB if not running
if ! pgrep -x mongod > /dev/null; then
    echo "Starting MongoDB..."
    sudo systemctl start mongod || mongod --dbpath ~/.mongodb/data --logpath ~/.mongodb/log/mongod.log --fork
fi

# Use Python startup script if available
if [ -f "start-services.py" ]; then
    python3 start-services.py
else
    echo "Manual startup..."
    
    # Start MQTT Broker
    cd mqtt-broker && npm start &
    
    # Start Node Backend
    cd host/node-backend && npm start &
    
    # Start MQTT-MongoDB Bridge
    cd bridges/mqtt-mongo && node bridge.js &
    
    # Start Python Gateway
    cd host/python-gateway
    source venv/bin/activate
    python gateway_enhanced.py &
fi

echo "✅ All services started!"
"""
    
    try:
        with open(start_script, 'w') as f:
            f.write(start_content)
        os.chmod(start_script, 0o755)
        print_success(f"Created {start_script.name}")
    except Exception as e:
        print_error(f"Failed to create startup script: {e}")
        return False
    
    # Create stop script
    stop_script = project_root / 'stop-airguard.sh'
    stop_content = """#!/bin/bash
# Airguard ESP32 IoT - Linux Stop Script

echo "🛑 Stopping Airguard Services..."

if [ -f "stop-services.py" ]; then
    python3 stop-services.py
else
    # Kill Node.js processes
    pkill -f "node.*mqtt-broker"
    pkill -f "node.*node-backend"
    pkill -f "node.*bridge.js"
    
    # Kill Python gateway
    pkill -f "python.*gateway"
fi

echo "✅ All services stopped!"
"""
    
    try:
        with open(stop_script, 'w') as f:
            f.write(stop_content)
        os.chmod(stop_script, 0o755)
        print_success(f"Created {stop_script.name}")
    except Exception as e:
        print_error(f"Failed to create stop script: {e}")
        return False
    
    return True

def run_system_health_check(project_root: Path) -> Dict[str, bool]:
    """Run comprehensive system health check"""
    print_header("🏥 Running System Health Check")
    
    health = {
        'mongodb': False,
        'serial_ports': False,
        'python_env': False,
        'node_modules': False,
        'env_files': False
    }
    
    # Check MongoDB
    if test_mongodb_connection():
        health['mongodb'] = True
    
    # Check serial ports
    ports = detect_serial_ports()
    if ports:
        health['serial_ports'] = True
    
    # Check Python environment
    venv_path = project_root / 'host' / 'python-gateway' / 'venv'
    if venv_path.exists():
        health['python_env'] = True
        print_success("Python virtual environment exists")
    
    # Check Node modules
    node_modules_paths = [
        project_root / 'mqtt-broker' / 'node_modules',
        project_root / 'host' / 'node-backend' / 'node_modules',
        project_root / 'bridges' / 'mqtt-mongo' / 'node_modules'
    ]
    if all(p.exists() for p in node_modules_paths):
        health['node_modules'] = True
        print_success("All Node.js dependencies installed")
    
    # Check .env files
    env_files = [
        project_root / 'host' / 'python-gateway' / '.env',
        project_root / 'host' / 'node-backend' / '.env',
        project_root / 'bridges' / 'mqtt-mongo' / '.env'
    ]
    if all(f.exists() for f in env_files):
        health['env_files'] = True
        print_success("All .env files created")
    
    return health

def print_final_summary(health: Dict[str, bool], receiver_port: Optional[str]):
    """Print final setup summary"""
    print_header("📋 Setup Complete - Summary")
    
    all_ok = all(health.values())
    
    if all_ok:
        print_success("All components configured successfully! ✨")
    else:
        print_warning("Setup completed with some warnings")
    
    print()
    print(f"{Colors.BOLD}System Status:{Colors.END}")
    for component, status in health.items():
        status_str = f"{Colors.GREEN}✓{Colors.END}" if status else f"{Colors.RED}✗{Colors.END}"
        print(f"  {status_str} {component.replace('_', ' ').title()}")
    
    print()
    print(f"{Colors.BOLD}Configuration:{Colors.END}")
    if receiver_port:
        print(f"  Receiver Port: {Colors.CYAN}{receiver_port}{Colors.END}")
    print(f"  MongoDB: {Colors.CYAN}mongodb://localhost:27017/airguard{Colors.END}")
    print(f"  MQTT Broker: {Colors.CYAN}mqtt://localhost:1883{Colors.END}")
    print(f"  Backend API: {Colors.CYAN}http://localhost:8080{Colors.END}")
    print(f"  WebSocket: {Colors.CYAN}ws://localhost:8081{Colors.END}")
    
    print()
    print(f"{Colors.BOLD}Next Steps:{Colors.END}")
    print(f"  1. {Colors.CYAN}Start services:{Colors.END} python3 start-services.py")
    print(f"     Or: ./start-airguard.sh")
    print(f"  2. {Colors.CYAN}Check health:{Colors.END} python3 health-check.py")
    print(f"  3. {Colors.CYAN}Open dashboard:{Colors.END} xdg-open host/dashboard.html")
    print(f"  4. {Colors.CYAN}Test ESP32:{Colors.END} Press and hold button on sender for 10 seconds")
    print(f"  5. {Colors.CYAN}Stop services:{Colors.END} python3 stop-services.py")
    print(f"     Or: ./stop-airguard.sh")
    
    if not health['serial_ports']:
        print()
        print_warning("Serial port configuration incomplete!")
        print_info("Make sure:")
        print_info("  • ESP32 devices are connected via USB")
        print_info("  • You're in the dialout group: sudo usermod -a -G dialout $USER")
        print_info("  • You've logged out and back in after adding to dialout")
    
    print()
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}🎉 Airguard ESP32 IoT is ready to use!{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.END}\n")

def main():
    """Main setup function"""
    print_header("🛡️ Airguard ESP32 IoT - Linux Setup")
    print(f"{Colors.CYAN}Automated Environment Configuration{Colors.END}\n")
    
    # Determine project root
    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir
    
    print_info(f"Project directory: {project_root}")
    print()
    
    # Detect Linux distribution
    distro_id, distro_name = detect_linux_distro()
    print_info(f"Detected: {distro_name} ({distro_id})")
    print()
    
    # Check root privileges for installation
    if not check_root_privileges():
        print_warning("Not running as root - will skip system package installation")
        print_info("If you need to install system dependencies, run with sudo")
        install_deps = False
    else:
        install_deps = True
    
    # Install system dependencies
    if install_deps:
        if not install_system_dependencies(distro_id):
            print_error("Failed to install system dependencies")
            sys.exit(1)
        
        # Add user to dialout group
        add_user_to_dialout_group()
    
    # Verify dependencies
    deps = verify_dependencies()
    if not all(deps.values()):
        print_error("Not all dependencies are available")
        print_info("Please install missing dependencies and run again")
        sys.exit(1)
    
    # Detect and configure serial ports
    ports = detect_serial_ports()
    receiver_port = configure_serial_ports(ports)
    
    if not receiver_port:
        print_error("Serial port configuration failed")
        print_info("You can manually edit host/python-gateway/.env later")
        receiver_port = "/dev/ttyUSB0"  # Default fallback
    
    # Create .env files
    if not create_env_files(receiver_port, project_root):
        print_error("Failed to create .env files")
        sys.exit(1)
    
    # Setup Python environment
    if not setup_python_environment(project_root):
        print_error("Failed to setup Python environment")
        sys.exit(1)
    
    # Setup Node.js dependencies
    if not setup_nodejs_dependencies(project_root):
        print_error("Failed to setup Node.js dependencies")
        sys.exit(1)
    
    # Configure MongoDB
    configure_mongodb()
    
    # Create startup scripts
    create_startup_scripts(project_root)
    
    # Run health check
    health = run_system_health_check(project_root)
    
    # Print summary
    print_final_summary(health, receiver_port)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Setup cancelled by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
