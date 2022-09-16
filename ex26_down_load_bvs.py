# !/usr/bin/python
# -*- coding:utf-8 -*-

import shutil
import requests, time, hashlib, urllib.request, re, json
from moviepy.editor import *
import os, sys, threading
import signal
import imageio
from tqdm import tqdm
from matplotlib.font_manager import json_dump, json_load
from multiprocessing.dummy import Pool as ThreadPool
import numpy as np
import cv2
from utils import urls,get_angle,download_video,play_video,img_pre_process,\
    face_align_landmark,get_got_bvs,NumpyArrayEncoder
from insightface.app import FaceAnalysis
import onnxruntime

imageio.plugins.ffmpeg.download()

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


# 访问API地址
def get_play_list(start_url, cid, quality):
    # print(start_url,'start_url')
    # https://api.bilibili.com/x/web-interface/view?aid=216980413/?p=1 start_url
    entropy = 'rbMCKn@KuamXWlPMoJGsKcbiJKUfkPF_8dABscJntvqhRSETg'
    appkey, sec = ''.join([chr(ord(i) + 2) for i in entropy[::-1]]).split(':')
    params = 'appkey=%s&cid=%s&otype=json&qn=%s&quality=%s&type=' % (appkey, cid, quality, quality)
    chksum = hashlib.md5(bytes(params + sec, 'utf8')).hexdigest()
    # print('appkey',appkey,'sec',sec,'params',params,'chksum',chksum)
    url_api = 'https://interface.bilibili.com/v2/playurl?%s&sign=%s' % (params, chksum)
    # print(url_api,'url_api')
    headers = {
        'Referer': start_url,  # 注意加上referer
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    }
    # print(url_api)
    html = requests.get(url_api, headers=headers).json()
    # print(json.dumps(html))
    video_list = []
    for i in html['durl']:
        video_list.append(i['url'])
        # print(i['url'])
    # print(video_list)
    return video_list

#  下载视频
def down_video(video_list, start_url, page,bv_nub,video_path):
    # num = 1
    # for i in video_list:
    i = video_list[0]
    opener = urllib.request.build_opener()
    # 请求头
    opener.addheaders = [
        # ('Host', 'upos-hz-mirrorks3.acgvideo.com'),  #注意修改host,不用也行
        ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:56.0) Gecko/20100101 Firefox/56.0'),
        ('Accept', '*/*'),
        ('Accept-Language', 'en-US,en;q=0.5'),
        ('Accept-Encoding', 'gzip, deflate, br'),
        ('Range', 'bytes=0-'),  # Range 的值要为 bytes=0- 才能下载完整视频
        ('Referer', start_url),  # 注意修改referer,必须要加的!
        ('Origin', 'https://www.bilibili.com'),
        ('Connection', 'keep-alive'),
    ]
    # print(i,'url')
    urllib.request.install_opener(opener)
    # if len(video_list) > 1:
    #     urllib.request.urlretrieve(url=i, filename=path + bv_nub+'{}.mp4'.format(num)) 
    # else:
    video_name = video_path + bv_nub+'.mp4'
    urllib.request.urlretrieve(url=i, filename=video_name)
    # return video_path 
    # num += 1video_pathvideo_path

def bv2av(x):
    table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
    tr = {}
    for i in range(58):
        tr[table[i]] = i
    s = [11, 10, 3, 8, 4, 6]
    xor = 177451812
    add = 8728348608
    r = 0
    for i in range(6):
        r += tr[x[s[i]]] * 58 ** i
    return (r - add) ^ xor

