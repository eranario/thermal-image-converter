# Thermal Image Converter

Converts DJI drone thermal JPEG images (R-JPEG) into single-band GeoTIFF files where each pixel holds the temperature value in degrees Celsius.

## Table of Contents
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Options](#options)
- [Output Layout](#output-layout)
- [Example](#example)
- [License](#license)

## Requirements
- Python 3.11+
- [DJI Thermal SDK](https://www.dji.com/global/downloads/softwares/dji-thermal-sdk) (not included)
- `exiftool` — handled automatically by `setup.sh` on Linux/WSL; included as `exiftool.exe` for Windows

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/eranario/thermal-image-converter.git
   cd thermal-image-converter
   ```

2. **Run the setup script** (installs exiftool, creates the Python environment, and checks for the DJI SDK):
   ```sh
   bash setup.sh
   ```

3. **Download the [DJI Thermal SDK](https://www.dji.com/global/downloads/softwares/dji-thermal-sdk) and place its contents in a `dji_thermal_sdk/` folder:**
   ```
   dji_thermal_sdk/
   ├── utility/
   │   └── bin/
   │       ├── linux/
   │       │   └── release_x64/
   │       │       └── libdirp.so
   │       └── windows/
   │           └── release_x64/
   │               └── libdirp.dll
   └── ...
   ```

4. **Activate the environment:**
   ```sh
   source .venv/bin/activate
   ```

## Usage

```sh
python dji_thermal_converter.py --input-dir <path> [OPTIONS]
```

Point `--input-dir` at any folder containing DJI thermal images (files ending in `_T.JPG`). Converted TIFFs and RGB symlinks are written into an `output/` subfolder created inside that directory.

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--input-dir` | `input_images` | Path to folder containing `_T.JPG` thermal images |
| `--distance` | `5.0` | Distance to subject (m) |
| `--humidity` | `70.0` | Relative humidity (%) |
| `--emissivity` | `1.0` | Surface emissivity (0–1) |
| `--reflected-temperature` | `23.0` | Reflected/apparent temperature (°C) |
| `--ambient-temperature` | `25.0` | Ambient temperature (°C) |

> **Note:** The DJI Thermal SDK uses *reflected temperature* (`--reflected-temperature`) for atmosphere correction. `--ambient-temperature` is accepted for logging/reference; the SDK does not expose a separate ambient-temperature field.

## Output Layout

```
<input-dir>/
├── DJI_0001_T.JPG          ← source thermal image
├── DJI_0001_V.JPG          ← source RGB image
└── output/
    ├── thermal_conv/
    │   └── DJI_0001_T.tif  ← converted GeoTIFF (float32, °C per pixel)
    └── rgb_symlink/
        └── DJI_0001_V.JPG  ← symlink to paired RGB image
```

## Example

```sh
python dji_thermal_converter.py \
  --input-dir /mnt/data/flight_2024_06_29 \
  --distance 10 \
  --humidity 65 \
  --emissivity 0.95 \
  --reflected-temperature 22.0 \
  --ambient-temperature 25.0
```

## License
GNU General Public License v3.0 — see [LICENSE](LICENSE).
