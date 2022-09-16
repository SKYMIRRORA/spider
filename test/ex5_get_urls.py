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


def get_bvs():
    url = "https://www.bilibili.com/v/channel/2511282?tab=multiple&cid=15"
    # url = 'https://www.bilibili.com/v/channel/2511282?tab=featured&cid=15'
    # url = "https://www.bilibili.com/v/life/daily?tag=530003"
    all_bvs = json_load("all_bvs.json")
    bvs = []
    app = FaceAnalysis(providers=['CUDAExecutionProvider', 'CPUExecutionProvider'], allowed_modules=['detection'])
    app.prepare(ctx_id=0, det_size=(640, 640))
    driver = webdriver.Firefox()
    # driver = webdriver.Chrome()
    driver.get(url)
    sleep(1)
    try:

        driver.find_elements(By.CLASS_NAME,"play-selector__item")[1].click()

        for i in tqdm(range(2),desc='Scrolling down'):
            #向下移动一次
            js="var q=document.getElementById('container').scrollTop=%d*document.body.scrollHeight"%(i+1)
            driver.execute_script(js) 
            sleep(1)

        # soup=BeautifulSoup(driver.page_source,"lxml")
        soup=BeautifulSoup(driver.page_source,"html.parser")
        # print('soup*****************')
        driver.close()
        
    except Exception as e:
        
        print(e)
    finally:
        divs = soup.find_all("div",class_="video-card")
        # print(divs,'divs**************************')
        print("length of divs:",len(divs))
        with requests.Session() as ses:
            for div in tqdm(divs,desc="Processing"):
                print(div,'a*****************8')
                # <a class="cover-picture" data-v-6694beea="" href="//www.bilibili.com/video/BV1oB4y1z77H" target="_blank">
                a = div.find("a",class_ = "cover-picture")
                bv = a["href"].split("/video/")[1]
                if bv in all_bvs or bv in bvs:
                    continue

                #检测封面是否存在人脸    
                # <img alt="" class="cover-picture__image" data-v-6694beea="" data-v-748372c9="" src="//i0.hdslb.com/bfs/archive/76b07937a19039537007d0aa59c228bdf9cf7b24.jpg@206w_116h_1c_90q.webp" v-lazy="//i0.hdslb.com/bfs/archive/76b07937a19039537007d0aa59c228bdf9cf7b24.jpg"/>
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

        with open("%drencenthot.json"%(len(bvs)), "w") as f:
            json.dump(bvs,f,indent = 2,cls=NumpyArrayEncoder)
        print("finished")


def get_got_bvs(filename):
    real_urls = json_load(filename)
    got_bvs = []
    for real_url in real_urls:
        got_bvs.append(real_url['bv'])
    return got_bvs

def get_real_urls(bvs): #可以通过一个B站视频的解析API获取视频真实地址
    try:
        parser_url = "https://api.injahow.cn/bparse/"
        with requests.Session() as s:
            # ip = "151.181.91.10:80"
            # proxies = {"http":ip,"https":ip}
            # s.proxies.update(proxies)
            real_urls = []
            got_bvs = get_got_bvs('got_urls.json')
            downed_bvs = json_load('downed_bvs.json')
            noface_bvs = json_load('noface_bvs.json')
            for bv in tqdm(bvs):
                # print(11111111111)
                if (bv in downed_bvs) or (bv in got_bvs) or (bv in noface_bvs):
                    continue
                payload = {"bv":bv,"format":"mp4"}
                print(payload)
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
        got_urls = json_load("got_urls.json")
        got_urls.extend(real_urls)
        
        with open("got_urls.json", "w") as f:
            json.dump(got_urls,f,indent = 2,cls=NumpyArrayEncoder)

        with open("all_bvs.json", "w") as f:
            json.dump(bvs,f,indent = 2,cls=NumpyArrayEncoder)
        return real_urls



