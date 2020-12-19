from urllib.parse import urlencode
import requests
from pyquery import PyQuery as pq
import time
import os
import csv
import json
import datetime

class SaveCSV(object):
    def save(self, keyword_list,path, item):
        try:
            if not os.path.exists(path):
                with open(path, "w", newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=keyword_list) 
                    writer.writeheader() 

            with open(path, "a", newline='', encoding='utf-8') as csvfile:  
                writer = csv.DictWriter(csvfile, fieldnames=keyword_list)
                writer.writerow(item)  

        except Exception as e:
            print("write error==>", e)
            with open("error.txt", "w") as f:
                f.write(json.dumps(item) + ",\n")
            pass
        
def get_page(page, title):
    params = {
        'containerid': '100103type=1&q='+title,
        'page': page,
        'type':'all',
        'queryVal':title,
        'featurecode':'20000320',
        'luicode':'10000011',
        'lfid':'106003type=1',
        'title':title
    }
    base_url = 'https://m.weibo.cn/api/container/getIndex?'
    url = base_url + urlencode(params)
    try:
        headers = {
            'Host': 'm.weibo.cn',
            'Referer': 'https://m.weibo.cn/u/2830678474',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError as e:
        print('Error', e.args)
        
# 解析接口返回的json字符串
def parse_page(json , label):
    res = []
    res_show = []
    if json:
        items = json.get('data').get('cards')
        for i in items:
            if i == None:
                continue
            item = i.get('mblog')
            if item == None:
                continue
                
            
            now = datetime.datetime.now()
            ans = datetime.datetime.strftime(now, "%Y-%m-%d %H:%M:%S")
            weibo = {}
            weibo['标题'] = item.get('id')
            weibo['时间'] = ans
            weibo['URL'] = []
            weibo['正文内容'] = pq(item.get('text')).text().replace(" ", "").replace("\n" , "")
            
            weibo_show = {}
            weibo_show['id'] = item.get('id')
            weibo_show['time'] = item.get('created_at')
            weibo_show['con'] = pq(item.get('text')).text().replace(" ", "").replace("\n" , "")
            res.append(weibo)
            res_show.append(weibo_show)
    return res, res_show

def wei_main(title, beginPage, endPage):
    path = "dataset/微博_" + title + ".csv"
    item_list = ['标题', '时间', 'URL', '正文内容' ]
    s = SaveCSV()
    for page in range(beginPage, endPage):
        try:
            time.sleep(5)        
            json = get_page(page, title)
            results, show = parse_page(json, title)
            if requests == None:
                continue
            for result in results:
                if result == None:
                    continue
                s.save(item_list, path, result)
        except TypeError:
            print("完成")
            continue
    return show
