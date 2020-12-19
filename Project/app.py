from datetime import timedelta
import matplotlib.pyplot as plt
from flask import Flask, render_template, request
import config
from gensim.models import word2vec
import json
from elasticSearch import ElasticObj
import make_picture as mp
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from pyecharts.charts import WordCloud, Line, Bar
from pyecharts.globals import SymbolType
from spider_tian import main
from spider_wei import wei_main
from spider_ren import ren_main
from spider_dou import dou_main
from spider_tie import tie_main
from spider_zu import zu_main
import pie as pi
from tf_idf import tf_idf_cal
import pred as pr
import arima
import os

app = Flask(__name__)
# app.debug = True
app.config.from_object(config)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # 设置最大缓存时间

obj = ElasticObj("ott", "_doc")


# 主页
@app.route('/')
def index():
    return render_template('index.html')


# 热词搜索页面
@app.route('/hotword')
def hotword():
    return render_template('hotword.html')


# 爬虫页面
@app.route('/pa')
def pa():
    return render_template('pa.html')


# 情感趋势页面
@app.route('/trend')
def trend():
    return render_template('trend.html')


# 根据时间和关键词搜索相关词条页面
@app.route('/search')
def search():
    return render_template('search.html')


# 用户登录页面
@app.route('/login')
def login():
    return render_template('login.html')


# 疫情可视化页面
@app.route('/visual')
def visual():
    return render_template('visual.html')


# 相关词搜索页面
@app.route('/relatedwords')
def relatedwords():
    return render_template("search_related_words_page.html")


# 相关词显示页面
@app.route('/search/words', methods=['POST'])
def flask_json_analysis():
    if request.method == "POST":  # post请求
        json_data = request.form.get('json_data')  # json_data这个参数是前台html文件中定义的文件名  # json.dumps方法
        name = json.dumps(json_data, ensure_ascii=False)
        name = eval(name)
        model = word2vec.Word2Vec.load('corpus.model')
        indexes = model.wv.most_similar(name, topn=10)
        data1 = []
        data2 = []
        for index in indexes:
            data1.append(index[0])
            data2.append(index[1])
        pie = pi.pie_base(data1, data2)
        return render_template('search_word_results_page.html',
                               myechart=pie.render_embed(),
                               data_dict=dict(indexes),
                               word=name)


# 搜索词条显示页面
@app.route('/searchresult', methods=["POST"])
def query():
    search_text = request.form.get("word")
    begin = request.form.get("begin")
    end = request.form.get("end")
    choice = request.form.get("sentiment")
    if begin == "" and end == "" and choice == "":
        data = obj.Get_Data_By_Body("match", "content", search_text)
    elif begin != "" and end != "" and choice == "":
        data = obj.Get_data_time(begin, end, search_text)
    elif begin != "" and end != "" and choice != "":
        data = obj.Get_data_time_sentiment(begin, end, search_text, choice)
    dicd = {}
    for hit in data:
        dicd[hit['_source']['content']] = [hit['_score'], hit['_source']['time'], hit['_source']['sentiment']]
    return render_template('page.html', data_dict=dicd, length=len(dicd), word=search_text)


# 热搜词显示页面
@app.route('/hotwordresult', methods=["POST"])
def hotwordans():
    begindate = request.form.get("begin")
    enddate = request.form.get("end")
    begindate = begindate
    enddate = enddate
    data = obj.Hot_words_time(begindate, enddate)
    dicd = {}
    flag = 0
    for i in data:
        if flag == 10:
            break
        else:
            flag += 1
            dicd[i['key']] = i['doc_count']
    l = []
    for i in data:
        l.append((i['key'], i['doc_count']))
    word_cloud = (
        WordCloud()
            .add("", l, word_size_range=[15, 150], shape=SymbolType.DIAMOND)
    )
    return render_template('hotwordresult.html',
                           myechart=word_cloud.render_embed(),
                           data_dict=dicd,
                           begin=begindate,
                           end=enddate)


# 情感趋势显示页面
@app.route('/trendresult', methods=["POST"])
def trendresult():
    word = request.form.get("word")
    begin = request.form.get("begin")
    end = request.form.get("end")
    if begin == "" and end == "":
        date_list = mp.Get_time_14()  # 当前时间回溯14天
    else:
        date_list = mp.Get_time_every(begin, end)  # 当前时间段
    [date_list_new, date_every_sentiment] = mp.get_sentiment(date_list, word)
    [date_list_new, date_every_num] = mp.draw_bar(date_list, word)
    [date_l, true_l, predict_l] = arima.arima_model(date_list_new, date_every_sentiment)
    bar = Bar(init_opts=opts.InitOpts(theme=ThemeType.WESTEROS))
    dictd = {}
    for i in range(len(date_every_sentiment)):
        if date_every_sentiment[i] < 0.2:
            dictd[date_list_new[i]] = "高度预警"
        elif date_every_sentiment[i] < 0.3:
            dictd[date_list_new[i]] = "中度预警"
        elif date_every_sentiment[i] < 0.4:
            dictd[date_list_new[i]] = "低度预警"
    # 统计趋势
    c = (
        Line(init_opts=opts.InitOpts(theme=ThemeType.WESTEROS))
            .add_xaxis(date_l)
            .add_yaxis('实际值', true_l, is_connect_nones=True)
            .add_yaxis('预测值', predict_l, is_connect_nones=True)
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    )
    # 统计数量
    bar.add_xaxis(date_list_new)
    bar.add_yaxis("涉及的词条数量", date_every_num)
    # 预警
    return render_template('trendresult.html',
                           myechart1=c.render_embed(),
                           myechart2=bar.render_embed(),
                           begin=date_list[0],
                           end=date_list[-1],
                           data=dictd,
                           length=len(dictd))


