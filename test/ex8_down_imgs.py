from time import time
import requests
import bs4 as bs
import os
import cv2 as cv
import json
import numpy as np
from tqdm import tqdm
from insightface.app import FaceAnalysis
import ex1_get_bv_nub

MAX_NUM_IMGS = 80

class Downloader:
    bv = ""
    url = ""
    capture = None
    fps = 0
    w=0
    h=0
    count_frame = 0
    count_save = 0

    imgs_dir = "images"
    bv_dir = ""
    faces_dir = ""

    faces_json = {}
    data_list = []

    benchmark_dic = {}
    detected_list = []

    sim_list = []
    app = FaceAnalysis(providers=['CUDAExecutionProvider', 'CPUExecutionProvider'], allowed_modules=['detection','genderage','recognition'])
    app.prepare(ctx_id=0, det_size=(640, 640))

    def __init__(self) -> None:
        pass

    def reset_url(self,real_url):
        self.bv = real_url["bv"]
        self.url = real_url["url"]
        try:
            self.capture = cv.VideoCapture(self.url)
        except:
            print("Error:failed to open video")
        else:
            self.bv_dir = os.path.join(self.imgs_dir,real_url["bv"])
            self.faces_dir = self.bv_dir+"/faces"
            if not os.path.exists(self.bv_dir):
                os.mkdir(self.bv_dir)
                os.mkdir(self.faces_dir)
            self.fps = self.capture.get(cv.CAP_PROP_FPS)
            self.w = self.capture.get(cv.CAP_PROP_FRAME_WIDTH)
            self.h = self.capture.get(cv.CAP_PROP_FRAME_HEIGHT)
            self.faces_json = {}
            self.data_list = []
            self.faces_json["bv"]=real_url["bv"]
            self.faces_json["url"]="https://www.bilibili.com/video/"+real_url["bv"]
            self.sim_list = [0]*8

    def similarity_detection(self,face1,face2):
        v1 = face1["embedding"]
        v2 = face2["embedding"]
        dot = np.dot(v1,v2)
        norm = np.linalg.norm(v1)*np.linalg.norm(v2)
        sim = dot/norm

        if sim < 0.2 or sim == 1:
            return False
        index = int((sim - 0.2)/0.1)
        if self.sim_list[index] < 10:
            self.sim_list[index] +=1
            return sim
        else:
            return False

    def get_benchmark_img(self):
            print("Start to get benchmark.")
            self.benchmark_dic={"img":None,"face":None,"timestamp":"","loss":100}
            self.detected_list = []
            while self.capture.isOpened():
                ret = self.capture.grab()
                if not ret:break
                self.count_frame = self.count_frame + 1
                if self.count_frame % self.fps == 0:              
                    ret, frame = self.capture.retrieve()             
                    if ret:
                        faces = self.app.get(frame) 
                        if len(faces):
                            for face in faces:
                                timestamp = get_timestamp(self.count_frame/self.fps)
                                face["timestamp"] = timestamp
                                self.detected_list.append({"img":frame,"face":face})
                                
                                face_loss = get_face_loss(face)                                                       
                                if face_loss < self.benchmark_dic["loss"]:
                                    self.benchmark_dic["img"] = frame
                                    self.benchmark_dic["face"] = face
                                    self.benchmark_dic["timestamp"] = timestamp
                                    self.benchmark_dic["loss"] = face_loss
                if self.benchmark_dic["loss"] < 0.2: 
                    break
            if cv.imwrite(self.faces_dir+"/benchmark.jpg",self.benchmark_dic["img"]):
                self.benchmark_dic["face"]["index"] = "benchmark"
                self.benchmark_dic["face"]["loss"] = self.benchmark_dic["loss"]
                self.data_list.append(self.benchmark_dic["face"])
                print("Finished getting benchmark.")
            else:
                print("Error:failed to save benchmark")

    def download_images(self):
        print("Start to get download images.")
        for data in self.detected_list:
            sim = self.similarity_detection(self.benchmark_dic["face"],data["face"])
            if sim:
                save_path = self.faces_dir + "/%d.jpg"%(self.count_save+1)
                if cv.imwrite(save_path,data["img"]):
                    self.count_save += 1
                    data["face"]["index"] = self.count_save
                    data["face"]["sim"] = sim
                    self.data_list.append(data["face"])

        while self.capture.isOpened() and self.count_save < MAX_NUM_IMGS:
            ret = self.capture.grab()
            if not ret:break
            self.count_frame = self.count_frame + 1
            if self.count_frame % self.fps == 0:              
                ret, frame = self.capture.retrieve()
                if ret:
                    faces = self.app.get(frame)
                    if len(faces):
                        for face in faces:
                            sim = self.similarity_detection(self.benchmark_dic["face"],face)
                            if sim:
                                timestamp = get_timestamp(self.count_frame/self.fps)
                                save_path = self.faces_dir + "/%d.jpg"%(self.count_save+1)
                                if cv.imwrite(save_path,frame):
                                    self.count_save += 1
                                    face["timestamp"] = timestamp
                                    face["index"] = self.count_save           
                                    face["sim"] = sim
                                    self.data_list.append(face)

        self.faces_json["total"] = len(self.data_list)
        self.faces_json["similarity"] = self.sim_list
        self.faces_json["data"]=self.data_list
        with open(self.bv_dir+"/faces_data.json", "w") as f:
            json.dump(self.faces_json,f,indent = 2,cls=NumpyArrayEncoder)
        print("Finished downloading images.")

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

def get_face_loss(face):
    va = face["kps"][1] - face["kps"][0]
    vb = face["kps"][4] - face["kps"][1]
    vc = face["kps"][4] - face["kps"][3]
    vd = face["kps"][3] - face["kps"][0]
    v_horizontal = np.array([1,0])
    v_vertical = np.array([0,1])
    l1 = get_vectors_ang(va,v_horizontal)
    l2 = get_vectors_ang(vc,v_horizontal)
    l3 = abs(get_vectors_ang(vb,v_vertical)-get_vectors_ang(vd,v_vertical))
    nose_x = face["kps"][2][0]
    center_x = (face["kps"][0][0]+face["kps"][1][0])/2
    l4 = abs(nose_x - center_x)
    l5 = 1 - face["det_score"]
    face_loss = l1 + l2 + l3 + l4/100 + l5
    return face_loss

def get_vectors_ang(v1,v2):
    dot = np.dot(v1,v2)
    norm = np.linalg.norm(v1)*np.linalg.norm(v2)
    return np.arccos(dot/norm)

def get_timestamp(ms):
    s = ms
    h = int(s/3600)
    m = int(s/60%60)
    s = int(s%60)
    ret = "%02d:%02d:%02d"%(h,m,s)
    return ret

if __name__ == "__main__":
    bv = "BV1tT411u74B"
    real_url = ex1_get_bv_nub.get_real_url(bv) #字典类型
    down = Downloader()
    down.reset_url(real_url)
    down.get_benchmark_img()
    down.download_images()
