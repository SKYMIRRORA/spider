import cv2
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

class inf_img():
    def __init__(self,video_path,bv_nubs,save_img_path) -> None:
        self.pbar = tqdm(total=len(bv_nubs))
        self.app = FaceAnalysis(providers=['CUDAExecutionProvider', 'CPUExecutionProvider'], allowed_modules=['detection'])
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        self.onnx_model = "FaceQnet.onnx"
        onnxruntime.set_default_logger_severity(3)
        self.ort_session = onnxruntime.InferenceSession(self.onnx_model, providers=['CUDAExecutionProvider','CPUExecutionProvider'])
        self.ort_session.set_providers(['CUDAExecutionProvider'], [ {'device_id': 0}])
        self.output_names = [self.ort_session.get_outputs()[0].name]
        self.input_name = self.ort_session.get_inputs()[0].name
        self.bv_nubs = bv_nubs
        self.save_img_path = save_img_path
        self.video_path = video_path

    def inference(self,bv_nub):
        # source_path = '{}.mp4'.format(self.bv_nubs)
        bv_dir = os.path.join(self.video_path,bv_nub)
        img_dir = os.path.join(self.save_img_path,bv_nub.split('.')[0])
        # print(bv_dir,img_dir)
        if not os.path.exists(img_dir):
            os.mkdir(img_dir)
        # print(bv_dir)
        try:
            capture = cv2.VideoCapture(bv_dir)
        except Exception as e:
            print(e)
            print("=======Error:failed to open video======== " + bv_dir)
        else:
            idx = 0
            # fps = int(capture.get(cv2.CAP_PROP_FPS))
            count_save = 0
            while True:
                idx += 1
                ret = capture.grab()
                if not ret:
                    break
                if idx % 30 == 1:
                    ret, frame = capture.retrieve()
                    if frame is None:    # exist broken frame
                        break
                    faces = self.app.get(frame)
                    for face in faces:
                        #人脸角度过滤
                        angle1, angle2=get_angle(face["kps"])
                        if angle1 < 30 or angle2 < 30:
                            continue
                        
                        #抠下人脸小图
                        box = face["bbox"]
                        box = box.astype(np.int_)
                        for i in range(len(box)):
                            if box[i]<0: box[i] = 0
                        if box[3] - box[1] < 80 or box[2] - box[0] < 80:
                            continue
                        wimg = frame[box[1]:box[3],box[0]:box[2]]
                        
                        #人脸质量过滤
                        processed_img = img_pre_process(wimg)
                        img = np.array([processed_img])
                        output = self.ort_session.run(self.output_names, {self.input_name: img})
                        if output[0][0][0] < 0.4:
                            continue
                        
                        #人脸矫正
                        for x in range(5):
                            face["kps"][x][0] -= box[0]
                            face["kps"][x][1] -= box[1]
                        ndimage = face_align_landmark(wimg,face["kps"])
                        
                        save_path = os.path.join(img_dir,"%d.jpg"%(count_save+1))
                        print(img_dir,'img_dir')
                        print(save_path)
                        if cv.imwrite(save_path,ndimage):
                            count_save += 1  
            capture.release()
        
        finally:
            self.pbar.update(1)

    def run(self):        
        try:
            pool = ThreadPool(10)
            pool.map(self.inference,self.bv_nubs)
        except:
            print("Error: unable to start thread")
        finally:
            pool.close()
            pool.join()
            print("Finished!")

if __name__ == "__main__":
    day = '9-7'
    video_path = '/media/huangrq/BIGDISK/reptile_faces2/video/{}/'.format(day)
    save_img_path = '/media/huangrq/BIGDISK/reptile_faces2/images/{}/'.format(day)
    bv_nubs = os.listdir(video_path)
    ii = inf_img(video_path,bv_nubs,save_img_path)
    ii.run()






