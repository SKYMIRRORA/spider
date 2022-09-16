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


urls = [
    #搞笑 1979 1
    "https://www.bilibili.com/v/channel/1833?tab=multiple&cid=0",
    #vlog | 近期热门 1070 2
    "https://www.bilibili.com/v/channel/2511282?tab=multiple&cid=15",
     #美食 851 3
    "https://www.bilibili.com/v/channel/20215?tab=multiple&cid=11",
    #韩国 829 4
    "https://www.bilibili.com/v/channel/116?tab=multiple&cid=0",
    #vlog | 精选 1070 5
    'https://www.bilibili.com/v/channel/2511282?tab=featured&cid=15',
    #体育 595 6
    "https://www.bilibili.com/v/channel/41103?tab=multiple&cid=21",
    #人文 551 7
    "https://www.bilibili.com/v/channel/40737?tab=multiple&cid=0",
    #旅游|近期热门 429 8
    "https://www.bilibili.com/v/channel/6572?tab=multiple&cid=15",
    #演奏 407 9
    "https://www.bilibili.com/v/channel/373?tab=multiple&cid=0",
    #演奏400 10
    "https://www.bilibili.com/v/channel/373?tab=multiple&cid=6",
    #汽车 393  11
    "https://www.bilibili.com/v/channel/13760?tab=multiple&cid=15",
    #翻唱 348 12
    "https://www.bilibili.com/v/channel/386?tab=multiple&cid=0",
    #服饰 306 13
    "https://www.bilibili.com/v/channel/313718?tab=multiple&cid=0",
    #美妆 302 14
    "https://www.bilibili.com/v/channel/832569?tab=multiple&cid=0",
    #健身 282 15
    "https://www.bilibili.com/v/channel/4344?tab=multiple&cid=21",
    #服饰 301 16
    "https://www.bilibili.com/v/channel/313718?tab=multiple&cid=5",
    #乐器 244 17
    "https://www.bilibili.com/v/channel/14704?tab=multiple&cid=0",
    #户外 210 18
    "https://www.bilibili.com/v/channel/114088?tab=multiple&cid=0",
    #日本 209 19
    "https://www.bilibili.com/v/channel/860?tab=multiple&cid=0",
    #摄影 201 20
    "https://www.bilibili.com/v/channel/25450?tab=multiple&cid=0",
    #英国 189 21
    "https://www.bilibili.com/v/channel/3504?tab=multiple&cid=0",
    #英语 148 22
    "https://www.bilibili.com/v/channel/8816?tab=multiple&cid=15",
    #吃货 138 23
    "https://www.bilibili.com/v/channel/6942?tab=multiple&cid=11",
    #职场 132 24
    "https://www.bilibili.com/v/channel/47481?tab=multiple&cid=0",
    #美国 127 25
    "https://www.bilibili.com/v/channel/5794?tab=multiple&cid=0",
    #彩妆 124 26
    "https://www.bilibili.com/v/channel/499816?tab=multiple&cid=0",
    #彩妆 122 27
    "https://www.bilibili.com/v/channel/499816?tab=multiple&cid=5",
    #家常菜 119 28
    "https://www.bilibili.com/v/channel/94337?tab=multiple&cid=0",
    #影视混剪 116 29
    "https://www.bilibili.com/v/channel/882598?tab=multiple&cid=18",
    #吉他 108 30
    "https://www.bilibili.com/v/channel/3185?tab=multiple&cid=6",
    #篮球 108 31
    "https://www.bilibili.com/v/channel/1265?tab=multiple&cid=21",
    #家居 107 32
    "https://www.bilibili.com/v/channel/649117?tab=multiple&cid=0",
    #健康 99 33
    "https://www.bilibili.com/v/channel/37242?tab=multiple&cid=0",
    #减肥 98 34
    "https://www.bilibili.com/v/channel/20805?tab=multiple&cid=5",
    #减肥 98 35
    "https://www.bilibili.com/v/channel/20805?tab=multiple&cid=21",
    #穿搭 96 36
    "https://www.bilibili.com/v/channel/1139735?tab=multiple&cid=5",
    #明星舞蹈 93 37
    "https://www.bilibili.com/v/channel/6012204?tab=multiple&cid=14",
    #潮流 89 38
    "https://www.bilibili.com/v/channel/91251?tab=multiple&cid=5",
    #萌娃 85 39
    "https://www.bilibili.com/v/channel/356262?tab=multiple&cid=0",
    #欧美音乐 85 40
    "https://www.bilibili.com/v/channel/17034?tab=multiple&cid=6",
    #探店 83 41
    "https://www.bilibili.com/v/channel/1469519?tab=multiple&cid=0",
    #化妆 76 42
    "https://www.bilibili.com/v/channel/13175?tab=multiple&cid=0",
    #街舞 76 43
    "https://www.bilibili.com/v/channel/5574?tab=multiple&cid=14",
    #种草 69 44
    "https://www.bilibili.com/v/channel/1128093?tab=multiple&cid=5",
    #韩剧 67 45
    "https://www.bilibili.com/v/channel/53056?tab=multiple&cid=18",
    #说唱 66 46
    "https://www.bilibili.com/v/channel/529?tab=multiple&cid=6",
    #rap 66 47
    "https://www.bilibili.com/v/channel/246?tab=multiple&cid=6",
    #考研 65 48
    "https://www.bilibili.com/v/channel/372799?tab=multiple&cid=0",
    #农村 60 49
    "https://www.bilibili.com/v/channel/59846?tab=multiple&cid=0",
    #电音 63 50
    "https://www.bilibili.com/v/channel/14426?tab=multiple&cid=6",
    #日语 57 51
    "https://www.bilibili.com/v/channel/3086?tab=multiple&cid=0",
     #翻跳 55 52
    "https://www.bilibili.com/v/channel/31878?tab=multiple&cid=14",
    #泰国 53 53
    "https://www.bilibili.com/v/channel/547?tab=multiple&cid=0",
    #互联网 52 54
    "https://www.bilibili.com/v/channel/23901?tab=multiple&cid=0",
    #极限运动 49 55
    "https://www.bilibili.com/v/channel/8876?tab=multiple&cid=0",
    #情侣 48 56
    "https://www.bilibili.com/v/channel/66611?tab=multiple&cid=0",
    #方言 48 57
    "https://www.bilibili.com/v/channel/3492?tab=multiple&cid=0",
    #上海 46 58
    "https://www.bilibili.com/v/channel/596?tab=multiple&cid=0",
    #护肤 45 59
    "https://www.bilibili.com/v/channel/612086?tab=multiple&cid=0",
    #护肤 44 60
    "https://www.bilibili.com/v/channel/612086?tab=multiple&cid=5",
     #汉服 43 61
    "https://www.bilibili.com/v/channel/32454?tab=multiple&cid=5",
    #化妆品 42 62
    "https://www.bilibili.com/v/channel/519896?tab=multiple&cid=5",
    #装修 42 63
    "https://www.bilibili.com/v/channel/161357?tab=multiple&cid=0",
    #文学 42 64
    "https://www.bilibili.com/v/channel/13509?tab=multiple&cid=0",
    #歪果仁 41 65
    "https://www.bilibili.com/v/channel/322082?tab=multiple&cid=0",
    #宅舞 41 66
    "https://www.bilibili.com/v/channel/9500?tab=multiple&cid=14",
    #发型 40 67
    "https://www.bilibili.com/v/channel/13896?tab=multiple&cid=5",
     #吉他说唱 40 68
    "https://www.bilibili.com/v/channel/87121?tab=multiple&cid=6",
    #开口脆 39 69
    "https://www.bilibili.com/v/channel/12784?tab=multiple&cid=6",
    #耳机 39 70
    "https://www.bilibili.com/v/channel/8734?tab=multiple&cid=0",
    #理财 37 71
    "https://www.bilibili.com/v/channel/487255?tab=multiple&cid=0",
    #秀场 37 72
    "https://www.bilibili.com/v/channel/516500?tab=multiple&cid=0",
    #粤语 36 73
    "https://www.bilibili.com/v/channel/1730?tab=multiple&cid=0",
    #烘焙 36 74 
    "https://www.bilibili.com/v/channel/218245?tab=multiple&cid=0",
    #摇滚 34 75
    "https://www.bilibili.com/v/channel/7993?tab=multiple&cid=6",
    #舞蹈教学 34 76
    "https://www.bilibili.com/v/channel/157087?tab=multiple&cid=14",
    #HIPHOP 34 77
    "https://www.bilibili.com/v/channel/9374?tab=multiple&cid=6",
    #化妆教程 32 78
    "https://www.bilibili.com/v/channel/261355?tab=multiple&cid=5",
    #早餐 32 79
    "https://www.bilibili.com/v/channel/36893?tab=multiple&cid=0",
    #泰剧 30 80
    "https://www.bilibili.com/v/channel/179103?tab=multiple&cid=18",
    #韩舞 30 81
    "https://www.bilibili.com/v/channel/159571?tab=multiple&cid=14",
    #甜品 29 82
    "https://www.bilibili.com/v/channel/454809?tab=multiple&cid=0",
    #戏曲 28 83
    "https://www.bilibili.com/v/channel/170646?tab=multiple&cid=0",
    #国风音乐 27 84
    "https://www.bilibili.com/v/channel/1728359?tab=multiple&cid=0",
    #德国 27 85
    "https://www.bilibili.com/v/channel/310?tab=multiple&cid=0",
    #英语口语 25 86
    "https://www.bilibili.com/v/channel/602557?tab=multiple&cid=0",
    #面试 24 87
    "https://www.bilibili.com/v/channel/32613?tab=multiple&cid=0",
     #中国舞 24 88
    "https://www.bilibili.com/v/channel/451792?tab=multiple&cid=14",
    #自驾游 24 89
    "https://www.bilibili.com/v/channel/637832?tab=multiple",
     #旅拍 22 90
    "https://www.bilibili.com/v/channel/395596?tab=multiple",
    #cosplay 22 91
    "https://www.bilibili.com/v/channel/88?tab=multiple&cid=0",
    #心理学 22 92
    "https://www.bilibili.com/v/channel/41917?tab=multiple&cid=0",
    #印度 22 93
    "https://www.bilibili.com/v/channel/2633?tab=multiple&cid=0",
    #钓鱼 21 94
    "https://www.bilibili.com/v/channel/4248?tab=multiple&cid=0",
    #古典音乐 21 95
    "https://www.bilibili.com/v/channel/32767?tab=multiple&cid=0",
    #配饰 21 96
    "https://www.bilibili.com/v/channel/1599602?tab=multiple&cid=0",
    #小吃 21 97
    "https://www.bilibili.com/v/channel/56406?tab=multiple&cid=0",
     #木吉他 21 98
    "https://www.bilibili.com/v/channel/35258?tab=multiple&cid=6",
    #饮料 20 99
    "https://www.bilibili.com/v/channel/72140?tab=multiple&cid=0",
    #记实 20 100
    "https://www.bilibili.com/v/channel/52179?tab=multiple&cid=0",
    #嘻哈 20 101
    "https://www.bilibili.com/v/channel/21297?tab=multiple&cid=6",
    #脱口秀 20 102
    "https://www.bilibili.com/v/channel/4346?tab=multiple&cid=0",
    #乐队 18 103
    "https://www.bilibili.com/v/channel/7114?tab=multiple&cid=0",
    #毕业季 18 104
    "https://www.bilibili.com/v/channel/68321?tab=multiple&cid=0",
    #编舞 18 105
    "https://www.bilibili.com/v/channel/148123?tab=multiple&cid=14",
    #爵士舞 17 106
    "https://www.bilibili.com/v/channel/290069?tab=multiple&cid=14",
    #试吃 17 107
    "https://www.bilibili.com/v/channel/490608?tab=multiple&cid=11",
    #瑜伽 17.6 108
    "https://www.bilibili.com/v/channel/22269?tab=multiple&cid=21",
    #咖啡 17 109
    "https://www.bilibili.com/v/channel/41593?tab=multiple&cid=0",
    #滑板 16 110
    "https://www.bilibili.com/v/channel/20495?tab=multiple&cid=21",
    #民乐 16 111
    "https://www.bilibili.com/v/channel/11259?tab=multiple&cid=0",
    #武器 15 112
    "https://www.bilibili.com/v/channel/3988?tab=multiple&cid=0",
    #武汉 15 113
    "https://www.bilibili.com/v/channel/23182?tab=multiple&cid=0",
    #鞋子推荐 15 114
    "https://www.bilibili.com/v/channel/3327666?tab=multiple&cid=0",
    #京剧 15 115
    "https://www.bilibili.com/v/channel/5195?tab=multiple&cid=0",
    #口红 13 116
    "https://www.bilibili.com/v/channel/645936?tab=multiple&cid=5",
    #日常妆 13 117
    "https://www.bilibili.com/v/channel/598357?tab=multiple&cid=5",
    #珠宝 16 118
    "https://www.bilibili.com/v/channel/304169?tab=multiple&cid=5",
    #奢侈品 13 119
    "https://www.bilibili.com/v/channel/220187?tab=multiple&cid=5",
    #古风舞 2.7 120
    "https://www.bilibili.com/v/channel/921323?tab=multiple&cid=14",
    #现代舞 10 121
    "https://www.bilibili.com/v/channel/66209?tab=multiple&cid=14",
    #vlog | 校园 6.3 122
    "https://www.bilibili.com/v/channel/5727642?tab=multiple",
    #房车 7.3 123
    "https://www.bilibili.com/v/channel/630567?tab=multiple",
    #穷游 3.6 124
    "https://www.bilibili.com/v/channel/298164?tab=multiple",
    #日本旅游 3.2 125
    "https://www.bilibili.com/v/channel/264846?tab=multiple",
    #民宿 2.3 126
    "https://www.bilibili.com/v/channel/671689?tab=multiple",
    #冲浪 2.3 127
    "https://www.bilibili.com/v/channel/20098?tab=multiple&cid=21",
    #古典舞 11 128
    "https://www.bilibili.com/v/channel/161247?tab=multiple&cid=14",
    #广场舞 10 129
    "https://www.bilibili.com/v/channel/165210?tab=multiple&cid=14",
    #蹦迪 5.4 130
    "https://www.bilibili.com/v/channel/1527081?tab=multiple&cid=14",
    ]

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

