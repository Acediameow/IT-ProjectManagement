from bs4 import BeautifulSoup
import csv
import re
import requests


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


def change(content):
    content = "\n" + Tool().replace(content) + "\n"
    content = content
    return content


def getHtmlText(url):
    try:
        r = requests.get(url)
        r.encoding = r.apparent_encoding
        html = r.text
        soup = BeautifulSoup(html, 'html.parser')
        print("解析网页成功")
        return soup
    except:
        print("解析网页出错")


def getHtmlList(main_url, begin, end, writer, time_list, url_list, title_list, con_list):
    try:
        for num in range(end - begin + 1):
            develop_url = main_url + '&pn=' + str(begin + num)
            page = getHtmlText(develop_url)
            managesInfo = page.find_all('li')
            li_info = managesInfo[4:-1]
            for i in li_info:
                pattern = re.compile('<h3><a href="(.*?)" target="_blank">', re.S)
                pattern_t = re.compile('<h3><a href=.*?>(.*?)</a></h3>', re.S)
                pattern_ti = re.compile('时间：<span>(.*?)</span>', re.S)
                item_url = re.findall(pattern, str(i))[0]
                item_title = re.findall(pattern_t, str(i))[0]
                item_title = change(item_title)
                item_time = re.findall(pattern_ti, str(i))
                try:
                    con_page = getHtmlText(item_url)
                    pattern_c = re.compile('<div class="bbs-content clearfix">(.*?)</div>', re.S)
                    item_con = re.findall(pattern_c, str(con_page))[0]
                    item_con = change(item_con)
                except:
                    pattern_c = re.compile('<p>"(.*?)"</p>', re.S)
                    item_con = re.findall(pattern_c, str(i))[0]
                    item_con = change(item_con)
                title_list.append(item_title)
                url_list.append(item_url)
                con_list.append(item_con)
                time_list.append(item_time[0])
                writer.writerow((item_title, item_time[0], item_url, item_con))
            print("获取网页成功")
    except:
        print("获取网页失败")


def save(path):
    fname = path
    fp = open(fname, 'a', newline='', encoding='utf-8-sig')
    writer = csv.writer(fp)
    writer.writerow(("标题", "时间", "URL", "正文内容"))
    return writer


def main(key_word, beginPage, endPage):
    title_list = []
    url_list = []
    con_list = []
    time_list = []
    main_url = 'https://search.tianya.cn/bbs?q=' + str(key_word)

    fpath = r'dataset/天涯_' + key_word + '.csv'
    writer = save(fpath)
    getHtmlList(main_url, beginPage, endPage, writer, time_list, url_list, title_list, con_list)

    return time_list, url_list, title_list, con_list
