"""
抽取轮廓(等值面)的操作对象是标量数据。
其思想是：将数据集中标量值等于某一指定恒量值的部分提取出来。对于3D的数据集而言，产生的是一个等值面；对于2D的数据集而言，产生的是一个等值线。
其典型的应用有气象图中的等温线、地形图中的等高线。

对于医学数据而言，不同的标量值代表的是人体的不同部分，因而可以分别提取出人的皮肤或骨头。

抽取轮廓的功能是由一个过滤器实现的，如vtkContourFilter、vtkMarchingCubes。vtkContourFilter可以接受任意数据集类型作为输入，因而具有一般性。

使用vtkContourFilter 时，除了需要设置输入数据集外，还需要指定一个或多个用于抽取的标量值。可用如下两种方法进行设置。
使用方法SetValue()逐个设置抽取值。该方法有个两个参数：第一个参数是抽取值的索引号，表示第几个抽取值。索引号从0开始计数；第二个参数就是指定的抽取值。
使用方法GenerateValues()自动产生一系列抽取值。该方法有三个参数：第一个参数是抽取值的个数，后面两个参数是抽取值的取值范围。
"""


"""
The following reader is used to read a series of 2D slices(images) that compose the volume.
The slice dimensions are set, and the pixel spacing.The data Endianness must also be specified.
The reader uses the FilePrefix in combination with the slice number to construct filenames using the format FilePrefix. 
In this case the FilePrefix is the root name of the file.
"""

import vtk
from vtkmodules.vtkIOGeometry import vtkSTLWriter


def VolumeRendering(path, intensityList):
    # source—filter——mapper——actor——render——renderWindow——interactor

    v16 = vtk.vtkDICOMImageReader()
    v16.SetDirectoryName(path)

    """
    An isosurface, or contour value of 500 is known to correspond to the skin of the patient.
    Once generated, a vtkPolyDataNormals filter is used to create normals for smooth surface shading during rendering.
    """

    # 创建filter
    skinExtractor = vtk.vtkContourFilter() # ContourFilter
    skinExtractor.SetInputConnection(v16.GetOutputPort())

    skin, vessel, bone = intensityList
    skinExtractor.SetValue(0, bone)
    skinExtractor.SetValue(1, vessel)
    skinExtractor.SetValue(2, skin)

    # skinExtractor.GenerateValues(2,100,500)  # skeleton,85以下有杂点


    # 创建normal
    skinNormals = vtk.vtkPolyDataNormals()
    skinNormals.SetInputConnection(skinExtractor.GetOutputPort())
    skinNormals.SetFeatureAngle(60.0)

    # 创建mapper
    skinMapper = vtk.vtkPolyDataMapper()
    skinMapper.SetInputConnection(skinNormals.GetOutputPort())
    skinMapper.ScalarVisibilityOff()

    """
    设置颜色RGB颜色系统就是由三个颜色分量：红色(R)、绿色(G)和蓝色(B)的组合表示，在VTK里这三个分量的取值都是从0到1，(0, 0, 0)表示黑色，(1, 1, 1)表示白色。
    vtkProperty::SetColor(r,g, b)采用的就是RGB颜色系统设置颜色属性值。
    """

    # 创建Actor
    skin = vtk.vtkActor()
    skin.SetMapper(skinMapper)

    skin.GetProperty().SetColor(1, 1, 1)
    skin.GetProperty().SetDiffuseColor(1, .49, .25) # 1,49,25
    skin.GetProperty().SetSpecular(.5)
    skin.GetProperty().SetSpecularPower(20)
    skin.GetProperty().SetRepresentationToSurface()


    # 创建filter，构建图形的方框
    outlineData = vtk.vtkOutlineFilter() # OutlineFilter
    outlineData.SetInputConnection(v16.GetOutputPort())

    # 创建mapper
    mapOutline = vtk.vtkPolyDataMapper() # Mapper
    mapOutline.SetInputConnection(outlineData.GetOutputPort())

    # 创建actor
    outline = vtk.vtkActor() # Actor
    outline.SetMapper(mapOutline)
    outline.GetProperty().SetColor(0, 0, 0) # 0, 0, 0

    # 创建render, renderWindow, renderWindowInteractor
    render = vtk.vtkRenderer()  # 渲染器
    renderWindow = vtk.vtkRenderWindow()  # 渲染窗口,创建窗口
    interactor = vtk.vtkRenderWindowInteractor()  # 窗口交互

    render.AddActor(outline)
    render.AddActor(skin)
    renderWindow.AddRenderer(render)  # 渲染窗口
    interactor.SetRenderWindow(renderWindow)

    # 创建camera
    camera = vtk.vtkCamera()
    camera.SetViewUp(0, 0, -1)
    camera.SetPosition(0, 1, 0)
    camera.SetFocalPoint(0, 0, 0)
    camera.ComputeViewPlaneNormal()
    camera.Dolly(1.5) # The Dolly() method moves the camera towards the Focal Point, thereby enlarging the image.
    # aCamera.Roll(180)
    # aCamera.Yaw(60)

    # 创建style
    style = vtk.vtkInteractorStyleTrackballCamera()
    interactor.SetInteractorStyle(style)

    render.SetActiveCamera(camera)
    render.ResetCamera()
    render.SetBackground(250, 250, 250)
    # renWin.SetSize(640, 480) # 用于设置窗口的大小，以像素为单位。
    renderWindow.SetSize(1500, 1200)
    render.ResetCameraClippingRange()

    # # 写入到stl文件
    # fileSTL='output/leg_SR_2.stl'
    # stlWriter=vtk.vtkSTLWriter() # 导出到stl
    # stlWriter.SetFileName(fileSTL)
    # stlWriter.SetInputConnection(skinNormals.GetOutputPort())
    # stlWriter.Write()



    # 初始化和启动
    interactor.Initialize()
    interactor.Start()


def main():
    # path=r"E:\Research\MR-Navigation\Data\20231031_lung-data"
    # path="../../Data/20240409_leg-data"
    # path='../../Data/part1'
    # path = '../../Data/part2'
    path = r"E:\Research\MR-Navigation\Data\20240903_qiu_xiu_fang\qiu_xiu_fang\_tangyueshan__0330052740"

    intensityList = [0, 100, 1000]  # -1000,-100,100

    VolumeRendering(path, intensityList)


if __name__ == '__main__':
    main()