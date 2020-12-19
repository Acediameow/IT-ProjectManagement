import urllib.request
from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv
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


class BDTB:
    def __init__(self, baseUrl):
        self.headers = {
            'User-Agent': r'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT) '
                          r'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
            'Referer': r'https://www.qiushibaike.com/',
            'Connection': 'keep-alive'
        }
        self.baseURL = baseUrl
        self.seeLZ = '?see_lz=1'
        self.tool = Tool()
        self.floor = 1

    def getPage(self):
        url = self.baseURL + self.seeLZ
        req = urllib.request.Request(url, headers=self.headers)
        res = urllib.request.urlopen(req).read().decode()
        return res

    def getContent(self, page):
        pattern = re.compile('<div id="post_content_.*?>(.*?)</div>', re.S)
        pattern_t = re.compile('<span class="tail-info">1楼</span><span class="tail-info">(.*?)</span>', re.S)
        items = re.findall(pattern, page)
        items_t = re.findall(pattern_t, page)
        contents = []
        for item in items:
            content = "\n" + self.tool.replace(item) + "\n"
            contents.append(content.encode('utf-8'))
        return content, items_t[0]

    def start(self):
        indexPage = self.getPage()
        time, content = self.getContent(indexPage)
        return content, time


def save(kw):
    fname = ("dataset/贴吧_" + kw + r".csv")
    fp = open(fname, 'a', newline='', encoding='utf-8-sig')
    writer = csv.writer(fp)
    writer.writerow(("标题", "时间", "URL", "正文内容"))
    return writer


def all_nr(kw2_url, full_url, writer, time_list, url_list, title_list, con_list):
    html = urlopen(full_url)
    bsObj = BeautifulSoup(html, 'html.parser')
    t1 = bsObj.find_all('a')

    for t2 in t1:
        t3 = str(t2.get('href'))
        t31 = str(t2.get('title'))
        if len(t3) == 13 and t31 != None and t3[1] == 'p':
            url = str(kw2_url) + str(t3)
            bdtb = BDTB(url)
            time, content = bdtb.start()
            time = str(time) + ":00"
            title_list.append(t31)
            url_list.append(url)
            con_list.append(content)
            time_list.append(time)
            writer.writerow((t31, time, url, content))


def tiebaSpider(kw_url, kw2_url, beginPage, endPage, writer, time_list, url_list, title_list, con_list):
    for page in range(beginPage, endPage + 1):
        pn = (page - 1) * 50
        full_url = kw_url + "&pn=" + str(pn)
        print("\n%s" % full_url)
        all_nr(kw2_url, full_url, writer, time_list, url_list, title_list, con_list)


def tie_main(kw, beginPage, endPage):
    title_list = []
    url_list = []
    con_list = []
    time_list = []
    kw_url = "http://tieba.baidu.com/f?"
    kw2_url = "http://tieba.baidu.com"
    kw_key = urllib.parse.urlencode({"kw": kw})
    full_url = kw_url + kw_key
    writer = save(kw)
    tiebaSpider(full_url, kw2_url, beginPage, endPage, writer, time_list, url_list, title_list, con_list)
    return time_list, url_list, title_list, con_list
