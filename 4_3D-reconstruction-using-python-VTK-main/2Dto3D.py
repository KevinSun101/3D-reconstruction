#!/usr/bin/env python

import vtk


def main():

    '''
    A class holding colors and their names. 
    '''
    colors = vtk.vtkNamedColors()

    # dicom_dir ="../../Data/20230906_lung-data"
    dicom_dir = "../../Data/20240409_leg-data"


    iso_value = 100

    if iso_value is None and dicom_dir is not None:
        print('An ISO value is needed.')
        return ()

    volume = vtk.vtkImageData()
    if dicom_dir is None:
        pass

    else:
        reader = vtk.vtkDICOMImageReader()
        reader.SetDirectoryName(dicom_dir)
        reader.Update()
        volume.DeepCopy(reader.GetOutput())

    surface = vtk.vtkMarchingCubes()
    surface.SetInputData(volume)
    surface.ComputeNormalsOn()

    # SetValue --------------------------------------------------------------------------------------------------
    surface.SetValue(0, -900)
    surface.SetValue(1, -100)
    surface.SetValue(2, 100)

    renderer = vtk.vtkRenderer()
    renderer.SetBackground(colors.GetColor3d('DarkSlateGray'))

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetWindowName('MarchingCubes')

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(surface.GetOutputPort())
    mapper.ScalarVisibilityOff()

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(colors.GetColor3d('MistyRose'))

    renderer.AddActor(actor)

    render_window.Render()
    interactor.Start()




if __name__ == '__main__':
    main()