def face_align_landmark(img, landmark, image_size=(112, 112), method="similar"):
    tform = transform.AffineTransform() if method == "affine" else transform.SimilarityTransform()
    src = np.array(
        [[38.2946, 51.6963], [73.5318, 51.5014], [56.0252, 71.7366], [41.5493, 92.3655], [70.729904, 92.2041]],
        dtype=np.float32
    )
    tform.estimate(landmark, src)
    # ndimage = transform.warp(img, tform.inverse, output_shape=image_size)
    # ndimage = (ndimage * 255).astype(np.uint8)
    M = tform.params[0:2, :]
    ndimage = cv.warpAffine(img, M, image_size, borderValue=0.0)
    # return ndimage
    if len(ndimage.shape) == 2:
        ndimage = np.stack([ndimage, ndimage, ndimage], -1)
    # else:
    #     ndimage = cv2.cvtColor(ndimage, cv2.COLOR_BGR2RGB)
    return ndimage

def img_pre_process(img):
    model_input_shape = (3, 224, 224)
    h = model_input_shape[1]
    w = model_input_shape[2]

    # the same as origin code written by author, its important
    image_arr = cv.resize(img, (w, h)).astype("float32")
    # image_arr = cv2.resize(cv2.imread(image), (w, h))
    return np.ascontiguousarray(image_arr)

class Down():
    imgs_dir = ""
    real_urls = []
    error_bvs = []
    pbar = None
    app = None
    downed_bvs = []
    noface_bvs = []

    def __init__(self,real_urls,imgs_dir) -> None:
        self.imgs_dir = imgs_dir
        self.real_urls = real_urls
        self.pbar = tqdm(total=len(real_urls))
        self.noface_bvs = []
        self.app = FaceAnalysis(providers=['CUDAExecutionProvider', 'CPUExecutionProvider'], allowed_modules=['detection'])
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        self.onnx_model = "FaceQnet.onnx"
        onnxruntime.set_default_logger_severity(3)
        self.ort_session = onnxruntime.InferenceSession(self.onnx_model, providers=['CUDAExecutionProvider','CPUExecutionProvider'])
        self.ort_session.set_providers(['CUDAExecutionProvider'], [ {'device_id': 0}])
        self.output_names = [self.ort_session.get_outputs()[0].name]
        self.input_name = self.ort_session.get_inputs()[0].name
    
    def down_imgs(self,real_url):
        try:
            # print(real_url,'------------------')
            capture = cv.VideoCapture(real_url["url"])
        except Exception as e:
            print(e)
            print("=======Error:failed to open video======== " +real_url["bv"])
            self.error_bvs.append(real_url["bv"])
        else:
            if(capture.isOpened()):
                bv_dir = self.imgs_dir + real_url["bv"]
                # bv_dir = self.imgs_dir + 'BV1pB4y1x7wC'
                faces_dir = bv_dir 
                if real_url["bv"] not in os.listdir(self.imgs_dir):
                    # os.mkdir(bv_dir)
                    os.mkdir(faces_dir)
                    fps = int(capture.get(cv.CAP_PROP_FPS))
                    count_frame = 0
                    count_save = 0
                    while capture.isOpened():
                        ret = capture.grab()
                        count_frame = count_frame + 1 
                        if not ret:break
                        if count_frame % fps == 0:
                            ret, frame = capture.retrieve()
                            if not ret:break
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
                                
                                save_path = faces_dir + "/%d.jpg"%(count_save+1)
                                if cv.imwrite(save_path,ndimage):
                                    count_save += 1  
                faces_path = self.imgs_dir + real_url["bv"] + '/faces/'
                if len(os.listdir(faces_path)) == 0:
                    self.noface_bvs.append(real_url["bv"])
                    
            else:
                print("not opened")               
        finally:
            self.pbar.update(1)

    def run(self):
        try:
            pool = ThreadPool()
            pool.map(self.down_imgs,self.real_urls)
        except:
            print("Error: unable to start thread")
        finally:
            with open("error_bvs.json", "w") as ef:
                json.dump(self.error_bvs,ef,indent = 2,cls=NumpyArrayEncoder)
            with open("noface_bvs2.json", "w") as f:
                json.dump(self.noface_bvs,f,indent = 2,cls=NumpyArrayEncoder)
            pool.close()
            pool.join()
            print("Finished!")

