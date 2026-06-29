#!/usr/bin/env bash
set -euo pipefail

echo "=== thermal-image-converter setup ==="

# 1. exiftool
echo ""
echo "[1/3] Installing exiftool..."
if command -v exiftool &>/dev/null; then
    echo "  exiftool already installed: $(exiftool -ver)"
else
    sudo apt-get update -qq
    sudo apt-get install -y libimage-exiftool-perl
    echo "  exiftool installed: $(exiftool -ver)"
fi

# 2. uv
echo ""
echo "[2/3] Setting up Python environment with uv..."
if ! command -v uv &>/dev/null; then
    echo "  uv not found, installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # add uv to PATH for the rest of this script
    export PATH="$HOME/.local/bin:$PATH"
fi
echo "  uv: $(uv --version)"

uv venv --python 3.11 .venv
source .venv/bin/activate
uv pip install -e .
echo "  Python deps installed."

# 3. DJI Thermal SDK check
echo ""
echo "[3/3] Checking for DJI Thermal SDK..."
SDK_LIB="dji_thermal_sdk/utility/bin/linux/release_x64/libdirp.so"
if [ -f "$SDK_LIB" ]; then
    echo "  DJI Thermal SDK found at $SDK_LIB"
else
    echo ""
    echo "  !! DJI Thermal SDK not found at $SDK_LIB"
    echo "  Download it from: https://www.dji.com/global/downloads/softwares/dji-thermal-sdk"
    echo "  Then extract and place it so the repo root contains:"
    echo ""
    echo "    dji_thermal_sdk/"
    echo "    ├── utility/"
    echo "    │   └── bin/"
    echo "    │       └── linux/"
    echo "    │           └── release_x64/"
    echo "    │               └── libdirp.so"
    echo "    └── ..."
    echo ""
fi

echo "=== Setup complete ==="
echo ""
echo "Activate your environment with:"
echo "  source .venv/bin/activate"
echo ""
echo "Then run the converter with:"
echo "  python dji_thermal_converter.py --help"
