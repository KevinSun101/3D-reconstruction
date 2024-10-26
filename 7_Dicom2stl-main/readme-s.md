To extract the type "bone" from a zip of dicom images to an output file "bone.stl":
```shell
dicom2stl -t bone -o ./Output/bone.stl ../../Data/20240409_leg-data
```

```shell
dicom2stl -t skin --ct -o ./Output/skin1.stl ../../Data/20240409_leg-data
```

缩小到256个体积，太小了，精度不够