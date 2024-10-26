import vtk
import numpy as np


def CreateLut():
    colors = vtk.vtkNamedColors()

    colorLut = vtk.vtkLookupTable()
    colorLut.SetNumberOfColors(17)
    colorLut.SetTableRange(0, 16)
    colorLut.Build()

    colorLut.SetTableValue(0, 0, 0, 0, 0)
    colorLut.SetTableValue(1, colors.GetColor4d("salmon"))  # blood
    colorLut.SetTableValue(2, colors.GetColor4d("beige"))  # brain
    colorLut.SetTableValue(3, colors.GetColor4d("orange"))  # duodenum
    colorLut.SetTableValue(4, colors.GetColor4d("misty_rose"))  # eye_retina
    colorLut.SetTableValue(5, colors.GetColor4d("white"))  # eye_white
    colorLut.SetTableValue(6, colors.GetColor4d("tomato"))  # heart
    colorLut.SetTableValue(7, colors.GetColor4d("raspberry"))  # ileum
    colorLut.SetTableValue(8, colors.GetColor4d("banana"))  # kidney
    colorLut.SetTableValue(9, colors.GetColor4d("peru"))  # l_intestine
    colorLut.SetTableValue(10, colors.GetColor4d("pink"))  # liver
    colorLut.SetTableValue(11, colors.GetColor4d("powder_blue"))  # lung
    colorLut.SetTableValue(12, colors.GetColor4d("carrot"))  # nerve
    colorLut.SetTableValue(13, colors.GetColor4d("wheat"))  # skeleton
    colorLut.SetTableValue(14, colors.GetColor4d("violet"))  # spleen
    colorLut.SetTableValue(15, colors.GetColor4d("plum"))  # stomach

    return colorLut


def CreateTissueMap():
    tissueMap = dict()
    tissueMap["blood"] = 1
    tissueMap["brain"] = 2
    tissueMap["duodenum"] = 3
    tissueMap["eyeRetina"] = 4
    tissueMap["eyeWhite"] = 5
    tissueMap["heart"] = 6
    tissueMap["ileum"] = 7
    tissueMap["kidney"] = 8
    tissueMap["intestine"] = 9
    tissueMap["liver"] = 10
    tissueMap["lung"] = 11
    tissueMap["nerve"] = 12
    tissueMap["skeleton"] = 13
    tissueMap["spleen"] = 14
    tissueMap["stomach"] = 15

    return tissueMap


tissueMap = CreateTissueMap()
colorLut = CreateLut()


