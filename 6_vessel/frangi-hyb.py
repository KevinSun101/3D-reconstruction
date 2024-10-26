# 这个是把所有popi数据提取肺部和血管mask (3+1（验证case4），popi原始的那个6个数据只用了前三个（这三个是有10个points）)
# 这个是
import os, sys, time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import SimpleITK as sitk
import numpy as np
import json

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from skimage.filters import frangi
import cv2

# root ="../../Data/20230906_lung-data" # get_program_parameters()
root = "../../Data/20240409_leg-data" # get_program_parameters()

def Getvessel(case='1', T='00', offset = 1024):
    path=root
    print(path)
    vol = sitk.ReadImage(path)  #原始resample体数据
    vol = sitk.GetArrayFromImage(vol).astype(np.int16) + offset


    #利用 frangi 增强血管
    vol0 = frangi(vol, sigmas=range(1, 3, 1), alpha=0.5, beta=0.5, gamma=3, black_ridges=False, mode='constant', cval=0)
    cv2.normalize(vol0, vol0, 0, 1, cv2.NORM_MINMAX)
    thresh = np.percentile(sorted(vol0[vol0 > 0]), 86)
    vessel = (vol0 - thresh) * (vol0 > thresh) / (1 - thresh)
    vessel[vessel > 0] = 1
    vessel[vessel <= 0] = 0
    print('血管的 max min', vessel.max(), vessel.min())

    img1 = sitk.GetImageFromArray(vessel) # blood_new.mha
    vol2 = vol * vessel
    img2 = sitk.GetImageFromArray(vol2) # blood_region.mha


    return img1, img2

def GetAllVesselMask():
    for i in range(1, 5):
        for j in range(0,10):
            path1 = os.path.join(root, "Case{0}Pack".format(i), "VesselMask", "C{0}T{1}0_r_vessel_mask.mha".format(i, j))
            path2 = os.path.join(root, "Case{0}Pack".format(i), "Vessel", "C{0}T{1}0_r_vessel.mha".format(i, j))
            print(path1)
            print(path2)
            vol1, vol2 = Getvessel(case=str(i), T="{}0".format(j)) # ----------------------------------------------
            sitk.WriteImage(vol1, path1), sitk.WriteImage(vol2, path2)
            # del vol1, vol2


def GetTime(startTime, endTime):
    return round(endTime - startTime, 6)

def main():
    startTime = time.time()
    # GetAllpopiLungMask()
    # vol1, vol10 = Getvessel(case='1', T="00", dataset='popi')
    GetAllVesselMask()
    endTime = time.time()
    Cost_Time = GetTime(startTime,endTime)
    print("Time2: ",Cost_Time)

if __name__ == "__main__":
    main()

