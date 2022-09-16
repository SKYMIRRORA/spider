from importlib.resources import path
import os
import shutil

path1 = '/media/huangrq/BIGDISK/dataset/zhangwj5/video/9-10'
path2 = "/media/huangrq/BIGDISK/dataset/zhaohr/video/9-10"
for bv in os.listdir(path1):
    bv_path = os.path.join(path1,bv)
    try:
       shutil.move(bv_path,"video/9-10")
    except:
        print("device is busy")
for bv in os.listdir(path2):
    bv_path = os.path.join(path2,bv)
    try:
       shutil.move(bv_path,"video/9-10")
    except:
        print("device is busy")








