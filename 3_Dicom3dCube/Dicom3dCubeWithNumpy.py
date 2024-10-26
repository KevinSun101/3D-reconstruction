"""
DICOM files --> 3D numpy array --> vtk array --> vtk 3D visualization
1. read a series of DICOM files by pydicom
2. create a 3D numpy array(NHW) by stacking a series of 2D DICOM image data(HW) and preprocessing(hu, resample,..etc) below
    1. HU
    2. resample
3. convert the 3D numpy to vtk 3D array(vtkImageData)
4. bridge vtk 3D array `vtkImageData` to `vtkAlgorigthmOutput` by `vtkTrivialProducer`, then process with marching cubes algorithm  
5. render vtk 3D array
"""


import numpy as np

import vtk
from vtkmodules.util import numpy_support
from utils import CreateTissue, get_pixels_hu, load_scan, resample


def main():
    # dicom_dir ="../../Data/20230906_lung-data" # get_program_parameters()
    dicom_dir = "../../Data/20240409_leg-data"  # get_program_parameters()

    # Load the DICOM files
    slices = load_scan(dicom_dir)

    # pixel aspects, assuming all slices are the same
    ps = slices[0].PixelSpacing
    ss = slices[0].SliceThickness
    ax_aspect = ps[1] / ps[0]
    sag_aspect = ps[1] / ss
    cor_aspect = ss / ps[0]

    print(
        f"PixelSpacing[{ps}] SliceThickness[{ss}] AxialAspect[{ax_aspect}] SagittalAspect[{sag_aspect}] CoronalAspect[{cor_aspect}]"
    )

    # Convert raw data into Houndsfeld units
    img3d = get_pixels_hu(slices)

    print(f"img3d [{img3d.shape}] [{img3d.dtype}] [{img3d.nbytes}] [{np.mean(img3d)}] ")

    # Resample
    img3d_after_resamp, spacing = resample(img3d, slices)

    print(
        f"img3d_after_resamp [{img3d_after_resamp.shape}] [{img3d_after_resamp.dtype}] [{img3d_after_resamp.nbytes}] [{np.mean(img3d_after_resamp)}] "
    )

    # Prepare 3D visualization
    print(f"3D visualization...")

    # Convert numpy array to vtk array
    img3d_64f = img3d_after_resamp.astype(np.float64)
    num, h, w = img3d_64f.shape
    print(f"img3d_64f [{img3d_64f.shape}] [{np.max(img3d_64f[1])}]")

    imageData = vtk.vtkImageData()
    depthArray = numpy_support.numpy_to_vtk(
        num_array=img3d_64f.ravel(), deep=True, array_type=vtk.VTK_FLOAT
    )
    imageData.SetDimensions((w, h, num))  # x,y,z coordination system
    imageData.SetSpacing([1, 1, 1])
    # imageData.SetSpacing([ps[0], ps[1], ss])
    imageData.SetOrigin([0, 0, 0])
    imageData.GetPointData().SetScalars(depthArray)

    image_producer: vtk.vtkAlgorithm = vtk.vtkTrivialProducer()  # data provider
    image_producer.SetOutput(imageData)

    # Rendering

    # Setup render
    renderer = vtk.vtkRenderer()
    renderer.AddActor(CreateTissue(image_producer, -900, -400, "lung"))
    renderer.AddActor(CreateTissue(image_producer, 0, 120, "blood"))
    renderer.AddActor(CreateTissue(image_producer, 100, 2000, "skeleton"))
    renderer.SetBackground(1.0, 1.0, 1.0)
    renderer.ResetCamera()

    # Setup render window
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(renderer)
    renWin.SetSize(800, 800)
    renWin.Render()

    # Setup render window interaction
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    # Setup coordinate axes helper
    axesActor = vtk.vtkAxesActor()
    widget = vtk.vtkOrientationMarkerWidget()
    rgba = [0] * 4
    colors = vtk.vtkNamedColors()
    colors.GetColor("Carrot", rgba)
    widget.SetOutlineColor(rgba[0], rgba[1], rgba[2])
    widget.SetOrientationMarker(axesActor)
    widget.SetInteractor(iren)
    widget.SetViewport(0.0, 0.0, 0.4, 0.4)
    widget.SetEnabled(1)
    widget.InteractiveOn()

    iren.Initialize()
    iren.Start()


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