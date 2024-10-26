import cv2 as cv
import SimpleITK as sitk
from vesselness2d import *


# 对于3D Frangi滤波，与2D Frangi不同点在于
# 1、高斯滤波考虑第三个维度
# 2、构造三阶海森矩阵，[[Ixx,Ixy,Ixz],[Ixy,Iyy,Iyz],[Ixz,Iyz,Izz]]
# 3、求解三阶海森矩阵的特征值lambda1，lambda2，lambda3，并按照绝对值的大小排序
# 4、为减小求解时间，对于Ixx+Iyy+Izz<0的情况直接将灰度置为0
# 5、使用三维滤波公式求解体素灰度值
class vesselness3d:
    def __init__(self, image, sigma, spacing):
        super(vesselness3d, self).__init__()
        self.image = image
        self.sigma = sigma
        self.spacing = spacing
        self.size = image.shape

    def gaussian(self, image, sigma):
        siz = sigma * 6
        temp = round(siz / self.spacing[0] / 2)
        # processing x-axis
        x = [i for i in range(-temp, temp + 1)]
        x = np.array(x)
        H = np.exp(-(x ** 2 / (2 * ((sigma / self.spacing[0]) ** 2))))
        H = H / np.sum(H)
        Hx = H.reshape(len(H), 1, 1)
        I = ndimage.filters.convolve(image, Hx, mode='nearest')

        # processing y-axis
        temp = round(siz / self.spacing[1] / 2)
        x = [i for i in range(-temp, temp + 1)]
        x = np.array(x)
        H = np.exp(-(x ** 2 / (2 * ((sigma / self.spacing[1]) ** 2))))
        H = H / np.sum(H[:])
        Hy = H.reshape(1, len(H), 1)
        I = ndimage.filters.convolve(I, Hy, mode='nearest')

        # processing z-axis
        temp = round(siz / self.spacing[2] / 2)
        x = [i for i in range(-temp, temp + 1)]
        x = np.array(x)
        H = np.exp(-(x ** 2 / (2 * ((sigma / self.spacing[2]) ** 2))))
        H = H / np.sum(H[:])
        Hz = H.reshape(1, 1, len(H))
        I = ndimage.filters.convolve(I, Hz, mode='nearest')
        return I

    def gradient2(self, F, option):
        k = self.size[0]
        l = self.size[1]
        h = self.size[2]
        D = np.zeros(F.shape)
        if option == "x":
            D[0, :, :] = F[1, :, :] - F[0, :, :]
            D[k - 1, :, :] = F[k - 1, :, :] - F[k - 2, :, :]
            # take center differences on interior points
            D[1:k - 2, :, :] = (F[2:k - 1, :, :] - F[0:k - 3, :, :]) / 2
        elif option == "y":
            D[:, 0, :] = F[:, 1, :] - F[:, 0, :]
            D[:, l - 1, :] = F[:, l - 1, :] - F[:, l - 2, :]
            D[:, 1:l - 2, :] = (F[:, 2:l - 1, :] - F[:, 0:l - 3, :]) / 2
        elif option == "z":
            D[:, :, 0] = F[:, :, 1] - F[:, :, 0]
            D[:, :, h - 1] = F[:, :, h - 1] - F[:, :, h - 2]
            D[:, :, 1:h - 2] = (F[:, :, 2:h - 1] - F[:, :, 0:h - 3]) / 2
        return D

    def Hessian2d(self, image, sigma):
        image = self.gaussian(image, sigma)
        self.gaus_image = image
        Dz = self.gradient2(image, "z")
        Dzz = self.gradient2(Dz, "z")

        Dy = self.gradient2(image, "y")
        Dyy = self.gradient2(Dy, "y")
        Dyz = self.gradient2(Dy, "z")

        Dx = self.gradient2(image, "x")
        Dxx = self.gradient2(Dx, "x")
        Dxy = self.gradient2(Dx, 'y')
        Dxz = self.gradient2(Dx, "z")
        return Dxx, Dyy, Dzz, Dxy, Dxz, Dyz

    def eigvalOfhessian2d(self, array):
        tmp = np.linalg.eig(array)
        lamda = sorted([(abs(tmp[0][0]), tmp[0][0]), (abs(tmp[0][1]), tmp[0][1]), (abs(tmp[0][2]), tmp[0][2])])
        Lambda1 = lamda[0][1]
        Lambda2 = lamda[1][1]
        Lambda3 = lamda[2][1]
        return Lambda1, Lambda2, Lambda3

    def imageEigenvalues(self, I, sigma):
        self.hxx, self.hyy, self.hzz, self.hxy, self.hxz, self.hyz = self.Hessian2d(I, sigma)
        hxx = self.hxx
        hyy = self.hyy
        hzz = self.hzz
        hxy = self.hxy
        hxz = self.hxz
        hyz = self.hyz

        hxx = hxx.flatten()
        hyy = hyy.flatten()
        hzz = hzz.flatten()
        hxy = hxy.flatten()
        hxz = hxz.flatten()
        hyz = hyz.flatten()

        Lambda1_list = []
        Lambda2_list = []
        Lambda3_list = []
        count = 0
        for i in range(len(hxx)):
            if hxx[i] + hyy[i] + hzz[i] <= 0:
                Lambda1, Lambda2, Lambda3 = 0, 0, 0
            else:
                array = np.array([[hxx[i], hxy[i], hxz[i]], [hxy[i], hyy[i], hyz[i]], [hxz[i], hyz[i], hzz[i]]])
                Lambda1, Lambda2, Lambda3 = self.eigvalOfhessian2d(array)
            if Lambda1 != 0 and Lambda2 != 0 and Lambda3 != 0:
                count += 1

            Lambda1_list.append(Lambda1)
            Lambda2_list.append(Lambda2)
            Lambda3_list.append(Lambda3)

        Lambda1_list = np.array(Lambda1_list)
        Lambda2_list = np.array(Lambda2_list)
        Lambda3_list = np.array(Lambda3_list)
        Lambda1_list[(np.isinf(Lambda1_list))] = 0
        Lambda2_list[(np.isinf(Lambda2_list))] = 0
        Lambda3_list[(np.isinf(Lambda3_list))] = 0

        # Lambda1_list[(np.absolute(Lambda1_list) < 1e-4)] = 0
        Lambda1_list = Lambda1_list.reshape(self.size)
        # Lambda2_list[(np.absolute(Lambda2_list) < 1e-4)] = 0
        Lambda2_list = Lambda2_list.reshape(self.size)
        # Lambda3_list[(np.absolute(Lambda3_list) < 1e-4)] = 0
        Lambda3_list = Lambda3_list.reshape(self.size)
        return Lambda1_list, Lambda2_list, Lambda3_list

    def vesselness3d(self):
        for k in range(len(self.sigma)):
            lambda1, lambda2, lambda3 = self.imageEigenvalues(self.image, self.sigma[k])
            c = self.gaus_image.max() / 2

            item1 = (1 - np.exp(-2 * (lambda2 ** 2) / (lambda3 ** 2)))
            item2 = np.exp(-2 * (lambda1 ** 2) / np.absolute(lambda2 * lambda3))
            item3 = (1 - np.exp(-(lambda1 ** 2 + lambda2 ** 2 + lambda3 ** 2) / (2 * c ** 2)))

            item1[lambda3 == 0] = 0
            item2[lambda3 == 0] = 0

            response = item1 * item2 * item3

            response[np.where(np.isnan(response))] = 0

            if k == 0:
                vesselness = response
            else:
                vesselness = np.maximum(vesselness, response)

        vesselness = (vesselness / (vesselness.max())) * 20000
        vesselness[vesselness > 200] = 200
        return vesselness


if __name__ == "__main__":
    sigma = [0.5, 1, 1.5, 2, 2.5]
    path = "../../Data/part1.nii.gz"
    # path = "../../Data/20230906_lung-data"

    img = sitk.ReadImage(path)
    img_data = sitk.GetArrayFromImage(img)
    space = img.GetSpacing()
    direction = img.GetDirection()
    origin = img.GetOrigin()
    img_data = 200 - img_data
    v = vesselness3d(img_data, sigma, list(space))
    image_data = v.vesselness3d()
    img = sitk.GetImageFromArray(image_data)
    img.SetOrigin(origin)
    img.SetDirection(direction)
    img.SetSpacing(space)
    sitk.WriteImage(img, "Frangi_vessel_001.nii.gz")

