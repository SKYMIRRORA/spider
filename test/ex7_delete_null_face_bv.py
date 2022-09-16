import os
import shutil

path = '/media/huangrq/BIGDISK/DownLoad/torchproject/spider/8-24'

for bv in os.listdir(path):
    # print(bv)
    bv_path = os.path.join(path,bv)
    if len(os.listdir(bv_path)) == 0:
        shutil.rmtree(bv_path)
        # print(bv_path)