def play_video(real_url):
    try:
        capture = cv.VideoCapture(real_url["url"])
    except:
        print("Error: failed to open video")
    else:
        fps = capture.get(cv.CAP_PROP_FPS)
        w = capture.get(cv.CAP_PROP_FRAME_WIDTH)
        h = capture.get(cv.CAP_PROP_FRAME_HEIGHT)
        window_name = "fps:%d w:%d h:%d" %(fps,w,h)
        cv.namedWindow(window_name,cv.WINDOW_NORMAL)
        cv.resizeWindow(window_name,960,540)
        app = FaceAnalysis(providers=['CUDAExecutionProvider', 'CPUExecutionProvider'], allowed_modules=['detection'])
        app.prepare(ctx_id=0, det_size=(640, 640)) 
        with tqdm(total=100) as pbar:
            last_progress = 0
            progress = 0
            while capture.isOpened():   
                ret,frame=capture.read() # frame是一帧
                progress = round(capture.get(cv.CAP_PROP_POS_AVI_RATIO)*100,2)
                pbar.update(progress-last_progress)
                last_progress = progress
                if not ret:break # 当获取完最后一帧就结束
                # print(capture.get(cv.CAP_PROP_POS_MSEC)) # 当前视频播放进度
                faces = app.get(frame)
                if len(faces):
                    for face in faces:
                        box = face["bbox"]
                        box = box.astype(np.int_)
                        cv.rectangle(frame, (box[0],box[1]),(box[2],box[3]), (255, 0, 0), 2)
                cv.imshow(window_name,frame)
                cv.waitKey(1)


def download_video(real_url):
    start = time()
    user_agent = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0"
    headers = {
        "User-Agent" : user_agent,
    }
    video = requests.get(url=real_url["url"],headers=headers).content
    with open("testvideo.mp4", "wb") as f:
        f.write(video)
    end = time()
    print("耗时：",end - start)

def get_angle(points):
    v1x = points[0][0] - points[2][0]
    v1y = points[0][1] - points[2][1]

    v2x = points[1][0] - points[2][0]
    v2y = points[1][1] - points[2][1]

    v3x = points[3][0] - points[2][0]
    v3y = points[3][1] - points[2][1]

    v4x = points[4][0] - points[2][0]
    v4y = points[4][1] - points[2][1]

    cross_val1 = v1x * v2y - v1y * v2x
    dot_val1 = v1x * v2x + v1y * v2y
    rad1 = math.atan2(cross_val1, dot_val1)
    angle1 = rad1 / np.pi * 180.0
    angle1 = abs(angle1)

    cross_val2 = v3x * v4y - v3y * v4x
    dot_val2 = v3x * v4x + v3y * v4y
    rad2 = math.atan2(cross_val2, dot_val2)
    angle2 = rad2 / np.pi * 180.0
    angle2 = abs(angle2)

    return angle1, angle2


if __name__ == "__main__":
    # 从B站上爬取视频bv号并保存W
    get_bvs()

    # 解析bv获取视频链接并保存
    # bvs = json_load('9rencenthot.json')
    # bvs = json_load("all_bvs.json")
    # get_real_urls(bvs)

    # #多线程下载图片
    # real_urls = json_load("got_urls.json")
    # imgs_dir = "./8-26/"
    # down = Down(real_urls,imgs_dir)
    # down.run()
    # down = Down([{'url':'https://www.bilibili.com/video/BV1pB4y1x7wC'}],imgs_dir=imgs_dir)


    #下载单个链接视频图片
    # real_urls = [{'bv':'BV1YS4y18736',
    #              'url':'https://upos-sz-mirrorali.bilivideo.com/upgcxcode/00/83/710268300/710268300-1-208.mp4?e=ig8euxZM2rNcNbhMhzdVhwdlhzKzhwdVhoNvNC8BqJIzNbfq9rVEuxTEnE8L5F6VnEsSTx0vkX8fqJeYTj_lta53NCM=&uipk=5&nbs=1&deadline=1658731546&gen=playurlv2&os=alibv&oi=2030413803&trid=0e8b4454e76c4145b3ef5bd7357763f6T&mid=0&platform=html5&upsig=f91a31de2c680c13432f398f9522b45a&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,mid,platform&bvc=vod&nettype=0&bw=343014&orderid=0,1&logo=80000000'}]
    # down1 = Down(real_urls)
    # down1.down_imgs(real_urls[0])

    # print(cv.getBuildInformation())


