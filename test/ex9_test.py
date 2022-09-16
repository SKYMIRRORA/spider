import json,requests,time
import pandas as pd
import re
from bs4 import BeautifulSoup
import chardet
import datetime


def search_video(search_name,pages):
    """
    search_name: str; 输入搜索关键词
    pages: int; 输入需要爬取的页数

    return:
    bvid_lst: list; 返回BV号列表
    up_lst: list; 返回up主名字列表；与BV号一一对应
    """
    bvid_lst = []
    up_lst = []
    for page in range(1,pages):
        url = ('http://search.bilibili.com/all?keyword='+search_name+
               '&single_column=0&&order=dm&page='+str(page))
        req = requests.get(url)
        content = req.text
        pattern = re.compile('<a href="//www.bilibili.com/video/(.*?)\?from=search" title=')
        pattern_up = re.compile('<a href="//space.bilibili.com/.*?class="up-name">(.*?)</a></span>')
        lst_add = pattern.findall(content)
        up_lst_add = pattern_up.findall(content)
        
        while len(lst_add)==0:
            url = ('http://search.bilibili.com/all?keyword='+search_name+
                   '&single_column=0&&order=dm&page='+str(page))
            req = requests.get(url)
            content = req.text
            pattern = re.compile('<a href="//www.bilibili.com/video/(.*?)\?from=search" title=')
            pattern_up = re.compile('<a href="//space.bilibili.com/.*?class="up-name">(.*?)</a></span>')
            lst_add = pattern.findall(content)
            up_lst_add = pattern_up.findall(content)    
        
        
        time.sleep(1)
        print('第{}页'.format(page),lst_add)
        up_lst.extend(up_lst_add)
        bvid_lst.extend(lst_add)
    return bvid_lst,up_lst


#这一部分用于转化BV号->AV号
table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
tr = {}
for i in range(58):
    tr[table[i]] = i
s = [11, 10, 3, 8, 4, 6]
xor = 177451812
add = 8728348608

def bv2av(x):
    r = 0
    for i in range(6):
        r += tr[x[s[i]]] * 58 ** i
    return (r - add) ^ xor

def get_aid(bvid):
    if 'BV' in bvid:
        return bv2av(bvid)
    else:
        return bvid


def get_base_info(aid):
    base_info_url = f'https://api.bilibili.com/x/web-interface/archive/stat?aid={aid}'
    try:
        base_info = requests.get(base_info_url,headers={'User-Agent':'Mozilla/5.0'}).json()['data']
        #print('播放量：{}\n弹幕数量：{}\n收藏数量：{}\n硬币数量：{}\n分享数量：{}\n点赞数量：{}\n-----\n评论数量：{}'.format(
        #       base_info['view'],base_info['danmaku'],base_info['favorite'],base_info['coin'],base_info['share'],
        #       base_info['like'],base_info['reply']))
    except:
        print('Error')
    return base_info


# bvid_lst,up_lst = search_video('原神',20*100)
# print(bvid_lst,up_lst)
# bvid = get_aid('BV1DB4y157ox')
# print(bvid)



if __name__=='__main__':
    dic_header = {'User-Agent':'Mozilla/5.0'}
    search_name = '原神'
    bvid_lst,up_lst = search_video(search_name,pages=2)
    #df_result = pd.DataFrame(columns=['aid','cid','title','time','tag_lst','base_info','comment_datas','danmaku'])
    df_result = pd.DataFrame()
    for idx,bvid in enumerate(bvid_lst):
        print('正在提取第{}个视频的信息，BV号为：{}'.format(idx+1,bvid))
        aid = get_aid(bvid)
        # cid = get_cid(bvid)
        # title,ttime,tag_lst = get_title_time_tag(bvid)
        up_name = up_lst[idx]
        base_info = get_base_info(aid)
        #comment_datas = get_comment_datas(aid)
        #danmaku = get_danmaku_datas(cid)
        df_result= df_result.append({'aid':aid,
                                     '播放量':base_info['view'],'弹幕数量':base_info['danmaku'],
                                     '收藏数量':base_info['favorite'],'硬币数量':base_info['coin'],
                                     '分享数量':base_info['share'],'点赞数量':base_info['like'],
                                     '评论数量':base_info['reply']},ignore_index=True)
        print(df_result)
        time.sleep(1)