# 爬虫结果页面
@app.route("/paresult")
def paresult():
    key = request.args.get('q')
    st = request.args.get('q1')
    en = request.args.get('q2')
    way = request.args.get('vehicle')
    # 人民网
    if way == "人民网":
        time_list, url_list, title_list, con_list = ren_main()
        res = []
        for i in range(len(time_list)):
            res.append({"k": time_list[i], "v": url_list[i], "j": title_list[i], "m": con_list[i]})
        with app.app_context():
            rendered = render_template('pa_tian.html',
                                       title="Search In “RenMinWang”",
                                       word=key,
                                       length=len(time_list),
                                       result=res)

    # 天涯论坛
    if way == "天涯论坛":
        time_list, url_list, title_list, con_list = main(key, int(st), int(en))
        res = []
        for i in range(len(time_list)):
            res.append({"k": time_list[i], "v": url_list[i], "j": title_list[i], "m": con_list[i]})
        with app.app_context():
            rendered = render_template('pa_tian.html',
                                       title="Search In “TianYaLunTan”",
                                       word=key,
                                       length=len(time_list),
                                       result=res)

    # 微博
    if way == "微博":
        res = wei_main(key, int(st), int(en))
        with app.app_context():
            rendered = render_template('pa_wei.html',
                                       title="Search In “WeiBo”",
                                       word=key,
                                       length=len(res),
                                       result=res)

    # 豆瓣
    if way == "豆瓣":
        time_list, url_list, title_list, con_list = dou_main(key)
        res = []
        for i in range(len(time_list)):
            res.append({"k": time_list[i], "v": url_list[i], "j": title_list[i], "m": con_list[i]})
        with app.app_context():
            rendered = render_template('pa_tian.html',
                                       title="Search In “DouBan”",
                                       word=key,
                                       length=len(time_list),
                                       result=res)

    # 贴吧
    if way == "贴吧":
        time_list, url_list, title_list, con_list = tie_main(key, int(st), int(en))
        res = []
        for i in range(len(time_list)):
            res.append({"k": time_list[i], "v": url_list[i], "j": title_list[i], "m": con_list[i]})
        with app.app_context():
            rendered = render_template('pa_tian.html',
                                       title="Search In “BaiDuTieBa”",
                                       word=key,
                                       length=len(time_list),
                                       result=res)

    # 组织网
    if way == "组织网":
        time_list, url_list, title_list, con_list = zu_main(int(st), int(en))
        res = []
        for i in range(len(time_list)):
            res.append({"k": time_list[i], "v": url_list[i], "j": title_list[i], "m": con_list[i]})
        with app.app_context():
            rendered = render_template('pa_tian.html',
                                       title="Search In “TianYaLunTan”",
                                       word=key,
                                       length=len(time_list),
                                       result=res)
    return rendered


@app.route("/tf_idf")
def tfidf():
    return render_template('tf_idf.html')


@app.route("/tf_sou")
def tfsou():
    key = request.args.get('q')
    keywords = tf_idf_cal(key)

    with app.app_context():
        rendered = render_template('tf_idf_res.html',
                                   title="TF_IDF特征词提取",
                                   word=key,
                                   result=keywords,
                                   name=plt.show())
    return rendered


# 特征词搜索
@app.route("/tf")
def show():
    return render_template('tf_idf_show.html')


# 特征词搜索结果
@app.route("/tf_show")
def hello():
    key = request.args.get('q')
    keywords = tf_idf_cal(key)
    bar_get = bar(keywords)
    return render_template('bar1.html',
                           myechart=bar_get.render_embed(),
                           host=3333)


# 预测搜索页面
@app.route('/pred')
def pred():
    return render_template("pred_search.html")


# 预测结果页面
@app.route('/predresult', methods=['POST'])
def predresult():
    if request.method == "POST":
        json_data = request.form.get('json_data')
        name = json.dumps(json_data, ensure_ascii=False)
        name = eval(name)
        data_pred = pr.predresult(name)
        return render_template("pred_results.html", data_dict=data_pred)


# 各种pyecharts产物
@app.route('/line')
def line():
    return render_template('line.html')


@app.route('/wordcloud')
def wordcloud():
    return render_template('wordcloud.html')


@app.route('/pie')
def pie():
    return render_template('pie.html')


@app.route('/bar')
def bar():
    return render_template('bar.html')


def bar(keywords):
    xaxis = []
    yaxis = []
    for i in keywords:
        xaxis.append(i[0])
        yaxis.append(i[1])

    bar = Bar(init_opts=opts.InitOpts(theme=ThemeType.WALDEN))
    bar.add_xaxis(xaxis[:25])
    bar.add_yaxis("重要性", yaxis[:25])

    bar.set_global_opts(title_opts=opts.TitleOpts(title='TF-IDF Ranking'))
    bar.set_global_opts(toolbox_opts=opts.ToolboxOpts(is_show=True))
    bar.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    bar.reversal_axis()
    return bar


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3333, threaded=False)
