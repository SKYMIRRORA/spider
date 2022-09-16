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

def get_bvs(url_index):
    # print(len(urls),'len(urls)') 65
    url = urls[url_index]
    # url = "https://www.bilibili.com/v/life/daily?tag=530003"
    all_bvs = json_load("jsons/all_bvs.json")
    bvs = []
    app = FaceAnalysis(providers=['CUDAExecutionProvider', 'CPUExecutionProvider'], allowed_modules=['detection'])
    app.prepare(ctx_id=0, det_size=(640, 640))
    firefox_option = webdriver.FirefoxOptions()
    firefox_option.add_argument('--headless')
    driver = webdriver.Firefox(options=firefox_option)
    driver.get(url)
    sleep(1)
    try:
        driver.find_elements(By.CLASS_NAME,"play-selector__item")[1].click()

        for i in tqdm(range(400),desc='Scrolling down'):
            js="var q=document.getElementById('container').scrollTop=%d*document.body.scrollHeight"%(i+1)
            driver.execute_script(js) 
            sleep(1)

        soup=BeautifulSoup(driver.page_source,"html.parser")
        driver.close()
        
    except Exception as e:
        
        print(e)
    finally:
        divs = soup.find_all("div",class_="video-card")
        print("length of divs:",len(divs))
        with requests.Session() as ses:
            for div in tqdm(divs,desc="Processing"):
                a = div.find("a",class_ = "cover-picture")
                bv = a["href"].split("/video/")[1]
                if bv in all_bvs or bv in bvs:
                    continue

                #检测封面是否存在人脸    
                cover_url = "http:" + a.find("img",class_ = "cover-picture__image")["v-lazy"]
                cover_req = ses.get(cover_url)
                try:
                    cover = cv.imdecode(np.frombuffer(cover_req.content, np.uint8), cv.IMREAD_COLOR)
                    faces = app.get(cover)
                except:
                    print("Error:failed to read " + bv)
                    continue
                if len(faces):                
                    bvs.append(bv)

        with open("jsons/%drencenthot.json"%(len(bvs)), "w") as f:
            json.dump(bvs,f,indent = 2,cls=NumpyArrayEncoder)

        all_bvs = json_load("jsons/all_bvs.json")
        all_bvs.extend(bvs)
        with open("jsons/all_bvs.json", "w") as f:
            json.dump(all_bvs,f,indent = 2,cls=NumpyArrayEncoder)
        print("finished")


if __name__ == "__main__":
    # 从B站上爬取视频bv号并保存W
    url_index = 1
    get_bvs(url_index)
   

