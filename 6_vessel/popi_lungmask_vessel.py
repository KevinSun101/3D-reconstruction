# 这个是把所有popi数据提取肺部和血管mask (3+1（验证case4），popi原始的那个6个数据只用了前三个（这三个是有10个points）)
# 这个是
import os, sys, time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import airlab as al
# import dirlab.dirlabhelper as dlh
# import mymedicallib.utils as mut
# import lungmask.mask as lm
import SimpleITK as sitk
# import torch as th
import numpy as np
import json
# from dirlab.dirlabhelper import Dataloader
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from skimage.filters import frangi
import cv2

# root = 'D:/Data3/POPI'
# root ="../../Data/20230906_lung-data" # get_program_parameters()
root = "../../Data/20240409_leg-data" # get_program_parameters()

def GetVolPath(dataset='popi',resample=True,case='1', T='00'):
    if dataset == 'popi':
        if resample:
            volpath = os.path.join(root, "Case{0}Pack".format(case), "Resample", "C{0}T{1}_r.mha".format(case, T))
    return volpath

# 下面GetVolumeData实际操作是用来生成lungmask的
# def GetVolumeData(dataset='popi',case='1', T='00', offset=0):
#     path = GetVolPath(dataset,case=case, T=T)
#     vol = sitk.ReadImage(path)
#     vol = sitk.GetArrayFromImage(vol).astype(np.int16) + offset
#     print("此时体数据路径，及大小", path, vol.shape)
#     vol = sitk.GetImageFromArray(vol)
#     seg = lm.apply(vol)
#     print("此lung mask大小",  seg.shape)
#     mask = sitk.GetImageFromArray(seg)
#     return mask

# def GetAllpopiLungMask():
#     for i in range(1, 5):
#         # vol6 = Dataloader.GetVolumeData(case=str(i), resample=True, T="50", root=dirlabroot, voltype='sitk',
#         #                                 offset=-1000, dataset='dirlab')
#         vol1 = GetVolumeData(case=str(i),T="00",  dataset='popi')
#         vol2 = GetVolumeData(case=str(i), T="10",  dataset='popi')
#         vol3 = GetVolumeData(case=str(i), T="20",  dataset='popi')
#         vol4 = GetVolumeData(case=str(i), T="30",  dataset='popi')
#         vol5 = GetVolumeData(case=str(i), T="40",  dataset='popi')
#         vol6 = GetVolumeData(case=str(i), T="50", dataset='popi')
#         vol7 = GetVolumeData(case=str(i),  T="60", dataset='popi')
#         vol8 = GetVolumeData(case=str(i), T="70", dataset='popi')
#         vol9 = GetVolumeData(case=str(i),  T="80", dataset='popi')
#         vol10 = GetVolumeData(case=str(i),  T="90", dataset='popi')
#
#         vol1 = sitk.GetArrayFromImage(vol1)
#         vol2 = sitk.GetArrayFromImage(vol2)
#         vol3 = sitk.GetArrayFromImage(vol3)
#         vol4 = sitk.GetArrayFromImage(vol4)
#         vol5 = sitk.GetArrayFromImage(vol5)
#         vol6 = sitk.GetArrayFromImage(vol6)
#         vol7 = sitk.GetArrayFromImage(vol7)
#         vol8 = sitk.GetArrayFromImage(vol8)
#         vol9 = sitk.GetArrayFromImage(vol9)
#         vol10 = sitk.GetArrayFromImage(vol10)
#
#         vol1[vol1 == 2] = 1
#         vol2[vol2 == 2] = 1
#         vol3[vol3 == 2] = 1
#         vol4[vol4 == 2] = 1
#         vol5[vol5 == 2] = 1
#         vol6[vol6 == 2] = 1
#         vol7[vol7 == 2] = 1
#         vol8[vol8 == 2] = 1
#         vol9[vol9 == 2] = 1
#         vol10[vol10 == 2] = 1
#
#         vol1 = sitk.GetImageFromArray(vol1)
#         vol2 = sitk.GetImageFromArray(vol2)
#         vol3 = sitk.GetImageFromArray(vol3)
#         vol4 = sitk.GetImageFromArray(vol4)
#         vol5 = sitk.GetImageFromArray(vol5)
#         vol6 = sitk.GetImageFromArray(vol6)
#         vol7 = sitk.GetImageFromArray(vol7)
#         vol8 = sitk.GetImageFromArray(vol8)
#         vol9 = sitk.GetImageFromArray(vol9)
#         vol10 = sitk.GetImageFromArray(vol10)
#
#         # p = os.path.join(root, "Case{0}Pack".format(i), "LungMask")
#         # if not os.path.exists(p):
#         #     os.makedirs(p)
#
#         path1 = os.path.join(root, "Case{0}Pack".format(i), "LungMask", "C{0}T00_r_lung_mask.mha".format(i))
#         path2 = os.path.join(root, "Case{0}Pack".format(i), "LungMask", "C{0}T10_r_lung_mask.mha".format(i))
#         path3 = os.path.join(root, "Case{0}Pack".format(i), "LungMask", "C{0}T20_r_lung_mask.mha".format(i))
#         path4 = os.path.join(root, "Case{0}Pack".format(i), "LungMask", "C{0}T30_r_lung_mask.mha".format(i))
#         path5 = os.path.join(root, "Case{0}Pack".format(i), "LungMask", "C{0}T40_r_lung_mask.mha".format(i))
#         path6 = os.path.join(root, "Case{0}Pack".format(i), "LungMask", "C{0}T50_r_lung_mask.mha".format(i))
#         path7 = os.path.join(root, "Case{0}Pack".format(i), "LungMask", "C{0}T60_r_lung_mask.mha".format(i))
#         path8 = os.path.join(root, "Case{0}Pack".format(i), "LungMask", "C{0}T70_r_lung_mask.mha".format(i))
#         path9 = os.path.join(root, "Case{0}Pack".format(i), "LungMask", "C{0}T80_r_lung_mask.mha".format(i))
#         path10 = os.path.join(root, "Case{0}Pack".format(i), "LungMask", "C{0}T90_r_lung_mask.mha".format(i))
#
#         sitk.WriteImage(vol1, path1)
#         sitk.WriteImage(vol2, path2)
#         sitk.WriteImage(vol3, path3)
#         sitk.WriteImage(vol4, path4)
#         sitk.WriteImage(vol5, path5)
#         sitk.WriteImage(vol6, path6)
#         sitk.WriteImage(vol7, path7)
#         sitk.WriteImage(vol8, path8)
#         sitk.WriteImage(vol9, path9)
#         sitk.WriteImage(vol10, path10)



