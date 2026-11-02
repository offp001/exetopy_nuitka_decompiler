# ExeToPy (Nuitka)

- Convert .exe files compiled with Nuitka to readable python files

## Requirements

- Python 3.10 or newer
- Python `pefile` module
- Git
- CMake
- GCC / G++ build tools
- GNU Make

### Arch Linux

```bash
sudo pacman -S --needed python git cmake gcc make python-pefile
```

### Fedora

```bash
sudo dnf install -y python3 python3-pefile git cmake gcc gcc-c++ make
```

### Debian / Ubuntu

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-pefile git cmake build-essential
```

### openSUSE

```bash
sudo zypper install python3 python3-pefile git cmake gcc gcc-c++ make
```

### Verify Installation

```bash
python3 --version
python3 -c "import pefile; print('dependencies OK')"
git --version
cmake --version
```

## Requirements

- Python 3 or Python

## Usage

Run the following command from the folder:

```bash
python3 exetopy.py your_program_name.exe
```

## Note

This project uses hexpyrion for making the file .pyc files, hexpyrion gets error while converting .pyc files to python files, thats why i created this repo.

<p align="center">
  <sub>by offp001</sub>
</p>