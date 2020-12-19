import datetime
import locale
from elasticSearch import ElasticObj

# 可以用中文格式化
locale.setlocale(locale.LC_CTYPE, 'chinese')

obj = ElasticObj("ott", "_doc")

def Get_time_every(begin_date_str, end_date_str):  #指定时间段
    date_list = []
    begin_date = datetime.datetime.strptime(begin_date_str, "%Y-%m-%d %H:%M:%S")
    end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y-%m-%d %H:%M:%S")
        date_list.append(date_str)
        begin_date += datetime.timedelta(days=1)
    return date_list

def Get_time_14():  # 往前回溯14天
    date_list = []
    end_date = datetime.datetime.now()
    begin_date = end_date - datetime.timedelta(days=14)
    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y-%m-%d %H:%M:%S")
        date_list.append(date_str)
        begin_date += datetime.timedelta(days=1)
    return date_list

def Get_time_every(begin_date_str, end_date_str):
    date_list = []
    begin_date = datetime.datetime.strptime(begin_date_str, "%Y-%m-%d %H:%M:%S")
    end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y-%m-%d %H:%M:%S")
        date_list.append(date_str)
        begin_date += datetime.timedelta(days=1)
    return date_list

def get_sentiment(date_list, word):
    date_every_sentiment = []
    date_list_new = []
    for i in range(len(date_list) - 1):
        data_sentiment = obj.Get_data_time(date_list[i], date_list[i + 1], word)
        if len(data_sentiment) == 0:
             continue
        else:
            date_list_new.append(date_list[i])
            sum = 0
            for j in data_sentiment:
                if j['_source']['sentiment'] not in ['1', '0']:
                    continue
                sum += int(j['_source']['sentiment'])
            date_every_sentiment.append(sum / len(data_sentiment))

    return [date_list_new, date_every_sentiment]

def draw_bar(date_list, word):
    date_every_num = []
    date_list_new = []
    for i in range(len(date_list) - 1):
        data = obj.Get_data_time(date_list[i], date_list[i + 1], word)
        if len(data) == 0:
             continue
        else:
            date_every_num.append(len(data))
            date_list_new.append(date_list[i])
    return [date_list_new, date_every_num]

