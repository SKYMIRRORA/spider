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
from utils import urls,get_angle,download_video,play_video,img_pre_process,\
    face_align_landmark,get_got_bvs,NumpyArrayEncoder


def get_real_urls(bvs): #可以通过一个B站视频的解析API获取视频真实地址
    try:
        #一个ip只能申请108次
        parser_url = "https://api.injahow.cn/bparse/"
        with requests.Session() as s:
            # ip = "151.181.91.10:80"
            # proxies = {"http":ip,"https":ip}
            # s.proxies.update(proxies)
            real_urls = []
            got_bvs = get_got_bvs('jsons/got_urls.json')
            downed_bvs = json_load('jsons/downed_bvs.json')
            noface_bvs = json_load('jsons/noface_bvs.json')
            for bv in tqdm(bvs):
                if (bv in downed_bvs) or (bv in got_bvs) or (bv in noface_bvs):
                    # print('downed bvs')
                    continue
                payload = {"bv":bv,"format":"mp4"}
                try:
                    page = s.get(url=parser_url,params=payload).json()          
                except:
                    tqdm.write("failed to parse")
                    break
                else:
                    if page["code"] == 0:
                        real_url = {"bv":bv,"url":page["url"]}
                        real_urls.append(real_url)
                    elif page["code"] == 1:
                        tqdm.write("ip is limited")
                        break
                    elif page["code"] == -412:
                        tqdm.write('请求被拦截')
                        break
                    else:
                        bvs.remove(bv)
                        continue
    except Exception as e:
        tqdm.write("Error:",e)
    finally:  
        got_urls = json_load("jsons/got_urls.json")
        got_urls.extend(real_urls)
        
        with open("jsons/got_urls.json", "w") as f:
            json.dump(got_urls,f,indent = 2,cls=NumpyArrayEncoder)

        with open("jsons/all_bvs.json", "w") as f:
            json.dump(bvs,f,indent = 2,cls=NumpyArrayEncoder)
        return real_urls

if __name__ == "__main__":
    # 解析bv获取视频链接并保存
    bvs = json_load("jsons/all_bvs.json")
    get_real_urls(bvs)
 
