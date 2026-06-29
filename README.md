# Thermal Image Converter

Converts DJI drone thermal JPEG images (R-JPEG) into single-band GeoTIFF files where each pixel holds the temperature value in degrees Celsius.

## Table of Contents
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Options](#options)
- [Example](#example)
- [License](#license)

## Requirements
- Python 3.11+
- [DJI Thermal SDK](https://www.dji.com/global/downloads/softwares/dji-thermal-sdk) (not included)
- `exiftool` — included as `exiftool.exe` for Windows; on macOS/Linux install via your package manager

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/your-username/thermal-image-converter.git
   cd thermal-image-converter
   ```

2. **Create a virtual environment and install dependencies with `uv`:**
   ```sh
   uv venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

   Or with plain `pip`:
   ```sh
   pip install dji-thermal-sdk rasterio tqdm
   ```

3. **Download the [DJI Thermal SDK](https://www.dji.com/global/downloads/softwares/dji-thermal-sdk) and place its contents in a `dji_thermal_sdk/` folder:**
   ```
   dji_thermal_sdk/
   ├── dataset/
   ├── doc/
   ├── sample/
   ├── tsdk-core/
   ├── utility/
   ├── History.txt
   ├── License.txt
   └── Readme.md
   ```

4. **Make sure `exiftool` is available:**
   - Windows: `exiftool.exe` is included in the repository root.
   - macOS: `brew install exiftool`
   - Linux: `apt install libimage-exiftool-perl`

## Usage

1. Place thermal JPEG images (files ending in `_T.JPG`) in the `input_images/` folder.
2. Run the script:
   ```sh
   python dji_thermal_converter.py [OPTIONS]
   ```
3. Converted GeoTIFF files appear in `output_images/`.

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `--distance` | `5.0` | Distance to subject (m) |
| `--humidity` | `70.0` | Relative humidity (%) |
| `--emissivity` | `1.0` | Surface emissivity (0–1) |
| `--reflected-temperature` | `23.0` | Reflected/apparent temperature (°C) |
| `--ambient-temperature` | `25.0` | Ambient temperature (°C) |

> **Note:** The DJI Thermal SDK uses *reflected temperature* (`--reflected-temperature`) for atmosphere correction via the `reflection` field in `dirp_measurement_params_t`. `--ambient-temperature` is accepted on the CLI for logging/reference; the SDK does not expose a separate ambient-temperature field.

## Example

```sh
# Use default parameters
python dji_thermal_converter.py

# Custom measurement conditions
python dji_thermal_converter.py \
  --distance 10 \
  --humidity 60 \
  --emissivity 0.95 \
  --reflected-temperature 22.0 \
  --ambient-temperature 25.0
```

Input:
```
input_images/
├── image1_T.JPG
├── image2_T.JPG
└── image3_T.JPG
```

Output:
```
output_images/
├── image1.tif
├── image2.tif
└── image3.tif
```

## License
GNU General Public License v3.0 — see [LICENSE](LICENSE).
