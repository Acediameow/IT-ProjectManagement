# 要用到的库
import jieba
import jieba.analyse
import re
import keras
import pandas as pd
from gensim.models import word2vec
import numpy as np
from sklearn.externals import joblib
from sklearn.decomposition import PCA
from elasticSearch import ElasticObj

obj = ElasticObj("ott", "_doc")


# 计算词向量
def getvec(sent, stopword, model):
    senvec = []
    word_l = jieba.analyse.extract_tags(sent, topK=50, withWeight=False, allowPOS=('a', 'e', 'n', 'nr', 'ns', 'v'))
    for word in word_l:
        if word in stopword:
            continue
        else:
            try:
                senvec.append(model[word])
            except:
                pass
    return np.array(senvec, dtype='float')


def build_vec(data, stopword, model):
    Input = []
    out_line = []
    for line in data:
        vec = getvec(line, stopword, model)
        if len(vec) != 0:
            res = sum(vec) / len(vec)
            Input.append(res)
        else:
            out_line.append(line)
    return Input, out_line


# 获得测试集
def get_train(data, stopword, model):
    pos, out_line = build_vec(data, stopword, model)
    X = pos[:]
    return np.array(X), out_line


# pca降维
def pca(X):
    pca = PCA().fit(X)
    X_reduced = PCA(n_components=20).fit_transform(X)
    return X_reduced


# 载入停用词文件
def stopw(file):
    stopword = []
    with open(file, 'r', encoding='utf-8') as text:
        s = re.split(u'\n', text.read())
        for word in s:
            stopword.append(word)
    return stopword


# 预测
def predresult(name):
    oldname = name
    name = 'jieba/sentence_train_' + name + '.csv'
    # 载入数据
    data = pd.read_csv(name, delimiter=',', header=None, names='0', encoding='utf-8')
    data1 = data['0']
    # 停用词处理
    file1 = 'dataset/stopwords.txt'
    stopword = stopw(file1)
    # 特征提取关键词，计算词向量
    model = word2vec.Word2Vec.load('corpus.model')
    # 得到测试集
    X, out_line = get_train(data1, stopword, model)
    X_reduced = X.reshape(X.shape[0], 1, X.shape[1])
    # 找出无法预测的数据，删掉
    number = []
    for i in out_line:
        num = data[data['0'] == i].index.tolist()[0]
        number.append(num)
    # 预测类别
    keras.backend.clear_session()
    new_model = joblib.load('lstm_model_200.pkl')
    pred = new_model.predict(X_reduced)
    pred = np.abs(pred)
    pred_list = []
    for i in range(len(pred)):
        if pred[i][0] < 0.4:
            pred_list.append(0)
        else:
            pred_list.append(1)

    for i in number:
        pred_list.insert(int(i), 1)

    pred_list = pd.DataFrame(pred_list)
    data3 = []
    data2 = data['0']
    for i in range(len(data2)):
        data3.append(data2[i][:75])
    data3 = pd.DataFrame(data3)
    data_pred = pd.concat([data3, pred_list], axis=1)
    data_pred.columns = ['data', 'pred']
    data_dict = data_pred.set_index('data')['pred'].to_dict()
    oldname = 'dataset/' + oldname + '.csv'
    olddata = pd.read_csv(oldname)
    olddata['情感倾向'] = pred_list
    olddata.to_csv(oldname, index=False)
    obj.Index_Data_FromCSV(oldname)
    return data_dict
