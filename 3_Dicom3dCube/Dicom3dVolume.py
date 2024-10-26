"""
DICOM files --> vtk array --> vtk 3D visualization
1. read a series of DICOM files by vtkDICOMImageReader(which will do HU)
2. process vtk 3D array with volume 
3. render vtk 3D array
"""

import vtkmodules.all as vtk


def main():

    # dicom_dir = r"E:\Research\MR-Navigation\Data\20231031_lung-data"
    dicom_dir = r"E:\Research\MR-Navigation\Data\20240409_leg-data" # get_program_parameters()
    # dicom_dir = r"E:\Research\MR-Navigation\Data\qiu_xiu_fang\qiu_xiu_fang\_tangyueshan__0330052740"

    reader = vtk.vtkDICOMImageReader()
    reader.SetDirectoryName(dicom_dir)
    reader.Update()

    # The volume will be displayed by ray-cast alpha compositing.
    # A ray-cast mapper is needed to do the ray-casting.
    volume_mapper = vtk.vtkFixedPointVolumeRayCastMapper()
    volume_mapper.SetInputConnection(reader.GetOutputPort())

    '''
    The color transfer function maps voxel intensities to colors.
    It is modality-specific, and often anatomy-specific as well.
    The goal is to one color for flesh (between 500 and 1000) and another color for bone (1150 and over).
    '''
    #  ----------------------------------------------------------------------------------------------------------------
    volume_color = vtk.vtkColorTransferFunction()
    volume_color.AddRGBPoint(-1000, 0.0, 0.0, 0.0)
    volume_color.AddRGBPoint(-100, 128.0 / 255.0, 128.0 / 255.0, 100.0 / 255.0)
    # volume_color.AddRGBPoint(1000, 240.0 / 255.0, 184.0 / 255.0, 160.0 / 255.0)
    volume_color.AddRGBPoint(50, 1.0, 0.5, 0.6)  # Ivory

    # The opacity transfer function is used to control the opacity of different tissue types. -----------------------
    volume_scalar_opacity = vtk.vtkPiecewiseFunction()
    volume_scalar_opacity.AddPoint(-1000, 0.00)
    volume_scalar_opacity.AddPoint(-100, 0.15)
    # volume_scalar_opacity.AddPoint(1000, 0.15)
    volume_scalar_opacity.AddPoint(50, 0.25)

    '''
    The gradient opacity function is used to decrease the opacity in the 'flat' regions of the volume 
    while maintaining the opacity at the boundaries between tissue types.  The gradient is measured as the amount 
    by which the intensity changes over unit distance. For most medical data, the unit distance is 1mm.
    '''
    #  ----------------------------------------------------------------------------------------------------------------
    volume_gradient_opacity = vtk.vtkPiecewiseFunction()
    volume_gradient_opacity.AddPoint(0, 0.0)
    volume_gradient_opacity.AddPoint(90, 0.5)
    volume_gradient_opacity.AddPoint(100, 1.0)

    # The VolumeProperty attaches the color and opacity functions to the
    # volume, and sets other volume properties.  The interpolation should
    # be set to linear to do a high-quality rendering.  The ShadeOn option
    # turns on directional lighting, which will usually enhance the
    # appearance of the volume and make it look more '3D'.  However,
    # the quality of the shading depends on how accurately the gradient
    # of the volume can be calculated, and for noisy data the gradient
    # estimation will be very poor.  The impact of the shading can be
    # decreased by increasing the Ambient coefficient while decreasing
    # the Diffuse and Specular coefficient.  To increase the impact
    # of shading, decrease the Ambient and increase the Diffuse and Specular.
    volume_property = vtk.vtkVolumeProperty()
    volume_property.SetColor(volume_color)
    volume_property.SetScalarOpacity(volume_scalar_opacity)
    volume_property.SetGradientOpacity(volume_gradient_opacity)
    volume_property.SetInterpolationTypeToLinear()
    volume_property.ShadeOn()
    volume_property.SetAmbient(0.9)
    volume_property.SetDiffuse(0.9)
    volume_property.SetSpecular(0.9)

    # The vtkVolume is a vtkProp3D (like a vtkActor) and controls the position
    # and orientation of the volume in world coordinates.
    volume = vtk.vtkVolume()
    volume.SetMapper(volume_mapper)
    volume.SetProperty(volume_property)

    # Setup render
    renderer = vtk.vtkRenderer()
    renderer.AddViewProp(volume)
    renderer.SetBackground(1.0, 1.0, 1.0)
    renderer.ResetCamera()

    # Set up an initial view of the volume.  The focal point will be the
    # center of the volume, and the camera position will be 400mm to the
    # patient's left (which is our right).
    camera = renderer.GetActiveCamera()
    c = volume.GetCenter()
    # camera.SetViewUp(0, 0, -1)
    # camera.SetPosition(c[0], c[1] - 400, c[2])
    # camera.SetFocalPoint(c[0], c[1], c[2])
    camera.Azimuth(0.0)
    camera.Elevation(80.0)

    # Setup render window
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(renderer)
    renWin.SetSize(640, 480)

    renWin.Render()

    # Setup render window interactor
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    iren.Initialize()
    iren.Start()


# def get_program_parameters():
#     import argparse
#
#     description = "DICOM Directory including `*.dcm` files"
#     epilogue = """
#     This example reads a series of DICOM files, and render 3d volume.
#     """
#     parser = argparse.ArgumentParser(
#         description=description,
#         epilog=epilogue,
#         formatter_class=argparse.RawDescriptionHelpFormatter,
#     )
#     parser.add_argument(
#         "dicom_dir", help="a DICOM files directory, like: patients/series/"
#     )
#     args = parser.parse_args()
#     return args.dicom_dir


if __name__ == "__main__":
    main()