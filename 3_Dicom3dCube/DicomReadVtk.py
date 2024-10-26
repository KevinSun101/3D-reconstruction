"""
1. read DICOM files via VTK `vtkDICOMImageReader` class
2. convert vtk 3D array to numpy 3D array
"""
from vtk.util import numpy_support
import numpy as np
import vtk


def main():
    dicom_dir = "/media/kevin/DATA2/Skw/DATA/协和项目三维重建/data/dicom文件" # get_program_parameters()

    reader = vtk.vtkDICOMImageReader()
    reader.SetDirectoryName(dicom_dir)
    reader.Update()

    # Load dimensions using `GetDataExtent`
    _extent = reader.GetDataExtent()
    ConstPixelDims = [
        _extent[1] - _extent[0] + 1,
        _extent[3] - _extent[2] + 1,
        _extent[5] - _extent[4] + 1,
    ]  # x,y,z
    w = ConstPixelDims[0]  #
    h = ConstPixelDims[1]  #
    num = ConstPixelDims[2]  #

    # Load spacing values
    ConstPixelSpacing = reader.GetPixelSpacing()  # x, y, z

    print(
        f"PixelSpacing[{ConstPixelSpacing[0]}, {ConstPixelSpacing[1]}] SliceThickness[{ConstPixelSpacing[2]}]"
    )

    # Get the 'vtkImageData' object from the reader
    imageData = reader.GetOutput()
    # Get the 'vtkPointData' object from the 'vtkImageData' object
    pointData = imageData.GetPointData()
    # Ensure that only one array exists within the 'vtkPointData' object
    assert pointData.GetNumberOfArrays() == 1
    # Get the `vtkArray` (or whatever derived type) which is needed for the `numpy_support.vtk_to_numpy` function
    arrayData = pointData.GetArray(0)

    # Convert the `vtkArray` to a NumPy array
    ArrayDicom = numpy_support.vtk_to_numpy(arrayData)
    # Reshape the NumPy array to 3D using 'ConstPixelDims' as a 'shape'
    ArrayDicom = ArrayDicom.reshape((num, h, w), order="F")

    print(
        f"ArrayDicom [{ArrayDicom.shape}] [{ArrayDicom.dtype}] [{ArrayDicom.nbytes}] [{np.mean(ArrayDicom)}] "
    )


def get_program_parameters():
    import argparse

    description = "DICOM Directory including `*.dcm` files"
    epilogue = """
    Derived from VTK/Examples/Cxx/Medical1.cxx
    This example reads a volume dataset, extracts an isosurface that
     represents the skin and displays it.
    """
    parser = argparse.ArgumentParser(
        description=description,
        epilog=epilogue,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("dicom_dir", help="patients/series/")
    args = parser.parse_args()
    return args.dicom_dir


if __name__ == "__main__":
    main()