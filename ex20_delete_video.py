# get file size in python
import os
import shutil

path = "/media/huangrq/BIGDISK/reptile_faces2/video/9-7/"
for video in os.listdir(path):
    video_path = os.path.join(path,video)

    file_stats = os.stat(video_path)
    if file_stats.st_size < 2 * 1024 * 1024: #删除小于2m的文件
        # shutil.rmtree(video_path)
        os.remove(video_path)

# print(file_stats)
# print(f'File Size in Bytes is {file_stats.st_size}')
# print(f'File Size in MegaBytes is {file_stats.st_size / (1024 * 1024)}')