TypeError: Cannot handle this data type: (1, 1, 3), ＜f4

猜测是imageio包的问题，将原本2.31.1版本的imageio卸载，重新装2.9.0版本的imageio就解决了。