import requests, csv
from lxml import html
from fake_useragent import UserAgent


def spider_html_info(url, writer, time_list, url_list, title_list, con_list):
    try:
        headers = {
            "User-Agent": UserAgent().chrome
        }
        response = requests.get(url=url, headers=headers).text
        text_html = html.fromstring(response)

        next_url = "http://www.chinanpo.gov.cn" + text_html.xpath('/html/body/div[2]/div/ul[1]/li[2]/a[2]/@href')[0]

        article_title = text_html.xpath('//*[@id="fontinfo"]/p[2]/b[1]//text()')
        title = "".join(article_title)
        if title == "":
            title = "".join(text_html.xpath('//*[@id="fontinfo"]/p[3]/b[1]//text()'))

        publish_time = text_html.xpath('/html/body/div[2]/div/ul[1]/li[3]/strong/text()')[0][5:]

        source_text = text_html.xpath('//*[@id="fontinfo"]/p[last()]//text()')[0]
        source = source_text[3:]

        text_list = text_html.xpath('//*[@id="fontinfo"]//text()')
        article_text = "".join(text_list).replace('\r\n', '').replace("\xa0", "").replace("\t", "").replace(source_text,
                                                                                                            "").replace(
            title, "")
        publish_time = str(publish_time) + " 00:00:00"
        time_list.append(publish_time)
        url_list.append(url)
        title_list.append(title)
        con_list.append(article_text)
        writer.writerow((title, publish_time, url, article_text))
    except:
        pass

    return next_url


def zu_main(st, end):
    count = 1
    start = st + 128010 - 1
    url = "http://www.chinanpo.gov.cn/1944/" + str(start) + "/index.html"

    fp = open('dataset/中国社会组织_疫情.csv', 'a', newline='', encoding='utf-8-sig')
    writer = csv.writer(fp)
    writer.writerow(("标题", "时间", "URL", "正文内容"))
    time_list, url_list, title_list, con_list = [], [], [], []

    for i in range(end - st + 1):
        next_url = spider_html_info(url, writer, time_list, url_list, title_list, con_list)
        url = next_url
        count = count + 1
    return time_list, url_list, title_list, con_list
