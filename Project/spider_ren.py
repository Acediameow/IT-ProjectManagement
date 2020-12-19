import csv
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
    
def get_content(url):
    #print(url)
    try:
        content = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(content,"html.parser")
        #来源
        ly = soup.find(attrs={"class":"fl"}).get_text()
        #print(ly)
        #正文
        zw = soup.find(attrs={"class":"box_con"})
        #防止某些文章仅图片
        if zw is not None:
            zw = zw.get_text()
            zw = zw.replace("\n", "")
        else:
            zw = ""
        print("succeed")
        return ly, zw
    except Exception as e:
        ly = ""
        page = url
        print("except")
        return ly, page

def ren_main():
    time_list, url_list, title_list, con_list = [], [], [], []
    url = "http://society.people.com.cn/GB/369130/431577/431608/index.html"
    driver = webdriver.Chrome() 
    driver.implicitly_wait(5)
    chrome_option = webdriver.ChromeOptions()
    driver.get(url) 
    driver.implicitly_wait(6) 
    
    con = []
    url_list = []
    
    titles = driver.find_elements_by_xpath('//div[@class=" p2j_list_lt fl"]/ul/li')
    for t in titles:
        con.append(t.text)
    links = driver.find_elements_by_xpath('//div[@class=" p2j_list_lt fl"]/ul/li/a')
    for link in links:
        url_list.append(link.get_attribute('href'))
        
    path = "dataset/人民网_疫情.csv"
    csvfile = open(path, 'a', newline='', encoding = 'utf-8-sig')
    writer = csv.writer(csvfile)
    writer.writerow(("标题", "时间", "URL", "正文内容"))
    
    k = 0
    while k<len(titles):
        con_title = con[k].split('\n')[0]
        con_time = con[k].split('\n')[1]
        url = url_list[k]
        ly, zw = get_content(url)

        time_list.append(con_time)
        url_list.append(url)
        title_list.append(con_title)
        con_list.append(zw)

        writer.writerow((con_title, con_time, url, zw))
        k += 1
        
    csvfile.close()
    return time_list, url_list, title_list, con_list