# def GetAllDirlabVessel():
#     root = 'E:\\DataSet\\Dirlab4DCT\\vesselmask'
#
#     for i in range(30, 50):
#         c = int((i - 30) / 2) + 1
#         rootdir = 'E:/shikong/chest/DataSet/4DCT/Case{0}Pack/VesselMask'.format(str(c))
#         inpath = os.path.join(root, str(i))
#         vol = mut.readmat(inpath)
#         if not os.path.exists(rootdir):
#             os.makedirs(rootdir)
#         if i % 2 == 0:
#             outpath = os.path.join(rootdir, 'C{0}T00_r_v.mha'.format(str(c)))
#         else:
#             outpath = os.path.join(rootdir, 'C{0}T50_r_v.mha'.format(str(c)))
#         sitk.WriteImage(vol, outpath)


#  提取lung区域

# 好像没用
def Getvessel(case='1', T='00', offset = 1024):

    path=root
    # path1 = os.path.join(root, "Case{0}Pack".format(case), "Resample", "C{0}T{1}_r.mha".format(case, T))
    # path2 = os.path.join(root, "Case{0}Pack".format(case), "LungMask", "C{0}T{1}_r_lung_mask.mha".format(case,T))
    # 提取 lung region
    # print(path)
    vol = sitk.ReadImage(path)  #原始resample体数据
    vol = sitk.GetArrayFromImage(vol).astype(np.int16) + offset

    # vol2 = sitk.ReadImage(path2)  #原始 resample 后lung mask just掩膜
    # vol2 = sitk.GetArrayFromImage(vol2)
    # vol = vol1 * vol2

    #利用 frangi 增强血管
    vol0 = frangi(vol, sigmas=range(1, 3, 1), alpha=0.5, beta=0.5, gamma=3, black_ridges=False, mode='constant', cval=0)

    cv2.normalize(vol0, vol0, 0, 1, cv2.NORM_MINMAX)
    thresh = np.percentile(sorted(vol0[vol0 > 0]), 86)
    vessel = (vol0 - thresh) * (vol0 > thresh) / (1 - thresh)
    vessel[vessel > 0] = 1
    vessel[vessel <= 0] = 0
    print('血管的 max min', vessel.max(), vessel.min())

    img2 = sitk.GetImageFromArray(vessel)
    vol3 = vol1 * vessel
    img3 = sitk.GetImageFromArray(vol3)

    # sitk.WriteImage(img2, "blood_new.mha")
    # sitk.WriteImage(img3, "blood_region.mha")

    return img2, img3

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

        # path1 = os.path.join(root, "Case{0}Pack".format(i), "VesselMask", "C{0}T00_r_vessel_mask.mha".format(i))
        # path10 = os.path.join(root, "Case{0}Pack".format(i), "Vessel", "C{0}T00_r_vessel.mha".format(i))
        #
        # path2 = os.path.join(root, "Case{0}Pack".format(i), "VesselMask", "C{0}T10_r_vessel_mask.mha".format(i))
        # path20 = os.path.join(root, "Case{0}Pack".format(i), "Vessel", "C{0}T10_r_vessel.mha".format(i))
        #
        # path3 = os.path.join(root, "Case{0}Pack".format(i), "VesselMask", "C{0}T20_r_vessel_mask.mha".format(i))
        # path30 = os.path.join(root, "Case{0}Pack".format(i), "Vessel", "C{0}T20_r_vessel.mha".format(i))
        #
        # path4 = os.path.join(root, "Case{0}Pack".format(i), "VesselMask", "C{0}T30_r_vessel_mask.mha".format(i))
        # path40 = os.path.join(root, "Case{0}Pack".format(i), "Vessel", "C{0}T30_r_vessel.mha".format(i))
        #
        # path5 = os.path.join(root, "Case{0}Pack".format(i), "VesselMask", "C{0}T40_r_vessel_mask.mha".format(i))
        # path50 = os.path.join(root, "Case{0}Pack".format(i), "Vessel", "C{0}T40_r_vessel.mha".format(i))
        #
        # path6 = os.path.join(root, "Case{0}Pack".format(i), "VesselMask", "C{0}T50_r_vessel_mask.mha".format(i))
        # path60 = os.path.join(root, "Case{0}Pack".format(i), "Vessel", "C{0}T50_r_vessel.mha".format(i))
        #
        # path7 = os.path.join(root, "Case{0}Pack".format(i), "VesselMask", "C{0}T60_r_vessel_mask.mha".format(i))
        # path70 = os.path.join(root, "Case{0}Pack".format(i), "Vessel", "C{0}T60_r_vessel.mha".format(i))
        #
        # path8 = os.path.join(root, "Case{0}Pack".format(i), "VesselMask", "C{0}T70_r_vessel_mask.mha".format(i))
        # path80 = os.path.join(root, "Case{0}Pack".format(i), "Vessel", "C{0}T70_r_vessel.mha".format(i))
        #
        # path9 = os.path.join(root, "Case{0}Pack".format(i), "VesselMask", "C{0}T80_r_vessel_mask.mha".format(i))
        # path90 = os.path.join(root, "Case{0}Pack".format(i), "Vessel", "C{0}T80_r_vessel.mha".format(i))
        #
        # path100 = os.path.join(root, "Case{0}Pack".format(i), "VesselMask", "C{0}T90_r_vessel_mask.mha".format(i))
        # path1000 = os.path.join(root, "Case{0}Pack".format(i), "Vessel", "C{0}T90_r_vessel.mha".format(i))
        #
        #
        #
        #
        # vol2, vol20 = Getvessel(case=str(i), offset=0, T="10", dataset='dirlab')
        # sitk.WriteImage(vol2, path2), sitk.WriteImage(vol20, path20)
        # del vol2, vol20
        # vol3, vol30 = Getvessel(case=str(i), offset=0, T="20", dataset='dirlab')
        # sitk.WriteImage(vol3, path3), sitk.WriteImage(vol30, path30)
        # del vol3, vol30
        # vol4, vol40 = Getvessel(case=str(i), offset=0, T="30", dataset='dirlab')
        # sitk.WriteImage(vol4, path4), sitk.WriteImage(vol40, path40)
        # del vol4, vol40
        # vol5, vol50 = Getvessel(case=str(i), offset=0, T="40", dataset='dirlab')
        # sitk.WriteImage(vol5, path5), sitk.WriteImage(vol50, path50)
        # del vol5, vol50
        # vol6, vol60 = Getvessel(case=str(i), offset=0, T="50", dataset='dirlab')
        # sitk.WriteImage(vol6, path6), sitk.WriteImage(vol60, path60)
        # del vol6, vol60
        # vol7, vol70 = Getvessel(case=str(i), offset=0, T="60", dataset='dirlab')
        # sitk.WriteImage(vol7, path7), sitk.WriteImage(vol70, path70)
        # del vol7, vol70
        # vol8, vol80 = Getvessel(case=str(i), offset=0, T="70", dataset='dirlab')
        # sitk.WriteImage(vol8, path8), sitk.WriteImage(vol80, path80)
        # del vol8, vol80
        # vol9, vol90 = Getvessel(case=str(i), offset=0, T="80", dataset='dirlab')
        # sitk.WriteImage(vol9, path9), sitk.WriteImage(vol90, path90)
        # del vol9, vol90
        # vol100, vol1000 = Getvessel(case=str(i), offset=0, T="90", dataset='dirlab')
        # sitk.WriteImage(vol100, path100), sitk.WriteImage(vol1000, path1000)
        # del vol100, vol1000
        # # p = os.path.join(dirlabroot, "Case{0}Pack".format(i), "Vessel")
        # # if not os.path.exists(p):
        # #     os.makedirs(p)



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