# Generate a 3D mesh with marching cubes algorithm
def CreateTissue(image_producer: vtk.vtkAlgorithm, ThrIn, ThrOut, color="skeleton", isoValue=127.5):
    selectTissue = vtk.vtkImageThreshold()
    selectTissue.ThresholdBetween(ThrIn, ThrOut)
    selectTissue.ReplaceInOn()
    selectTissue.SetInValue(255)
    selectTissue.ReplaceOutOn()
    selectTissue.SetOutValue(0)
    # selectTissue.SetInputData(imageData)
    selectTissue.SetInputConnection(image_producer.GetOutputPort())
    # selectTissue.Update()

    gaussianRadius = 5
    gaussianStandardDeviation = 1 # 2.0
    gaussian = vtk.vtkImageGaussianSmooth()
    gaussian.SetStandardDeviations(
        gaussianStandardDeviation, gaussianStandardDeviation, gaussianStandardDeviation
    )
    gaussian.SetRadiusFactors(gaussianRadius, gaussianRadius, gaussianRadius)
    gaussian.SetInputConnection(selectTissue.GetOutputPort())

    # isoValue = 127.5
    mcubes = vtk.vtkMarchingCubes()
    mcubes.SetInputConnection(gaussian.GetOutputPort())
    mcubes.ComputeScalarsOff()
    mcubes.ComputeGradientsOff()
    mcubes.ComputeNormalsOff()
    mcubes.SetValue(0, isoValue)

    smoothingIterations = 10 # 5
    passBand = 0.001
    featureAngle = 60.0
    smoother = vtk.vtkWindowedSincPolyDataFilter()
    smoother.SetInputConnection(mcubes.GetOutputPort())
    smoother.SetNumberOfIterations(smoothingIterations)
    smoother.BoundarySmoothingOff()
    smoother.FeatureEdgeSmoothingOff()
    smoother.SetFeatureAngle(featureAngle)
    smoother.SetPassBand(passBand)
    smoother.NonManifoldSmoothingOn()
    smoother.NormalizeCoordinatesOn()
    smoother.Update()

    normals = vtk.vtkPolyDataNormals()
    normals.SetInputConnection(smoother.GetOutputPort())
    normals.SetFeatureAngle(featureAngle)

    stripper = vtk.vtkStripper()
    stripper.SetInputConnection(normals.GetOutputPort())

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(stripper.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(colorLut.GetTableValue(tissueMap[color])[:3])
    actor.GetProperty().SetSpecular(0.5)
    actor.GetProperty().SetSpecularPower(10)

    return actor


import pathlib
import pydicom
from typing import List


def load_scan(dicom_dir: str) -> List[pydicom.FileDataset]:
    slices = [pydicom.dcmread(f,force=True) for f in pathlib.Path(dicom_dir).glob("*.dcm")]
    print(f"file count: {len(slices)}")

    # skip files with no SliceLocation or InstanceNumber(eg scout views)
    slices = list(filter(lambda s: hasattr(s, "SliceLocation"), slices))

    print(f"file count with SliceLocation: {len(slices)}")
    slices = sorted(slices, key=lambda s: s.SliceLocation)

    return slices


def get_pixels_hu(slices: List[pydicom.FileDataset]) -> np.ndarray:
    # s.pixel_array: 2D array with HW format
    # img3d: 3D array with NHW format
    img3d = np.stack([s.pixel_array for s in slices])

    # Convert to int16 (from sometimes int16),
    # should be possible as values should always be low enough (<32k)
    img3d = img3d.astype(np.int16)

    # Set outside-of-scan pixels to 1
    # The intercept is usually -1024, so air is approximately 0
    # img3d[img3d == -1000] = 0
    img3d[img3d == -2000] = 0

    # Convert to Hounsfield units (HU)

    # Operate on whole array
    intercept = slices[0].RescaleIntercept
    slope = slices[0].RescaleSlope

    if slope != 1:
        img3d = slope * img3d.astype(np.float64)
        img3d = img3d.astype(np.int16)

    img3d += np.int16(intercept)

    # # Operate on individual array
    # for n in range(len(slices)):
    #     intercept = slices[n].RescaleIntercept
    #     slope = slices[n].RescaleSlope

    #     if slope != 1:
    #         img3d[n] = slope * img3d[n].astype(np.float64)
    #         img3d[n] = img3d[n].astype(np.int16)

    #     img3d[n] += np.int16(intercept)

    return np.array(img3d, dtype=np.int16)


def get_pixels(scans: List[pydicom.FileDataset]) -> np.ndarray:
    # s.pixel_array: 2D array with HW format
    # img3d: 3D array with NHW format
    img3d = np.stack([s.pixel_array for s in scans])

    return img3d


def plot_stack_sample(stack, rows=6, cols=6, start_with=10, show_every=3):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(rows, cols, figsize=[12, 12])
    for i in range(rows * cols):
        ind = start_with + i * show_every
        ax[int(i / rows), int(i % rows)].set_title("slice %d" % ind)
        ax[int(i / rows), int(i % rows)].imshow(stack[ind], cmap="gray")
        ax[int(i / rows), int(i % rows)].axis("off")
    plt.show()


def resample(image, scan, new_spacing=[1, 1, 1]):
    import scipy.ndimage

    # Determine current pixel spacing
    spacing = np.array(
        [
            float(scan[0].SliceThickness),
            scan[0].PixelSpacing[0],
            scan[0].PixelSpacing[1],
        ]
    )

    resize_factor = spacing / new_spacing
    new_real_shape = image.shape * resize_factor
    new_shape = np.round(new_real_shape)
    real_resize_factor = new_shape / image.shape
    new_spacing = spacing / real_resize_factor

    image = scipy.ndimage.interpolation.zoom(image, real_resize_factor)

    return image, new_spacing