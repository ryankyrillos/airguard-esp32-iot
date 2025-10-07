#!/usr/bin/env python3
"""
Airguard Services Shutdown Script
Cross-platform service stopper (Windows, macOS, Linux)
"""

import sys
import signal
import platform
import subprocess
import psutil

# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RED = '\033[91m'
    RESET = '\033[0m'

def print_color(text, color=Colors.WHITE):
    """Print colored text"""
    print(f"{color}{text}{Colors.RESET}")

def print_success(text):
    """Print success message"""
    print_color(f"[OK] {text}", Colors.GREEN)

def print_error(text):
    """Print error message"""
    print_color(f"[ERROR] {text}", Colors.RED)

def find_airguard_processes():
    """Find all Airguard-related processes"""
    processes = {
        'node': [],
        'python': [],
        'npm': []
    }
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            proc_info = proc.info
            proc_name = proc_info['name'].lower()
            cmdline = ' '.join(proc_info.get('cmdline', [])).lower()
            
            # Find Node.js processes (MQTT broker, backend, bridge)
            if 'node' in proc_name or 'node.exe' in proc_name:
                if any(x in cmdline for x in ['mqtt', 'backend', 'bridge', 'server.js', 'broker.js']):
                    processes['node'].append(proc)
            
            # Find Python gateway processes
            elif 'python' in proc_name:
                if 'gateway' in cmdline:
                    processes['python'].append(proc)
            
            # Find npm processes
            elif 'npm' in proc_name:
                processes['npm'].append(proc)
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    return processes

def stop_processes(process_list, process_type):
    """Stop a list of processes"""
    if not process_list:
        print_color(f"  No {process_type} processes found", Colors.YELLOW)
        return
    
    print_color(f"  Found {len(process_list)} {process_type} process(es)", Colors.WHITE)
    
    stopped_count = 0
    for proc in process_list:
        try:
            proc_name = proc.info.get('name', 'Unknown')
            pid = proc.info.get('pid', 'Unknown')
            print_color(f"    Stopping {proc_name} (PID: {pid})...", Colors.WHITE)
            
            # Try graceful shutdown first
            proc.terminate()
            try:
                proc.wait(timeout=3)
                stopped_count += 1
            except psutil.TimeoutExpired:
                # Force kill if graceful shutdown fails
                proc.kill()
                proc.wait(timeout=2)
                stopped_count += 1
                
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print_color(f"    Could not stop process: {e}", Colors.YELLOW)
    
    if stopped_count > 0:
        print_success(f"{stopped_count} {process_type} process(es) stopped")
    else:
        print_color(f"  No {process_type} processes stopped", Colors.YELLOW)

def main():
    """Main shutdown sequence"""
    print()
    print_color("Stopping Airguard services...", Colors.YELLOW)
    print()
    
    # Find all Airguard processes
    processes = find_airguard_processes()
    
    total_found = sum(len(v) for v in processes.values())
    
    if total_found == 0:
        print_color("No Airguard processes found running", Colors.YELLOW)
        print()
        return
    
    print_color(f"Found {total_found} Airguard-related process(es)", Colors.CYAN)
    print()
    
    # Stop Node.js processes
    print_color("Stopping Node.js processes...", Colors.YELLOW)
    stop_processes(processes['node'], "Node.js")
    print()
    
    # Stop npm processes
    print_color("Stopping npm processes...", Colors.YELLOW)
    stop_processes(processes['npm'], "npm")
    print()
    
    # Stop Python processes
    print_color("Stopping Python processes...", Colors.YELLOW)
    stop_processes(processes['python'], "Python")
    print()
    
    print_color("=" * 50, Colors.CYAN)
    print_color("All services stopped!", Colors.GREEN)
    print_color("=" * 50, Colors.CYAN)
    print()
    print_color("Run 'python start-services.py' to restart", Colors.CYAN)
    print()

if __name__ == "__main__":
    try:
        # Check if psutil is installed
        import psutil
    except ImportError:
        print_color("ERROR: psutil module not found", Colors.RED)
        print_color("Install with: pip install psutil", Colors.CYAN)
        sys.exit(1)
    
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_color("Shutdown cancelled by user", Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        print_error(f"Shutdown failed: {e}")
        sys.exit(1)
