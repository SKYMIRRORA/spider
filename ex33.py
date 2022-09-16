import requests
import json



url_api = 'https://www.beesproxy.com/free'
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    }
    # print(url_api)
html = requests.get(url_api, headers=headers).json()
print(html)






