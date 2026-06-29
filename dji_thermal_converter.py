from dji_thermal_sdk.dji_sdk import *
from dji_thermal_sdk.utility import getJPEGHandle
import numpy as np
import ctypes as CT
from ctypes import *
import rasterio
import argparse
import os
import subprocess
import logging
from tqdm import tqdm
import warnings
warnings.filterwarnings("ignore")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def parse_args():
    parser = argparse.ArgumentParser(
        description='Convert DJI thermal JPG images to GeoTIFF with Celsius values.'
    )
    parser.add_argument('--distance', type=float, default=5.0,
                        help='Distance to subject (m). Default: 5.0')
    parser.add_argument('--humidity', type=float, default=70.0,
                        help='Relative humidity (%%). Default: 70.0')
    parser.add_argument('--emissivity', type=float, default=1.0,
                        help='Surface emissivity (0–1). Default: 1.0')
    parser.add_argument('--ambient-temperature', type=float, default=25.0,
                        help='Ambient temperature (°C). Default: 25.0')
    parser.add_argument('--reflected-temperature', type=float, default=23.0,
                        help='Reflected temperature (°C). Default: 23.0')
    return parser.parse_args()


def main():
    """
    Converts all thermal JPG images in the "input_images" folder to TIFF format
    with Celsius temperature values. Resulting images are located in the
    "output_images" folder.

    Requirements:
        - "dji_thermal_sdk" folder in the directory
        - "exiftool" / "exiftool.exe" on PATH or in the directory
        - Input images should be in "input_images" folder
        - Output images will be saved in "output_images" folder

    Steps:
        1. List all thermal JPG images in the input folder.
        2. Convert each image to TIFF format with temperature values in a single
           layer using the provided measurement parameters.
        3. Move TIFF files to the output folder.
        4. Delete temporary files.
    """
    args = parse_args()

    logging.info(
        f"Measurement params — distance: {args.distance} m, "
        f"humidity: {args.humidity} %, emissivity: {args.emissivity}, "
        f"reflected temp: {args.reflected_temperature} °C, "
        f"ambient temp: {args.ambient_temperature} °C"
    )

    input_folder = 'input_images'
    output_folder = 'output_images'

    os.makedirs(output_folder, exist_ok=True)

    input_files = [f for f in os.listdir(input_folder) if f.endswith('_T.JPG')]

    if not input_files:
        logging.warning('No thermal images found in the input directory.')
        return

    logging.info('Converting thermal JPG files to thermal TIFF files')
    for file in tqdm(input_files):
        try:
            jpg_to_thermal_tif(file, input_folder, args)
        except Exception as e:
            logging.error(f"Error converting {file}: {e}")

    tif_files = [f for f in os.listdir(input_folder) if f.endswith('.tif')]
    no_meta_tif_files = [f for f in os.listdir(input_folder) if f.endswith('original')]

    logging.info('Moving TIFF files')
    for file in tif_files:
        os.rename(os.path.join(input_folder, file),
                  os.path.join(output_folder, file))

    logging.info('Deleting temporary files')
    for file in no_meta_tif_files:
        os.remove(os.path.join(input_folder, file))

    logging.info('Done!')


def jpg_to_thermal_tif(filename: str, input_folder: str, args) -> None:
    """
    Converts an RJPEG thermal image to TIF format with a single layer containing
    temperature values in Celsius, applying custom measurement parameters.

    Args:
        filename:     Name of the file inside input_folder.
        input_folder: Path to the folder containing the image files.
        args:         Parsed argparse namespace with measurement parameters.
    """
    dll_path = "dji_thermal_sdk/utility/bin/windows/release_x64/libdirp.dll"
    dji_init(dll_path)

    filepath = os.path.join(input_folder, filename)
    out_file = os.path.splitext(filename)[0] + '.tif'
    out_filepath = os.path.join(input_folder, out_file)

    # Create the DIRP handle for this image
    ret = getJPEGHandle(filepath)
    if ret != 0:
        raise ValueError(f"Failed to open {filepath} (error {ret}). "
                         "Is the DJI Thermal SDK installed?")

    # Apply custom measurement parameters
    params = dirp_measurement_params_t()
    params.distance = CT.c_float(args.distance)
    params.humidity = CT.c_float(args.humidity)
    params.emissivity = CT.c_float(args.emissivity)
    # The SDK field is "reflection" — this is the reflected/apparent temperature
    # used for atmosphere correction (analogous to --reflected-temperature).
    # --ambient-temperature is accepted on the CLI for reference; the DJI SDK
    # does not expose a separate ambient-temperature field.
    params.reflection = CT.c_float(args.reflected_temperature)

    ret = dirp_set_measurement_params(DIRP_HANDLE, CT.byref(params))
    if ret != DIRP_SUCCESS:
        raise ValueError(f"dirp_set_measurement_params failed (error {ret})")

    # Get image dimensions
    resolution = dirp_resolution_t()
    dirp_get_rjpeg_resolution(DIRP_HANDLE, CT.byref(resolution))
    img_h, img_w = resolution.height, resolution.width

    # Measure temperature — each pixel is a float32 value in °C
    size = img_h * img_w * CT.sizeof(CT.c_float)
    raw_buffer = CT.create_string_buffer(size)
    ret = dirp_measure_ex(DIRP_HANDLE, CT.byref(raw_buffer), size)
    if ret != DIRP_SUCCESS:
        raise ValueError(f"dirp_measure_ex failed (error {ret})")

    img = np.frombuffer(raw_buffer.raw, dtype=np.float32).reshape(img_h, img_w)

    with rasterio.open(
        out_filepath, 'w',
        driver='GTiff',
        height=img_h,
        width=img_w,
        count=1,
        dtype=rasterio.float32,
    ) as dst:
        dst.write(img, 1)

    # Copy EXIF/XMP metadata from the source JPG to the output TIFF
    subprocess.run(
        ['exiftool', '-tagsfromfile', filepath, out_filepath],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )


if __name__ == '__main__':
    main()
