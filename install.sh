
#!/usr/bin/env bash

set -e

if [ "$EUID" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
fi

if [ -f /etc/arch-release ]; then
    echo "[*] Arch"
    $SUDO pacman -Syu --needed python git cmake gcc make python-pefile

elif [ -f /etc/fedora-release ]; then
    echo "[*] Fedora"
    $SUDO dnf install -y python3 python3-pefile git cmake gcc gcc-c++ make

elif [ -f /etc/debian_version ]; then
    echo "[*] Debian/Ubuntu"
    $SUDO apt update
    $SUDO apt install -y python3 python3-pip python3-pefile git cmake build-essential

elif [ -f /etc/SUSE-brand ] || [ -f /etc/SUSE-release ]; then
    echo "[*] openSUSE"
    $SUDO zypper install -y python3 python3-pefile git cmake gcc gcc-c++ make

elif command -v apk >/dev/null 2>&1; then
    echo "[*] Alpine Linux"
    $SUDO apk add python3 py3-pefile git cmake build-base

else
    echo "[!] Unsupported Linux distro."
    exit 1
fi

echo
echo "[*] Checking Python dependencies..."

python3 -c "import pefile; print('[+] pefile installed successfully')"

echo
echo "[+] Requirements installation completed."
