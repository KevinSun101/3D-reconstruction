import vtk
# source->filter(MC算法)->mapper->actor->render->renderwindow->interactor

def VolumeRendering(path, intensityList):
    # 读取Dicom数据，对应source
    v16 = vtk.vtkDICOMImageReader()
    v16.SetDirectoryName(path)

    # 创建marchingCubes，利用封装好的MC算法抽取等值面，对应filter
    marchingCubes = vtk.vtkMarchingCubes()
    marchingCubes.SetInputConnection(v16.GetOutputPort())

    skin, vessel, bone = intensityList

    marchingCubes.SetValue(0, bone)     # skeleton,
    marchingCubes.SetValue(1, vessel)     # 0, -10;
    marchingCubes.SetValue(2, skin)     # 0, -10;

    # marchingCubes.GenerateValues(2, 100, 500)


    # 创建stripper，剔除旧的或废除的数据单元，提高绘制速度，对应filter
    stripper = vtk.vtkStripper()
    stripper.SetInputConnection(marchingCubes.GetOutputPort())

    # 创建mapper
    mapper = vtk.vtkPolyDataMapper()
    # mapper.SetInputConnection(marchingCubes.GetOutputPort())
    mapper.SetInputConnection(stripper.GetOutputPort())

    # 创建actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # actor.GetProperty().SetColor(1, 1, 1) # 角色的颜色设置
    actor.GetProperty().SetDiffuseColor(1, 1, 1) # 1, .49, .25,
    actor.GetProperty().SetSpecular(.5)# .1. 设置高光照明系数
    actor.GetProperty().SetSpecularPower(100) #100,设置高光能量


    # 创建render, renderWindow, renderWindowInteractor
    render = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    interactor = vtk.vtkRenderWindowInteractor()
    render.AddActor(actor)  # 将角色添加到舞台中
    renderWindow.AddRenderer(render)
    interactor.SetRenderWindow(renderWindow)

    # 定义舞台上的相机，对应render
    camera = vtk.vtkCamera()
    camera.SetViewUp(0, 0, -1)
    camera.SetPosition(0, 1, 0)
    camera.SetFocalPoint(0, 0, 0)
    camera.ComputeViewPlaneNormal()
    camera.Dolly(1.5)


    style = vtk.vtkInteractorStyleTrackballCamera() # 设置style
    interactor.SetInteractorStyle(style)

    render.SetActiveCamera(camera) # 将相机添加到舞台renderer
    render.ResetCamera() # 将相机的焦点移动至中央

    # # 写入到stl文件
    # stlWriter=vtk.vtkSTLWriter() # 导出到stl
    # stlWriter.SetFileName('output/1.stl')
    # stlWriter.SetInputConnection(skinExtractor.GetOutputPort())
    # stlWriter.Write()

    interactor.Initialize()
    interactor.Start()



def main():
    # path="../../Data/20230906_lung-data"
    path="../../Data/20240409_leg-data"
    # path='../../Data/part1'
    # path = '../../Data/part2'

    intensityList=[100, 200,300] # -1000,-100,100

    VolumeRendering(path, intensityList)

if __name__ == '__main__':
    main()


