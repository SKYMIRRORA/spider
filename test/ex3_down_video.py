from time import sleep, time
from matplotlib.font_manager import json_dump, json_load
import requests
from bs4 import BeautifulSoup
import os

import cv2 as cv
import json
import numpy as np
from tqdm import tqdm
from insightface.app import FaceAnalysis
from selenium import webdriver

from multiprocessing.dummy import Pool as ThreadPool


from random import choice
from selenium.webdriver.common.by import By
import math
from skimage import transform
import onnxruntime

class NumpyArrayEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumpyArrayEncoder, self).default(obj)


def get_got_bvs(filename):
    real_urls = json_load(filename)
    got_bvs = []
    for real_url in real_urls:
        got_bvs.append(real_url['bv'])
    return got_bvs

class Down():
    imgs_dir = ""
    pbar = None

    def __init__(self,real_urls,imgs_dir) -> None:
        self.imgs_dir = imgs_dir
        self.real_urls = real_urls
        self.pbar = tqdm(total=len(real_urls))
        # self.downed_bvs = json_load("jsons/downed_bvs.json")
        self.bvs = []
        self.error_bvs = []
        self.downed_bvs = json_load("jsons/downed_bvs.json")


    def down_imgs(self,real_url):
        # print(11111111111111111)
        print(real_url['bv'])
        error_bvs = json_load("jsons/error_bvs.json")
        downed_bvs_tmp = json_load("jsons/downed_bvs_tmp.json")
     
        if (real_url["bv"] in self.downed_bvs) or (real_url['bv'] in error_bvs) or (real_url['bv'] in downed_bvs_tmp):
            return
        try:
            user_agent = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0"
            headers = {
                "User-Agent" : user_agent,
            }
            self.bvs.append(real_url["bv"])
            rq = requests.get(real_url["url"], headers=headers, stream=True) 
            frame_nub = 0
            with open('{}{}.mp4'.format(self.imgs_dir,real_url["bv"]), "wb") as mp4:
                for chunk in rq.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        # print(chunk)
                        mp4.write(chunk)  
                    # frame_nub += 1  
        except Exception as e:
            print(e)
            print("=======Error:failed to open video======== " +real_url["bv"])
            self.error_bvs.append(real_url["bv"])                      
        finally:
            self.pbar.update(1)

    def run(self):
        try:
            pool = ThreadPool()
            #线程池没满，就创建新线程执行任务，线程池满了则等待
            pool.map(self.down_imgs,self.real_urls)
        except:
            print("Error: unable to start thread")
        finally:
            # self.downed_bvs.extend(self.bvs)
            with open("jsons/downed_bvs_tmp.json", "w") as df:
                json.dump(self.bvs,df,indent = 2,cls=NumpyArrayEncoder)
            error_bvs = json_load("jsons/error_bvs.json")
            # print(111111111111)
            error_bvs.extend(self.error_bvs)
            with open("jsons/error_bvs.json", "w") as ef:
                json.dump(error_bvs,ef,indent = 2,cls=NumpyArrayEncoder)
            pool.close()
            pool.join()
            print("Finished!")

if __name__ == "__main__":
    #23426
    # #多线程下载图片
    import argparse
    parser = argparse.ArgumentParser(description='do ijb test')
    parser.add_argument('--day', default='8-31', help='day.')
    args = parser.parse_args()

    real_urls = json_load("jsons/got_urls.json")
    imgs_dir = "/media/huangrq/BIGDISK/reptile_faces2/video/{}/".format(args.day)
    print(imgs_dir)
    down = Down(real_urls,imgs_dir)
    down.run()






