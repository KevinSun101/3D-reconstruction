import os
from scipy import ndimage
import SimpleITK as sitk

from PIL import Image
import cv2
import matplotlib.pyplot as plt
from vesselness2d import *

img_dir = 'images/test.tif' #路径写自己的

#reading image
image = Image.open(img_dir).convert("RGB")
image = np.array(image)
plt.figure(figsize=(10,10))
plt.imshow(image, cmap='gray')

#convert forgeground to background and vice-versa
image = 255-image

image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
thr = np.percentile(image[(image > 0)], 1)*0.9
image[(image <= thr)] = thr
image = image - np.min(image)
image = image / np.max(image)

sigma=[0.5,1, 1.5, 2, 2.5]
spacing = [1, 1]
tau = 2

output = vesselness2d(image, sigma, spacing, tau)
output = output.vesselness2d()

plt.figure(figsize=(10,10))
plt.imshow(output, cmap='gray')
