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



if __name__ == "__main__":
    downed_bvs = json_load("jsons/downed_bvs.json")
    all_bvs = json_load("jsons/all_bvs.json")
    # all_bvs = json_load("jsons/all_bvs.json")
    # downed_bvs.extend(downed_bvs_tmp)
    undown_bvs = []
    for bv in all_bvs:
        if bv not in downed_bvs:
            undown_bvs.append(bv)

    with open("jsons/undown_bvs.json", "w") as df:
        json.dump(undown_bvs,df,indent = 2,cls=NumpyArrayEncoder)