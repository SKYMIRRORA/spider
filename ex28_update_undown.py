from time import sleep, time
from matplotlib.font_manager import json_dump, json_load
import requests
from bs4 import BeautifulSoup
import os
import cv2 as cv
import json
import numpy as np
from tqdm import tqdm
from selenium import webdriver
from multiprocessing.dummy import Pool as ThreadPool
from random import choice
from selenium.webdriver.common.by import By
import math


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
    undown_bvs = json_load("jsons/undown_bvs.json")
    down_tmp = json_load("jsons/downed_bvs_tmp.json")
    # all_bvs = json_load("jsons/all_bvs.json")
    # downed_bvs.extend(downed_bvs_tmp)
    new_undown_bvs = []
    for bv in undown_bvs:
        if bv not in down_tmp:
            new_undown_bvs.append(bv)

    with open("jsons/undown_bvs.json", "w") as df:
        json.dump(new_undown_bvs,df,indent = 2,cls=NumpyArrayEncoder)