import csv
import json
import requests
from urllib.parse import urlencode
import urllib.request
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import urllib


class Tool:
    removeImg = re.compile('<img.*?>| {7}|')
    removeAddr = re.compile('<a.*?>|</a>')
    replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    replaceTD = re.compile('<td>')
    replacePara = re.compile('<p.*?>')
    replaceBR = re.compile('<br><br>|<br>')
    removeExtraTag = re.compile('<.*?>')

    def replace(self, x):
        x = re.sub(self.removeImg, "", x)
        x = re.sub(self.removeAddr, "", x)
        x = re.sub(self.replaceLine, "\n", x)
        x = re.sub(self.replaceTD, "\t", x)
        x = re.sub(self.replacePara, "\n    ", x)
        x = re.sub(self.replaceBR, "\n", x)
        x = re.sub(self.removeExtraTag, "", x)
        return x.strip()


class DouBan:
    def __init__(self, url):
        self.url = url
        self.tool = Tool()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'
        }
        self.url_list = []
        self.result_data = {}

    def change_con(self, content):
        content = "\n" + Tool().replace(content) + "\n"
        content = content
        return content

    def page_con(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.encoding = "utf8"
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            print("解析网页成功")
            return soup
        except:
            print("解析网页出错")

    def page_data(self, key_word, writer, time_list, url_list, title_list, con_list, db):
        try:
            fname = '豆瓣_' + key_word + '.csv'
            con = db.page_con(self.url)
            managesInfo = con.find_all('h3')
            for i in managesInfo:
                pattern = re.compile('<a href="(.*?)" onclick=.*?>', re.S)
                item_url = re.findall(pattern, str(i))[0]
                res = db.page_con(item_url)
                pattern_tit = re.compile('<h1>(.*?)</h1>', re.S)
                pattern_time = re.compile('<span class="pub-date">(.*?)</span>', re.S)
                pattern_con = re.compile('<div class="note">(.*?)<div id="link-report_note">', re.S)
                item_title = re.findall(pattern_tit, str(res))[0]
                item_time = re.findall(pattern_time, str(res))[0]
                item_con = re.findall(pattern_con, str(res))[0]
                item_con = "\n" + Tool().replace(item_con) + "\n"
                writer.writerow([item_title, item_time, item_url, item_con])

                time_list.append(item_time)
                u = item_url[:20] + '...'
                url_list.append(u)
                title_list.append(item_title)
                con_list.append(item_con)
            print("获取网页成功")
        except:
            print("获取网页失败")

    def write_csv(self, key_word):
        fname = 'dataset/豆瓣_' + key_word + '.csv'
        fp = open(fname, 'a', newline='', encoding='utf-8-sig')
        writer = csv.writer(fp)
        writer.writerow(("标题", "时间", "URL", "正文内容"))
        return writer


def dou_main(key_word):
    time_list, url_list, title_list, con_list = [], [], [], []
    main_url = 'https://www.douban.com/search?cat=1015&q='
    url = main_url + key_word
    db = DouBan(url)
    writer = db.write_csv(key_word)
    db.page_data(key_word, writer, time_list, url_list, title_list, con_list, db)
    return time_list, url_list, title_list, con_list
