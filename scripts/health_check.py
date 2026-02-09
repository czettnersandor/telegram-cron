#!/usr/bin/env python3
"""
Example script: System health check
Monitors CPU, memory, and reports if thresholds are exceeded
"""

import psutil
import socket

# Configuration
CPU_THRESHOLD = 80.0  # percent
MEMORY_THRESHOLD = 85.0  # percent

def check_system_health():
    """Check system health metrics"""
    issues = []
    
    # Get hostname
    hostname = socket.gethostname()
    
    # Check CPU usage
    cpu_percent = psutil.cpu_percent(interval=1)
    if cpu_percent > CPU_THRESHOLD:
        issues.append(f"CPU: {cpu_percent}% (threshold: {CPU_THRESHOLD}%)")
    
    # Check memory usage
    memory = psutil.virtual_memory()
    if memory.percent > MEMORY_THRESHOLD:
        issues.append(f"Memory: {memory.percent}% (threshold: {MEMORY_THRESHOLD}%)")
    
    # Check disk I/O (optional - can be slow)
    # disk_io = psutil.disk_io_counters()
    
    # Report if issues found
    if issues:
        print(f"🔴 System Health Alert - {hostname}")
        print("")
        for issue in issues:
            print(f"  • {issue}")
        print("")
        print(f"CPU: {cpu_percent}%")
        print(f"Memory: {memory.percent}% ({memory.used / (1024**3):.1f}GB / {memory.total / (1024**3):.1f}GB)")
        print(f"Swap: {psutil.swap_memory().percent}%")
    else:
        # Everything is fine, no update needed
        print("NOUPDATE")

if __name__ == "__main__":
    check_system_health()
