"""
DICOM files --> vtk array --> vtk 3D visualization
1. read a series of DICOM files by vtkDICOMImageReader(which will do HU and don't resample)
2. process vtk 3D array with marching cubes algorithm
3. render vtk 3D array
"""
import vtk
from utils import CreateTissue


def main():
    # dicom_dir ="../../Data/20230906_lung-data" # get_program_parameters()
    dicom_dir = "../../Data/20240409_leg-data" # get_program_parameters()


    reader = vtk.vtkDICOMImageReader()
    reader.SetDirectoryName(dicom_dir)
    reader.Update()

    # Setup render --------------------------------------------------------------------------------------------------
    renderer = vtk.vtkRenderer()
    renderer.AddActor(CreateTissue(reader, -900, -400, "lung"))
    renderer.AddActor(CreateTissue(reader, 0, 120, "blood"))
    renderer.AddActor(CreateTissue(reader, 100, 2000, "skeleton"))




    renderer.SetBackground(1.0, 1.0, 1.0)
    renderer.ResetCamera()

    # Setup render window
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(renderer)
    renWin.SetSize(800, 800)
    renWin.Render()

    # Setup render window interactor
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