# 保存为OBJ格式文件

import numpy as np
 
 
def stl_get(stl_path):
    points=[]
    f = open(stl_path)
    lines = f.readlines()
    prefix='vertex'
    num=3
    for line in lines:
        #print (line)
 
        if line.startswith(prefix):
            values = line.strip().split()
            #print(values[1:4])
            if num%3==0:
                points.append([values[1],values[2],values[3]])
                num=0
            num+=1
        #print(type(line))
    points=np.array(points,dtype='float64')
 
    #points=points*1000#3d打印用
 
    
    f.close()
    #print(points.shape)
    #np.save("/home/pxing/codes/point_improve/feature_get/point_get/index_mm_level.npy", t)
    return points
 
# 点云数据
 
stl_path='1.stl'
points = stl_get(stl_path)
 
 
# 计算点云的法向量
def compute_normals(points):
    normals = []
    for i, p0 in enumerate(points):
        v1 = points[(i+1) % len(points)] - p0
        v2 = points[(i+2) % len(points)] - p0
        normals.append(np.cross(v1, v2))
    return normals
 
normals = compute_normals(points)
 
# 将点云和法向量保存为OBJ格式文件
with open('output.obj', 'w') as f:
    for i, p in enumerate(points):
        f.write(f'v {p[0]} {p[1]} {p[2]}\n')
        n = normals[i]
        f.write(f'vn {n[0]} {n[1]} {n[2]}\n')
 
    # 将点云转换为面信息
    for i in range(0, len(points), 3):
        f.write(f'f {i+1}//{i+1} {i+2}//{i+2} {i+3}//{i+3}\n')