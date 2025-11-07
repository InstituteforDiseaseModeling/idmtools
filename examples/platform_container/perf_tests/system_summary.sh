#!/usr/bin/env bash
# ==============================
# System Summary Information
# ==============================

echo "========================================"
echo " 🧩 System Summary ($(hostname))"
echo "========================================"

# CPU Info
echo -e "\n .  CPU Information"
lscpu | grep -E '^Architecture|^Model name|^CPU\(s\)|Thread|Core|Socket|Vendor ID|Hypervisor'

# Memory Info
echo -e "\n . Memory Information"
free -h | awk '/Mem:/ {printf "Total: %s | Used: %s | Free: %s | Available: %s\n", $2, $3, $4, $7}'

# Disk Info
echo -e "\n . Disk Usage (top-level filesystems)"
df -h --output=source,fstype,size,used,avail,pcent,target | grep -vE 'tmpfs|udev'

# Virtualization Info
echo -e "\n . Virtualization"
if command -v systemd-detect-virt &> /dev/null; then
    virt_type=$(systemd-detect-virt)
    echo "Virtualization type: $virt_type"
else
    echo "Virtualization type: (tool not found)"
fi

# OS and Kernel
echo -e "\n . OS and Kernel"
echo "OS: $(grep PRETTY_NAME /etc/os-release | cut -d= -f2 | tr -d '\"')"
echo "Kernel: $(uname -r)"

# CPU Load
echo -e "\n . Current CPU Load (1/5/15 min)"
uptime | awk -F'load average:' '{print $2}'

echo -e "\n Summary complete."
echo "========================================"