class DownVideos():
    def __init__(self,video_dir,bv_img_dir,nub_thread) -> None:
        self.pbar = tqdm(total=len(bvs))
        self.video_dir = video_dir
        self.bv_img_dir = bv_img_dir
        self.nub_thread = nub_thread
        self.downed_bvs_tmp = []

        self.app = FaceAnalysis(providers=['CUDAExecutionProvider', 'CPUExecutionProvider'], allowed_modules=['detection'])
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        self.onnx_model = "FaceQnet.onnx"
        onnxruntime.set_default_logger_severity(3)
        self.ort_session = onnxruntime.InferenceSession(self.onnx_model, providers=['CUDAExecutionProvider','CPUExecutionProvider'])
        self.ort_session.set_providers(['CUDAExecutionProvider'], [ {'device_id': 0}])
        self.output_names = [self.ort_session.get_outputs()[0].name]
        self.input_name = self.ort_session.get_inputs()[0].name

    def inference(self,bv_nub):
        # source_path = '{}.mp4'.format(self.bv_nubs)
        bv_dir = os.path.join(self.video_dir,bv_nub + '.mp4')
        img_dir = os.path.join(self.bv_img_dir,bv_nub)
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
                        # ndimage = cv2.resize(wimg,(112,112))
                        
                        save_path = os.path.join(img_dir,"%d.jpg"%(count_save+1))
                        # print(img_dir,'img_dir')
                        # print(save_path)
                        if cv2.imwrite(save_path,ndimage):
                            count_save += 1  
            capture.release()
        



    def spider_video(self,bv_nub):
        # bv_nub = 'BV1Xa411P731'
        self.downed_bvs_tmp.append(bv_nub)
        start = str(bv2av(bv_nub))
        if start.isdigit() == True:  # 如果输入的是av号
            # 获取cid的api, 传入aid即可
            start_url = 'https://api.bilibili.com/x/web-interface/view?aid=' + start
    
        # 视频质量
        # <accept_format><![CDATA[flv,flv720,flv480,flv360]]></accept_format>
        # <accept_description><![CDATA[高清 1080P,高清 720P,清晰 480P,流畅 360P]]></accept_description>
        # <accept_quality><![CDATA[80,64,32,16]]></accept_quality>
        # quality = input('请输入您要下载视频的清晰度(1080p:80;720p:64;480p:32;360p:16)(填写80或64或32或16):')
        quality = "80"
        # 获取视频的cid,title
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
        }
        html = requests.get(start_url, headers=headers).json()
        # print(start_url)
        # print(html)
        data = html['data']
        cid_list = []
        if '?p=' in start:
            # 单独下载分P视频中的一集
            p = re.search(r'\?p=(\d+)',start).group(1)
            cid_list.append(data['pages'][int(p) - 1])
        else:
            # 如果p不存在就是全集下载
            cid_list = data['pages']

        try:
            for i, item in enumerate(cid_list):
                # print(cid_list)
                cid = str(item['cid'])
                page = str(item['page'])
                start_url = start_url + "/?p=" + page
                video_list = get_play_list(start_url, cid, quality)
                down_video(video_list, start_url, page,bv_nub,self.video_dir)
                
                # bv_img_path = self.path + bv_nub
                # if not os.path.exists(bv_img_path):
                #     os.mkdir(bv_img_path)
                self.inference(bv_nub)
                break
        except Exception as e:
            print(e)
            print("=======Error:failed to open video======== " +bv_nub)
            # self.error_bvs.append(real_url["bv"])                      
        finally:
            if os.path.exists(os.path.join(self.video_dir,bv_nub + '.mp4')):
                os.remove(os.path.join(self.video_dir,bv_nub + '.mp4'))
            self.pbar.update(1)

    def run(self,bvs):
        try:
            pool = ThreadPool(self.nub_thread)
            #线程池没满，就创建新线程执行任务，线程池满了则等待
            pool.map(self.spider_video,bvs)
        except:
            print("Error: unable to start thread")
        finally:
            with open("jsons/downed_bvs_tmp.json", "w") as ef:
                json.dump(self.downed_bvs_tmp,ef,indent = 2,cls=NumpyArrayEncoder) 
            pool.close()
            pool.join()
            print("Finished!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='do ijb test')
    parser.add_argument('--day', default='9-10', help='day.')
    args = parser.parse_args()

    video_dir = "/media/huangrq/BIGDISK/reptile_faces2/video/{}/".format(args.day)
    imgs_dir = "/media/huangrq/BIGDISK/reptile_faces2/images/{}/".format(args.day)

    nub_thread = 10
    bvs = json_load("jsons/undown_bvs.json")
    dv = DownVideos(video_dir,imgs_dir,nub_thread)
    dv.run(bvs)