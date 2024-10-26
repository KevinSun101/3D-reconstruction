"""
1. read DICOM files via pydicom
2. convert vtk 3D array to numpy 3D array
"""
import time
import numpy as np
import vtk
from utils import get_pixels_hu, load_scan


def main():
    start = time.time()

    # dicom_dir ="../../Data/20230906_lung-data" # get_program_parameters()
    dicom_dir = "../../Data/20240409_leg-data"  # get_program_parameters()

    # Load the DICOM files
    slices = load_scan(dicom_dir)

    # pixel aspects, assuming all slices are the same
    ps = slices[0].PixelSpacing
    ss = slices[9].SliceThickness
    ax_aspect = ps[1] / ps[0]
    sag_aspect = ps[1] / ss
    cor_aspect = ss / ps[0]

    # NOTE: `SliceThickness` from DICOM tag may be different with `slice_thickness` here
    try:
        slice_thickness = np.abs(
            slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2]
        )
    except:
        slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)

    print(f"PixelSpacing[{ps}] SliceThickness[{ss}] [{slice_thickness}]")

    # Convert raw data into Houndsfeld units
    img3d = get_pixels_hu(slices)

    print(f"img3d [{img3d.shape}] [{img3d.dtype}] [{img3d.nbytes}] [{np.mean(img3d)}] ")

    stop = time.time()
    hr = (stop - start) / 3600
    print('training time : {} hrs'.format(hr))


# def get_program_parameters():
#     import argparse
#
#     description = "DICOM Directory including `*.dcm` files"
#     epilogue = """
#     Derived from VTK/Examples/Cxx/Medical1.cxx
#     This example reads a volume dataset, extracts an isosurface that
#      represents the skin and displays it.
#     """
#     parser = argparse.ArgumentParser(
#         description=description,
#         epilog=epilogue,
#         formatter_class=argparse.RawDescriptionHelpFormatter,
#     )
#     parser.add_argument("dicom_dir", help="patients/series/")
#     args = parser.parse_args()
#     return args.dicom_dir


if __name__ == "__main__":
    main()