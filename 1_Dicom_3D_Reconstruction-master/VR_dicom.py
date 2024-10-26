import vtk
# from vtk.util.misc import vtkGetDataRoot

"""
The volume will be displayed by ray-cast alpha compositing. A ray-cast mapper is needed to do the ray-casting, 
and a compositing function is needed to do the compositing along the ray.
"""

def VolumeRendering(path, intensityList):

    # 读取数据
    v16 = vtk.vtkDICOMImageReader()
    v16.SetDirectoryName(path)

    # 创建mapper
    volumeMapper = vtk.vtkGPUVolumeRayCastMapper()
    volumeMapper.SetInputConnection(v16.GetOutputPort())
    volumeMapper.SetBlendModeToComposite()

    """
    The color transfer function maps voxel intensities to colors. The goal is to one color for flesh 
    (between 500 and 1000) and another color for bone (1150 and over).
    """
    skin, vessel, bone= intensityList
    volumeColor = vtk.vtkColorTransferFunction()
    volumeColor.AddRGBPoint(skin, 0, 0, 0) #1000
    volumeColor.AddRGBPoint(vessel, 0.2, .3, .4) #
    volumeColor.AddRGBPoint(bone, 1, 1, 1)

    ''' 
    The opacity transfer function is used to control the opacity of different tissue types. 
    '''
    volumeScalarOpacity = vtk.vtkPiecewiseFunction()
    volumeScalarOpacity.AddPoint(skin,    0.00)
    volumeScalarOpacity.AddPoint(vessel,  0.05)
    volumeScalarOpacity.AddPoint(bone, 0.15)

    """
    The gradient opacity function is used to decrease the opacity in the "flat" regions of the volume 
    while maintaining the opacity at the boundaries between tissue types.  
    """
    volumeGradientOpacity = vtk.vtkPiecewiseFunction()
    volumeGradientOpacity.AddPoint(0,   0.0)
    volumeGradientOpacity.AddPoint(90,  0.5)
    volumeGradientOpacity.AddPoint(100, 1.0)


    # 创建property
    volumeProperty = vtk.vtkVolumeProperty()
    volumeProperty.SetColor(volumeColor)
    volumeProperty.SetScalarOpacity(volumeScalarOpacity)
    volumeProperty.SetGradientOpacity(volumeGradientOpacity)
    volumeProperty.SetInterpolationTypeToLinear()

    """
    The ShadeOn option turns on directional lighting, which will usually enhance the appearance of the volume 
    and make it look more "3D". However, the quality of the shading depends on how accurately the gradient of 
    the volume can be calculated, and for noisy data the gradient estimation will be very poor.  
    The impact of the shading can be decreased by increasing the Ambient coefficient while decreasing the Diffuse and Specular coefficient. 
    """
    volumeProperty.ShadeOn()
    volumeProperty.SetAmbient(0.9)
    volumeProperty.SetDiffuse(0.5) # 0.9
    volumeProperty.SetSpecular(0.5) # 0.9

    # 创建volume (like a vtkActor), and controls the position and orientation of the volume in world coordinates.
    volume = vtk.vtkVolume()
    volume.SetMapper(volumeMapper)
    volume.SetProperty(volumeProperty)

    # 创建render, renderWindow, renderWindowInteractor
    render = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    interactor = vtk.vtkRenderWindowInteractor()  # the interactor enables mouse- and keyboard-based interaction with the scene.
    render.AddViewProp(volume)  # add the volume to the renderer
    renderWindow.AddRenderer(render)
    interactor.SetRenderWindow(renderWindow)



    # 创建camera, Method1
    camera = vtk.vtkCamera()
    camera.SetViewUp(0, 0, -1)
    camera.SetPosition(0, 1, 0)
    camera.SetFocalPoint(0, 0, 0)
    camera.ComputeViewPlaneNormal()
    render.SetActiveCamera(camera) # 将相机添加到舞台renderer

    camera.Dolly(1.5)
    style = vtk.vtkInteractorStyleTrackballCamera() # 设置style
    interactor.SetInteractorStyle(style)
    render.ResetCamera()  # 将相机的焦点移动至中央



    # 创建camera，Method2，比Method1差劲多了
    # """
    # Set up an initial view of the volume.  The focal point will be the center of the volume, and the camera position
    # will be 400mm to the patient's left (which is our right).
    # """
    # camera = render.GetActiveCamera()
    # c = volume.GetCenter()
    # camera.SetFocalPoint(c[0], c[1], c[2])
    # camera.SetPosition(c[0] + 400, c[1], c[2])
    # camera.SetViewUp(0, 0, -1)
    # ----------------------------------------------------------------------------------------------------玩一玩

    # # 写入到stl文件
    # stlWriter=vtk.vtkSTLWriter() # 导出到stl
    # stlWriter.SetFileName('output/leg_V1.stl')
    # stlWriter.SetInputConnection(volumeMapper.GetOutputPort())
    # stlWriter.Write()



    renderWindow.SetSize(640, 480)
    interactor.Initialize() # Interact with the data.
    interactor.Start()


def main():
    # path=r"E:\Research\MR-Navigation\Data\20231031_lung-data"
    # path = r"E:\Research\MR-Navigation\Data\20240409_leg-data"
    # path='../../Data/part1'
    # path = '../../Data/part2'
    path = r"E:\Research\MR-Navigation\Data\20240409_leg-data"

    intensityList = [-1000, -100, 100]  # -1000,-100,100

    VolumeRendering(path, intensityList)


if __name__ == '__main__':
    main()









"""
没用到的代码
# The following reader is used to read a series of 2D slices (images) that compose the volume. 
# The slice dimensions are set, and the pixel spacing. The data Endianness must also be specified. 
# The reader uses the FilePrefix in combination with the slice number to construct filenames using the format FilePrefix.
# In this case the FilePrefix is the root name of the file: quarter.

# v16 = vtk.vtkVolume16Reader()
# v16.SetDataDimensions(64, 64)
# v16.SetImageRange(1, 93)
# v16.SetDataByteOrderToLittleEndian()
# v16.SetFilePrefix("/media/kevin/DATA2/Skw/DATA/协和项目三维重建/data/dicom文件")
# v16.SetDataSpacing(3.2, 3.2, 1.5)
"""